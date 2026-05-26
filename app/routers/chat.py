import json
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core import store
from app.core.dependencies import get_api_key_user
from app.models.requests import ChatCompletionRequest, ExtractRequest
from app.providers.base import ChatRequest, Message
from app.providers.registry import get_provider
from app.services import session as session_svc
from app.services.cost import estimate_cost

router = APIRouter(prefix="/v1", tags=["chat"])


def _build_provider_request(body: ChatCompletionRequest, history: list[Message]) -> ChatRequest:
    incoming = [Message(role=m.role, content=m.content) for m in body.messages]
    messages = history + incoming
    return ChatRequest(
        model=body.model,
        messages=messages,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
        stream=body.stream,
        session_id=body.session_id,
    )


@router.post("/chat")
async def chat(
    body: ChatCompletionRequest,
    user: store.User = Depends(get_api_key_user),
):
    try:
        provider = get_provider(body.model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    history = session_svc.get_history(body.session_id) if body.session_id else []
    req = _build_provider_request(body, history)

    if body.stream:
        return StreamingResponse(
            _stream_generator(provider, req, body, user),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    resp = await provider.complete(req)
    cost = estimate_cost(resp.model, resp.usage.prompt_tokens, resp.usage.completion_tokens)

    if body.session_id:
        last_user = Message(role="user", content=body.messages[-1].content)
        assistant = Message(role="assistant", content=resp.content)
        session_svc.append_exchange(body.session_id, last_user, assistant)

    return {
        "id": resp.id,
        "model": resp.model,
        "provider": resp.provider,
        "content": resp.content,
        "usage": {
            "prompt_tokens": resp.usage.prompt_tokens,
            "completion_tokens": resp.usage.completion_tokens,
            "total_tokens": resp.usage.total_tokens,
        },
        "estimated_cost_usd": round(cost, 8),
    }


async def _stream_generator(provider, req: ChatRequest, body: ChatCompletionRequest, user: store.User):
    """SSE generator — yields chunks then [DONE]."""
    collected: list[str] = []
    try:
        async for chunk in provider.stream(req):
            collected.append(chunk)
            yield f"data: {json.dumps({'content': chunk})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return

    full_content = "".join(collected)
    if body.session_id:
        last_user = Message(role="user", content=body.messages[-1].content)
        assistant = Message(role="assistant", content=full_content)
        session_svc.append_exchange(body.session_id, last_user, assistant)

    yield "data: [DONE]\n\n"


@router.delete("/sessions/{session_id}", status_code=204)
async def clear_session(session_id: str, user: store.User = Depends(get_api_key_user)):
    session_svc.clear_session(session_id)


@router.post("/extract")
async def extract(
    body: ExtractRequest,
    user: store.User = Depends(get_api_key_user),
):
    """Structured extraction using Instructor. Returns JSON validated against response_schema."""
    try:
        provider = get_provider(body.model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    import instructor
    from pydantic import create_model
    from pydantic import Field as PydanticField

    # Build a Pydantic model from the user-supplied JSON Schema properties
    schema_props: dict = body.response_schema.get("properties", {})
    required_fields: list = body.response_schema.get("required", list(schema_props.keys()))

    field_definitions: dict = {}
    type_map = {"string": str, "integer": int, "number": float, "boolean": bool, "array": list}
    for field_name, field_schema in schema_props.items():
        py_type = type_map.get(field_schema.get("type", "string"), str)
        if field_name in required_fields:
            field_definitions[field_name] = (py_type, ...)
        else:
            field_definitions[field_name] = (py_type, None)

    if not field_definitions:
        raise HTTPException(status_code=422, detail="response_schema must have at least one property")

    DynamicModel = create_model("ExtractedData", **field_definitions)

    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    # Use Instructor with the appropriate client
    from app.core.config import settings
    if provider.name == "openai":
        from openai import AsyncOpenAI
        client = instructor.from_openai(AsyncOpenAI(api_key=settings.openai_api_key))
    elif provider.name == "anthropic":
        from anthropic import AsyncAnthropic
        client = instructor.from_anthropic(AsyncAnthropic(api_key=settings.anthropic_api_key))
    else:
        raise HTTPException(status_code=400, detail="provider_not_supported_for_extract")

    result = await client.chat.completions.create(
        model=body.model,
        messages=messages,
        response_model=DynamicModel,
        max_tokens=body.max_tokens,
    )

    return result.model_dump()

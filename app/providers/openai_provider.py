import uuid
from typing import AsyncIterator

from openai import AsyncOpenAI

from app.core.config import settings
from app.providers.base import ChatProvider, ChatRequest, ChatResponse, Usage, Message


def _to_openai_messages(messages: list[Message]) -> list[dict]:
    return [{"role": m.role, "content": m.content} for m in messages]


class OpenAIProvider(ChatProvider):
    name = "openai"

    def __init__(self):
        self._client: AsyncOpenAI | None = None

    @property
    def is_configured(self) -> bool:
        return bool(settings.openai_api_key)

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    async def complete(self, request: ChatRequest) -> ChatResponse:
        client = self._get_client()
        resp = await client.chat.completions.create(
            model=request.model,
            messages=_to_openai_messages(request.messages),
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        choice = resp.choices[0]
        usage = resp.usage
        return ChatResponse(
            id=resp.id,
            model=resp.model,
            content=choice.message.content or "",
            usage=Usage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
            ),
            provider=self.name,
        )

    async def stream(self, request: ChatRequest) -> AsyncIterator[str]:
        client = self._get_client()
        async with client.chat.completions.stream(
            model=request.model,
            messages=_to_openai_messages(request.messages),
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        ) as stream:
            async for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    yield delta

import uuid
from typing import AsyncIterator

from anthropic import AsyncAnthropic

from app.core.config import settings
from app.providers.base import ChatProvider, ChatRequest, ChatResponse, Usage, Message


def _split_messages(messages: list[Message]) -> tuple[str | None, list[dict]]:
    """Anthropic requires system prompt as a top-level param, not in messages."""
    system: str | None = None
    chat: list[dict] = []
    for m in messages:
        if m.role == "system":
            system = m.content
        else:
            chat.append({"role": m.role, "content": m.content})
    return system, chat


class AnthropicProvider(ChatProvider):
    name = "anthropic"

    def __init__(self):
        self._client: AsyncAnthropic | None = None

    @property
    def is_configured(self) -> bool:
        return bool(settings.anthropic_api_key)

    def _get_client(self) -> AsyncAnthropic:
        if self._client is None:
            self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def complete(self, request: ChatRequest) -> ChatResponse:
        client = self._get_client()
        system, chat_messages = _split_messages(request.messages)

        kwargs: dict = dict(
            model=request.model,
            messages=chat_messages,
            max_tokens=request.max_tokens,
        )
        if system:
            kwargs["system"] = system

        resp = await client.messages.create(**kwargs)
        content = resp.content[0].text if resp.content else ""
        return ChatResponse(
            id=resp.id,
            model=resp.model,
            content=content,
            usage=Usage(
                prompt_tokens=resp.usage.input_tokens,
                completion_tokens=resp.usage.output_tokens,
                total_tokens=resp.usage.input_tokens + resp.usage.output_tokens,
            ),
            provider=self.name,
        )

    async def stream(self, request: ChatRequest) -> AsyncIterator[str]:
        client = self._get_client()
        system, chat_messages = _split_messages(request.messages)

        kwargs: dict = dict(
            model=request.model,
            messages=chat_messages,
            max_tokens=request.max_tokens,
        )
        if system:
            kwargs["system"] = system

        async with client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text

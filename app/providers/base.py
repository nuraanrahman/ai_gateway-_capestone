from abc import ABC, abstractmethod
from typing import AsyncIterator
from dataclasses import dataclass


@dataclass
class Message:
    role: str   # "system" | "user" | "assistant"
    content: str


@dataclass
class ChatRequest:
    model: str
    messages: list[Message]
    max_tokens: int = 1024
    temperature: float = 1.0
    stream: bool = False
    session_id: str | None = None


@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ChatResponse:
    id: str
    model: str
    content: str
    usage: Usage
    provider: str


class ChatProvider(ABC):
    name: str = ""

    @abstractmethod
    async def complete(self, request: ChatRequest) -> ChatResponse:
        """Return a full synchronous response."""
        ...

    @abstractmethod
    async def stream(self, request: ChatRequest) -> AsyncIterator[str]:
        """Yield content chunks as they arrive."""
        ...

    @property
    def is_configured(self) -> bool:
        """Return True when the required API key is present."""
        return True

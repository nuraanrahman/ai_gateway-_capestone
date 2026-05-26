from pydantic import BaseModel, Field
from typing import Optional, Any


class RegisterRequest(BaseModel):
    email: str = Field(..., examples=["dev@example.com"])
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: str
    password: str


class CreateKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, examples=["my-app"])


class MessageInput(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = Field(..., examples=["gpt-4o-mini", "claude-haiku-4-5"])
    messages: list[MessageInput]
    max_tokens: int = Field(default=1024, ge=1, le=8192)
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    stream: bool = False
    session_id: Optional[str] = None


class ExtractRequest(BaseModel):
    model: str = Field(..., examples=["gpt-4o-mini"])
    messages: list[MessageInput]
    response_schema: dict[str, Any] = Field(..., description="JSON Schema for the desired output")
    max_tokens: int = Field(default=1024, ge=1, le=8192)

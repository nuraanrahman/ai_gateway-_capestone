from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class APIKeyResponse(BaseModel):
    id: str
    name: str
    key: str  # raw key — returned only once at creation
    created_at: datetime


class APIKeyInfo(BaseModel):
    id: str
    name: str
    created_at: datetime
    revoked: bool


class ErrorResponse(BaseModel):
    error: dict

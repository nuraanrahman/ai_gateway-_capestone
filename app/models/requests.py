from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    email: str = Field(..., examples=["dev@example.com"])
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: str
    password: str


class CreateKeyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, examples=["my-app"])

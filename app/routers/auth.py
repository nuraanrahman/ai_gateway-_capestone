from fastapi import APIRouter, Depends, HTTPException, status

from app.core import store
from app.core.dependencies import get_current_user
from app.core.security import hash_password, verify_password, create_access_token, generate_api_key
from app.models.requests import RegisterRequest, LoginRequest, CreateKeyRequest
from app.models.responses import TokenResponse, APIKeyResponse, APIKeyInfo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest):
    if store.get_user(body.email):
        raise HTTPException(status_code=409, detail="email_already_registered")
    user = store.create_user(body.email, hash_password(body.password))
    return {"id": user.id, "email": user.email}


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    user = store.get_user(body.email)
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials")
    return TokenResponse(access_token=create_access_token(user.email))


@router.post("/keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_key(body: CreateKeyRequest, user: store.User = Depends(get_current_user)):
    raw_key, hashed_key = generate_api_key()
    key = store.create_api_key(user.id, body.name, hashed_key)
    return APIKeyResponse(id=key.id, name=key.name, key=raw_key, created_at=key.created_at)


@router.get("/keys", response_model=list[APIKeyInfo])
async def list_keys(user: store.User = Depends(get_current_user)):
    return [
        APIKeyInfo(id=k.id, name=k.name, created_at=k.created_at, revoked=k.revoked)
        for k in store.list_user_keys(user.id)
    ]


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_key(key_id: str, user: store.User = Depends(get_current_user)):
    revoked = store.revoke_api_key(key_id, user.id)
    if not revoked:
        raise HTTPException(status_code=404, detail="key_not_found")

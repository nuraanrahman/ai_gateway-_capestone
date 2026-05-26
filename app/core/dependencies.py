from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core import store
from app.core.security import decode_access_token, hash_api_key

bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> store.User:
    """Validate JWT → return User. Used on auth-management routes."""
    token = credentials.credentials
    try:
        email = decode_access_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    if email is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_token")
    user = store.get_user(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found")
    return user


def get_api_key_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> store.User:
    """Validate gateway API key → return User. Used on all /v1/* routes."""
    raw_key = credentials.credentials
    hashed = hash_api_key(raw_key)
    key = store.get_api_key_by_hash(hashed)
    if key is None or key.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_api_key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = next((u for u in store.users.values() if u.id == key.user_id), None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user_not_found")
    return user

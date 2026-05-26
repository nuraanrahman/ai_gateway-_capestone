import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, ExpiredSignatureError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


# --- Passwords ---

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# --- JWTs ---

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "exp": expire}, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """Returns the subject (user email) or raises HTTPException-ready ValueError."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        return payload.get("sub")
    except ExpiredSignatureError:
        raise ValueError("token_expired")
    except JWTError:
        raise ValueError("token_invalid")


# --- API Keys ---

def generate_api_key() -> tuple[str, str]:
    """Returns (raw_key, hashed_key). Store the hash; return the raw key once."""
    raw = "gw-" + secrets.token_urlsafe(32)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()

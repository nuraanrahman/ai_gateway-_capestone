"""
In-memory store for users and API keys.
Survives the process lifetime — good enough for a capstone demo.
Replace with Redis/Postgres for a production build.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional
import uuid


@dataclass
class User:
    id: str
    email: str
    hashed_password: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class APIKey:
    id: str
    user_id: str
    name: str
    hashed_key: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    revoked: bool = False


# Module-level singletons — imported wherever needed
users: Dict[str, User] = {}           # email → User
api_keys: Dict[str, APIKey] = {}      # key_id → APIKey
api_key_hash_index: Dict[str, str] = {}  # hash → key_id  (fast lookup on each request)


def create_user(email: str, hashed_password: str) -> User:
    user = User(id=str(uuid.uuid4()), email=email, hashed_password=hashed_password)
    users[email] = user
    return user


def get_user(email: str) -> Optional[User]:
    return users.get(email)


def create_api_key(user_id: str, name: str, hashed_key: str) -> APIKey:
    key = APIKey(id=str(uuid.uuid4()), user_id=user_id, name=name, hashed_key=hashed_key)
    api_keys[key.id] = key
    api_key_hash_index[hashed_key] = key.id
    return key


def get_api_key_by_hash(hashed_key: str) -> Optional[APIKey]:
    key_id = api_key_hash_index.get(hashed_key)
    if key_id is None:
        return None
    return api_keys.get(key_id)


def revoke_api_key(key_id: str, user_id: str) -> bool:
    key = api_keys.get(key_id)
    if key is None or key.user_id != user_id:
        return False
    key.revoked = True
    api_key_hash_index.pop(key.hashed_key, None)
    return True


def list_user_keys(user_id: str) -> list[APIKey]:
    return [k for k in api_keys.values() if k.user_id == user_id]

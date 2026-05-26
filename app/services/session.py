"""
In-memory session store for conversation history.
Keyed by session_id. Each session holds an ordered list of messages.
"""
from collections import defaultdict
from app.providers.base import Message

_sessions: dict[str, list[Message]] = defaultdict(list)


def get_history(session_id: str) -> list[Message]:
    return list(_sessions[session_id])


def append_exchange(session_id: str, user_msg: Message, assistant_msg: Message) -> None:
    _sessions[session_id].append(user_msg)
    _sessions[session_id].append(assistant_msg)


def clear_session(session_id: str) -> bool:
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False

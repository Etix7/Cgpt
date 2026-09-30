"""Persistent chat history, keyed by chat id (like sgpt's --chat / --repl)."""

from __future__ import annotations

import json

from .config import CHAT_CACHE_DIR, cfg


class ChatSession:
    """Stores a conversation as a JSON list of {role, content} messages."""

    def __init__(self, chat_id: str) -> None:
        self.chat_id = chat_id
        self.path = CHAT_CACHE_DIR / f"{chat_id}.json"

    def load(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def save(self, messages: list[dict]) -> None:
        CHAT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        limit = cfg.get_int("CHAT_CACHE_LENGTH")
        if limit > 0 and len(messages) > limit:
            messages = messages[-limit:]
        self.path.write_text(json.dumps(messages, indent=2), encoding="utf-8")

    def exists(self) -> bool:
        return self.path.exists()

    @staticmethod
    def list_ids() -> list[str]:
        if not CHAT_CACHE_DIR.exists():
            return []
        return sorted(p.stem for p in CHAT_CACHE_DIR.glob("*.json"))

    def show(self) -> list[dict]:
        return self.load()

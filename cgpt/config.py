"""Configuration loading for Claude_Gpt.

Settings are resolved with this precedence (highest first):
    1. Command-line flags (handled in cli.py)
    2. Environment variables (CLAUDE_GPT_* and ANTHROPIC_API_KEY)
    3. The config file ~/.config/claude-gpt/.claude-gptrc  (INI-less KEY=VALUE format)
    4. Built-in defaults below
"""

from __future__ import annotations

import os
from pathlib import Path

# --- Paths -----------------------------------------------------------------

CONFIG_DIR = Path(os.environ.get("CLAUDE_GPT_CONFIG_DIR", Path.home() / ".config" / "claude-gpt"))
CONFIG_PATH = CONFIG_DIR / ".claude-gptrc"
ROLES_DIR = CONFIG_DIR / "roles"
CHAT_CACHE_DIR = CONFIG_DIR / "chats"

# --- Defaults --------------------------------------------------------------

DEFAULTS: dict[str, str] = {
    "DEFAULT_MODEL": "claude-opus-5-5",
    "DEFAULT_MAX_TOKENS": "4096",
    # "adaptive" lets Claude decide how much to think; "off" disables it where
    # the model allows (see client.py for how this maps onto the request).
    "THINKING": "off",
    # Effort trades depth for speed/cost: low | medium | high | xhigh | max
    "EFFORT": "low",
    "CHAT_CACHE_LENGTH": "100",
    # Ask before running a generated shell command, or run it straight away.
    "SHELL_INTERACTION": "true",
    "CODE_THEME": "monokai",
    "PRETTIFY_MARKDOWN": "true",
    # OS/shell hints injected into the shell role. "auto" = detect at runtime.
    "OS_NAME": "auto",
    "SHELL_NAME": "auto",
}


def _read_config_file() -> dict[str, str]:
    if not CONFIG_PATH.exists():
        return {}
    values: dict[str, str] = {}
    for raw in CONFIG_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip()
    return values


def ensure_config() -> None:
    """Create the config dir and a default .claude-gptrc on first run."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ROLES_DIR.mkdir(parents=True, exist_ok=True)
    CHAT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_PATH.exists():
        lines = ["# claude-gpt configuration — edit values as you like\n"]
        lines += [f"{k}={v}" for k, v in DEFAULTS.items()]
        CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


class Config:
    """Resolved configuration with env > file > defaults precedence."""

    def __init__(self) -> None:
        self._file = _read_config_file()

    def get(self, key: str) -> str:
        env = os.environ.get(f"CLAUDE_GPT_{key}")
        if env is not None:
            return env
        if key in self._file:
            return self._file[key]
        return DEFAULTS.get(key, "")

    def get_bool(self, key: str) -> bool:
        return self.get(key).strip().lower() in {"1", "true", "yes", "on"}

    def get_int(self, key: str) -> int:
        try:
            return int(self.get(key))
        except (TypeError, ValueError):
            return int(DEFAULTS.get(key, "0") or 0)

    @property
    def api_key(self) -> str | None:
        # The Anthropic SDK also reads ANTHROPIC_API_KEY itself, but we surface
        # a friendly error early if nothing is configured.
        return os.environ.get("ANTHROPIC_API_KEY") or self._file.get("ANTHROPIC_API_KEY")


cfg = Config()

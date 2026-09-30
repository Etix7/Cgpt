"""Orchestrates a single request: build messages, stream the answer, render it,
and persist chat history when a chat id is given."""

from __future__ import annotations

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from .cache import ChatSession
from .client import ClaudeClient
from .config import cfg
from .roles import Role

console = Console()


class Handler:
    def __init__(
        self,
        role: Role,
        model: str | None = None,
        max_tokens: int | None = None,
        chat_id: str | None = None,
        markdown: bool | None = None,
    ) -> None:
        self.role = role
        self.client = ClaudeClient(model=model, max_tokens=max_tokens)
        self.chat_id = chat_id
        self.session = ChatSession(chat_id) if chat_id else None
        # Raw roles (shell/code) must never be prettified — we need the exact text.
        raw = role.name in {"shell", "code", "describe_shell"}
        self.markdown = (
            (cfg.get_bool("PRETTIFY_MARKDOWN") if markdown is None else markdown)
            and not raw
        )

    def _messages(self, prompt: str) -> tuple[list[dict], list[dict]]:
        history = self.session.load() if self.session else []
        messages = history + [{"role": "user", "content": prompt}]
        return history, messages

    def run(self, prompt: str) -> str:
        history, messages = self._messages(prompt)

        if self.markdown:
            answer = self._stream_markdown(messages)
        else:
            answer = self._stream_plain(messages)

        if self.session is not None:
            history.append({"role": "user", "content": prompt})
            history.append({"role": "assistant", "content": answer})
            self.session.save(history)
        return answer

    def _stream_plain(self, messages: list[dict]) -> str:
        parts: list[str] = []
        for chunk in self.client.stream(self.role.prompt, messages):
            parts.append(chunk)
            console.print(chunk, end="", markup=False, highlight=False)
        console.print()
        return "".join(parts)

    def _stream_markdown(self, messages: list[dict]) -> str:
        parts: list[str] = []
        theme = cfg.get("CODE_THEME")
        with Live(console=console, refresh_per_second=12, vertical_overflow="visible") as live:
            for chunk in self.client.stream(self.role.prompt, messages):
                parts.append(chunk)
                live.update(Markdown("".join(parts), code_theme=theme))
        return "".join(parts)

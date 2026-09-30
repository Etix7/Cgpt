"""Thin wrapper over the Anthropic SDK for cgpt.

Uses streaming so long outputs never hit HTTP timeouts and so the REPL/answer
can render tokens as they arrive.
"""

from __future__ import annotations

from collections.abc import Iterator

from anthropic import Anthropic

from .config import cfg


class ClaudeClient:
    def __init__(self, model: str | None = None, max_tokens: int | None = None) -> None:
        # The SDK reads ANTHROPIC_API_KEY from the environment. We only pass a
        # key explicitly if the user put one in the config file instead.
        api_key = cfg.api_key
        self._client = Anthropic(api_key=api_key) if api_key else Anthropic()
        self.model = model or cfg.get("DEFAULT_MODEL")
        self.max_tokens = max_tokens or cfg.get_int("DEFAULT_MAX_TOKENS")

    def _request_kwargs(self, system: str, messages: list[dict]) -> dict:
        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": messages,
        }

        # Effort (low..max) is a GA control on current models; harmless to send.
        effort = cfg.get("EFFORT").strip().lower()
        if effort in {"low", "medium", "high", "xhigh", "max"}:
            kwargs["output_config"] = {"effort": effort}

        # Thinking: "adaptive" turns it on and lets Claude budget it; "off"
        # leaves it unset so the model runs at its default (fast for shell use).
        thinking = cfg.get("THINKING").strip().lower()
        if thinking == "adaptive":
            kwargs["thinking"] = {"type": "adaptive"}

        return kwargs

    def stream(self, system: str, messages: list[dict]) -> Iterator[str]:
        """Yield text chunks as they are generated."""
        kwargs = self._request_kwargs(system, messages)
        with self._client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                yield text

    def complete(self, system: str, messages: list[dict]) -> str:
        """Return the full response text (still streamed under the hood)."""
        return "".join(self.stream(system, messages))

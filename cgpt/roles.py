"""Built-in and user-defined roles (system prompts) for cgpt."""

from __future__ import annotations

import json
import platform
from dataclasses import dataclass

from .config import ROLES_DIR, cfg


def _detect_os() -> str:
    override = cfg.get("OS_NAME")
    if override and override != "auto":
        return override
    system = platform.system()
    if system == "Linux":
        # Try to enrich with the distribution name when available.
        try:
            data = {}
            with open("/etc/os-release", encoding="utf-8") as fh:
                for line in fh:
                    if "=" in line:
                        k, _, v = line.partition("=")
                        data[k] = v.strip().strip('"')
            pretty = data.get("PRETTY_NAME")
            if pretty:
                return f"Linux/{pretty}"
        except OSError:
            pass
        return "Linux"
    if system == "Darwin":
        return f"macOS {platform.mac_ver()[0]}".strip()
    if system == "Windows":
        return f"Windows {platform.release()}"
    return system or "unknown"


def _detect_shell() -> str:
    import os

    override = cfg.get("SHELL_NAME")
    if override and override != "auto":
        return override
    if platform.system() == "Windows":
        # PSModulePath is set inside PowerShell sessions.
        if os.environ.get("PSModulePath"):
            return "powershell.exe"
        return "cmd.exe"
    shell = os.environ.get("SHELL", "/bin/bash")
    return shell.rsplit("/", 1)[-1]


# --- Built-in role prompts -------------------------------------------------

DEFAULT_ROLE = """You are cgpt, a concise programming and system-administration assistant.
You answer questions directly and factually. Provide short, correct answers.
Prefer code and commands over prose. Do not add warnings or notes unless asked."""


def shell_role() -> str:
    return f"""You are a shell-command generator.
Operating system: {_detect_os()}
Shell: {_detect_shell()}

Return ONLY a single shell command (or a chain joined with the shell's operators)
that accomplishes the user's request. Output the raw command with no code fences,
no markdown, no explanation, and no leading prompt characters. If details are
missing, choose sensible defaults. If the request cannot be done with a command,
reply with a short message starting with 'echo '."""


DESCRIBE_SHELL_ROLE = """You describe shell commands.
Given a shell command, explain concisely what it does, argument by argument.
Be brief. Use a short bullet list. Do not suggest alternatives unless asked."""


def code_role() -> str:
    return """You are a code generator.
Return ONLY source code that fulfills the request. Output raw code with no markdown
code fences, no explanations, and no commentary before or after. If a language is
not specified, infer the most appropriate one from the request."""


@dataclass
class Role:
    name: str
    prompt: str

    @classmethod
    def get(cls, name: str) -> "Role":
        builtins = {
            "default": DEFAULT_ROLE,
            "shell": shell_role(),
            "describe_shell": DESCRIBE_SHELL_ROLE,
            "code": code_role(),
        }
        if name in builtins:
            return cls(name, builtins[name])
        path = ROLES_DIR / f"{name}.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls(data["name"], data["prompt"])
        raise KeyError(f"Role '{name}' not found. Create it with: cgpt --create-role {name}")

    def save(self) -> None:
        ROLES_DIR.mkdir(parents=True, exist_ok=True)
        path = ROLES_DIR / f"{self.name}.json"
        path.write_text(
            json.dumps({"name": self.name, "prompt": self.prompt}, indent=2),
            encoding="utf-8",
        )

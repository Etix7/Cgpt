"""cgpt command-line interface — an sgpt-style assistant powered by Claude."""

from __future__ import annotations

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.rule import Rule

from . import __version__
from .cache import ChatSession
from .config import cfg, ensure_config
from .handler import Handler
from .roles import Role
from .shell import run_command

console = Console()
err = Console(stderr=True)

app = typer.Typer(
    add_completion=False,
    no_args_is_help=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    help="cgpt — ask Claude from your terminal. Generate shell commands, code, or answers.",
)


def _read_stdin() -> str:
    if sys.stdin is not None and not sys.stdin.isatty():
        return sys.stdin.read().strip()
    return ""


def _resolve_role(shell: bool, code: bool, describe_shell: bool, role: Optional[str]) -> Role:
    if role:
        return Role.get(role)
    if shell:
        return Role.get("shell")
    if code:
        return Role.get("code")
    if describe_shell:
        return Role.get("describe_shell")
    return Role.get("default")


def _shell_interaction(command: str, model: Optional[str], max_tokens: Optional[int]) -> None:
    """Offer Execute / Describe / Abort for a generated shell command."""
    if not cfg.get_bool("SHELL_INTERACTION"):
        console.print(command, markup=False, highlight=False)
        return
    while True:
        choice = typer.prompt(
            "[E]xecute, [D]escribe, [A]bort", default="e", show_default=False
        ).strip().lower()
        if choice in {"e", "execute", ""}:
            code = run_command(command)
            if code != 0:
                err.print(f"[yellow]Command exited with status {code}.[/yellow]")
            return
        if choice in {"d", "describe"}:
            handler = Handler(Role.get("describe_shell"), model=model, max_tokens=max_tokens)
            handler.run(command)
            continue
        if choice in {"a", "abort"}:
            err.print("[dim]Aborted.[/dim]")
            return


def _repl(chat_id: str, role: Role, model: Optional[str], max_tokens: Optional[int], md: Optional[bool]) -> None:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory

    handler = Handler(role, model=model, max_tokens=max_tokens, chat_id=chat_id, markdown=md)
    session = ChatSession(chat_id)
    console.print(Rule(f"cgpt REPL · chat '{chat_id}' · role '{role.name}'"))
    console.print("[dim]Type your message. Commands: exit | quit | /shell <cmd> | /clear[/dim]")
    if session.exists():
        console.print(f"[dim]Resuming — {len(session.load()) // 2} previous exchange(s).[/dim]")

    pt = PromptSession(history=InMemoryHistory())
    while True:
        try:
            text = pt.prompt(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Bye.[/dim]")
            return
        if not text:
            continue
        if text in {"exit", "quit"}:
            return
        if text == "/clear":
            session.save([])
            console.print("[dim]History cleared.[/dim]")
            continue
        if text.startswith("/shell "):
            run_command(text[len("/shell "):])
            continue
        handler.run(text)


@app.command()
def main(
    prompt: Optional[str] = typer.Argument(None, help="The prompt to send to Claude."),
    shell: bool = typer.Option(False, "--shell", "-s", help="Generate and optionally run a shell command."),
    code: bool = typer.Option(False, "--code", "-c", help="Generate code only (no prose)."),
    describe_shell: bool = typer.Option(False, "--describe-shell", "-d", help="Explain a shell command."),
    role: Optional[str] = typer.Option(None, "--role", help="Use a named role (system prompt)."),
    chat: Optional[str] = typer.Option(None, "--chat", help="Continue a persistent chat by id."),
    repl: Optional[str] = typer.Option(None, "--repl", help="Start an interactive REPL for the given chat id."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override the Claude model."),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Max output tokens."),
    md: Optional[bool] = typer.Option(None, "--md/--no-md", help="Force markdown rendering on/off."),
    create_role: Optional[str] = typer.Option(None, "--create-role", help="Create a role interactively."),
    show_role: Optional[str] = typer.Option(None, "--show-role", help="Print a role's prompt."),
    list_roles: bool = typer.Option(False, "--list-roles", help="List available roles."),
    list_chats: bool = typer.Option(False, "--list-chats", help="List saved chat ids."),
    show_chat: Optional[str] = typer.Option(None, "--show-chat", help="Print a saved chat."),
    version: bool = typer.Option(False, "--version", help="Show version and exit."),
) -> None:
    ensure_config()

    if version:
        console.print(f"cgpt {__version__}")
        raise typer.Exit()

    # --- Role management -------------------------------------------------
    if create_role:
        console.print(f"Enter the system prompt for role '{create_role}' (end with Ctrl-D / Ctrl-Z):")
        body = sys.stdin.read().strip()
        Role(create_role, body).save()
        console.print(f"[green]Saved role '{create_role}'.[/green]")
        raise typer.Exit()
    if show_role:
        console.print(Role.get(show_role).prompt)
        raise typer.Exit()
    if list_roles:
        from .config import ROLES_DIR

        builtins = ["default", "shell", "code", "describe_shell"]
        custom = [p.stem for p in ROLES_DIR.glob("*.json")] if ROLES_DIR.exists() else []
        for name in builtins:
            console.print(f"{name} [dim](built-in)[/dim]")
        for name in sorted(custom):
            console.print(name)
        raise typer.Exit()

    # --- Chat management -------------------------------------------------
    if list_chats:
        ids = ChatSession.list_ids()
        console.print("\n".join(ids) if ids else "[dim]No saved chats.[/dim]")
        raise typer.Exit()
    if show_chat:
        for msg in ChatSession(show_chat).show():
            tag = "you" if msg["role"] == "user" else "claude"
            console.print(Rule(tag))
            console.print(msg["content"], markup=False)
        raise typer.Exit()

    resolved_role = _resolve_role(shell, code, describe_shell, role)

    # --- REPL ------------------------------------------------------------
    if repl:
        _repl(repl, resolved_role, model, max_tokens, md)
        raise typer.Exit()

    # --- Assemble the prompt (arg + piped stdin) -------------------------
    stdin_text = _read_stdin()
    parts = [p for p in (stdin_text, prompt) if p]
    full_prompt = "\n\n".join(parts).strip()
    if not full_prompt:
        err.print("[red]No prompt provided.[/red] Pass text as an argument or pipe it via stdin.")
        raise typer.Exit(code=1)

    handler = Handler(
        resolved_role, model=model, max_tokens=max_tokens, chat_id=chat, markdown=md
    )
    answer = handler.run(full_prompt)

    # After generating a shell command, offer to run it.
    if resolved_role.name == "shell":
        _shell_interaction(answer.strip(), model, max_tokens)


if __name__ == "__main__":
    app()

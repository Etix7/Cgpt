# cgpt

A command-line productivity tool powered by **Claude** — a
[shell_gpt](https://github.com/ther1d/shell_gpt)-style assistant that lives in
your terminal. Ask questions, generate and run shell commands, produce code, and
hold persistent conversations, all from the shell.

Built on the official [`anthropic`](https://pypi.org/project/anthropic/) SDK.

## Features

- **Q&A** — `cgpt "how do I flatten a list in Python?"`
- **Shell commands** — `cgpt -s "find files larger than 100MB"` → generates the
  command and offers **[E]xecute / [D]escribe / [A]bort**
- **Code only** — `cgpt -c "fizzbuzz in rust"` → raw code, no prose
- **Explain a command** — `cgpt -d "tar -xzvf a.tar.gz"`
- **Reads stdin** — `git diff | cgpt "write a commit message"`
- **Persistent chats** — `cgpt --chat mychat "..."` remembers context
- **Interactive REPL** — `cgpt --repl mychat`
- **Custom roles** — reusable system prompts
- Streaming output with Markdown + syntax highlighting

## Install

```bash
cd cgpt
pip install -e .
```

Set your API key (the SDK reads it from the environment):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# Windows PowerShell:  $env:ANTHROPIC_API_KEY = "sk-ant-..."
```

## Usage

```bash
# Simple question
cgpt "what is the difference between TCP and UDP?"

# Generate a shell command and choose what to do with it
cgpt -s "recursively delete all .pyc files"

# Pipe context in
cat error.log | cgpt "what is causing this error?"

# Code generation
cgpt -c "python function to debounce calls" > debounce.py

# Persistent conversation
cgpt --chat refactor "here is my module: ..."
cgpt --chat refactor "now add type hints"

# Interactive REPL (commands: exit | /shell <cmd> | /clear)
cgpt --repl refactor

# Roles
cgpt --create-role sql        # paste a system prompt, end with Ctrl-D / Ctrl-Z
cgpt --role sql "top 5 customers by revenue"
cgpt --list-roles
```

## Configuration

On first run, `~/.config/cgpt/.cgptrc` is created. Every key can also be set via
a `CGPT_<KEY>` environment variable, which takes precedence.

| Key | Default | Meaning |
|-----|---------|---------|
| `DEFAULT_MODEL` | `claude-opus-5-5` | Model id. Use `claude-sonnet-5-5` or `claude-haiku-4-5` for faster/cheaper replies. |
| `DEFAULT_MAX_TOKENS` | `4096` | Max output tokens. |
| `THINKING` | `off` | `adaptive` to let Claude reason first; `off` for snappy answers. |
| `EFFORT` | `low` | `low`/`medium`/`high`/`xhigh`/`max` — depth vs. speed. |
| `SHELL_INTERACTION` | `true` | Prompt E/D/A after generating a shell command. |
| `PRETTIFY_MARKDOWN` | `true` | Render answers as Markdown. |
| `CODE_THEME` | `monokai` | Syntax-highlighting theme. |
| `OS_NAME` / `SHELL_NAME` | `auto` | Override the OS/shell hints given to the shell role. |

Override per-invocation:

```bash
cgpt -m claude-sonnet-5-5 "quick question"
cgpt --no-md -c "one-liner"
```

## Safety note

Generated shell commands are **not** run without your confirmation unless you set
`SHELL_INTERACTION=false`. Always read a command before executing it.

## Licence

**Propriétaire — Tous droits réservés.** Copyright © 2026 Étienne Bigant (Etix7).

Ce logiciel n'est **pas** open source. Toute copie, distribution, modification ou
réutilisation de tout ou partie du code est interdite sans autorisation écrite
préalable de l'auteur. Le simple fait que le dépôt soit consultable ne concède
aucun droit d'usage. Voir le fichier [LICENSE](LICENSE) pour les termes complets.

> Les dépendances tierces (SDK `anthropic`, `typer`, `rich`, `prompt_toolkit`)
> restent soumises à leurs propres licences.

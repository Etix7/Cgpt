# Claude_Gpt

> Open-source Claude-powered **cybersecurity** assistant for the terminal.
> The installed command is **`cgpt`**. Built for Kali Linux and any security workstation.

**Claude_Gpt** brings Claude to the place cyber professionals actually work — the
terminal. Ask security questions, generate ready-to-run commands for your favourite
tools (nmap, ffuf, nuclei, hashcat, sqlmap…), produce tooling scripts, and switch
between offensive, defensive and analysis mindsets with built-in **security roles**.

For pentesters, red/blue teamers, SOC analysts, CTF players, students and
researchers — working within authorized engagements, labs or CTFs.

Built on the official [`anthropic`](https://pypi.org/project/anthropic/) SDK.

## Features

- **Security Q&A** — `cgpt "explain how kerberoasting works and how to detect it"`
- **Shell commands** — `cgpt -s "nmap full TCP scan with service detection on 10.0.0.5"`
  → generates the command and offers **[E]xecute / [D]escribe / [A]bort**
- **Tooling & scripts** — `cgpt -c "python script to brute-force a login form"` → raw code
- **Explain a command** — `cgpt -d "hashcat -m 22000 hash.hc22000 wordlist.txt"`
- **Reads stdin** — `nmap -oX - 10.0.0.5 | cgpt "summarize the attack surface"`
- **Security roles** — `--role recon | web | exploit | blueteam | forensics | osint | ctf | report`
- **Persistent chats** & **interactive REPL** — keep engagement context across prompts
- **Custom roles** — save your own reusable system prompts
- Streaming output with Markdown + syntax highlighting

### Built-in security roles

| Role | Focus |
|------|-------|
| `default` | General cybersecurity assistant |
| `shell` (`-s`) | Generate a single command (security tooling aware) |
| `code` (`-c`) | Generate tooling / PoC / automation code |
| `recon` | Reconnaissance, enumeration, attack-surface mapping |
| `web` | Web app testing (OWASP, Burp, ffuf, sqlmap, nuclei) |
| `exploit` | Vulnerability / CVE / PoC analysis (with detection & fix) |
| `blueteam` | Detection engineering, hunting, hardening (Sigma/SPL/KQL/YARA) |
| `forensics` | DFIR — memory/disk/network/log analysis (Volatility, Sleuth Kit) |
| `osint` | Open-source intelligence & footprinting |
| `ctf` | CTF solving across pwn/rev/web/crypto/forensics |
| `report` | Turn findings into a professional pentest writeup |

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
# Security question
cgpt "how does an NTLM relay attack work, and how do I defend against it?"

# Generate a command and choose what to do with it (Execute / Describe / Abort)
cgpt -s "nmap top 1000 ports with service and OS detection on 10.10.10.0/24"

# Pipe recon output back in for analysis
nmap -sV -oX - 10.10.10.5 | cgpt "summarize the attack surface and likely entry points"
sudo tcpdump -c 200 -w - | cgpt "any suspicious traffic here?"

# Generate tooling / a PoC
cgpt -c "python script that fuzzes a URL parameter for SQLi and reports anomalies" > sqli_fuzz.py

# Security roles
cgpt --role recon "enumeration plan for an unauthenticated web host at 10.10.10.5"
cgpt --role web "test this login form for auth bypass: https://target.lab/login"
cgpt --role blueteam "write a Sigma rule for suspicious PowerShell encoded commands"
cgpt --role forensics "triage steps for a compromised Linux box, memory first"
cgpt --role osint "footprint the domain example.com from public sources only"

# Persistent engagement context + interactive REPL
cgpt --chat htb-boxA "target: 10.10.10.5, web on 80, ssh on 22. plan the assessment"
cgpt --chat htb-boxA "found a possible LFI on /view?file= — how do I confirm it?"
cgpt --repl htb-boxA          # commands: exit | /shell <cmd> | /clear

# Custom roles
cgpt --create-role ad         # paste a system prompt, end with Ctrl-D / Ctrl-Z
cgpt --role ad "BloodHound path from a low-priv user to Domain Admin — what to run?"
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

## Responsible use

Claude_Gpt is a tool for **authorized** security work only — engagements you have
written permission for, your own lab, or sanctioned CTFs. Do not use it against
systems you don't own or aren't allowed to test. You are responsible for what you
run: generated shell commands are **not** executed without your confirmation unless
you set `SHELL_INTERACTION=false`, so always read a command before running it.

## License

**GNU General Public License v3.0 or later (GPLv3+).** Copyright © 2026 Étienne Bigant (Etix7).

Claude_Gpt is free/open-source software: you may use, study, share and modify it.
If you distribute it or a modified version, that version must also be released under
the GPL and keep the source available — so it stays open for the whole community and
can't be repackaged as closed-source. See the [LICENSE](LICENSE) file for the full
terms, or <https://www.gnu.org/licenses/gpl-3.0.html>.

> Third-party dependencies (`anthropic`, `typer`, `rich`, `prompt_toolkit`) remain
> under their own licenses.

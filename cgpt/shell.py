"""Run generated shell commands, honouring the platform's shell."""

from __future__ import annotations

import os
import platform
import subprocess


def run_command(command: str) -> int:
    """Execute a command string in the user's shell. Returns the exit code."""
    system = platform.system()
    if system == "Windows":
        if os.environ.get("PSModulePath"):
            full = ["powershell.exe", "-NoProfile", "-Command", command]
        else:
            full = ["cmd.exe", "/c", command]
        completed = subprocess.run(full)
    else:
        shell = os.environ.get("SHELL", "/bin/bash")
        completed = subprocess.run([shell, "-c", command])
    return completed.returncode

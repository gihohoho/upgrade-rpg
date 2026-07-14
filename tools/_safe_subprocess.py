#!/usr/bin/env python3
"""Small subprocess helpers that decode mixed UTF-8/Windows console output safely."""
from __future__ import annotations

import locale
import subprocess
from pathlib import Path
from typing import Sequence


def decode_output(raw: bytes | None) -> str:
    if not raw:
        return ""

    encodings = ["utf-8-sig", locale.getpreferredencoding(False), "cp949"]
    tried: set[str] = set()
    for encoding in encodings:
        normalized = (encoding or "").lower()
        if not normalized or normalized in tried:
            continue
        tried.add(normalized)
        try:
            return raw.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue

    return raw.decode("utf-8", errors="replace")


def run_captured(
    command: Sequence[str],
    *,
    cwd: Path | str | None = None,
    timeout: float | None = None,
    check: bool = False,
) -> tuple[subprocess.CompletedProcess[bytes], str]:
    """Run a command and return safely decoded combined stdout/stderr."""
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        text=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
        timeout=timeout,
    )
    return completed, decode_output(completed.stdout).strip()

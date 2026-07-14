#!/usr/bin/env python3
"""Smoke checks for Windows cp949/UTF-8 subprocess output decoding."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from _safe_subprocess import run_captured  # noqa: E402


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    cases = [
        ("utf-8", "Docker 상태 → 정상"),
        ("cp949", "윈도우 한글 출력 정상"),
    ]
    for encoding, expected in cases:
        script = f"import sys; sys.stdout.buffer.write({expected!r}.encode({encoding!r}))"
        completed, output = run_captured([sys.executable, "-c", script], cwd=ROOT, timeout=10)
        if completed.returncode != 0:
            return fail(f"child command failed for {encoding}")
        if output != expected:
            return fail(f"decode mismatch for {encoding}: {output!r}")

    print("OK: Windows subprocess UTF-8/cp949 decode smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

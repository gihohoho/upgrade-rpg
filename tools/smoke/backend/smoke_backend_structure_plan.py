#!/usr/bin/env python3
"""Smoke check for the v274 backend structure plan."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / "docs/generated/BACKEND_STRUCTURE_PLAN.md"
TOOL = ROOT / "tools/report_backend_structure_plan.py"

REQUIRED_TEXT = [
    "Backend Structure Plan — v274",
    "문서화/분석 단계",
    "route path",
    "API response body",
    "Preview/Apply request body",
    "Write Guard",
    "DB schema",
    "authentication",
    "GET /api/v1/health",
    "GET /api/v1/admin/requirements",
    "v275 Backend route map 자동 보고서",
]


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if not TOOL.exists():
        return fail(f"missing tool: {TOOL.relative_to(ROOT).as_posix()}")
    if not REPORT.exists():
        return fail(f"missing report: {REPORT.relative_to(ROOT).as_posix()}")

    result = subprocess.run(
        [sys.executable, str(TOOL.relative_to(ROOT)), "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        return fail("backend structure report is not up to date")

    text = REPORT.read_text(encoding="utf-8")
    for needle in REQUIRED_TEXT:
        if needle not in text:
            return fail(f"report missing required text: {needle}")

    print("OK: backend structure plan smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

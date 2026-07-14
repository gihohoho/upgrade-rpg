#!/usr/bin/env python3
"""Smoke checks for the current PostgreSQL runtime inspection and baseline plan."""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_postgres_runtime_readonly_state.py"
STATE_DOC = ROOT / "docs/current/POSTGRES_RUNTIME_READONLY_STATE.md"
STRATEGY_DOC = ROOT / "docs/current/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    for path in (TOOL, STATE_DOC, STRATEGY_DOC):
        if not path.exists():
            return fail(f"missing file: {path.relative_to(ROOT).as_posix()}")

    source = TOOL.read_text(encoding="utf-8")
    ast.parse(source, filename=str(TOOL))

    required_markers = [
        '"readOnly": True',
        '"mutationCommandsExecuted": False',
        '["docker", "compose", "ps"]',
        '["docker", "volume", "inspect", name]',
        'SELECT COUNT(*)',
        'alembicVersionTableExists',
        'existing-schema-without-alembic-baseline',
        'schema-drift',
        'empty-database',
        'method="GET"',
    ]
    for marker in required_markers:
        if marker not in source:
            return fail(f"runtime checker missing marker: {marker}")

    forbidden_source = [
        "DROP SCHEMA",
        "TRUNCATE ",
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
        '["docker", "compose", "up"]',
        '["docker", "compose", "down"]',
        '["docker", "volume", "rm"]',
        '"revision", "--autogenerate"',
        '"upgrade", "head"',
        '"stamp", "head"',
    ]
    for marker in forbidden_source:
        if marker in source:
            return fail(f"runtime checker contains mutation marker: {marker}")

    run = subprocess.run(
        [sys.executable, str(TOOL), "--json", "--skip-counts", "--health-timeout", "0.1"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    if run.returncode != 0:
        sys.stdout.write(run.stdout)
        sys.stderr.write(run.stderr)
        return fail("runtime checker must return zero without --strict")
    payload = json.loads(run.stdout)
    if payload.get("readOnly") is not True:
        return fail("runtime checker must declare readOnly=true")
    if payload.get("mutationCommandsExecuted") is not False:
        return fail("runtime checker must declare mutationCommandsExecuted=false")
    if "database" not in payload or "health" not in payload or "docker" not in payload:
        return fail("runtime checker JSON shape is incomplete")

    state_text = STATE_DOC.read_text(encoding="utf-8")
    for marker in (
        "PostgreSQL 런타임 비파괴 상태 점검 — v287",
        "python tools/check_postgres_runtime_readonly_state.py",
        "existing-schema-without-alembic-baseline",
        "docker compose down -v",
    ):
        if marker not in state_text:
            return fail(f"runtime state doc missing: {marker}")

    strategy_text = STRATEGY_DOC.read_text(encoding="utf-8")
    for marker in (
        "PostgreSQL / Alembic 최초 baseline 전략 — v290",
        "existing-schema-without-alembic-baseline",
        "기존 `create_all()` schema와 데이터를 보존하는 baseline 방식",
        "python tools/check_postgres_schema_equivalence.py",
        "stamp head",
        "별도 빈 임시 PostgreSQL DB",
    ):
        if marker not in strategy_text:
            return fail(f"baseline strategy doc missing: {marker}")

    print("OK: PostgreSQL runtime read-only state smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

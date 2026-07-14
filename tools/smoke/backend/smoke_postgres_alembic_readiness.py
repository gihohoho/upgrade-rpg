#!/usr/bin/env python3
"""Smoke checks for the current PostgreSQL/Alembic preparation artifacts."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
REPORT_TOOL = ROOT / "tools/report_postgres_alembic_readiness.py"
CHECK_TOOL = ROOT / "tools/check_postgres_alembic_prerequisites.py"
STATE_TOOL = ROOT / "tools/check_alembic_readonly_state.py"
REPORT = ROOT / "docs/current/POSTGRES_ALEMBIC_READINESS.md"
CHECKLIST = ROOT / "docs/current/POSTGRES_ALEMBIC_LOCAL_CHECKLIST.md"
ASYNC_FIX_DOC = ROOT / "docs/current/ALEMBIC_ASYNC_ENV_FIX.md"
RUNTIME_TOOL = ROOT / "tools/check_postgres_runtime_readonly_state.py"
RUNTIME_DOC = ROOT / "docs/current/POSTGRES_RUNTIME_READONLY_STATE.md"
BASELINE_DOC = ROOT / "docs/current/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md"

REQUIRED_REPORT_TEXT = [
    "PostgreSQL / Alembic Readiness — v302",
    "SQLAlchemy model table 수 | 22개",
    "Alembic asyncpg-compatible online env | 있음",
    "Alembic versions 폴더 | 있음",
    "Alembic revision 수 | 1개",
    "async_engine_from_config()",
    "tools/check_postgres_runtime_readonly_state.py",
    "tools/check_postgres_schema_equivalence.py",
    "tools/check_postgres_backup_restore_preflight.py",
    "tools/create_postgres_backup.py",
    "tools/create_postgres_restore_rehearsal_database.py",
    "tools/restore_postgres_rehearsal_database.py",
    "tools/create_postgres_migration_test_database.py",
    "tools/create_postgres_initial_alembic_revision.py",
    "tools/upgrade_postgres_migration_test_database.py",
    "tools/downgrade_postgres_migration_test_database.py",
    "tools/reupgrade_postgres_migration_test_database.py",
    "tools/check_postgres_source_baseline_stamp_preflight.py",
    "tools/stamp_postgres_restore_rehearsal_database.py",
    "POSTGRES_INITIAL_ALEMBIC_REVISION_MANUAL_REVIEW.md",
    "Alembic script template | 있음",
    "setup_dev_db.py --reset",
    "docker compose down -v",
    "DB schema",
    "Alembic revision 생성",
]

REQUIRED_CHECKLIST_TEXT = [
    "backend/.venv",
    ".venv\\Scripts\\activate",
    "python tools/check_alembic_readonly_state.py",
    "docker compose ps",
    "python -m alembic revision --autogenerate",
    "새 npm 라이브러리나 프레임워크를 추가하지 않았습니다",
]

REQUIRED_ASYNC_DOC_TEXT = [
    "MissingGreenlet",
    "async_engine_from_config()",
    "connection.run_sync",
    "python tools/check_alembic_readonly_state.py",
    "DB schema",
]


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def main() -> int:
    for path in (REPORT_TOOL, CHECK_TOOL, STATE_TOOL, RUNTIME_TOOL, REPORT, CHECKLIST, ASYNC_FIX_DOC, RUNTIME_DOC, BASELINE_DOC):
        if not path.exists():
            return fail(f"missing file: {path.relative_to(ROOT).as_posix()}")

    report_check = run([sys.executable, "tools/report_postgres_alembic_readiness.py", "--check"])
    if report_check.returncode != 0:
        sys.stdout.write(report_check.stdout)
        sys.stderr.write(report_check.stderr)
        return fail("PostgreSQL/Alembic report is stale")

    report_text = REPORT.read_text(encoding="utf-8")
    for needle in REQUIRED_REPORT_TEXT:
        if needle not in report_text:
            return fail(f"readiness report missing: {needle}")

    checklist_text = CHECKLIST.read_text(encoding="utf-8")
    for needle in REQUIRED_CHECKLIST_TEXT:
        if needle not in checklist_text:
            return fail(f"local checklist missing: {needle}")

    async_doc_text = ASYNC_FIX_DOC.read_text(encoding="utf-8")
    for needle in REQUIRED_ASYNC_DOC_TEXT:
        if needle not in async_doc_text:
            return fail(f"async fix document missing: {needle}")

    checker = run([sys.executable, "tools/check_postgres_alembic_prerequisites.py", "--json"])
    if checker.returncode != 0:
        sys.stderr.write(checker.stderr)
        return fail("read-only prerequisite checker returned non-zero without --strict")
    payload = json.loads(checker.stdout)
    if payload.get("readOnly") is not True:
        return fail("checker must declare readOnly=true")
    if payload.get("databaseConnectionAttempted") is not False:
        return fail("checker must not attempt a database connection")
    keys = {item.get("key") for item in payload.get("checks", [])}
    for required in {"python", "virtualenv", "docker", "docker-compose", "sqlalchemy", "alembic", "asyncpg", "psycopg"}:
        if required not in keys:
            return fail(f"checker missing prerequisite key: {required}")

    checker_source = CHECK_TOOL.read_text(encoding="utf-8")
    forbidden = ["psycopg.connect", "asyncpg.connect", "create_engine(", "create_async_engine(", "alembic upgrade"]
    for marker in forbidden:
        if marker in checker_source:
            return fail(f"checker contains forbidden DB/migration operation: {marker}")

    state_source = STATE_TOOL.read_text(encoding="utf-8")
    for required in ('run_command(backend, "history")', 'run_command(backend, "heads")', 'run_command(backend, "current")'):
        if required not in state_source:
            return fail(f"Alembic state checker missing: {required}")
    for dangerous in ('run_command(backend, "revision")', 'run_command(backend, "upgrade")', 'run_command(backend, "downgrade")', 'run_command(backend, "stamp")'):
        if dangerous in state_source:
            return fail(f"Alembic state checker contains mutation command: {dangerous}")

    print("OK: PostgreSQL/Alembic readiness smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

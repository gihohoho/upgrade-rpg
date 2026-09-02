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
REPORT = ROOT / "docs/generated/POSTGRES_ALEMBIC_READINESS.md"
CHECKLIST = ROOT / "docs/reference/database/POSTGRES_ALEMBIC_LOCAL_CHECKLIST.md"
ASYNC_FIX_DOC = ROOT / "docs/reference/database/ALEMBIC_ASYNC_ENV_FIX.md"
RUNTIME_TOOL = ROOT / "tools/check_postgres_runtime_readonly_state.py"
RUNTIME_DOC = ROOT / "docs/reference/database/POSTGRES_RUNTIME_READONLY_STATE.md"
BASELINE_DOC = ROOT / "docs/reference/database/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md"

REQUIRED_REPORT_TEXT = [
    "PostgreSQL / Alembic Readiness — v377",
    "latest: v391.vue-game-shop-settings-ui-foundation",
    "strict result: vue-game-shop-settings-ui-foundation",
    "local Alembic source graph head: v377_auth_email_public_security",
    "local/Neon applied DB revision: v377_auth_email_public_security / v377_auth_email_public_security",
    "actual target v377 apply: local 1 / Neon 1",
    "private email environment: prepared",
    "legacy evidence: source 8db9bcb / stale and preserved",
    "recovery1 roundtrip/local backup/apply: source 345872a / verified",
    "local auth POST: protection store available / legacy no-email login compatible",
    "local Brevo E2E: Naver delivery / link verification / login verified",
    "provider finalize: local multi-worker ownership diagnosed / direct provider healthy",
    "recovery2 roundtrip/Neon backup/apply: verified / one attempt each",
    "public backend/static: v377/v378 live",
    "model application tables: 25",
    "local/Neon application tables: 25 / 25",
    "next safe stage: migrate-vue-game-combat-runtime-foundation",
    "SQLAlchemy model table 수 | 25개",
    "local/Neon DB application table 수 | 25개 / 25개",
    "Alembic asyncpg-compatible online env | 있음",
    "Alembic versions 폴더 | 있음",
    "Alembic revision 수 | 3개",
    "local source graph head | `v377_auth_email_public_security`",
    "local/Neon DB current | `v377_auth_email_public_security` / `v377_auth_email_public_security`",
    "v306 당시 model/schema",
    "local/Neon actual DB는 모두 v377",
    "Stage E-2 — v371 이메일 identity revision 준비 역사",
    "Stage E-3 — v377 공개 이메일 보안 revision 준비",
    "auth_rate_limit_buckets",
    "auth_email_outbox",
    "tools/prepare_v377_email_security_environment.py",
    "tools/run_v377_auth_security_migration_roundtrip.py",
    "tools/apply_v377_auth_security_migration.py",
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
    "tools/stamp_postgres_source_database.py",
    "tools/check_postgres_baseline_completion_state.py",
    "tools/check_postgres_next_revision_preflight.py",
    "tools/check_postgres_deployment_runtime_readiness.py",
    "tools/check_runtime_config_hardening.py",
    "Stage F — 운영·배포 runtime readiness",
    "runtime config hardening",
    "compare_metadata()",
    "sequence ownership",
    "alembic-managed-baseline-complete",
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

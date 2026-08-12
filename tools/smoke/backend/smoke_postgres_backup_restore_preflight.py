#!/usr/bin/env python3
"""Smoke checks for the v290 read-only PostgreSQL backup/restore preflight."""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_postgres_backup_restore_preflight.py"
DOC = ROOT / "docs/reference/database/POSTGRES_BACKUP_RESTORE_PREP.md"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    for path in (TOOL, DOC):
        if not path.exists():
            return fail(f"missing file: {path.relative_to(ROOT).as_posix()}")

    source = TOOL.read_text(encoding="utf-8")
    ast.parse(source, filename=str(TOOL))

    for marker in (
        'SOURCE_DATABASE = "rpg_game"',
        'RESTORE_REHEARSAL_DATABASE = "rpg_game_restore_rehearsal_v290"',
        'MIGRATION_TEST_DATABASE = "rpg_game_migration_empty_v290"',
        'BACKUP_DIRECTORY = "local-backups/postgres"',
        'rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump',
        '"databaseMutationAttempted": False',
        '"backupCreated": False',
        '"restoreAttempted": False',
        '"databaseCreateDropAttempted": False',
        '"alembicMutationAttempted": False',
        '"restoreIntoSourceDatabaseAllowed": False',
        '[command, "--version"]',
        'command, "--version"',
        'check_postgres_schema_equivalence.py',
    ):
        if marker not in source:
            return fail(f"preflight tool missing marker: {marker}")

    for forbidden in (
        '"revision", "--autogenerate"',
        '"upgrade", "head"',
        '"downgrade"',
        '"stamp", "head"',
        '"docker", "compose", "down"',
        'setup_dev_db.py',
        'CREATE DATABASE',
        'DROP DATABASE',
    ):
        if forbidden in source:
            return fail(f"preflight tool contains mutation marker: {forbidden}")

    run = subprocess.run(
        [sys.executable, str(TOOL), "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=60,
    )
    if run.returncode != 0:
        sys.stdout.write(run.stdout)
        sys.stderr.write(run.stderr)
        return fail("preflight must return zero without --strict")
    payload = json.loads(run.stdout)
    expected_false = (
        "databaseMutationAttempted",
        "backupCreated",
        "restoreAttempted",
        "databaseCreateDropAttempted",
        "dockerResourceChanged",
        "environmentFileChanged",
        "alembicMutationAttempted",
    )
    if payload.get("readOnly") is not True:
        return fail("readOnly flag must be true")
    for key in expected_false:
        if payload.get(key) is not False:
            return fail(f"{key} flag must be false")
    if payload.get("classification") not in {"ready-for-user-approval", "blocked"}:
        return fail("invalid preflight classification")
    if payload["databaseBoundary"]["sourceDatabase"] != "rpg_game":
        return fail("source database boundary changed")
    if payload["databaseBoundary"]["restoreIntoSourceDatabaseAllowed"] is not False:
        return fail("restore into source database must remain forbidden")
    if payload["backupPolicy"]["includeInGit"] is not False:
        return fail("backup must be excluded from Git")
    if payload["backupPolicy"]["includeInHandoffZip"] is not False:
        return fail("backup must be excluded from handoff ZIP")

    doc_text = DOC.read_text(encoding="utf-8")
    for marker in (
        "PostgreSQL backup/restore preflight — v290",
        "local-backups/postgres",
        "rpg_game_restore_rehearsal_v290",
        "rpg_game_migration_empty_v290",
        "pg_dump",
        "pg_restore",
        "createdb",
        "dropdb",
        "사용자 승인",
    ):
        if marker not in doc_text:
            return fail(f"preflight doc missing: {marker}")

    print("OK: PostgreSQL backup/restore preflight smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

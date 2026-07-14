#!/usr/bin/env python3
"""Downgrade the reviewed first revision only in the isolated migration DB.

Approved mutation boundary for v299:
- MAY run exactly `alembic downgrade base` against
  `rpg_game_migration_empty_v290`.
- MUST start from exact revision `v295_initial_schema` and its reviewed SHA.
- MUST preserve `rpg_game` and `rpg_game_restore_rehearsal_v290` unchanged.
- MUST leave only an empty `alembic_version` placeholder in the target DB.
- MUST NOT edit `.env`, create/drop/restore databases, run upgrade/stamp,
  write seed data, or target the source/rehearsal databases.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from _safe_subprocess import decode_output
from check_postgres_backup_restore_preflight import (
    MIGRATION_TEST_DATABASE,
    RESTORE_REHEARSAL_DATABASE,
)
from check_postgres_runtime_readonly_state import inspect_database
from create_postgres_migration_test_database import (
    MigrationTestDatabaseError,
    load_verified_restore_evidence,
    sanitize_database_state,
    validate_rehearsal_state,
    validate_source_state,
)
from create_postgres_restore_rehearsal_database import SOURCE_DATABASE_USER
from restore_postgres_rehearsal_database import inspect_named_database
from upgrade_postgres_migration_test_database import (
    REVISION_ID,
    REVISION_SHA256,
    UPGRADE_REPORT_RELATIVE_PATH,
    MigrationUpgradeError,
    reviewed_revision,
    target_database_url,
    validate_migration_after as validate_upgraded_migration_state,
)

TOOL_VERSION = "v299.postgres-migration-test-downgrade-base-ready"
DOWNGRADE_REPORT_RELATIVE_PATH = Path(
    "local-review-artifacts/alembic/v295_initial_schema.downgrade-v299.json"
)
DEFAULT_TIMEOUT_SECONDS = 300


class MigrationDowngradeError(RuntimeError):
    """Raised when a downgrade safety gate or postcondition fails."""


def ensure_under(root: Path, path: Path) -> Path:
    root_resolved = root.resolve()
    resolved = path.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise MigrationDowngradeError(f"unsafe path outside project: {path}")
    return resolved


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.partial")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def load_verified_upgrade_evidence(root: Path) -> dict[str, Any]:
    path = ensure_under(root, root / UPGRADE_REPORT_RELATIVE_PATH)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationDowngradeError(
            f"verified v298 upgrade report cannot be read: {path}: {exc}"
        ) from exc

    expected = {
        "result": "migration-test-database-upgraded-and-verified",
        "targetDatabase": MIGRATION_TEST_DATABASE,
        "revisionId": REVISION_ID,
        "revisionSha256": REVISION_SHA256,
        "upgradeExecuted": True,
        "downgradeExecuted": False,
        "stampExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise MigrationDowngradeError(
                f"v298 upgrade evidence mismatch: {key}={payload.get(key)!r}, expected={value!r}"
            )
    after = payload.get("migrationAfter") or {}
    if after.get("alembicCurrentRevisions") != [REVISION_ID]:
        raise MigrationDowngradeError("v298 upgrade report does not record the reviewed revision")
    if after.get("publicTableCount") != 23 or after.get("differenceCount") != 0:
        raise MigrationDowngradeError("v298 upgrade report postcondition is incomplete")
    return payload


def build_downgrade_command() -> list[str]:
    return [
        sys.executable,
        "-m",
        "alembic",
        "--config",
        "alembic.ini",
        "downgrade",
        "base",
    ]


def run_downgrade_command(
    root: Path,
    *,
    timeout: int,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> str:
    backend = root / "backend"
    env = os.environ.copy()
    env["DATABASE_URL"] = target_database_url(root)
    env["PYTHONPATH"] = str(backend.resolve()) + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    command = build_downgrade_command()
    try:
        completed = run_process(
            command,
            cwd=backend,
            env=env,
            text=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise MigrationDowngradeError(
            f"Alembic downgrade timed out after {timeout} seconds; no retry was attempted"
        ) from exc
    output = decode_output(completed.stdout).strip()
    if completed.returncode != 0:
        raise MigrationDowngradeError(
            f"Alembic downgrade failed with exit={completed.returncode}: {output or 'no output'}"
        )
    return output


def validate_migration_before(
    state: dict[str, Any], expected_tables: tuple[str, ...]
) -> dict[str, Any]:
    try:
        return validate_upgraded_migration_state(state, expected_tables)
    except MigrationUpgradeError as exc:
        raise MigrationDowngradeError(str(exc)) from exc


def validate_migration_after(state: dict[str, Any]) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise MigrationDowngradeError(
            f"post-downgrade migration DB connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != MIGRATION_TEST_DATABASE:
        raise MigrationDowngradeError("post-downgrade migration DB boundary mismatch")
    if state.get("user") != SOURCE_DATABASE_USER:
        raise MigrationDowngradeError("post-downgrade migration DB user boundary mismatch")
    if state.get("publicTables") != ["alembic_version"]:
        raise MigrationDowngradeError(
            "post-downgrade target must contain only the Alembic placeholder table"
        )
    if state.get("publicTableCount") != 1:
        raise MigrationDowngradeError("post-downgrade public table count must be 1")
    if state.get("tableCounts") != {"alembic_version": 0} or state.get("totalRows") != 0:
        raise MigrationDowngradeError("post-downgrade Alembic placeholder must be empty")
    if state.get("alembicVersionTableExists") is not True:
        raise MigrationDowngradeError("post-downgrade Alembic placeholder is missing")
    if state.get("alembicCurrentRevisions") not in ([], ()):
        raise MigrationDowngradeError(
            f"post-downgrade revision rows remain: {state.get('alembicCurrentRevisions')}"
        )
    if state.get("differenceCount") != 22:
        raise MigrationDowngradeError(
            f"post-downgrade model difference count must be 22: {state.get('differenceCount')}"
        )
    if state.get("schemaClassification") != "review-required":
        raise MigrationDowngradeError(
            "post-downgrade empty workspace must be classified review-required"
        )
    return sanitize_database_state(state)


def execute_downgrade(
    root: Path,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    restore_evidence: dict[str, Any] | None = None,
    upgrade_evidence: dict[str, Any] | None = None,
    source_before_raw: dict[str, Any] | None = None,
    source_after_raw: dict[str, Any] | None = None,
    rehearsal_before_raw: dict[str, Any] | None = None,
    rehearsal_after_raw: dict[str, Any] | None = None,
    migration_before_raw: dict[str, Any] | None = None,
    migration_after_raw: dict[str, Any] | None = None,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    root = root.resolve()
    revision_path, manual_review, automated_review = reviewed_revision(root)
    verified_upgrade = (
        upgrade_evidence if upgrade_evidence is not None else load_verified_upgrade_evidence(root)
    )
    try:
        verified_restore = (
            restore_evidence if restore_evidence is not None else load_verified_restore_evidence(root)
        )
        source_before = validate_source_state(
            source_before_raw
            if source_before_raw is not None
            else inspect_database(root, include_counts=True),
            verified_restore,
        )
        rehearsal_before = validate_rehearsal_state(
            rehearsal_before_raw
            if rehearsal_before_raw is not None
            else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
            verified_restore,
        )
    except MigrationTestDatabaseError as exc:
        raise MigrationDowngradeError(str(exc)) from exc

    migration_before = validate_migration_before(
        migration_before_raw
        if migration_before_raw is not None
        else inspect_named_database(root, MIGRATION_TEST_DATABASE),
        verified_restore["expectedTables"],
    )

    command_output = run_downgrade_command(root, timeout=timeout, run_process=run_process)

    try:
        source_after = validate_source_state(
            source_after_raw
            if source_after_raw is not None
            else inspect_database(root, include_counts=True),
            verified_restore,
        )
        rehearsal_after = validate_rehearsal_state(
            rehearsal_after_raw
            if rehearsal_after_raw is not None
            else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
            verified_restore,
        )
    except MigrationTestDatabaseError as exc:
        raise MigrationDowngradeError(str(exc)) from exc
    migration_after = validate_migration_after(
        migration_after_raw
        if migration_after_raw is not None
        else inspect_named_database(root, MIGRATION_TEST_DATABASE)
    )

    if source_before != source_after:
        raise MigrationDowngradeError("source DB changed during isolated migration downgrade")
    if rehearsal_before != rehearsal_after:
        raise MigrationDowngradeError("restore rehearsal DB changed during isolated migration downgrade")

    report_path = ensure_under(root, root / DOWNGRADE_REPORT_RELATIVE_PATH)
    result = {
        "toolVersion": TOOL_VERSION,
        "result": "migration-test-database-downgraded-to-base-and-verified",
        "targetDatabase": MIGRATION_TEST_DATABASE,
        "revisionId": REVISION_ID,
        "revisionRelativePath": revision_path.relative_to(root).as_posix(),
        "revisionSha256": REVISION_SHA256,
        "manualReview": {
            "result": manual_review["reviewResult"],
            "conclusion": manual_review["manualConclusion"],
        },
        "automatedReview": automated_review,
        "verifiedUpgradeReport": {
            "result": verified_upgrade["result"],
            "revisionId": verified_upgrade["revisionId"],
            "revisionSha256": verified_upgrade["revisionSha256"],
        },
        "alembicCommand": build_downgrade_command()[1:],
        "alembicCommandOutput": command_output,
        "sourceBefore": source_before,
        "sourceAfter": source_after,
        "rehearsalBefore": rehearsal_before,
        "rehearsalAfter": rehearsal_after,
        "migrationBefore": migration_before,
        "migrationAfter": migration_after,
        "upgradeExecuted": False,
        "downgradeExecuted": True,
        "stampExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
    }
    write_json_atomic(report_path, result)
    result["reportRelativePath"] = report_path.relative_to(root).as_posix()
    return result


def inspect_readiness(root: Path) -> dict[str, Any]:
    revision_path, manual_review, automated_review = reviewed_revision(root)
    upgrade = load_verified_upgrade_evidence(root)
    restore = load_verified_restore_evidence(root)
    source = validate_source_state(inspect_database(root, include_counts=True), restore)
    rehearsal = validate_rehearsal_state(
        inspect_named_database(root, RESTORE_REHEARSAL_DATABASE), restore
    )
    migration = validate_migration_before(
        inspect_named_database(root, MIGRATION_TEST_DATABASE), restore["expectedTables"]
    )
    return {
        "ready": True,
        "revision": revision_path.relative_to(root).as_posix(),
        "revisionSha256": REVISION_SHA256,
        "manualReview": manual_review["manualConclusion"],
        "automatedReview": automated_review["result"],
        "upgradeEvidence": upgrade["result"],
        "source": source,
        "rehearsal": rehearsal,
        "migration": migration,
    }


def render_inspection(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "PostgreSQL migration test downgrade readiness (read-only)",
            f"- target DB: {MIGRATION_TEST_DATABASE}",
            f"- current revision: {result['migration'].get('alembicCurrentRevisions')}",
            f"- revision SHA-256: {result['revisionSha256']}",
            f"- verified upgrade: {result['upgradeEvidence']}",
            f"- current public tables: {result['migration'].get('publicTableCount')}",
            "- result: ready-for-approved-downgrade-base",
            "- no DB schema/data mutation was executed.",
        ]
    )


def render_success(result: dict[str, Any]) -> str:
    after = result["migrationAfter"]
    return "\n".join(
        [
            "PostgreSQL isolated migration test downgrade",
            "The reviewed revision was downgraded to base only in the isolated migration DB.",
            "",
            f"- result: {result['result']}",
            f"- target DB: {result['targetDatabase']}",
            f"- downgraded revision: {result['revisionId']} -> base",
            f"- revision SHA-256: {result['revisionSha256']}",
            f"- target public tables after downgrade: {after.get('publicTableCount')}",
            "- target application tables remaining: 0",
            f"- target total rows: {after.get('totalRows')}",
            f"- target current revisions: {after.get('alembicCurrentRevisions')}",
            f"- expected empty-workspace schema: {after.get('schemaClassification')} / differences={after.get('differenceCount')}",
            "- source tables/rows preserved: 22/748",
            "- rehearsal tables/rows preserved: 22/748",
            f"- verification report: {result['reportRelativePath']}",
            "- upgrade, stamp, DB create/drop/restore, .env/Docker changes, and source writes were not executed.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--inspect", action="store_true", help="Read-only downgrade readiness inspection")
    group.add_argument("--execute", action="store_true", help="Downgrade the isolated migration DB to base")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    try:
        if args.inspect:
            print(render_inspection(inspect_readiness(root)))
            return 0
        if not args.execute:
            print("PostgreSQL isolated migration test downgrade — execution guard")
            print(f"- target DB: {MIGRATION_TEST_DATABASE}")
            print(f"- approved downgrade: {REVISION_ID} -> base")
            print("- --execute is required; no DB mutation was attempted.")
            return 2
        result = execute_downgrade(root, timeout=args.timeout)
        print(render_success(result))
        return 0
    except Exception as exc:
        print("PostgreSQL isolated migration test downgrade")
        print("- result: blocked-or-failed")
        print(f"- reason: {type(exc).__name__}: {exc}")
        print("- no automatic retry, upgrade, stamp, DB create/drop/restore, or source mutation was attempted.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

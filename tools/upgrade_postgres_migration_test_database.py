#!/usr/bin/env python3
"""Apply the manually reviewed first revision only to the isolated migration DB.

Approved mutation boundary for v298:
- MAY run exactly `alembic upgrade head` against
  `rpg_game_migration_empty_v290`.
- MUST use the exact reviewed revision file/SHA-256.
- MUST preserve `rpg_game` and `rpg_game_restore_rehearsal_v290` unchanged.
- MUST NOT edit `.env`, create/drop/restore databases, run downgrade/stamp,
  write seed data, or target the source/rehearsal databases.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from sqlalchemy.engine import make_url

from _safe_subprocess import decode_output
from check_postgres_backup_restore_preflight import (
    MIGRATION_TEST_DATABASE,
    RESTORE_REHEARSAL_DATABASE,
    SOURCE_DATABASE,
)
from check_postgres_runtime_readonly_state import inspect_database, load_backend_objects
from create_postgres_initial_alembic_revision import review_revision
from create_postgres_migration_test_database import (
    MigrationTestDatabaseError,
    load_verified_restore_evidence,
    sanitize_database_state,
    validate_rehearsal_state,
    validate_source_state,
)
from create_postgres_restore_rehearsal_database import SOURCE_DATABASE_USER
from restore_postgres_rehearsal_database import inspect_named_database

TOOL_VERSION = "v298.postgres-migration-test-upgrade-head-ready"
REVISION_ID = "v295_initial_schema"
REVISION_FILENAME = "v295_initial_schema_initial_postgresql_schema.py"
REVISION_SHA256 = "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa"
MANUAL_REVIEW_RELATIVE_PATH = Path("docs/current/review/v295_initial_schema.manual-review.json")
UPGRADE_REPORT_RELATIVE_PATH = Path(
    "local-review-artifacts/alembic/v295_initial_schema.upgrade-v298.json"
)
DEFAULT_TIMEOUT_SECONDS = 300


class MigrationUpgradeError(RuntimeError):
    """Raised when an upgrade safety gate or postcondition fails."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_under(root: Path, path: Path) -> Path:
    root_resolved = root.resolve()
    resolved = path.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise MigrationUpgradeError(f"unsafe path outside project: {path}")
    return resolved


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.partial")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def reviewed_revision(root: Path) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    versions_dir = ensure_under(root, root / "backend/alembic/versions")
    revision_files = sorted(
        path for path in versions_dir.glob("*.py") if path.name != "__init__.py"
    )
    if [path.name for path in revision_files] != [REVISION_FILENAME]:
        raise MigrationUpgradeError(
            "Alembic versions boundary mismatch; expected exactly the reviewed revision: "
            f"actual={[path.name for path in revision_files]}"
        )
    revision_path = revision_files[0]
    observed_sha = sha256_file(revision_path)
    if observed_sha != REVISION_SHA256:
        raise MigrationUpgradeError(
            f"reviewed revision SHA-256 mismatch: expected={REVISION_SHA256}, actual={observed_sha}"
        )

    review_path = ensure_under(root, root / MANUAL_REVIEW_RELATIVE_PATH)
    try:
        manual_review = json.loads(review_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationUpgradeError(f"manual review evidence cannot be read: {exc}") from exc
    required_review = {
        "reviewResult": "passed",
        "revisionId": REVISION_ID,
        "revisionSha256": REVISION_SHA256,
        "manualConclusion": "approved-for-isolated-empty-migration-database-upgrade-only",
        "sourceDatabaseApproval": False,
        "upgradeExecuted": False,
        "downgradeExecuted": False,
        "stampExecuted": False,
    }
    for key, expected in required_review.items():
        if manual_review.get(key) != expected:
            raise MigrationUpgradeError(
                f"manual review evidence mismatch: {key}={manual_review.get(key)!r}, expected={expected!r}"
            )

    automated_review = review_revision(root, revision_path)
    if automated_review.get("result") != "initial-alembic-revision-automated-review-passed":
        raise MigrationUpgradeError("reviewed revision automated review did not pass")
    if automated_review.get("revision") != REVISION_ID:
        raise MigrationUpgradeError("reviewed revision ID changed")
    if automated_review.get("tableCount") != 22 or automated_review.get("columnCount") != 209:
        raise MigrationUpgradeError("reviewed revision model baseline changed from 22 tables / 209 columns")
    if automated_review.get("upgradeOperationCounts") != {
        "create_index": 42,
        "create_table": 22,
    }:
        raise MigrationUpgradeError("reviewed revision upgrade operation boundary changed")
    if automated_review.get("downgradeOperationCounts") != {
        "drop_index": 42,
        "drop_table": 22,
    }:
        raise MigrationUpgradeError("reviewed revision downgrade operation boundary changed")
    return revision_path, manual_review, automated_review


def target_database_url(root: Path) -> str:
    settings, _ = load_backend_objects(root)
    source_url = make_url(settings.database_url)
    if source_url.database != SOURCE_DATABASE:
        raise MigrationUpgradeError(
            f"configured source DB mismatch: expected={SOURCE_DATABASE}, actual={source_url.database}"
        )
    target = source_url.set(database=MIGRATION_TEST_DATABASE)
    return target.render_as_string(hide_password=False)


def build_upgrade_command() -> list[str]:
    return [
        sys.executable,
        "-m",
        "alembic",
        "--config",
        "alembic.ini",
        "upgrade",
        "head",
    ]


def run_upgrade_command(
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
    command = build_upgrade_command()
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
        raise MigrationUpgradeError(
            f"Alembic upgrade timed out after {timeout} seconds; no retry was attempted"
        ) from exc
    output = decode_output(completed.stdout).strip()
    if completed.returncode != 0:
        raise MigrationUpgradeError(
            f"Alembic upgrade failed with exit={completed.returncode}: {output or 'no output'}"
        )
    return output


def validate_migration_before(state: dict[str, Any]) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise MigrationUpgradeError(
            f"migration DB connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != MIGRATION_TEST_DATABASE:
        raise MigrationUpgradeError("migration DB boundary mismatch")
    if state.get("user") != SOURCE_DATABASE_USER:
        raise MigrationUpgradeError("migration DB connection user boundary mismatch")
    if state.get("publicTables") != ["alembic_version"]:
        raise MigrationUpgradeError(
            "migration DB must contain only the empty alembic_version placeholder"
        )
    if state.get("publicTableCount") != 1:
        raise MigrationUpgradeError("migration DB placeholder table count is not 1")
    if state.get("tableCounts") != {"alembic_version": 0} or state.get("totalRows") != 0:
        raise MigrationUpgradeError("migration DB placeholder contains rows")
    if state.get("alembicVersionTableExists") is not True:
        raise MigrationUpgradeError("migration DB alembic_version placeholder is missing")
    if state.get("alembicCurrentRevisions") not in ([], ()):
        raise MigrationUpgradeError("migration DB already records an Alembic revision")
    if state.get("differenceCount") != 22:
        raise MigrationUpgradeError("migration DB pre-upgrade model difference count is not 22")
    return sanitize_database_state(state)


def validate_migration_after(state: dict[str, Any], expected_tables: tuple[str, ...]) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise MigrationUpgradeError(
            f"post-upgrade migration DB connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != MIGRATION_TEST_DATABASE or state.get("user") != SOURCE_DATABASE_USER:
        raise MigrationUpgradeError("post-upgrade migration DB/user boundary mismatch")
    expected_public = sorted((*expected_tables, "alembic_version"))
    if state.get("publicTables") != expected_public or state.get("publicTableCount") != 23:
        raise MigrationUpgradeError(
            "post-upgrade migration DB table set is not 22 model tables + alembic_version"
        )
    counts = {str(name): int(value) for name, value in (state.get("tableCounts") or {}).items()}
    expected_counts = {name: 0 for name in expected_tables}
    expected_counts["alembic_version"] = 1
    if counts != dict(sorted(expected_counts.items())):
        raise MigrationUpgradeError(f"post-upgrade row counts are unexpected: {counts}")
    if state.get("totalRows") != 1:
        raise MigrationUpgradeError("post-upgrade total rows must be the one Alembic revision row")
    if state.get("alembicCurrentRevisions") != [REVISION_ID]:
        raise MigrationUpgradeError(
            f"post-upgrade revision mismatch: {state.get('alembicCurrentRevisions')}"
        )
    if state.get("schemaClassification") != "structurally-equivalent":
        raise MigrationUpgradeError("post-upgrade schema is not structurally equivalent")
    if state.get("differenceCount") != 0:
        raise MigrationUpgradeError("post-upgrade schema difference count is not zero")
    return sanitize_database_state(state)


def execute_upgrade(
    root: Path,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    evidence: dict[str, Any] | None = None,
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
    try:
        verified = evidence if evidence is not None else load_verified_restore_evidence(root)
        source_before = validate_source_state(
            source_before_raw if source_before_raw is not None else inspect_database(root, include_counts=True),
            verified,
        )
        rehearsal_before = validate_rehearsal_state(
            rehearsal_before_raw
            if rehearsal_before_raw is not None
            else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
            verified,
        )
    except MigrationTestDatabaseError as exc:
        raise MigrationUpgradeError(str(exc)) from exc
    migration_before = validate_migration_before(
        migration_before_raw
        if migration_before_raw is not None
        else inspect_named_database(root, MIGRATION_TEST_DATABASE)
    )

    command_output = run_upgrade_command(root, timeout=timeout, run_process=run_process)

    try:
        source_after = validate_source_state(
            source_after_raw if source_after_raw is not None else inspect_database(root, include_counts=True),
            verified,
        )
        rehearsal_after = validate_rehearsal_state(
            rehearsal_after_raw
            if rehearsal_after_raw is not None
            else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
            verified,
        )
    except MigrationTestDatabaseError as exc:
        raise MigrationUpgradeError(str(exc)) from exc
    migration_after = validate_migration_after(
        migration_after_raw
        if migration_after_raw is not None
        else inspect_named_database(root, MIGRATION_TEST_DATABASE),
        verified["expectedTables"],
    )
    if source_before != source_after:
        raise MigrationUpgradeError("source DB changed during isolated migration upgrade")
    if rehearsal_before != rehearsal_after:
        raise MigrationUpgradeError("restore rehearsal DB changed during isolated migration upgrade")

    report_path = ensure_under(root, root / UPGRADE_REPORT_RELATIVE_PATH)
    result = {
        "toolVersion": TOOL_VERSION,
        "result": "migration-test-database-upgraded-and-verified",
        "targetDatabase": MIGRATION_TEST_DATABASE,
        "revisionId": REVISION_ID,
        "revisionRelativePath": revision_path.relative_to(root).as_posix(),
        "revisionSha256": REVISION_SHA256,
        "manualReview": {
            "result": manual_review["reviewResult"],
            "conclusion": manual_review["manualConclusion"],
        },
        "automatedReview": automated_review,
        "alembicCommand": build_upgrade_command()[1:],
        "alembicCommandOutput": command_output,
        "sourceBefore": source_before,
        "sourceAfter": source_after,
        "rehearsalBefore": rehearsal_before,
        "rehearsalAfter": rehearsal_after,
        "migrationBefore": migration_before,
        "migrationAfter": migration_after,
        "upgradeExecuted": True,
        "downgradeExecuted": False,
        "stampExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
    }
    write_json_atomic(report_path, result)
    result["reportRelativePath"] = report_path.relative_to(root).as_posix()
    return result


def inspect_readiness(root: Path) -> dict[str, Any]:
    revision_path, manual_review, automated_review = reviewed_revision(root)
    evidence = load_verified_restore_evidence(root)
    source = validate_source_state(inspect_database(root, include_counts=True), evidence)
    rehearsal = validate_rehearsal_state(
        inspect_named_database(root, RESTORE_REHEARSAL_DATABASE), evidence
    )
    migration = validate_migration_before(
        inspect_named_database(root, MIGRATION_TEST_DATABASE)
    )
    return {
        "ready": True,
        "revision": revision_path.relative_to(root).as_posix(),
        "revisionSha256": REVISION_SHA256,
        "manualReview": manual_review["manualConclusion"],
        "automatedReview": automated_review["result"],
        "source": source,
        "rehearsal": rehearsal,
        "migration": migration,
    }


def render_inspection(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "PostgreSQL migration test upgrade readiness (read-only)",
            f"- target DB: {MIGRATION_TEST_DATABASE}",
            f"- revision: {REVISION_ID}",
            f"- revision SHA-256: {result['revisionSha256']}",
            f"- manual review: {result['manualReview']}",
            f"- migration tables: {result['migration'].get('publicTables')}",
            f"- recorded revisions: {result['migration'].get('alembicCurrentRevisions')}",
            "- result: ready-for-separate-upgrade-approval",
            "- no DB schema/data mutation was executed.",
        ]
    )


def render_success(result: dict[str, Any]) -> str:
    after = result["migrationAfter"]
    return "\n".join(
        [
            "PostgreSQL isolated migration test upgrade",
            "The reviewed revision was applied only to the isolated migration DB.",
            "",
            f"- result: {result['result']}",
            f"- target DB: {result['targetDatabase']}",
            f"- revision: {result['revisionId']}",
            f"- revision SHA-256: {result['revisionSha256']}",
            f"- target public tables: {after.get('publicTableCount')}",
            "- target model tables: 22",
            f"- target total rows including Alembic control row: {after.get('totalRows')}",
            f"- target current revision: {after.get('alembicCurrentRevisions')}",
            f"- target schema: {after.get('schemaClassification')} / differences={after.get('differenceCount')}",
            "- source tables/rows preserved: 22/748",
            "- rehearsal tables/rows preserved: 22/748",
            f"- verification report: {result['reportRelativePath']}",
            "- downgrade, stamp, DB create/drop/restore, .env/Docker changes, and source writes were not executed.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--inspect", action="store_true", help="Read-only readiness inspection")
    group.add_argument("--execute", action="store_true", help="Apply upgrade head to the isolated migration DB")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    try:
        if args.inspect:
            print(render_inspection(inspect_readiness(root)))
            return 0
        if not args.execute:
            print("PostgreSQL isolated migration test upgrade - execution guard")
            print(f"- target DB: {MIGRATION_TEST_DATABASE}")
            print(f"- approved revision: {REVISION_ID}")
            print("- --execute is required; no DB mutation was attempted.")
            return 2
        result = execute_upgrade(root, timeout=args.timeout)
        print(render_success(result))
        return 0
    except Exception as exc:
        print("PostgreSQL isolated migration test upgrade")
        print("- result: blocked-or-failed")
        print(f"- reason: {type(exc).__name__}: {exc}")
        print("- no automatic retry, downgrade, stamp, DB create/drop/restore, or source mutation was attempted.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

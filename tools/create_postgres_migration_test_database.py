#!/usr/bin/env python3
"""Create one empty PostgreSQL database for first-Alembic migration testing.

This is the v294 execution step approved after the verified v293 restore
rehearsal completed successfully.

Approved mutation boundary:
- MAY create exactly `rpg_game_migration_empty_v290` once when absent.
- MUST preserve `rpg_game` and `rpg_game_restore_rehearsal_v290` unchanged.
- MUST NOT create tables/rows, restore an archive, drop a database, edit .env,
  change Docker resources, or run Alembic revision/upgrade/downgrade/stamp.
- MUST stop when the migration test database already exists.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from _safe_subprocess import decode_output
from check_postgres_backup_restore_preflight import (
    MIGRATION_TEST_DATABASE,
    POSTGRES_CONTAINER,
    RESTORE_REHEARSAL_DATABASE,
    SOURCE_DATABASE,
    collect as collect_preflight,
)
from check_postgres_runtime_readonly_state import inspect_database
from create_postgres_restore_rehearsal_database import (
    APPROVED_BACKUP_FILENAME,
    APPROVED_BACKUP_SHA256,
    SOURCE_DATABASE_USER,
    SUPPORTED_LOCALE_PROVIDERS,
    find_approved_verified_backup,
    validate_preflight,
)
from restore_postgres_rehearsal_database import (
    RESTORE_REPORT_SUFFIX,
    inspect_named_database,
)

TOOL_VERSION = "v294.postgres-migration-empty-database-create"
DEFAULT_TIMEOUT_SECONDS = 60


class MigrationTestDatabaseError(RuntimeError):
    """Raised when a safety gate or empty database creation check fails."""


def ensure_project_relative_file(root: Path, relative_path: str) -> Path:
    root_resolved = root.resolve()
    path = (root / relative_path).resolve()
    if root_resolved not in path.parents:
        raise MigrationTestDatabaseError(f"unsafe project-relative path: {relative_path}")
    return path


def load_verified_restore_evidence(root: Path) -> dict[str, Any]:
    """Revalidate the exact backup and the completed v293 restore report."""
    root = root.resolve()
    try:
        backup = find_approved_verified_backup(root)
    except Exception as exc:
        raise MigrationTestDatabaseError(str(exc)) from exc
    if Path(str(backup.get("backupRelativePath") or "")).name != APPROVED_BACKUP_FILENAME:
        raise MigrationTestDatabaseError("approved backup filename boundary changed")
    if backup.get("sha256") != APPROVED_BACKUP_SHA256:
        raise MigrationTestDatabaseError("approved backup SHA-256 boundary changed")

    manifest_path = ensure_project_relative_file(root, str(backup["manifestRelativePath"]))
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationTestDatabaseError(f"cannot read approved backup manifest: {exc}") from exc

    snapshot_relative = str(manifest.get("sourceSnapshotRelativePath") or "")
    if not snapshot_relative:
        raise MigrationTestDatabaseError("backup manifest is missing source snapshot evidence")
    snapshot_path = ensure_project_relative_file(root, snapshot_relative)
    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationTestDatabaseError(f"cannot read approved source snapshot: {exc}") from exc
    if snapshot != (manifest.get("sourceSnapshot") or {}):
        raise MigrationTestDatabaseError("source snapshot sidecar differs from manifest")

    tables = tuple(sorted(str(item) for item in (snapshot.get("publicTables") or [])))
    counts = {
        str(name): int(value) for name, value in (snapshot.get("tableCounts") or {}).items()
    }
    if len(tables) != 22 or snapshot.get("publicTableCount") != 22:
        raise MigrationTestDatabaseError("approved source snapshot table baseline is not 22")
    if set(tables) != set(counts):
        raise MigrationTestDatabaseError("approved source table list/count keys differ")
    if sum(counts.values()) != 748 or snapshot.get("totalRows") != 748:
        raise MigrationTestDatabaseError("approved source snapshot row baseline is not 748")
    if snapshot.get("alembicVersionTableExists") is not False:
        raise MigrationTestDatabaseError("approved source snapshot has Alembic baseline state")

    backup_path = ensure_project_relative_file(root, str(backup["backupRelativePath"]))
    report_path = backup_path.with_name(f"{backup_path.name}{RESTORE_REPORT_SUFFIX}")
    if not report_path.is_file():
        raise MigrationTestDatabaseError(
            f"verified v293 restore report is missing: {report_path.name}"
        )
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationTestDatabaseError(f"cannot read v293 restore report: {exc}") from exc

    if report.get("result") != "restore-rehearsal-completed-and-verified":
        raise MigrationTestDatabaseError("v293 restore report success classification is missing")
    if report.get("restoreCompleted") is not True or report.get("restoreSingleTransaction") is not True:
        raise MigrationTestDatabaseError("v293 restore report does not prove a completed single transaction")
    if report.get("sourceDatabase") != SOURCE_DATABASE:
        raise MigrationTestDatabaseError("v293 restore report source database mismatch")
    if report.get("targetDatabase") != RESTORE_REHEARSAL_DATABASE:
        raise MigrationTestDatabaseError("v293 restore report target database mismatch")
    report_backup = report.get("verifiedBackup") or {}
    if Path(str(report_backup.get("backupRelativePath") or "")).name != APPROVED_BACKUP_FILENAME:
        raise MigrationTestDatabaseError("v293 restore report backup filename mismatch")
    if report_backup.get("sha256") != APPROVED_BACKUP_SHA256:
        raise MigrationTestDatabaseError("v293 restore report backup SHA-256 mismatch")
    if report.get("sourceBefore") != report.get("sourceAfter"):
        raise MigrationTestDatabaseError("v293 restore report source before/after differs")
    target = report.get("targetAfter") or {}
    if target.get("publicTableCount") != 22 or target.get("totalRows") != 748:
        raise MigrationTestDatabaseError("v293 restored target baseline is not 22 tables / 748 rows")
    if target.get("schemaClassification") != "structurally-equivalent":
        raise MigrationTestDatabaseError("v293 restored target schema is not structurally equivalent")
    if target.get("differenceCount") != 0:
        raise MigrationTestDatabaseError("v293 restored target schema difference count is not zero")
    if target.get("alembicVersionTableExists") is not False:
        raise MigrationTestDatabaseError("v293 restored target unexpectedly has alembic_version")

    return {
        **backup,
        "backupPath": backup_path,
        "manifestPath": manifest_path,
        "sourceSnapshotPath": snapshot_path,
        "restoreReportPath": report_path,
        "expectedTables": tables,
        "expectedTableCounts": dict(sorted(counts.items())),
        "expectedTotalRows": 748,
        "restoreReport": report,
    }


def sanitize_database_state(state: dict[str, Any]) -> dict[str, Any]:
    allowed = (
        "database",
        "user",
        "schema",
        "serverVersion",
        "publicTableCount",
        "publicTables",
        "tableCountsCollected",
        "tableCounts",
        "totalRows",
        "alembicVersionTableExists",
        "alembicCurrentRevisions",
        "classification",
        "schemaClassification",
        "differenceCount",
    )
    return {key: state.get(key) for key in allowed}


def validate_source_state(state: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise MigrationTestDatabaseError(
            f"source database connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != SOURCE_DATABASE or state.get("user") != SOURCE_DATABASE_USER:
        raise MigrationTestDatabaseError("source database/user boundary mismatch")
    tables = tuple(sorted(str(item) for item in (state.get("publicTables") or [])))
    counts = {str(name): int(value) for name, value in (state.get("tableCounts") or {}).items()}
    if tables != evidence["expectedTables"]:
        raise MigrationTestDatabaseError("source table list differs from approved snapshot")
    if dict(sorted(counts.items())) != evidence["expectedTableCounts"]:
        raise MigrationTestDatabaseError("source table row counts differ from approved snapshot")
    if state.get("publicTableCount") != 22 or state.get("totalRows") != 748:
        raise MigrationTestDatabaseError("source total baseline is not 22 tables / 748 rows")
    if state.get("missingModelTables") or state.get("extraPublicTables"):
        raise MigrationTestDatabaseError("source model/public table boundary changed")
    if state.get("alembicVersionTableExists") is not False:
        raise MigrationTestDatabaseError("source Alembic baseline state changed")
    return sanitize_database_state(state)


def validate_rehearsal_state(state: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise MigrationTestDatabaseError(
            f"rehearsal database connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != RESTORE_REHEARSAL_DATABASE:
        raise MigrationTestDatabaseError("rehearsal database boundary mismatch")
    if state.get("user") != SOURCE_DATABASE_USER:
        raise MigrationTestDatabaseError("rehearsal connection user boundary mismatch")
    tables = tuple(sorted(str(item) for item in (state.get("publicTables") or [])))
    counts = {str(name): int(value) for name, value in (state.get("tableCounts") or {}).items()}
    if tables != evidence["expectedTables"]:
        raise MigrationTestDatabaseError("rehearsal table list differs from approved snapshot")
    if dict(sorted(counts.items())) != evidence["expectedTableCounts"]:
        raise MigrationTestDatabaseError("rehearsal table row counts differ from approved snapshot")
    if state.get("publicTableCount") != 22 or state.get("totalRows") != 748:
        raise MigrationTestDatabaseError("rehearsal total baseline is not 22 tables / 748 rows")
    if state.get("schemaClassification") != "structurally-equivalent":
        raise MigrationTestDatabaseError("rehearsal schema is not structurally equivalent")
    if state.get("differenceCount") != 0:
        raise MigrationTestDatabaseError("rehearsal schema difference count is not zero")
    if state.get("alembicVersionTableExists") is not False:
        raise MigrationTestDatabaseError("rehearsal database unexpectedly has alembic_version")
    return sanitize_database_state(state)


def validate_empty_migration_state(state: dict[str, Any]) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise MigrationTestDatabaseError(
            f"migration test database connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != MIGRATION_TEST_DATABASE:
        raise MigrationTestDatabaseError("migration test database boundary mismatch")
    if state.get("user") != SOURCE_DATABASE_USER:
        raise MigrationTestDatabaseError("migration test connection user boundary mismatch")
    if state.get("publicTableCount") != 0 or state.get("publicTables") not in ([], ()):
        raise MigrationTestDatabaseError("migration test database is not empty")
    if state.get("totalRows") != 0 or state.get("tableCounts") not in ({}, None):
        raise MigrationTestDatabaseError("migration test database contains rows")
    if state.get("alembicVersionTableExists") is not False:
        raise MigrationTestDatabaseError("migration test database unexpectedly has alembic_version")
    return sanitize_database_state(state)


def database_catalog_query() -> str:
    names = ", ".join(
        f"'{name}'"
        for name in (SOURCE_DATABASE, RESTORE_REHEARSAL_DATABASE, MIGRATION_TEST_DATABASE)
    )
    return (
        "SELECT COALESCE(json_agg(row_to_json(q)), '[]'::json)::text FROM ("
        'SELECT datname AS "database", pg_get_userbyid(datdba) AS "owner", '
        'pg_encoding_to_char(encoding) AS "encoding", datcollate AS "collate", '
        'datctype AS "ctype", datlocprovider::text AS "locale_provider", '
        "COALESCE(daticulocale, '') AS \"icu_locale\" "
        f"FROM pg_database WHERE datname IN ({names}) ORDER BY datname"
        ") q;"
    )


def build_catalog_command() -> list[str]:
    return [
        "docker",
        "exec",
        POSTGRES_CONTAINER,
        "psql",
        "--dbname=postgres",
        f"--username={SOURCE_DATABASE_USER}",
        "--no-password",
        "--tuples-only",
        "--no-align",
        "--set=ON_ERROR_STOP=1",
        f"--command={database_catalog_query()}",
    ]


def build_create_command(source_metadata: dict[str, Any]) -> list[str]:
    provider_code = str(source_metadata.get("locale_provider") or "")
    if provider_code not in SUPPORTED_LOCALE_PROVIDERS:
        raise MigrationTestDatabaseError(
            f"unsupported source locale provider for PostgreSQL 16: {provider_code or 'missing'}"
        )
    encoding = str(source_metadata.get("encoding") or "")
    collate = str(source_metadata.get("collate") or "")
    ctype = str(source_metadata.get("ctype") or "")
    if not encoding or not collate or not ctype:
        raise MigrationTestDatabaseError("source encoding/collation metadata is incomplete")

    command = [
        "docker",
        "exec",
        POSTGRES_CONTAINER,
        "createdb",
        f"--username={SOURCE_DATABASE_USER}",
        "--no-password",
        "--maintenance-db=postgres",
        f"--owner={SOURCE_DATABASE_USER}",
        "--template=template0",
        f"--encoding={encoding}",
        f"--lc-collate={collate}",
        f"--lc-ctype={ctype}",
    ]
    if provider_code == "i":
        icu_locale = str(source_metadata.get("icu_locale") or "")
        if not icu_locale:
            raise MigrationTestDatabaseError("source ICU locale is missing")
        command.extend(["--locale-provider=icu", f"--icu-locale={icu_locale}"])
    command.append(MIGRATION_TEST_DATABASE)
    return command


def run_json_command(
    command: list[str],
    *,
    root: Path,
    timeout: int,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]],
) -> Any:
    try:
        completed = run_process(
            command,
            cwd=root,
            text=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise MigrationTestDatabaseError(
            f"command timed out after {timeout} seconds: {' '.join(command[:5])}"
        ) from exc
    output = decode_output(completed.stdout).strip()
    if completed.returncode != 0:
        raise MigrationTestDatabaseError(
            f"command failed with exit={completed.returncode}: {output or 'no output'}"
        )
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise MigrationTestDatabaseError(f"unexpected PostgreSQL JSON output: {output}") from exc


def read_catalog(
    root: Path,
    *,
    timeout: int,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]],
) -> dict[str, dict[str, Any]]:
    rows = run_json_command(
        build_catalog_command(), root=root, timeout=timeout, run_process=run_process
    )
    if not isinstance(rows, list):
        raise MigrationTestDatabaseError("database catalog result is not a list")
    return {str(row.get("database")): row for row in rows if isinstance(row, dict)}


def run_create(
    root: Path,
    command: list[str],
    *,
    timeout: int,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]],
) -> None:
    try:
        completed = run_process(
            command,
            cwd=root,
            text=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise MigrationTestDatabaseError(f"createdb timed out after {timeout} seconds") from exc
    output = decode_output(completed.stdout).strip()
    if completed.returncode != 0:
        raise MigrationTestDatabaseError(
            f"createdb failed with exit={completed.returncode}: {output or 'no output'}"
        )


def validate_catalog_pair(catalog: dict[str, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    source = catalog.get(SOURCE_DATABASE)
    rehearsal = catalog.get(RESTORE_REHEARSAL_DATABASE)
    if source is None or rehearsal is None:
        raise MigrationTestDatabaseError("source or verified rehearsal database is missing")
    if source.get("owner") != SOURCE_DATABASE_USER or rehearsal.get("owner") != SOURCE_DATABASE_USER:
        raise MigrationTestDatabaseError("source/rehearsal owner boundary mismatch")
    for key in ("encoding", "collate", "ctype", "locale_provider", "icu_locale"):
        if source.get(key) != rehearsal.get(key):
            raise MigrationTestDatabaseError(f"source/rehearsal metadata differs for {key}")
    return source, rehearsal


def execute_creation(
    root: Path,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    preflight_payload: dict[str, Any] | None = None,
    restore_evidence: dict[str, Any] | None = None,
    source_state_before: dict[str, Any] | None = None,
    source_state_after: dict[str, Any] | None = None,
    rehearsal_state_before: dict[str, Any] | None = None,
    rehearsal_state_after: dict[str, Any] | None = None,
    migration_state_after: dict[str, Any] | None = None,
    catalog_before: dict[str, dict[str, Any]] | None = None,
    catalog_after: dict[str, dict[str, Any]] | None = None,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    root = root.resolve()
    preflight = preflight_payload if preflight_payload is not None else collect_preflight(root)
    try:
        validate_preflight(preflight)
    except Exception as exc:
        raise MigrationTestDatabaseError(str(exc)) from exc

    evidence = restore_evidence if restore_evidence is not None else load_verified_restore_evidence(root)
    before_source_raw = (
        source_state_before
        if source_state_before is not None
        else inspect_database(root, include_counts=True)
    )
    before_source = validate_source_state(before_source_raw, evidence)
    before_rehearsal_raw = (
        rehearsal_state_before
        if rehearsal_state_before is not None
        else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE)
    )
    before_rehearsal = validate_rehearsal_state(before_rehearsal_raw, evidence)

    catalog_before_raw = (
        catalog_before
        if catalog_before is not None
        else read_catalog(root, timeout=timeout, run_process=run_process)
    )
    source_metadata, rehearsal_metadata = validate_catalog_pair(catalog_before_raw)
    if MIGRATION_TEST_DATABASE in catalog_before_raw:
        raise MigrationTestDatabaseError(
            f"migration test database already exists; no create/drop/Alembic action was executed: "
            f"{MIGRATION_TEST_DATABASE}"
        )

    create_command = build_create_command(source_metadata)
    run_create(root, create_command, timeout=timeout, run_process=run_process)

    catalog_after_raw = (
        catalog_after
        if catalog_after is not None
        else read_catalog(root, timeout=timeout, run_process=run_process)
    )
    source_after_metadata, rehearsal_after_metadata = validate_catalog_pair(catalog_after_raw)
    if source_after_metadata != source_metadata or rehearsal_after_metadata != rehearsal_metadata:
        raise MigrationTestDatabaseError("source/rehearsal catalog metadata changed during creation")
    migration_metadata = catalog_after_raw.get(MIGRATION_TEST_DATABASE)
    if migration_metadata is None:
        raise MigrationTestDatabaseError(
            "createdb returned success but migration test DB is not visible; do not retry or drop automatically"
        )
    if migration_metadata.get("owner") != SOURCE_DATABASE_USER:
        raise MigrationTestDatabaseError("migration test database owner mismatch")
    for key in ("encoding", "collate", "ctype", "locale_provider", "icu_locale"):
        if migration_metadata.get(key) != source_metadata.get(key):
            raise MigrationTestDatabaseError(
                f"migration test database metadata differs for {key}; do not run Alembic"
            )

    migration_raw = (
        migration_state_after
        if migration_state_after is not None
        else inspect_named_database(root, MIGRATION_TEST_DATABASE)
    )
    migration = validate_empty_migration_state(migration_raw)

    after_source_raw = (
        source_state_after
        if source_state_after is not None
        else inspect_database(root, include_counts=True)
    )
    after_source = validate_source_state(after_source_raw, evidence)
    after_rehearsal_raw = (
        rehearsal_state_after
        if rehearsal_state_after is not None
        else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE)
    )
    after_rehearsal = validate_rehearsal_state(after_rehearsal_raw, evidence)
    if after_source != before_source:
        raise MigrationTestDatabaseError("source database changed during migration DB creation")
    if after_rehearsal != before_rehearsal:
        raise MigrationTestDatabaseError("restore rehearsal database changed during migration DB creation")

    return {
        "toolVersion": TOOL_VERSION,
        "result": "migration-test-database-created-empty-and-verified",
        "approvedMutation": "create-one-empty-isolated-migration-test-database",
        "databaseCreated": True,
        "databaseAlreadyExisted": False,
        "restoreAttempted": False,
        "databaseDropAttempted": False,
        "tableOrRowWriteAttempted": False,
        "sourceSchemaDataMutationAttempted": False,
        "rehearsalSchemaDataMutationAttempted": False,
        "dockerResourceChanged": False,
        "environmentFileChanged": False,
        "alembicRevisionAttempted": False,
        "alembicUpgradeAttempted": False,
        "alembicDowngradeAttempted": False,
        "alembicStampAttempted": False,
        "sourceDatabase": SOURCE_DATABASE,
        "rehearsalDatabase": RESTORE_REHEARSAL_DATABASE,
        "migrationTestDatabase": MIGRATION_TEST_DATABASE,
        "owner": SOURCE_DATABASE_USER,
        "container": POSTGRES_CONTAINER,
        "template": "template0",
        "sourceMetadata": source_metadata,
        "rehearsalMetadata": rehearsal_metadata,
        "migrationMetadata": migration_metadata,
        "sourceBefore": before_source,
        "sourceAfter": after_source,
        "rehearsalBefore": before_rehearsal,
        "rehearsalAfter": after_rehearsal,
        "migrationAfter": migration,
        "verifiedRestoreEvidence": {
            "backupRelativePath": evidence.get("backupRelativePath"),
            "backupSha256": evidence.get("sha256"),
            "restoreReportRelativePath": (
                evidence["restoreReportPath"].relative_to(root).as_posix()
                if isinstance(evidence.get("restoreReportPath"), Path)
                else evidence.get("restoreReportRelativePath")
            ),
        },
        "commands": {
            "catalogCheck": build_catalog_command(),
            "createDatabase": create_command,
        },
        "nextApprovalBoundary": (
            "review this empty DB result before generating the first Alembic revision; "
            "revision/autogenerate/upgrade/downgrade/stamp remain unapproved"
        ),
    }


def render_plan() -> str:
    return "\n".join(
        [
            "PostgreSQL empty migration test database creation — execution guard",
            f"- source DB (must remain unchanged): {SOURCE_DATABASE}",
            f"- verified rehearsal DB (must remain unchanged): {RESTORE_REHEARSAL_DATABASE}",
            f"- target DB (create only if absent): {MIGRATION_TEST_DATABASE}",
            f"- owner: {SOURCE_DATABASE_USER}",
            f"- requires v293 verified restore of: {APPROVED_BACKUP_FILENAME}",
            f"- required backup SHA-256: {APPROVED_BACKUP_SHA256}",
            "- no tables/rows, pg_restore, dropdb, .env edit, Docker change, or Alembic mutation",
            "- approved execution command: python tools/create_postgres_migration_test_database.py --execute",
        ]
    )


def render_success(result: dict[str, Any]) -> str:
    migration = result["migrationAfter"]
    source_before = result["sourceBefore"]
    source_after = result["sourceAfter"]
    rehearsal_before = result["rehearsalBefore"]
    rehearsal_after = result["rehearsalAfter"]
    evidence = result["verifiedRestoreEvidence"]
    return "\n".join(
        [
            "PostgreSQL empty migration test database creation",
            "One isolated empty database was created; no Alembic or existing DB mutation was executed.",
            "",
            f"- result: {result['result']}",
            f"- source DB: {result['sourceDatabase']} (unchanged)",
            f"- rehearsal DB: {result['rehearsalDatabase']} (preserved)",
            f"- migration test DB: {result['migrationTestDatabase']}",
            f"- target owner/user: {result['migrationMetadata'].get('owner')} / {migration.get('user')}",
            f"- template: {result['template']}",
            f"- target public tables: {migration.get('publicTableCount')}",
            f"- target total rows: {migration.get('totalRows')}",
            f"- target alembic_version: {'present' if migration.get('alembicVersionTableExists') else 'absent'}",
            f"- verified restore report: {evidence.get('restoreReportRelativePath')}",
            f"- backup SHA-256: {evidence.get('backupSha256')}",
            f"- source tables/rows before/after: {source_before.get('publicTableCount')}/{source_before.get('totalRows')} -> {source_after.get('publicTableCount')}/{source_after.get('totalRows')}",
            f"- rehearsal tables/rows before/after: {rehearsal_before.get('publicTableCount')}/{rehearsal_before.get('totalRows')} -> {rehearsal_after.get('publicTableCount')}/{rehearsal_after.get('totalRows')}",
            "- pg_restore, dropdb, .env/Docker changes, and Alembic revision/upgrade/downgrade/stamp were not executed.",
            "- next: share only this console result for the first Alembic revision review boundary.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Create the approved empty migration test DB after all gates pass",
    )
    parser.add_argument("--json", action="store_true", help="Print success result as JSON")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Per PostgreSQL client command timeout in seconds",
    )
    args = parser.parse_args()

    if not args.execute:
        print(render_plan())
        print("\nBLOCKED: --execute is required; no DB existence check or mutation was executed.")
        return 2

    root = Path(__file__).resolve().parents[1]
    try:
        result = execute_creation(root, timeout=args.timeout)
    except MigrationTestDatabaseError as exc:
        print("PostgreSQL empty migration test database creation")
        print("- result: blocked-or-failed")
        print(f"- reason: {exc}")
        print("- no automatic drop, restore, retry, or Alembic action was attempted.")
        return 1
    except Exception as exc:  # pragma: no cover - environment dependent
        print("PostgreSQL empty migration test database creation")
        print("- result: unexpected-error")
        print(f"- reason: {type(exc).__name__}: {exc}")
        print("- no automatic drop, restore, retry, or Alembic action was attempted.")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_success(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

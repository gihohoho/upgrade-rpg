#!/usr/bin/env python3
"""Restore the approved PostgreSQL archive into the isolated rehearsal DB.

This is the v293 execution step approved after the empty database
`rpg_game_restore_rehearsal_v290` was created and verified.

Approved mutation boundary:
- MAY run pg_restore exactly once against the pinned rehearsal database.
- MUST use one transaction so a restore error rolls back partial schema/data.
- MUST NOT target the source database, create/drop databases, clean existing
  objects, edit .env, change Docker resources, or run Alembic operations.
- MUST stop unless the target exists and is completely empty.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from _safe_subprocess import decode_output
from check_postgres_backup_restore_preflight import (
    POSTGRES_CONTAINER,
    RESTORE_REHEARSAL_DATABASE,
    SOURCE_DATABASE,
    collect as collect_preflight,
)
from check_postgres_runtime_readonly_state import (
    inspect_database,
    load_backend_objects,
    to_sync_url,
)
from check_postgres_schema_equivalence import (
    compare_table,
    model_signature,
    reflected_signature,
)
from create_postgres_backup import (
    run_toc_validation,
    validate_toc,
    write_text_atomic,
)
from create_postgres_restore_rehearsal_database import (
    APPROVED_BACKUP_FILENAME,
    APPROVED_BACKUP_SHA256,
    SOURCE_DATABASE_USER,
    find_approved_verified_backup,
    read_catalog,
    validate_preflight,
)

TOOL_VERSION = "v293.postgres-restore-rehearsal-execute"
DEFAULT_TIMEOUT_SECONDS = 300
RESTORE_REPORT_SUFFIX = ".restore-rehearsal-v293.json"


class RestoreRehearsalError(RuntimeError):
    """Raised when a restore boundary or post-restore verification fails."""


def ensure_project_relative_file(root: Path, relative_path: str) -> Path:
    root_resolved = root.resolve()
    path = (root / relative_path).resolve()
    if root_resolved not in path.parents:
        raise RestoreRehearsalError(f"unsafe project-relative path: {relative_path}")
    return path


def build_restore_command() -> list[str]:
    """Build a restore command pinned to the isolated target database only."""
    return [
        "docker",
        "exec",
        "-i",
        POSTGRES_CONTAINER,
        "pg_restore",
        f"--dbname={RESTORE_REHEARSAL_DATABASE}",
        f"--username={SOURCE_DATABASE_USER}",
        "--no-password",
        "--exit-on-error",
        "--single-transaction",
        "--no-owner",
        "--no-privileges",
    ]


def load_restore_evidence(root: Path) -> dict[str, Any]:
    """Load and revalidate the exact approved archive and source snapshot."""
    root = root.resolve()
    base = find_approved_verified_backup(root)
    if Path(str(base.get("backupRelativePath") or "")).name != APPROVED_BACKUP_FILENAME:
        raise RestoreRehearsalError("approved backup filename boundary changed")
    if base.get("sha256") != APPROVED_BACKUP_SHA256:
        raise RestoreRehearsalError("approved backup SHA-256 boundary changed")

    manifest_path = ensure_project_relative_file(root, str(base["manifestRelativePath"]))
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RestoreRehearsalError(f"cannot read approved backup manifest: {exc}") from exc

    snapshot_relative = str(manifest.get("sourceSnapshotRelativePath") or "")
    toc_relative = str(manifest.get("tocRelativePath") or "")
    if not snapshot_relative or not toc_relative:
        raise RestoreRehearsalError("manifest is missing source snapshot or TOC evidence")
    snapshot_path = ensure_project_relative_file(root, snapshot_relative)
    toc_path = ensure_project_relative_file(root, toc_relative)
    if not snapshot_path.is_file() or not toc_path.is_file():
        raise RestoreRehearsalError("source snapshot or TOC sidecar is missing")

    try:
        snapshot_file = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RestoreRehearsalError(f"cannot read source snapshot: {exc}") from exc
    snapshot_manifest = manifest.get("sourceSnapshot") or {}
    if snapshot_file != snapshot_manifest:
        raise RestoreRehearsalError("source snapshot sidecar differs from manifest")

    public_tables = [str(item) for item in (snapshot_file.get("publicTables") or [])]
    table_counts_raw = snapshot_file.get("tableCounts") or {}
    table_counts = {str(name): int(value) for name, value in table_counts_raw.items()}
    if len(public_tables) != 22 or snapshot_file.get("publicTableCount") != 22:
        raise RestoreRehearsalError("approved backup source table baseline is not 22")
    if set(public_tables) != set(table_counts):
        raise RestoreRehearsalError("approved source table list/count keys differ")
    if sum(table_counts.values()) != 748 or snapshot_file.get("totalRows") != 748:
        raise RestoreRehearsalError("approved backup source row baseline is not 748")
    if snapshot_file.get("alembicVersionTableExists") is not False:
        raise RestoreRehearsalError("approved backup unexpectedly contains Alembic baseline state")

    backup_path = ensure_project_relative_file(root, str(base["backupRelativePath"]))
    report_path = backup_path.with_name(f"{backup_path.name}{RESTORE_REPORT_SUFFIX}")
    if report_path.exists():
        raise RestoreRehearsalError(
            f"restore report already exists; refusing a repeated restore: {report_path.name}"
        )

    return {
        **base,
        "backupPath": backup_path,
        "manifestPath": manifest_path,
        "sourceSnapshotPath": snapshot_path,
        "tocPath": toc_path,
        "reportPath": report_path,
        "sourceSnapshot": snapshot_file,
        "expectedTables": tuple(sorted(public_tables)),
        "expectedTableCounts": dict(sorted(table_counts.items())),
        "expectedTotalRows": 748,
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
    )
    return {key: state.get(key) for key in allowed}


def validate_source_state(
    state: dict[str, Any], evidence: dict[str, Any]
) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise RestoreRehearsalError(
            f"source database connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != SOURCE_DATABASE or state.get("user") != SOURCE_DATABASE_USER:
        raise RestoreRehearsalError(
            "source database/user boundary mismatch: "
            f"{state.get('database')}/{state.get('user')}"
        )
    if state.get("tableCountsCollected") is not True:
        raise RestoreRehearsalError("source table counts were not collected")
    observed_tables = tuple(sorted(str(item) for item in (state.get("publicTables") or [])))
    observed_counts = {
        str(name): int(value) for name, value in (state.get("tableCounts") or {}).items()
    }
    if observed_tables != evidence["expectedTables"]:
        raise RestoreRehearsalError("source table list differs from the approved backup snapshot")
    if dict(sorted(observed_counts.items())) != evidence["expectedTableCounts"]:
        raise RestoreRehearsalError("source table row counts differ from the approved backup snapshot")
    if state.get("publicTableCount") != 22 or state.get("totalRows") != 748:
        raise RestoreRehearsalError("source total baseline differs from 22 tables / 748 rows")
    if state.get("missingModelTables") or state.get("extraPublicTables"):
        raise RestoreRehearsalError("source model/public table boundary changed")
    if state.get("alembicVersionTableExists") is not False:
        raise RestoreRehearsalError("source Alembic baseline state changed")
    return sanitize_database_state(state)


def inspect_named_database(root: Path, database_name: str) -> dict[str, Any]:
    """Inspect one explicitly named database without changing backend/.env."""
    try:
        settings, Base = load_backend_objects(root)
        source_url = make_url(to_sync_url(settings.database_url))
        if source_url.database != SOURCE_DATABASE:
            raise RestoreRehearsalError(
                f"configured source DB mismatch: expected={SOURCE_DATABASE}, actual={source_url.database}"
            )
        target_url = source_url.set(database=database_name)
        model_tables = {table.name: table for table in Base.metadata.sorted_tables}
        engine = create_engine(target_url, poolclass=NullPool, future=True)
        try:
            with engine.connect() as connection:
                inspector = inspect(connection)
                public_tables_all = sorted(inspector.get_table_names(schema="public"))
                actual_tables = set(public_tables_all) - {"alembic_version"}
                model_names = set(model_tables)
                identity = connection.execute(
                    text(
                        "SELECT current_database(), current_user, current_schema(), "
                        "current_setting('server_version')"
                    )
                ).one()

                preparer = connection.dialect.identifier_preparer
                schema_sql = preparer.quote_schema("public")
                counts: dict[str, int] = {}
                for table_name in public_tables_all:
                    table_sql = preparer.quote(table_name)
                    counts[table_name] = int(
                        connection.execute(
                            text(f"SELECT COUNT(*) FROM {schema_sql}.{table_sql}")
                        ).scalar_one()
                    )

                alembic_rows: list[str] = []
                if "alembic_version" in public_tables_all:
                    alembic_rows = [
                        str(row[0])
                        for row in connection.execute(
                            text(
                                "SELECT version_num FROM public.alembic_version "
                                "ORDER BY version_num"
                            )
                        ).all()
                    ]

                differences: list[Any] = []
                for table_name in sorted(model_names - actual_tables):
                    differences.append(
                        {
                            "category": "missing-table",
                            "table": table_name,
                            "detail": "model table absent from DB",
                        }
                    )
                for table_name in sorted(actual_tables - model_names):
                    differences.append(
                        {
                            "category": "extra-table",
                            "table": table_name,
                            "detail": "DB table absent from model",
                        }
                    )
                compared_tables: list[str] = []
                for table_name in sorted(model_names & actual_tables):
                    compared_tables.append(table_name)
                    differences.extend(
                        item.__dict__
                        for item in compare_table(
                            table_name,
                            model_signature(model_tables[table_name]),
                            reflected_signature(inspector, table_name),
                        )
                    )

                return {
                    "connected": True,
                    "database": str(identity[0]),
                    "user": str(identity[1]),
                    "schema": str(identity[2]),
                    "serverVersion": str(identity[3]),
                    "modelTableCount": len(model_names),
                    "publicTableCount": len(public_tables_all),
                    "publicTables": public_tables_all,
                    "tableCountsCollected": True,
                    "tableCounts": counts,
                    "totalRows": sum(counts.values()),
                    "alembicVersionTableExists": "alembic_version" in public_tables_all,
                    "alembicCurrentRevisions": alembic_rows,
                    "comparedTables": compared_tables,
                    "differenceCount": len(differences),
                    "differences": differences,
                    "schemaClassification": (
                        "structurally-equivalent" if not differences else "review-required"
                    ),
                    "classification": (
                        "empty-database"
                        if not public_tables_all
                        else "existing-schema-without-alembic-baseline"
                        if "alembic_version" not in public_tables_all
                        else "alembic-managed"
                    ),
                }
        finally:
            engine.dispose()
    except Exception as exc:
        return {
            "connected": False,
            "database": database_name,
            "error": f"{type(exc).__name__}: {exc}",
            "classification": "connection-failed",
        }


def validate_empty_target(state: dict[str, Any]) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise RestoreRehearsalError(
            f"target database connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != RESTORE_REHEARSAL_DATABASE:
        raise RestoreRehearsalError("target database boundary mismatch")
    if state.get("user") != SOURCE_DATABASE_USER:
        raise RestoreRehearsalError("target connection user boundary mismatch")
    if state.get("publicTableCount") != 0 or state.get("publicTables") not in ([], ()):
        raise RestoreRehearsalError(
            "target database is not empty; no restore/clean/drop was executed"
        )
    if state.get("totalRows") != 0 or state.get("tableCounts") not in ({}, None):
        raise RestoreRehearsalError("target database contains rows or table count entries")
    if state.get("alembicVersionTableExists") is not False:
        raise RestoreRehearsalError("target database unexpectedly contains alembic_version")
    return sanitize_database_state(state)


def validate_restored_target(
    state: dict[str, Any], evidence: dict[str, Any]
) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise RestoreRehearsalError(
            f"restored target connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != RESTORE_REHEARSAL_DATABASE:
        raise RestoreRehearsalError("restored target database boundary mismatch")
    if state.get("user") != SOURCE_DATABASE_USER:
        raise RestoreRehearsalError("restored target connection user boundary mismatch")
    observed_tables = tuple(sorted(str(item) for item in (state.get("publicTables") or [])))
    observed_counts = {
        str(name): int(value) for name, value in (state.get("tableCounts") or {}).items()
    }
    if observed_tables != evidence["expectedTables"]:
        raise RestoreRehearsalError("restored target table list differs from backup snapshot")
    if dict(sorted(observed_counts.items())) != evidence["expectedTableCounts"]:
        raise RestoreRehearsalError("restored target table row counts differ from backup snapshot")
    if state.get("publicTableCount") != 22 or state.get("totalRows") != 748:
        raise RestoreRehearsalError("restored target total is not 22 tables / 748 rows")
    if state.get("alembicVersionTableExists") is not False:
        raise RestoreRehearsalError("restored target unexpectedly contains alembic_version")
    if state.get("schemaClassification") != "structurally-equivalent":
        raise RestoreRehearsalError(
            f"restored target schema requires review: differences={state.get('differenceCount')}"
        )
    if state.get("differenceCount") != 0:
        raise RestoreRehearsalError("restored target schema difference count is not zero")
    sanitized = sanitize_database_state(state)
    sanitized.update(
        {
            "modelTableCount": state.get("modelTableCount"),
            "comparedTables": state.get("comparedTables"),
            "differenceCount": state.get("differenceCount"),
            "schemaClassification": state.get("schemaClassification"),
        }
    )
    return sanitized


def validate_catalog_boundary(catalog: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source = catalog.get(SOURCE_DATABASE)
    target = catalog.get(RESTORE_REHEARSAL_DATABASE)
    if source is None or target is None:
        raise RestoreRehearsalError("source or target database is missing from pg_database")
    if source.get("owner") != SOURCE_DATABASE_USER or target.get("owner") != SOURCE_DATABASE_USER:
        raise RestoreRehearsalError("source/target owner boundary mismatch")
    for key in ("encoding", "collate", "ctype", "locale_provider", "icu_locale"):
        if source.get(key) != target.get(key):
            raise RestoreRehearsalError(f"source/target database metadata differs for {key}")
    return {"source": source, "target": target}


def run_restore(
    root: Path,
    archive_path: Path,
    *,
    timeout: int,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]],
) -> tuple[list[str], str]:
    command = build_restore_command()
    try:
        with archive_path.open("rb") as archive:
            completed = run_process(
                command,
                cwd=root,
                text=False,
                stdin=archive,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                timeout=timeout,
            )
    except subprocess.TimeoutExpired as exc:
        raise RestoreRehearsalError(f"pg_restore timed out after {timeout} seconds") from exc
    output = decode_output(completed.stdout).strip()
    if completed.returncode != 0:
        raise RestoreRehearsalError(
            f"pg_restore failed with exit={completed.returncode}"
            + (f": {output}" if output else "")
        )
    return command, output


def execute_restore(
    root: Path,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    preflight_payload: dict[str, Any] | None = None,
    evidence: dict[str, Any] | None = None,
    source_state_before: dict[str, Any] | None = None,
    source_state_after: dict[str, Any] | None = None,
    target_state_before: dict[str, Any] | None = None,
    target_state_after: dict[str, Any] | None = None,
    catalog_before: dict[str, dict[str, Any]] | None = None,
    catalog_after: dict[str, dict[str, Any]] | None = None,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    root = root.resolve()
    preflight = preflight_payload if preflight_payload is not None else collect_preflight(root)
    validate_preflight(preflight)

    approved = evidence if evidence is not None else load_restore_evidence(root)
    before_source_raw = (
        source_state_before
        if source_state_before is not None
        else inspect_database(root, include_counts=True)
    )
    before_source = validate_source_state(before_source_raw, approved)

    catalog_before_raw = (
        catalog_before
        if catalog_before is not None
        else read_catalog(root, timeout=timeout, run_process=run_process)
    )
    boundary_before = validate_catalog_boundary(catalog_before_raw)

    before_target_raw = (
        target_state_before
        if target_state_before is not None
        else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE)
    )
    before_target = validate_empty_target(before_target_raw)

    toc_command, toc_text = run_toc_validation(
        root,
        approved["backupPath"],
        timeout=timeout,
        run_process=run_process,
    )
    toc_validation = validate_toc(toc_text, approved["expectedTables"])

    try:
        restore_command, restore_output = run_restore(
            root,
            approved["backupPath"],
            timeout=timeout,
            run_process=run_process,
        )
    except RestoreRehearsalError as exc:
        rollback_state = inspect_named_database(root, RESTORE_REHEARSAL_DATABASE)
        if rollback_state.get("connected") is True and rollback_state.get("publicTableCount") == 0:
            raise RestoreRehearsalError(
                f"{exc}; single-transaction rollback verified target remains empty"
            ) from exc
        raise RestoreRehearsalError(
            f"{exc}; target rollback state could not be verified—do not retry or drop automatically"
        ) from exc

    after_target_raw = (
        target_state_after
        if target_state_after is not None
        else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE)
    )
    after_target = validate_restored_target(after_target_raw, approved)

    catalog_after_raw = (
        catalog_after
        if catalog_after is not None
        else read_catalog(root, timeout=timeout, run_process=run_process)
    )
    boundary_after = validate_catalog_boundary(catalog_after_raw)
    if boundary_after != boundary_before:
        raise RestoreRehearsalError("source/target catalog metadata changed during restore")

    after_source_raw = (
        source_state_after
        if source_state_after is not None
        else inspect_database(root, include_counts=True)
    )
    after_source = validate_source_state(after_source_raw, approved)
    if after_source != before_source:
        raise RestoreRehearsalError("source read-only baseline changed during rehearsal restore")

    report_path: Path = approved["reportPath"]
    result = {
        "toolVersion": TOOL_VERSION,
        "result": "restore-rehearsal-completed-and-verified",
        "approvedMutation": "restore-one-verified-archive-into-one-isolated-empty-database",
        "restoreAttempted": True,
        "restoreCompleted": True,
        "restoreSingleTransaction": True,
        "sourceSchemaDataMutationAttempted": False,
        "databaseCreateAttempted": False,
        "databaseDropAttempted": False,
        "cleanExistingObjectsAttempted": False,
        "dockerResourceChanged": False,
        "environmentFileChanged": False,
        "alembicMutationAttempted": False,
        "sourceDatabase": SOURCE_DATABASE,
        "targetDatabase": RESTORE_REHEARSAL_DATABASE,
        "connectionUser": SOURCE_DATABASE_USER,
        "container": POSTGRES_CONTAINER,
        "verifiedBackup": {
            "backupRelativePath": approved["backupRelativePath"],
            "backupSizeBytes": approved["backupSizeBytes"],
            "sha256": approved["sha256"],
            "manifestRelativePath": approved["manifestRelativePath"],
        },
        "tocValidation": toc_validation,
        "sourceBefore": before_source,
        "sourceAfter": after_source,
        "targetBefore": before_target,
        "targetAfter": after_target,
        "catalogBoundary": boundary_after,
        "commands": {
            "archiveListValidation": toc_command,
            "restore": restore_command,
        },
        "restoreOutput": restore_output,
        "reportRelativePath": report_path.relative_to(root).as_posix(),
        "nextApprovalBoundary": (
            "review this verified restore result, then separately approve whether to preserve or "
            "drop the rehearsal database before preparing the empty Alembic migration test database"
        ),
    }
    write_text_atomic(
        report_path,
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    try:
        os.chmod(report_path, 0o600)
    except OSError:
        pass
    return result


def render_plan() -> str:
    return "\n".join(
        [
            "PostgreSQL restore rehearsal — execution guard",
            f"- source DB (must remain unchanged): {SOURCE_DATABASE}",
            f"- target DB (must already exist and be empty): {RESTORE_REHEARSAL_DATABASE}",
            f"- approved backup: {APPROVED_BACKUP_FILENAME}",
            f"- approved SHA-256: {APPROVED_BACKUP_SHA256}",
            "- pg_restore uses --single-transaction, --exit-on-error, --no-owner, --no-privileges",
            "- no --create, --clean, dropdb, .env edit, Docker change, or Alembic mutation",
            "- approved execution command: python tools/restore_postgres_rehearsal_database.py --execute",
        ]
    )


def render_success(result: dict[str, Any]) -> str:
    target = result["targetAfter"]
    source_before = result["sourceBefore"]
    source_after = result["sourceAfter"]
    backup = result["verifiedBackup"]
    toc = result["tocValidation"]
    return "\n".join(
        [
            "PostgreSQL restore rehearsal and verification",
            "The verified archive was restored only into the isolated rehearsal DB.",
            "",
            f"- result: {result['result']}",
            f"- source DB: {result['sourceDatabase']} (unchanged)",
            f"- target DB: {result['targetDatabase']}",
            f"- backup: {backup['backupRelativePath']}",
            f"- backup SHA-256: {backup['sha256']}",
            f"- restore transaction: {'single' if result['restoreSingleTransaction'] else 'unknown'}",
            f"- TOC definitions/data verified: {toc.get('tableDefinitionsVerified')} / {toc.get('tableDataEntriesVerified')}",
            f"- target public tables: {target.get('publicTableCount')}",
            f"- target total rows: {target.get('totalRows')}",
            f"- target schema: {target.get('schemaClassification')} / differences={target.get('differenceCount')}",
            f"- target alembic_version: {'present' if target.get('alembicVersionTableExists') else 'absent'}",
            f"- source tables before/after: {source_before.get('publicTableCount')} / {source_after.get('publicTableCount')}",
            f"- source rows before/after: {source_before.get('totalRows')} / {source_after.get('totalRows')}",
            f"- verification report: {result['reportRelativePath']}",
            "- target drop, source mutation, .env/Docker changes, and Alembic operations were not executed.",
            "- next: share only this console result; do not upload the dump or local restore report.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Restore the exact approved archive into the pinned empty rehearsal database",
    )
    parser.add_argument("--json", action="store_true", help="Print the success result as JSON")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Per PostgreSQL client command timeout in seconds",
    )
    args = parser.parse_args()

    if not args.execute:
        print(render_plan())
        return 2
    if args.timeout <= 0:
        print("ERROR: --timeout must be greater than zero", file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[1]
    try:
        result = execute_restore(root, timeout=args.timeout)
    except RestoreRehearsalError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - environment dependent safety net
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render_success(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

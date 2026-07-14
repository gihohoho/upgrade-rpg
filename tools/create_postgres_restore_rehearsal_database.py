#!/usr/bin/env python3
"""Create one empty, isolated PostgreSQL restore-rehearsal database.

This is the v292 execution step approved after a verified v291 backup was
created. It checks the target database catalog entry first and creates the
approved empty database only when it does not already exist.

Approved mutation boundary:
- MAY create exactly `rpg_game_restore_rehearsal_v290` once.
- MUST NOT restore the archive, create tables, write rows, drop a database,
  edit .env, change Docker resources, or run Alembic operations.
- MUST stop when the target database already exists.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from _safe_subprocess import decode_output
from check_postgres_backup_restore_preflight import (
    BACKUP_DIRECTORY,
    POSTGRES_CONTAINER,
    RESTORE_REHEARSAL_DATABASE,
    SOURCE_DATABASE,
    collect as collect_preflight,
)
from check_postgres_runtime_readonly_state import inspect_database
from create_postgres_backup import SOURCE_DATABASE_USER

TOOL_VERSION = "v292.postgres-restore-rehearsal-database-create"
APPROVED_BACKUP_FILENAME = "rpg_game_20260714_130403_KST_v290.custom.dump"
APPROVED_BACKUP_SHA256 = "b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481"
DEFAULT_TIMEOUT_SECONDS = 60
SUPPORTED_LOCALE_PROVIDERS = {"c": "libc", "i": "icu"}


class RehearsalDatabaseError(RuntimeError):
    """Raised when a safety gate, existence check, or creation check fails."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_project_relative_file(root: Path, relative_path: str) -> Path:
    root_resolved = root.resolve()
    path = (root / relative_path).resolve()
    if root_resolved not in path.parents:
        raise RehearsalDatabaseError(f"unsafe project-relative path: {relative_path}")
    return path


def validate_preflight(payload: dict[str, Any]) -> None:
    if payload.get("readyForUserApproval") is not True:
        reasons = payload.get("blockingReasons") or [payload.get("classification", "blocked")]
        raise RehearsalDatabaseError(
            "preflight blocked: " + "; ".join(str(item) for item in reasons)
        )
    tools = payload.get("toolAvailability") or {}
    if tools.get("selectedExecutionMode") != "docker-container":
        raise RehearsalDatabaseError(
            "v292 database creation requires selectedExecutionMode=docker-container"
        )
    container = tools.get("dockerContainer") or {}
    if container.get("name") != POSTGRES_CONTAINER or container.get("running") is not True:
        raise RehearsalDatabaseError(f"required container is not running: {POSTGRES_CONTAINER}")


def validate_source_state(state: dict[str, Any]) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise RehearsalDatabaseError(
            f"source database connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != SOURCE_DATABASE:
        raise RehearsalDatabaseError(
            f"source database boundary mismatch: expected={SOURCE_DATABASE}, "
            f"actual={state.get('database')}"
        )
    if state.get("user") != SOURCE_DATABASE_USER:
        raise RehearsalDatabaseError(
            f"source user boundary mismatch: expected={SOURCE_DATABASE_USER}, "
            f"actual={state.get('user')}"
        )
    if state.get("publicTableCount") != 22 or state.get("totalRows") != 748:
        raise RehearsalDatabaseError(
            "source baseline changed: expected publicTableCount=22 and totalRows=748, "
            f"actual={state.get('publicTableCount')}/{state.get('totalRows')}"
        )
    if state.get("missingModelTables") or state.get("extraPublicTables"):
        raise RehearsalDatabaseError("source table boundary changed")
    if state.get("alembicVersionTableExists") is not False:
        raise RehearsalDatabaseError("source Alembic baseline state changed")
    return {
        "database": state.get("database"),
        "user": state.get("user"),
        "serverVersion": state.get("serverVersion"),
        "publicTableCount": state.get("publicTableCount"),
        "totalRows": state.get("totalRows"),
        "classification": state.get("classification"),
        "alembicVersionTableExists": state.get("alembicVersionTableExists"),
    }


def find_approved_verified_backup(root: Path) -> dict[str, Any]:
    backup_dir = (root / BACKUP_DIRECTORY).resolve()
    if not backup_dir.exists():
        raise RehearsalDatabaseError(
            f"verified backup directory is missing: {BACKUP_DIRECTORY}"
        )
    approved_manifest = backup_dir / f"{APPROVED_BACKUP_FILENAME}.manifest.json"
    manifests = [approved_manifest] if approved_manifest.is_file() else []
    if not manifests:
        raise RehearsalDatabaseError(
            f"approved verified backup manifest is missing: {approved_manifest.name}"
        )

    failures: list[str] = []
    for manifest_path in manifests:
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            if payload.get("backupCreated") is not True or payload.get("backupValidated") is not True:
                raise RehearsalDatabaseError("manifest does not declare a verified backup")
            if payload.get("sourceDatabase") != SOURCE_DATABASE:
                raise RehearsalDatabaseError("manifest source database mismatch")
            if payload.get("sourceUser") != SOURCE_DATABASE_USER:
                raise RehearsalDatabaseError("manifest source user mismatch")
            if Path(str(payload.get("backupRelativePath") or "")).name != APPROVED_BACKUP_FILENAME:
                raise RehearsalDatabaseError("manifest backup filename is not the approved v292 artifact")

            backup_path = ensure_project_relative_file(root, str(payload["backupRelativePath"]))
            checksum_path = ensure_project_relative_file(root, str(payload["checksumRelativePath"]))
            if backup_path.parent != backup_dir or checksum_path.parent != backup_dir:
                raise RehearsalDatabaseError("backup artifacts are outside the approved directory")
            if not backup_path.is_file() or backup_path.stat().st_size <= 0:
                raise RehearsalDatabaseError("backup archive is missing or empty")
            if not checksum_path.is_file():
                raise RehearsalDatabaseError("checksum sidecar is missing")

            actual_hash = sha256_file(backup_path)
            manifest_hash = str(payload.get("sha256") or "")
            checksum_line = checksum_path.read_text(encoding="utf-8").strip()
            if actual_hash != manifest_hash:
                raise RehearsalDatabaseError("backup SHA-256 does not match the manifest")
            if actual_hash != APPROVED_BACKUP_SHA256:
                raise RehearsalDatabaseError("backup SHA-256 is not the exact user-approved v292 artifact")
            if checksum_line != f"{actual_hash}  {backup_path.name}":
                raise RehearsalDatabaseError("backup SHA-256 sidecar does not match")
            if int(payload.get("backupSizeBytes") or -1) != backup_path.stat().st_size:
                raise RehearsalDatabaseError("backup size does not match the manifest")

            source_snapshot = payload.get("sourceSnapshot") or {}
            if source_snapshot.get("publicTableCount") != 22 or source_snapshot.get("totalRows") != 748:
                raise RehearsalDatabaseError("backup source snapshot baseline is not 22 tables / 748 rows")

            return {
                "manifestRelativePath": manifest_path.relative_to(root).as_posix(),
                "backupRelativePath": backup_path.relative_to(root).as_posix(),
                "backupSizeBytes": backup_path.stat().st_size,
                "sha256": actual_hash,
                "sourcePublicTableCount": source_snapshot.get("publicTableCount"),
                "sourceTotalRows": source_snapshot.get("totalRows"),
            }
        except Exception as exc:
            failures.append(f"{manifest_path.name}: {exc}")

    raise RehearsalDatabaseError(
        "no valid verified backup remained after SHA-256 checks: " + "; ".join(failures)
    )


def database_catalog_query() -> str:
    names = ", ".join(f"'{name}'" for name in (SOURCE_DATABASE, RESTORE_REHEARSAL_DATABASE))
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
        raise RehearsalDatabaseError(
            f"unsupported source locale provider for PostgreSQL 16: {provider_code or 'missing'}"
        )
    encoding = str(source_metadata.get("encoding") or "")
    collate = str(source_metadata.get("collate") or "")
    ctype = str(source_metadata.get("ctype") or "")
    if not encoding or not collate or not ctype:
        raise RehearsalDatabaseError("source encoding/collation metadata is incomplete")

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
            raise RehearsalDatabaseError("source ICU locale is missing")
        command.extend(["--locale-provider=icu", f"--icu-locale={icu_locale}"])
    command.append(RESTORE_REHEARSAL_DATABASE)
    return command


def target_state_query() -> str:
    return (
        "SELECT json_build_object("
        "'database', current_database(), "
        "'user', current_user, "
        "'publicTableCount', (SELECT COUNT(*) FROM pg_catalog.pg_tables WHERE schemaname='public'), "
        "'alembicVersionTableExists', to_regclass('public.alembic_version') IS NOT NULL"
        ")::text;"
    )


def build_target_state_command() -> list[str]:
    return [
        "docker",
        "exec",
        POSTGRES_CONTAINER,
        "psql",
        f"--dbname={RESTORE_REHEARSAL_DATABASE}",
        f"--username={SOURCE_DATABASE_USER}",
        "--no-password",
        "--tuples-only",
        "--no-align",
        "--set=ON_ERROR_STOP=1",
        f"--command={target_state_query()}",
    ]


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
        raise RehearsalDatabaseError(
            f"command timed out after {timeout} seconds: {' '.join(command[:5])}"
        ) from exc
    output = decode_output(completed.stdout).strip()
    if completed.returncode != 0:
        raise RehearsalDatabaseError(
            f"command failed with exit={completed.returncode}: {output or 'no output'}"
        )
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise RehearsalDatabaseError(f"unexpected PostgreSQL JSON output: {output}") from exc


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
        raise RehearsalDatabaseError("database catalog result is not a list")
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
        raise RehearsalDatabaseError(f"createdb timed out after {timeout} seconds") from exc
    output = decode_output(completed.stdout).strip()
    if completed.returncode != 0:
        raise RehearsalDatabaseError(
            f"createdb failed with exit={completed.returncode}: {output or 'no output'}"
        )


def execute_creation(
    root: Path,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    preflight_payload: dict[str, Any] | None = None,
    source_state_before: dict[str, Any] | None = None,
    source_state_after: dict[str, Any] | None = None,
    backup_evidence: dict[str, Any] | None = None,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    root = root.resolve()
    preflight = preflight_payload if preflight_payload is not None else collect_preflight(root)
    validate_preflight(preflight)

    before_raw = (
        source_state_before
        if source_state_before is not None
        else inspect_database(root, include_counts=True)
    )
    before = validate_source_state(before_raw)
    backup = backup_evidence if backup_evidence is not None else find_approved_verified_backup(root)

    catalog_before = read_catalog(root, timeout=timeout, run_process=run_process)
    source_metadata = catalog_before.get(SOURCE_DATABASE)
    if source_metadata is None:
        raise RehearsalDatabaseError(f"source database is missing from pg_database: {SOURCE_DATABASE}")
    if source_metadata.get("owner") != SOURCE_DATABASE_USER:
        raise RehearsalDatabaseError(
            f"source database owner mismatch: expected={SOURCE_DATABASE_USER}, "
            f"actual={source_metadata.get('owner')}"
        )
    if RESTORE_REHEARSAL_DATABASE in catalog_before:
        raise RehearsalDatabaseError(
            f"target database already exists; no create/restore/drop was executed: "
            f"{RESTORE_REHEARSAL_DATABASE}"
        )

    create_command = build_create_command(source_metadata)
    run_create(root, create_command, timeout=timeout, run_process=run_process)

    catalog_after = read_catalog(root, timeout=timeout, run_process=run_process)
    target_metadata = catalog_after.get(RESTORE_REHEARSAL_DATABASE)
    if target_metadata is None:
        raise RehearsalDatabaseError(
            "createdb returned success but the target database is not visible; do not retry or drop automatically"
        )
    for key in ("owner", "encoding", "collate", "ctype", "locale_provider", "icu_locale"):
        if target_metadata.get(key) != source_metadata.get(key):
            raise RehearsalDatabaseError(
                f"created target metadata differs for {key}; do not restore or drop automatically"
            )

    target_state = run_json_command(
        build_target_state_command(), root=root, timeout=timeout, run_process=run_process
    )
    if not isinstance(target_state, dict):
        raise RehearsalDatabaseError("target state result is not an object")
    if target_state.get("database") != RESTORE_REHEARSAL_DATABASE:
        raise RehearsalDatabaseError("target connection boundary mismatch")
    if target_state.get("user") != SOURCE_DATABASE_USER:
        raise RehearsalDatabaseError("target owner/user boundary mismatch")
    if int(target_state.get("publicTableCount", -1)) != 0:
        raise RehearsalDatabaseError(
            "target database is not empty; do not restore or drop automatically"
        )
    if target_state.get("alembicVersionTableExists") is not False:
        raise RehearsalDatabaseError("target database unexpectedly contains alembic_version")

    after_raw = (
        source_state_after
        if source_state_after is not None
        else inspect_database(root, include_counts=True)
    )
    after = validate_source_state(after_raw)
    if after != before:
        raise RehearsalDatabaseError(
            "source read-only baseline changed during target creation; stop before restore"
        )

    return {
        "toolVersion": TOOL_VERSION,
        "result": "restore-rehearsal-database-created-empty-and-verified",
        "approvedMutation": "create-one-empty-isolated-database",
        "databaseCreated": True,
        "databaseAlreadyExisted": False,
        "restoreAttempted": False,
        "databaseDropAttempted": False,
        "sourceSchemaDataMutationAttempted": False,
        "dockerResourceChanged": False,
        "environmentFileChanged": False,
        "alembicMutationAttempted": False,
        "sourceDatabase": SOURCE_DATABASE,
        "targetDatabase": RESTORE_REHEARSAL_DATABASE,
        "owner": SOURCE_DATABASE_USER,
        "container": POSTGRES_CONTAINER,
        "template": "template0",
        "sourceMetadata": source_metadata,
        "targetMetadata": target_metadata,
        "targetState": target_state,
        "sourceBefore": before,
        "sourceAfter": after,
        "verifiedBackup": backup,
        "commands": {
            "catalogCheck": build_catalog_command(),
            "createDatabase": create_command,
            "targetEmptyCheck": build_target_state_command(),
        },
        "nextApprovalBoundary": (
            "request separate approval before pg_restore writes schema/data into the rehearsal database"
        ),
    }


def render_plan() -> str:
    return "\n".join(
        [
            "PostgreSQL restore rehearsal database creation — execution guard",
            f"- source DB (unchanged): {SOURCE_DATABASE}",
            f"- target DB (create only if absent): {RESTORE_REHEARSAL_DATABASE}",
            f"- owner: {SOURCE_DATABASE_USER}",
            f"- container: {POSTGRES_CONTAINER}",
            f"- requires approved backup: {APPROVED_BACKUP_FILENAME}",
            f"- required SHA-256: {APPROVED_BACKUP_SHA256}",
            "- no pg_restore, table/row creation, dropdb, .env edit, Docker change, or Alembic mutation",
            "- approved execution command: python tools/create_postgres_restore_rehearsal_database.py --execute",
        ]
    )


def render_success(result: dict[str, Any]) -> str:
    target = result["targetState"]
    backup = result["verifiedBackup"]
    return "\n".join(
        [
            "PostgreSQL restore rehearsal database creation",
            "One isolated empty database was created; no restore or source schema/data mutation was executed.",
            "",
            f"- result: {result['result']}",
            f"- source DB: {result['sourceDatabase']} (unchanged)",
            f"- target DB: {result['targetDatabase']}",
            f"- target owner: {result['targetMetadata'].get('owner')}",
            f"- target connection user: {target.get('user')}",
            f"- template: {result['template']}",
            f"- target public tables: {target.get('publicTableCount')}",
            f"- target alembic_version: {'present' if target.get('alembicVersionTableExists') else 'absent'}",
            f"- verified backup: {backup.get('backupRelativePath')}",
            f"- backup SHA-256: {backup.get('sha256')}",
            f"- source tables before/after: {result['sourceBefore']['publicTableCount']} / {result['sourceAfter']['publicTableCount']}",
            f"- source rows before/after: {result['sourceBefore']['totalRows']} / {result['sourceAfter']['totalRows']}",
            "- pg_restore, dropdb, .env edits, Docker changes, and Alembic operations were not executed.",
            "- next: share only this console result for a separate restore approval boundary.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Create the approved empty rehearsal database after all gates pass",
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
        print("\nBLOCKED: --execute is required; no database existence check or mutation was executed.")
        return 2

    root = Path(__file__).resolve().parents[1]
    try:
        result = execute_creation(root, timeout=args.timeout)
    except RehearsalDatabaseError as exc:
        print("PostgreSQL restore rehearsal database creation")
        print("- result: blocked-or-failed")
        print(f"- reason: {exc}")
        print("- no automatic restore or drop was attempted.")
        return 1
    except Exception as exc:  # pragma: no cover - environment dependent
        print("PostgreSQL restore rehearsal database creation")
        print("- result: unexpected-error")
        print(f"- reason: {type(exc).__name__}: {exc}")
        print("- no automatic restore or drop was attempted.")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_success(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

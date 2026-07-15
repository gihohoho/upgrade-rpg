#!/usr/bin/env python3
"""Create and verify one approved PostgreSQL logical backup without DB mutation.

This tool is the v291 execution step for the backup policy approved after the
v290 read-only preflight. It reads the source database through pg_dump and
creates local files only. It never restores data, creates/drops a database,
changes Docker resources, edits .env, or runs Alembic mutation commands.

Safety properties:

1. Re-runs the schema/preflight gate immediately before the dump.
2. Requires the existing Docker PostgreSQL container and exact source DB/user.
3. Streams the custom-format dump to a private .partial file without shell
   redirection, then validates it with pg_restore --list.
4. Publishes the final dump only after archive validation succeeds.
5. Writes SHA-256, TOC, source-count snapshot, and manifest sidecars.
6. Refuses overwrite/collision and never targets a restore database.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from _safe_subprocess import decode_output
from check_postgres_backup_restore_preflight import (
    BACKUP_DIRECTORY,
    POSTGRES_CONTAINER,
    SOURCE_DATABASE,
    collect as collect_preflight,
)
from check_postgres_runtime_readonly_state import inspect_database

TOOL_VERSION = "v291.postgres-backup-create-and-verify"
APPROVED_BACKUP_POLICY_VERSION = "v290"
SOURCE_DATABASE_USER = "rpg_user"
KST = timezone(timedelta(hours=9), name="KST")
DEFAULT_TIMEOUT_SECONDS = 300


class BackupError(RuntimeError):
    """Raised when a safety gate or backup verification fails."""


def private_mode(path: Path, mode: int) -> None:
    """Best-effort private permissions; Windows may not honor POSIX bits fully."""
    try:
        path.chmod(mode)
    except OSError:
        pass


def ensure_inside_project(root: Path, relative_directory: str) -> Path:
    root_resolved = root.resolve()
    target = (root / relative_directory).resolve()
    if target == root_resolved or root_resolved not in target.parents:
        raise BackupError(f"unsafe backup directory: {target}")
    return target


def filename_for(now: datetime) -> str:
    local = now.astimezone(KST)
    stamp = local.strftime("%Y%m%d_%H%M%S")
    return f"{SOURCE_DATABASE}_{stamp}_KST_{APPROVED_BACKUP_POLICY_VERSION}.custom.dump"


def build_dump_command() -> list[str]:
    return [
        "docker",
        "exec",
        POSTGRES_CONTAINER,
        "pg_dump",
        "--format=custom",
        "--no-password",
        f"--username={SOURCE_DATABASE_USER}",
        f"--dbname={SOURCE_DATABASE}",
    ]


def build_toc_command() -> list[str]:
    # pg_restore uses standard input when no archive filename is supplied.
    return ["docker", "exec", "-i", POSTGRES_CONTAINER, "pg_restore", "--list"]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_atomic(path: Path, value: str) -> None:
    partial = path.with_name(f"{path.name}.partial")
    if partial.exists():
        partial.unlink()
    with partial.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(value)
        handle.flush()
        os.fsync(handle.fileno())
    private_mode(partial, 0o600)
    os.replace(partial, path)
    private_mode(path, 0o600)


def source_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    allowed = (
        "database",
        "user",
        "schema",
        "serverVersion",
        "databaseSizeBytes",
        "databaseSizePretty",
        "modelTableCount",
        "publicTableCount",
        "modelTables",
        "publicTables",
        "missingModelTables",
        "extraPublicTables",
        "tableCountsCollected",
        "tableCounts",
        "nonEmptyTables",
        "totalRows",
        "alembicVersionTableExists",
        "alembicCurrentRevisions",
        "classification",
    )
    return {key: state.get(key) for key in allowed}


def validate_preflight(payload: dict[str, Any]) -> None:
    if payload.get("readyForUserApproval") is not True:
        reasons = payload.get("blockingReasons") or [payload.get("classification", "blocked")]
        raise BackupError("preflight blocked: " + "; ".join(str(item) for item in reasons))
    tools = payload.get("toolAvailability") or {}
    if tools.get("selectedExecutionMode") != "docker-container":
        raise BackupError("v291 backup execution requires selectedExecutionMode=docker-container")
    container = tools.get("dockerContainer") or {}
    if container.get("name") != POSTGRES_CONTAINER or container.get("running") is not True:
        raise BackupError(f"required container is not running: {POSTGRES_CONTAINER}")


def validate_source_state(state: dict[str, Any]) -> tuple[str, ...]:
    if state.get("connected") is not True:
        raise BackupError(f"source database connection failed: {state.get('error', 'unknown error')}")
    if state.get("database") != SOURCE_DATABASE:
        raise BackupError(
            f"source database boundary mismatch: expected={SOURCE_DATABASE}, actual={state.get('database')}"
        )
    if state.get("user") != SOURCE_DATABASE_USER:
        raise BackupError(
            f"source database user mismatch: expected={SOURCE_DATABASE_USER}, actual={state.get('user')}"
        )
    if state.get("missingModelTables") or state.get("extraPublicTables"):
        raise BackupError("source table boundary changed after schema gate")
    if state.get("tableCountsCollected") is not True:
        raise BackupError("source table counts were not collected")
    tables = tuple(str(item) for item in (state.get("publicTables") or []))
    if not tables:
        raise BackupError("source public table list is empty")
    if state.get("publicTableCount") != len(tables):
        raise BackupError("source public table count/list mismatch")
    return tables


def header_value(toc_text: str, label: str) -> str | None:
    match = re.search(rf"^;\s*{re.escape(label)}:\s*(.+?)\s*$", toc_text, flags=re.MULTILINE)
    return match.group(1) if match else None


def toc_has_entry(toc_text: str, object_type: str, table_name: str) -> bool:
    pattern = (
        rf"^\d+;\s+\d+\s+\d+\s+{re.escape(object_type)}\s+public\s+"
        rf"{re.escape(table_name)}(?:\s|$)"
    )
    return re.search(pattern, toc_text, flags=re.MULTILINE) is not None


def validate_toc(toc_text: str, expected_tables: tuple[str, ...]) -> dict[str, Any]:
    archive_format = header_value(toc_text, "Format")
    if archive_format != "CUSTOM":
        raise BackupError(f"unexpected archive format: {archive_format or 'missing'}")

    missing_definitions = [
        table for table in expected_tables if not toc_has_entry(toc_text, "TABLE", table)
    ]
    missing_data = [
        table for table in expected_tables if not toc_has_entry(toc_text, "TABLE DATA", table)
    ]
    if missing_definitions or missing_data:
        detail: list[str] = []
        if missing_definitions:
            detail.append("missing TABLE: " + ", ".join(missing_definitions))
        if missing_data:
            detail.append("missing TABLE DATA: " + ", ".join(missing_data))
        raise BackupError("archive TOC validation failed: " + "; ".join(detail))

    return {
        "format": archive_format,
        "tocEntries": header_value(toc_text, "TOC Entries"),
        "compression": header_value(toc_text, "Compression"),
        "dumpVersion": header_value(toc_text, "Dump Version"),
        "dumpedFromDatabaseVersion": header_value(toc_text, "Dumped from database version"),
        "dumpedByPgDumpVersion": header_value(toc_text, "Dumped by pg_dump version"),
        "expectedTableCount": len(expected_tables),
        "tableDefinitionsVerified": len(expected_tables),
        "tableDataEntriesVerified": len(expected_tables),
        "missingTableDefinitions": [],
        "missingTableDataEntries": [],
    }


def run_dump(
    root: Path,
    partial_path: Path,
    *,
    timeout: int,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]],
) -> list[str]:
    command = build_dump_command()
    try:
        with partial_path.open("xb") as output:
            private_mode(partial_path, 0o600)
            completed = run_process(
                command,
                cwd=root,
                text=False,
                stdin=subprocess.DEVNULL,
                stdout=output,
                stderr=subprocess.PIPE,
                check=False,
                timeout=timeout,
            )
            output.flush()
            os.fsync(output.fileno())
    except FileExistsError as exc:
        raise BackupError(f"partial backup already exists: {partial_path.name}") from exc
    except subprocess.TimeoutExpired as exc:
        partial_path.unlink(missing_ok=True)
        raise BackupError(f"pg_dump timed out after {timeout} seconds") from exc
    except Exception:
        partial_path.unlink(missing_ok=True)
        raise

    stderr = decode_output(completed.stderr).strip()
    if completed.returncode != 0:
        partial_path.unlink(missing_ok=True)
        raise BackupError(
            f"pg_dump failed with exit={completed.returncode}"
            + (f": {stderr}" if stderr else "")
        )
    if partial_path.stat().st_size <= 0:
        partial_path.unlink(missing_ok=True)
        raise BackupError("pg_dump produced an empty file")
    return command


def run_toc_validation(
    root: Path,
    archive_path: Path,
    *,
    timeout: int,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]],
) -> tuple[list[str], str]:
    command = build_toc_command()
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
        raise BackupError(f"pg_restore --list timed out after {timeout} seconds") from exc
    output = decode_output(completed.stdout).strip()
    if completed.returncode != 0:
        raise BackupError(
            f"pg_restore --list failed with exit={completed.returncode}"
            + (f": {output}" if output else "")
        )
    if not output:
        raise BackupError("pg_restore --list returned no TOC output")
    return command, output


def execute_backup(
    root: Path,
    *,
    now: datetime | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    preflight_payload: dict[str, Any] | None = None,
    source_state: dict[str, Any] | None = None,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    root = root.resolve()
    preflight = preflight_payload if preflight_payload is not None else collect_preflight(root)
    validate_preflight(preflight)

    observed = source_state if source_state is not None else inspect_database(root, include_counts=True)
    expected_tables = validate_source_state(observed)
    sanitized_source = source_snapshot(observed)

    backup_dir = ensure_inside_project(root, BACKUP_DIRECTORY)
    backup_dir.mkdir(parents=True, exist_ok=True)
    private_mode(backup_dir, 0o700)

    created_at = (now or datetime.now(KST)).astimezone(KST)
    filename = filename_for(created_at)
    dump_path = backup_dir / filename
    partial_path = backup_dir / f"{filename}.partial"
    checksum_path = backup_dir / f"{filename}.sha256"
    toc_path = backup_dir / f"{filename}.toc.txt"
    snapshot_path = backup_dir / f"{filename}.source.json"
    manifest_path = backup_dir / f"{filename}.manifest.json"
    artifacts = (dump_path, partial_path, checksum_path, toc_path, snapshot_path, manifest_path)
    collisions = [path.name for path in artifacts if path.exists()]
    if collisions:
        raise BackupError("refusing to overwrite existing backup artifact(s): " + ", ".join(collisions))

    dump_command: list[str] = []
    toc_command: list[str] = []
    try:
        dump_command = run_dump(
            root,
            partial_path,
            timeout=timeout,
            run_process=run_process,
        )
        toc_command, toc_text = run_toc_validation(
            root,
            partial_path,
            timeout=timeout,
            run_process=run_process,
        )
        toc_summary = validate_toc(toc_text, expected_tables)
        os.replace(partial_path, dump_path)
        private_mode(dump_path, 0o600)

        checksum = sha256_file(dump_path)
        write_text_atomic(checksum_path, f"{checksum}  {filename}\n")
        write_text_atomic(toc_path, toc_text + "\n")
        write_text_atomic(
            snapshot_path,
            json.dumps(sanitized_source, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )

        result = {
            "toolVersion": TOOL_VERSION,
            "approvedBackupPolicyVersion": APPROVED_BACKUP_POLICY_VERSION,
            "backupCreated": True,
            "backupValidated": True,
            "databaseMutationAttempted": False,
            "restoreAttempted": False,
            "databaseCreateDropAttempted": False,
            "dockerResourceChanged": False,
            "environmentFileChanged": False,
            "alembicMutationAttempted": False,
            "createdAtKst": created_at.isoformat(),
            "sourceDatabase": SOURCE_DATABASE,
            "sourceUser": SOURCE_DATABASE_USER,
            "container": POSTGRES_CONTAINER,
            "format": "PostgreSQL custom format",
            "backupRelativePath": dump_path.relative_to(root).as_posix(),
            "backupSizeBytes": dump_path.stat().st_size,
            "sha256": checksum,
            "checksumRelativePath": checksum_path.relative_to(root).as_posix(),
            "tocRelativePath": toc_path.relative_to(root).as_posix(),
            "sourceSnapshotRelativePath": snapshot_path.relative_to(root).as_posix(),
            "manifestRelativePath": manifest_path.relative_to(root).as_posix(),
            "sourceSnapshot": sanitized_source,
            "tocValidation": toc_summary,
            "commands": {
                "dump": dump_command,
                "archiveListValidation": toc_command,
            },
            "sensitiveDataPolicy": {
                "containsSensitiveGameAndUserData": True,
                "includeInGit": False,
                "includeInHandoffZip": False,
                "shareExternally": False,
            },
            "nextApprovalBoundary": (
                "inspect these local artifacts, then request separate approval before creating "
                "the restore rehearsal database"
            ),
        }
        write_text_atomic(
            manifest_path,
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )
        return result
    except Exception:
        partial_path.unlink(missing_ok=True)
        raise


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{size} B"


def render_plan() -> str:
    return "\n".join(
        [
            "PostgreSQL backup creation - execution guard",
            "- This command creates a local sensitive dump file only when --execute is supplied.",
            f"- source DB: {SOURCE_DATABASE}",
            f"- container: {POSTGRES_CONTAINER}",
            f"- output directory: {BACKUP_DIRECTORY}",
            f"- approved filename version: {APPROVED_BACKUP_POLICY_VERSION}",
            "- no restore, createdb, dropdb, Docker resource change, .env edit, or Alembic mutation",
            "- approved execution command: python tools/create_postgres_backup.py --execute",
        ]
    )


def render_success(result: dict[str, Any]) -> str:
    source = result["sourceSnapshot"]
    toc = result["tocValidation"]
    return "\n".join(
        [
            "PostgreSQL backup creation and archive verification",
            "Source DB was read by pg_dump; no DB schema/data mutation was executed.",
            "",
            "- result: backup-created-and-verified",
            f"- backup: {result['backupRelativePath']}",
            f"- size: {human_size(int(result['backupSizeBytes']))}",
            f"- SHA-256: {result['sha256']}",
            f"- source tables: {source.get('publicTableCount')}",
            f"- source total rows: {source.get('totalRows')}",
            f"- TOC format: {toc.get('format')}",
            f"- TOC table definitions verified: {toc.get('tableDefinitionsVerified')}",
            f"- TOC table data entries verified: {toc.get('tableDataEntriesVerified')}",
            f"- checksum: {result['checksumRelativePath']}",
            f"- TOC list: {result['tocRelativePath']}",
            f"- source snapshot: {result['sourceSnapshotRelativePath']}",
            f"- manifest: {result['manifestRelativePath']}",
            "- sensitive backup files remain under local-backups/ and must not be uploaded or committed.",
            "- restore rehearsal DB creation/restore/drop and Alembic operations were not executed.",
            "- next: share only this console result, not the .dump file, for the next approval boundary.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Create the approved local backup after re-running all safety gates",
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
        result = execute_backup(root, timeout=args.timeout)
    except BackupError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - environment dependent safety net
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render_success(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

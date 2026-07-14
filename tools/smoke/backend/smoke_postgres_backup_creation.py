#!/usr/bin/env python3
"""Smoke checks for the v291 approved PostgreSQL backup creation tool."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/create_postgres_backup.py"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_tool() -> Any:
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("create_postgres_backup", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load backup tool")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ready_preflight() -> dict[str, Any]:
    return {
        "readyForUserApproval": True,
        "classification": "ready-for-user-approval",
        "blockingReasons": [],
        "toolAvailability": {
            "selectedExecutionMode": "docker-container",
            "dockerContainer": {
                "name": "upgrade_rpg_postgres",
                "running": True,
            },
        },
    }


def source_state() -> dict[str, Any]:
    return {
        "connected": True,
        "database": "rpg_game",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "databaseSizeBytes": 12345,
        "databaseSizePretty": "12 kB",
        "modelTableCount": 2,
        "publicTableCount": 2,
        "modelTables": ["characters", "users"],
        "publicTables": ["characters", "users"],
        "missingModelTables": [],
        "extraPublicTables": [],
        "tableCountsCollected": True,
        "tableCounts": {"characters": 1, "users": 1},
        "nonEmptyTables": ["characters", "users"],
        "totalRows": 2,
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "existing-schema-without-alembic-baseline",
    }


def toc_text() -> str:
    return "\n".join(
        [
            ";",
            "; Archive created at 2026-07-14 12:00:00 KST",
            ";     dbname: rpg_game",
            ";     TOC Entries: 4",
            ";     Compression: -1",
            ";     Dump Version: 1.15-0",
            ";     Format: CUSTOM",
            ";     Dumped from database version: 16.14",
            ";     Dumped by pg_dump version: 16.14",
            ";",
            "1; 1259 100 TABLE public characters rpg_user",
            "2; 0 100 TABLE DATA public characters rpg_user",
            "3; 1259 101 TABLE public users rpg_user",
            "4; 0 101 TABLE DATA public users rpg_user",
        ]
    )


def fake_runner(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
    if "pg_dump" in command:
        output = kwargs.get("stdout")
        if output is None or not hasattr(output, "write"):
            raise AssertionError("pg_dump must stream to a binary file handle")
        output.write(b"PGDMP\x01\x0fFAKE-ARCHIVE-CONTENT")
        return subprocess.CompletedProcess(command, 0, stdout=None, stderr=b"")
    if "pg_restore" in command:
        archive = kwargs.get("stdin")
        if archive is None or archive.read(5) != b"PGDMP":
            raise AssertionError("pg_restore --list must validate the generated archive through stdin")
        archive.seek(0)
        return subprocess.CompletedProcess(command, 0, stdout=toc_text().encode("utf-8"), stderr=None)
    raise AssertionError(f"unexpected command: {command}")


def failing_toc_runner(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
    if "pg_dump" in command:
        kwargs["stdout"].write(b"PGDMP-invalid")
        return subprocess.CompletedProcess(command, 0, stdout=None, stderr=b"")
    if "pg_restore" in command:
        return subprocess.CompletedProcess(command, 1, stdout=b"invalid archive", stderr=None)
    raise AssertionError(f"unexpected command: {command}")


def main() -> int:
    if not TOOL.exists():
        return fail("missing tools/create_postgres_backup.py")

    module = load_tool()
    source = TOOL.read_text(encoding="utf-8")
    for required in (
        "--execute",
        "pg_dump",
        "pg_restore",
        "--format=custom",
        "--no-password",
        ".partial",
        "sha256",
        "manifest.json",
        "databaseMutationAttempted",
        "restoreAttempted",
        "databaseCreateDropAttempted",
    ):
        if required not in source:
            return fail(f"backup tool missing safety marker: {required}")

    dump_command = module.build_dump_command()
    toc_command = module.build_toc_command()
    if dump_command[:4] != ["docker", "exec", "upgrade_rpg_postgres", "pg_dump"]:
        return fail(f"unexpected dump command boundary: {dump_command}")
    if "--dbname=rpg_game" not in dump_command or "--username=rpg_user" not in dump_command:
        return fail("dump command must pin the approved source DB/user")
    if any(item in dump_command for item in ("--create", "--clean", "createdb", "dropdb")):
        return fail("dump command contains a forbidden mutation option")
    if toc_command != ["docker", "exec", "-i", "upgrade_rpg_postgres", "pg_restore", "--list"]:
        return fail(f"unexpected TOC validation command: {toc_command}")

    guard = subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if guard.returncode != 2 or "--execute" not in guard.stdout:
        return fail("tool must refuse backup creation unless --execute is supplied")

    with tempfile.TemporaryDirectory() as temporary:
        temp_root = Path(temporary)
        result = module.execute_backup(
            temp_root,
            now=datetime(2026, 7, 14, 3, 0, 0, tzinfo=timezone.utc),
            preflight_payload=ready_preflight(),
            source_state=source_state(),
            run_process=fake_runner,
        )
        backup = temp_root / result["backupRelativePath"]
        checksum = temp_root / result["checksumRelativePath"]
        toc = temp_root / result["tocRelativePath"]
        snapshot = temp_root / result["sourceSnapshotRelativePath"]
        manifest = temp_root / result["manifestRelativePath"]
        for path in (backup, checksum, toc, snapshot, manifest):
            if not path.exists():
                return fail(f"expected backup artifact missing: {path.name}")
        if backup.name != "rpg_game_20260714_120000_KST_v290.custom.dump":
            return fail(f"unexpected backup filename: {backup.name}")
        actual_hash = hashlib.sha256(backup.read_bytes()).hexdigest()
        if result["sha256"] != actual_hash or not checksum.read_text(encoding="utf-8").startswith(actual_hash):
            return fail("SHA-256 sidecar mismatch")
        if result["backupCreated"] is not True or result["backupValidated"] is not True:
            return fail("success result must declare created and validated")
        if result["databaseMutationAttempted"] is not False:
            return fail("backup tool must declare no database mutation")
        if result["restoreAttempted"] is not False or result["databaseCreateDropAttempted"] is not False:
            return fail("backup tool must not restore or create/drop databases")
        manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
        if manifest_payload.get("sha256") != actual_hash:
            return fail("manifest hash mismatch")
        if manifest_payload.get("sourceSnapshot", {}).get("totalRows") != 2:
            return fail("source row-count snapshot missing")
        partials = list((temp_root / "local-backups/postgres").glob("*.partial"))
        if partials:
            return fail(f"partial artifacts remain after success: {partials}")
        original_bytes = backup.read_bytes()
        try:
            module.execute_backup(
                temp_root,
                now=datetime(2026, 7, 14, 3, 0, 0, tzinfo=timezone.utc),
                preflight_payload=ready_preflight(),
                source_state=source_state(),
                run_process=fake_runner,
            )
        except module.BackupError:
            pass
        else:
            return fail("existing timestamp artifacts must never be overwritten")
        if backup.read_bytes() != original_bytes:
            return fail("collision guard changed an existing backup")

    with tempfile.TemporaryDirectory() as temporary:
        temp_root = Path(temporary)
        blocked = ready_preflight()
        blocked["readyForUserApproval"] = False
        blocked["blockingReasons"] = ["schema gate not passed"]
        try:
            module.execute_backup(
                temp_root,
                preflight_payload=blocked,
                source_state=source_state(),
                run_process=fake_runner,
            )
        except module.BackupError:
            pass
        else:
            return fail("blocked preflight must prevent backup creation")
        if (temp_root / "local-backups").exists():
            return fail("blocked preflight must not create the backup directory")

    with tempfile.TemporaryDirectory() as temporary:
        temp_root = Path(temporary)
        try:
            module.execute_backup(
                temp_root,
                now=datetime(2026, 7, 14, 3, 0, 1, tzinfo=timezone.utc),
                preflight_payload=ready_preflight(),
                source_state=source_state(),
                run_process=failing_toc_runner,
            )
        except module.BackupError:
            pass
        else:
            return fail("invalid archive must fail verification")
        artifacts = list((temp_root / "local-backups/postgres").glob("*"))
        if artifacts:
            return fail(f"failed validation must not publish artifacts: {artifacts}")

    print("OK: PostgreSQL backup creation smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

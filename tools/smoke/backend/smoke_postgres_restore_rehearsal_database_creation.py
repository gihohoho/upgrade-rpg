#!/usr/bin/env python3
"""Smoke checks for the v292 empty restore-rehearsal DB creation boundary."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/create_postgres_restore_rehearsal_database.py"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_tool() -> Any:
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location(
        "create_postgres_restore_rehearsal_database", TOOL
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load rehearsal database creation tool")
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
            "dockerContainer": {"name": "upgrade_rpg_postgres", "running": True},
        },
    }


def source_state() -> dict[str, Any]:
    tables = [f"table_{index:02d}" for index in range(22)]
    return {
        "connected": True,
        "database": "rpg_game",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "modelTableCount": 22,
        "publicTableCount": 22,
        "modelTables": tables,
        "publicTables": tables,
        "missingModelTables": [],
        "extraPublicTables": [],
        "tableCountsCollected": True,
        "tableCounts": {tables[0]: 748},
        "nonEmptyTables": [tables[0]],
        "totalRows": 748,
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "existing-schema-without-alembic-baseline",
    }


def create_verified_backup(root: Path, *, corrupt: bool = False) -> dict[str, Any]:
    backup_dir = root / "local-backups/postgres"
    backup_dir.mkdir(parents=True)
    filename = "rpg_game_20260714_130403_KST_v290.custom.dump"
    backup = backup_dir / filename
    backup.write_bytes(b"PGDMP-verified-backup")
    checksum = hashlib.sha256(backup.read_bytes()).hexdigest()
    checksum_path = backup_dir / f"{filename}.sha256"
    checksum_path.write_text(f"{checksum}  {filename}\n", encoding="utf-8")
    manifest = backup_dir / f"{filename}.manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "backupCreated": True,
                "backupValidated": True,
                "sourceDatabase": "rpg_game",
                "sourceUser": "rpg_user",
                "backupRelativePath": backup.relative_to(root).as_posix(),
                "checksumRelativePath": checksum_path.relative_to(root).as_posix(),
                "backupSizeBytes": backup.stat().st_size,
                "sha256": "0" * 64 if corrupt else checksum,
                "sourceSnapshot": {"publicTableCount": 22, "totalRows": 748},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "manifestRelativePath": manifest.relative_to(root).as_posix(),
        "backupRelativePath": backup.relative_to(root).as_posix(),
        "backupSizeBytes": backup.stat().st_size,
        "sha256": checksum,
        "sourcePublicTableCount": 22,
        "sourceTotalRows": 748,
    }


class FakeRunner:
    def __init__(self, *, target_exists: bool = False) -> None:
        self.target_exists = target_exists
        self.createdb_calls = 0
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        self.commands.append(command)
        joined = " ".join(command)
        if " psql " in f" {joined} " and "FROM pg_database" in joined:
            rows = [
                {
                    "database": "rpg_game",
                    "owner": "rpg_user",
                    "encoding": "UTF8",
                    "collate": "C.UTF-8",
                    "ctype": "C.UTF-8",
                    "locale_provider": "c",
                    "icu_locale": "",
                }
            ]
            if self.target_exists:
                rows.append(
                    {
                        "database": "rpg_game_restore_rehearsal_v290",
                        "owner": "rpg_user",
                        "encoding": "UTF8",
                        "collate": "C.UTF-8",
                        "ctype": "C.UTF-8",
                        "locale_provider": "c",
                        "icu_locale": "",
                    }
                )
            return subprocess.CompletedProcess(command, 0, stdout=json.dumps(rows).encode(), stderr=None)
        if " createdb " in f" {joined} ":
            self.createdb_calls += 1
            self.target_exists = True
            return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=None)
        if " psql " in f" {joined} " and "json_build_object" in joined:
            payload = {
                "database": "rpg_game_restore_rehearsal_v290",
                "user": "rpg_user",
                "publicTableCount": 0,
                "alembicVersionTableExists": False,
            }
            return subprocess.CompletedProcess(command, 0, stdout=json.dumps(payload).encode(), stderr=None)
        raise AssertionError(f"unexpected command: {command}")


def main() -> int:
    if not TOOL.exists():
        return fail("missing tools/create_postgres_restore_rehearsal_database.py")

    source = TOOL.read_text(encoding="utf-8")
    for marker in (
        "--execute",
        "RESTORE_REHEARSAL_DATABASE",
        "createdb",
        "--template=template0",
        "databaseAlreadyExisted",
        "restoreAttempted",
        "databaseDropAttempted",
        "sourceSchemaDataMutationAttempted",
        "alembicMutationAttempted",
        "SHA-256",
    ):
        if marker not in source:
            return fail(f"tool missing safety marker: {marker}")
    module = load_tool()
    guard = subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if guard.returncode != 2 or "--execute" not in guard.stdout:
        return fail("tool must refuse execution without --execute")

    metadata = {
        "database": "rpg_game",
        "owner": "rpg_user",
        "encoding": "UTF8",
        "collate": "C.UTF-8",
        "ctype": "C.UTF-8",
        "locale_provider": "c",
        "icu_locale": "",
    }
    create_command = module.build_create_command(metadata)
    expected_prefix = [
        "docker",
        "exec",
        "upgrade_rpg_postgres",
        "createdb",
        "--username=rpg_user",
        "--no-password",
        "--maintenance-db=postgres",
        "--owner=rpg_user",
        "--template=template0",
    ]
    if create_command[: len(expected_prefix)] != expected_prefix:
        return fail(f"unexpected createdb boundary: {create_command}")
    if create_command[-1] != "rpg_game_restore_rehearsal_v290":
        return fail("createdb target is not pinned")
    if any(item in create_command for item in ("rpg_game", "dropdb", "pg_restore")):
        return fail("createdb command contains an unsafe target or operation")
    for command in (module.build_catalog_command(), module.build_target_state_command(), create_command):
        if any(token in command for token in ("pg_restore", "dropdb", "alembic")):
            return fail(f"v292 command boundary contains forbidden operation: {command}")

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        backup = create_verified_backup(root)
        runner = FakeRunner()
        result = module.execute_creation(
            root,
            preflight_payload=ready_preflight(),
            source_state_before=source_state(),
            source_state_after=source_state(),
            backup_evidence=backup,
            run_process=runner,
        )
        if runner.createdb_calls != 1:
            return fail(f"createdb must run exactly once, actual={runner.createdb_calls}")
        if result.get("result") != "restore-rehearsal-database-created-empty-and-verified":
            return fail("unexpected success classification")
        if result.get("databaseCreated") is not True:
            return fail("success must declare databaseCreated=true")
        if result.get("restoreAttempted") is not False:
            return fail("v292 must not restore")
        if result.get("databaseDropAttempted") is not False:
            return fail("v292 must not drop a database")
        if result.get("sourceSchemaDataMutationAttempted") is not False:
            return fail("v292 must not mutate source schema/data")
        target = result.get("targetState") or {}
        if target.get("publicTableCount") != 0 or target.get("alembicVersionTableExists") is not False:
            return fail("target must be empty and have no alembic_version")
        if result.get("sourceBefore") != result.get("sourceAfter"):
            return fail("source baseline must remain identical")

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        backup = create_verified_backup(root)
        runner = FakeRunner(target_exists=True)
        try:
            module.execute_creation(
                root,
                preflight_payload=ready_preflight(),
                source_state_before=source_state(),
                source_state_after=source_state(),
                backup_evidence=backup,
                run_process=runner,
            )
        except module.RehearsalDatabaseError as exc:
            if "already exists" not in str(exc):
                return fail(f"existing-target guard returned unclear error: {exc}")
        else:
            return fail("existing target must block creation")
        if runner.createdb_calls != 0:
            return fail("existing target guard must prevent createdb")

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        create_verified_backup(root)
        original_approved_hash = module.APPROVED_BACKUP_SHA256
        module.APPROVED_BACKUP_SHA256 = hashlib.sha256(b"PGDMP-verified-backup").hexdigest()
        try:
            evidence = module.find_approved_verified_backup(root)
            if evidence.get("backupRelativePath", "").endswith(module.APPROVED_BACKUP_FILENAME) is not True:
                return fail("approved backup evidence did not pin the exact filename")
        finally:
            module.APPROVED_BACKUP_SHA256 = original_approved_hash

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        create_verified_backup(root, corrupt=True)
        original_approved_hash = module.APPROVED_BACKUP_SHA256
        module.APPROVED_BACKUP_SHA256 = hashlib.sha256(b"PGDMP-verified-backup").hexdigest()
        try:
            module.find_approved_verified_backup(root)
        except module.RehearsalDatabaseError as exc:
            if "SHA-256" not in str(exc):
                return fail(f"checksum guard returned unclear error: {exc}")
        else:
            return fail("corrupt backup manifest must block")
        finally:
            module.APPROVED_BACKUP_SHA256 = original_approved_hash

    blocked = ready_preflight()
    blocked["readyForUserApproval"] = False
    blocked["blockingReasons"] = ["schema gate not passed"]
    with tempfile.TemporaryDirectory() as temporary:
        runner = FakeRunner()
        try:
            module.execute_creation(
                Path(temporary),
                preflight_payload=blocked,
                source_state_before=source_state(),
                source_state_after=source_state(),
                backup_evidence={},
                run_process=runner,
            )
        except module.RehearsalDatabaseError:
            pass
        else:
            return fail("blocked preflight must prevent creation")
        if runner.commands:
            return fail("blocked preflight must run no PostgreSQL command")

    print("OK: PostgreSQL restore rehearsal database creation smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

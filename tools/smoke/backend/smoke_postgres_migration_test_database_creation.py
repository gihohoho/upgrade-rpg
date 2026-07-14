#!/usr/bin/env python3
"""Smoke checks for the v294 empty Alembic migration-test DB boundary."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/create_postgres_migration_test_database.py"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_tool() -> Any:
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location(
        "create_postgres_migration_test_database", TOOL
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load migration test database creation tool")
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


def counts() -> dict[str, int]:
    values = {f"table_{index:02d}": 0 for index in range(22)}
    values["table_00"] = 748
    return values


def source_state() -> dict[str, Any]:
    values = counts()
    tables = sorted(values)
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
        "tableCounts": values,
        "totalRows": 748,
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "existing-schema-without-alembic-baseline",
    }


def rehearsal_state() -> dict[str, Any]:
    values = counts()
    tables = sorted(values)
    return {
        "connected": True,
        "database": "rpg_game_restore_rehearsal_v290",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "modelTableCount": 22,
        "publicTableCount": 22,
        "publicTables": tables,
        "tableCountsCollected": True,
        "tableCounts": values,
        "totalRows": 748,
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "existing-schema-without-alembic-baseline",
        "schemaClassification": "structurally-equivalent",
        "differenceCount": 0,
    }


def empty_migration_state() -> dict[str, Any]:
    return {
        "connected": True,
        "database": "rpg_game_migration_empty_v290",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "modelTableCount": 22,
        "publicTableCount": 0,
        "publicTables": [],
        "tableCountsCollected": True,
        "tableCounts": {},
        "totalRows": 0,
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "empty-database",
        "schemaClassification": "review-required",
        "differenceCount": 22,
    }


def evidence() -> dict[str, Any]:
    values = counts()
    return {
        "backupRelativePath": "local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump",
        "sha256": "b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481",
        "restoreReportRelativePath": (
            "local-backups/postgres/"
            "rpg_game_20260714_130403_KST_v290.custom.dump.restore-rehearsal-v293.json"
        ),
        "expectedTables": tuple(sorted(values)),
        "expectedTableCounts": dict(sorted(values.items())),
        "expectedTotalRows": 748,
    }


def metadata(name: str) -> dict[str, Any]:
    return {
        "database": name,
        "owner": "rpg_user",
        "encoding": "UTF8",
        "collate": "C.UTF-8",
        "ctype": "C.UTF-8",
        "locale_provider": "c",
        "icu_locale": "",
    }


def catalog(*, target_exists: bool) -> dict[str, dict[str, Any]]:
    result = {
        "rpg_game": metadata("rpg_game"),
        "rpg_game_restore_rehearsal_v290": metadata("rpg_game_restore_rehearsal_v290"),
    }
    if target_exists:
        result["rpg_game_migration_empty_v290"] = metadata("rpg_game_migration_empty_v290")
    return result


class FakeRunner:
    def __init__(self) -> None:
        self.createdb_calls = 0
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        self.commands.append(command)
        if "createdb" not in command:
            raise AssertionError(f"unexpected command: {command}")
        self.createdb_calls += 1
        return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=None)


def main() -> int:
    if not TOOL.exists():
        return fail("missing tools/create_postgres_migration_test_database.py")
    source = TOOL.read_text(encoding="utf-8")
    for marker in (
        "--execute",
        "MIGRATION_TEST_DATABASE",
        "rpg_game_migration_empty_v290",
        "createdb",
        "--template=template0",
        "migration-test-database-created-empty-and-verified",
        "restoreAttempted",
        "databaseDropAttempted",
        "alembicRevisionAttempted",
        "alembicUpgradeAttempted",
        "alembicDowngradeAttempted",
        "alembicStampAttempted",
        "restore-rehearsal-completed-and-verified",
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

    create_command = module.build_create_command(metadata("rpg_game"))
    required = {
        "docker",
        "exec",
        "upgrade_rpg_postgres",
        "createdb",
        "--username=rpg_user",
        "--no-password",
        "--maintenance-db=postgres",
        "--owner=rpg_user",
        "--template=template0",
        "rpg_game_migration_empty_v290",
    }
    if not required.issubset(set(create_command)):
        return fail(f"createdb command missing required boundary: {create_command}")
    forbidden = {
        "rpg_game",
        "rpg_game_restore_rehearsal_v290",
        "dropdb",
        "pg_restore",
        "alembic",
    }
    if any(token in create_command for token in forbidden):
        return fail(f"createdb command contains forbidden target/operation: {create_command}")
    for command in (module.build_catalog_command(), create_command):
        if any(token in command for token in ("dropdb", "pg_restore", "alembic")):
            return fail(f"v294 command boundary contains forbidden operation: {command}")

    runner = FakeRunner()
    result = module.execute_creation(
        ROOT,
        preflight_payload=ready_preflight(),
        restore_evidence=evidence(),
        source_state_before=source_state(),
        source_state_after=source_state(),
        rehearsal_state_before=rehearsal_state(),
        rehearsal_state_after=rehearsal_state(),
        migration_state_after=empty_migration_state(),
        catalog_before=catalog(target_exists=False),
        catalog_after=catalog(target_exists=True),
        run_process=runner,
    )
    if runner.createdb_calls != 1:
        return fail(f"createdb must run exactly once, actual={runner.createdb_calls}")
    if result.get("result") != "migration-test-database-created-empty-and-verified":
        return fail("unexpected success classification")
    if result.get("databaseCreated") is not True:
        return fail("success must declare databaseCreated=true")
    for key in (
        "restoreAttempted",
        "databaseDropAttempted",
        "tableOrRowWriteAttempted",
        "sourceSchemaDataMutationAttempted",
        "rehearsalSchemaDataMutationAttempted",
        "dockerResourceChanged",
        "environmentFileChanged",
        "alembicRevisionAttempted",
        "alembicUpgradeAttempted",
        "alembicDowngradeAttempted",
        "alembicStampAttempted",
    ):
        if result.get(key) is not False:
            return fail(f"success changed forbidden boundary: {key}={result.get(key)}")
    target = result.get("migrationAfter") or {}
    if target.get("publicTableCount") != 0 or target.get("totalRows") != 0:
        return fail("migration target must remain empty")
    if target.get("alembicVersionTableExists") is not False:
        return fail("migration target must not have alembic_version")
    if result.get("sourceBefore") != result.get("sourceAfter"):
        return fail("source baseline must remain identical")
    if result.get("rehearsalBefore") != result.get("rehearsalAfter"):
        return fail("rehearsal baseline must remain identical")

    runner = FakeRunner()
    try:
        module.execute_creation(
            ROOT,
            preflight_payload=ready_preflight(),
            restore_evidence=evidence(),
            source_state_before=source_state(),
            rehearsal_state_before=rehearsal_state(),
            catalog_before=catalog(target_exists=True),
            run_process=runner,
        )
    except module.MigrationTestDatabaseError as exc:
        if "already exists" not in str(exc):
            return fail(f"existing-target guard returned unclear error: {exc}")
    else:
        return fail("existing migration target must block creation")
    if runner.createdb_calls != 0:
        return fail("existing-target guard must prevent createdb")

    drifted = rehearsal_state()
    drifted["differenceCount"] = 1
    drifted["schemaClassification"] = "review-required"
    runner = FakeRunner()
    try:
        module.execute_creation(
            ROOT,
            preflight_payload=ready_preflight(),
            restore_evidence=evidence(),
            source_state_before=source_state(),
            rehearsal_state_before=drifted,
            catalog_before=catalog(target_exists=False),
            run_process=runner,
        )
    except module.MigrationTestDatabaseError as exc:
        if "structurally equivalent" not in str(exc):
            return fail(f"rehearsal schema guard returned unclear error: {exc}")
    else:
        return fail("rehearsal schema drift must block migration DB creation")
    if runner.createdb_calls != 0:
        return fail("rehearsal drift guard must run no createdb")

    blocked = ready_preflight()
    blocked["readyForUserApproval"] = False
    blocked["blockingReasons"] = ["schema gate not passed"]
    runner = FakeRunner()
    try:
        module.execute_creation(
            ROOT,
            preflight_payload=blocked,
            restore_evidence=evidence(),
            source_state_before=source_state(),
            rehearsal_state_before=rehearsal_state(),
            catalog_before=catalog(target_exists=False),
            run_process=runner,
        )
    except module.MigrationTestDatabaseError:
        pass
    else:
        return fail("blocked preflight must prevent creation")
    if runner.commands:
        return fail("blocked preflight must run no PostgreSQL command")

    print("OK: PostgreSQL migration test database creation smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

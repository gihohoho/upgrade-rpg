#!/usr/bin/env python3
"""Smoke checks for the v293 isolated PostgreSQL restore rehearsal boundary."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/restore_postgres_rehearsal_database.py"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_tool() -> Any:
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("restore_postgres_rehearsal_database", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load restore rehearsal tool")
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


def expected_counts() -> dict[str, int]:
    counts = {f"table_{index:02d}": index for index in range(21)}
    counts["table_21"] = 748 - sum(counts.values())
    return counts


def source_state(counts: dict[str, int] | None = None) -> dict[str, Any]:
    values = counts or expected_counts()
    tables = sorted(values)
    return {
        "connected": True,
        "database": "rpg_game",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "publicTableCount": 22,
        "publicTables": tables,
        "missingModelTables": [],
        "extraPublicTables": [],
        "tableCountsCollected": True,
        "tableCounts": dict(values),
        "totalRows": sum(values.values()),
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "existing-schema-without-alembic-baseline",
    }


def empty_target_state() -> dict[str, Any]:
    return {
        "connected": True,
        "database": "rpg_game_restore_rehearsal_v290",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "publicTableCount": 0,
        "publicTables": [],
        "tableCountsCollected": True,
        "tableCounts": {},
        "totalRows": 0,
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "empty-database",
    }


def restored_target_state(counts: dict[str, int] | None = None) -> dict[str, Any]:
    values = counts or expected_counts()
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
        "tableCounts": dict(values),
        "totalRows": sum(values.values()),
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "comparedTables": tables,
        "differenceCount": 0,
        "differences": [],
        "schemaClassification": "structurally-equivalent",
        "classification": "existing-schema-without-alembic-baseline",
    }


def catalog() -> dict[str, dict[str, Any]]:
    metadata = {
        "owner": "rpg_user",
        "encoding": "UTF8",
        "collate": "C.UTF-8",
        "ctype": "C.UTF-8",
        "locale_provider": "c",
        "icu_locale": "",
    }
    return {
        "rpg_game": {"database": "rpg_game", **metadata},
        "rpg_game_restore_rehearsal_v290": {
            "database": "rpg_game_restore_rehearsal_v290",
            **metadata,
        },
    }


def toc_text(tables: tuple[str, ...]) -> str:
    lines = [
        ";",
        ";     TOC Entries: 44",
        ";     Compression: -1",
        ";     Dump Version: 1.15-0",
        ";     Format: CUSTOM",
        ";     Dumped from database version: 16.14",
        ";     Dumped by pg_dump version: 16.14",
        ";",
    ]
    object_id = 100
    for table in tables:
        lines.append(f"{object_id}; 1259 {object_id} TABLE public {table} rpg_user")
        object_id += 1
        lines.append(f"{object_id}; 0 {object_id - 1} TABLE DATA public {table} rpg_user")
        object_id += 1
    return "\n".join(lines)


def evidence(root: Path) -> dict[str, Any]:
    counts = expected_counts()
    backup = root / "local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump"
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_bytes(b"PGDMP-v293-smoke")
    return {
        "manifestRelativePath": "local-backups/postgres/test.manifest.json",
        "backupRelativePath": backup.relative_to(root).as_posix(),
        "backupSizeBytes": backup.stat().st_size,
        "sha256": "b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481",
        "backupPath": backup,
        "reportPath": backup.with_name(f"{backup.name}.restore-rehearsal-v293.json"),
        "expectedTables": tuple(sorted(counts)),
        "expectedTableCounts": dict(sorted(counts.items())),
        "expectedTotalRows": 748,
    }


class FakeRunner:
    def __init__(self, tables: tuple[str, ...], *, restore_exit: int = 0) -> None:
        self.tables = tables
        self.restore_exit = restore_exit
        self.restore_calls = 0
        self.list_calls = 0
        self.commands: list[list[str]] = []

    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        self.commands.append(command)
        if "pg_restore" not in command:
            raise AssertionError(f"unexpected command: {command}")
        if "--list" in command:
            self.list_calls += 1
            return subprocess.CompletedProcess(
                command, 0, stdout=toc_text(self.tables).encode(), stderr=None
            )
        self.restore_calls += 1
        return subprocess.CompletedProcess(
            command,
            self.restore_exit,
            stdout=b"" if self.restore_exit == 0 else b"simulated restore error",
            stderr=None,
        )


def main() -> int:
    if not TOOL.exists():
        return fail("missing tools/restore_postgres_rehearsal_database.py")
    source = TOOL.read_text(encoding="utf-8")
    for marker in (
        "--execute",
        "--single-transaction",
        "--exit-on-error",
        "--no-owner",
        "--no-privileges",
        "restore-rehearsal-completed-and-verified",
        "differenceCount",
        "expectedTableCounts",
        "databaseDropAttempted",
        "alembicMutationAttempted",
    ):
        if marker not in source:
            return fail(f"restore tool missing marker: {marker}")

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
        return fail("restore tool must refuse execution without --execute")

    command = module.build_restore_command()
    required = {
        "--dbname=rpg_game_restore_rehearsal_v290",
        "--username=rpg_user",
        "--single-transaction",
        "--exit-on-error",
        "--no-owner",
        "--no-privileges",
    }
    if not required.issubset(set(command)):
        return fail(f"restore command missing required boundary: {command}")
    forbidden = {"--create", "--clean", "dropdb", "createdb", "rpg_game"}
    if any(token in command for token in forbidden):
        return fail(f"restore command contains forbidden operation/source target: {command}")

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        approved = evidence(root)
        runner = FakeRunner(approved["expectedTables"])
        result = module.execute_restore(
            root,
            preflight_payload=ready_preflight(),
            evidence=approved,
            source_state_before=source_state(),
            source_state_after=source_state(),
            target_state_before=empty_target_state(),
            target_state_after=restored_target_state(),
            catalog_before=catalog(),
            catalog_after=catalog(),
            run_process=runner,
        )
        if runner.list_calls != 1 or runner.restore_calls != 1:
            return fail(
                f"expected one TOC check and one restore, actual={runner.list_calls}/{runner.restore_calls}"
            )
        if result.get("result") != "restore-rehearsal-completed-and-verified":
            return fail("unexpected restore success classification")
        if result.get("restoreCompleted") is not True:
            return fail("success must declare restoreCompleted=true")
        if result.get("sourceSchemaDataMutationAttempted") is not False:
            return fail("source mutation boundary changed")
        if result.get("databaseCreateAttempted") is not False:
            return fail("v293 must not create a database")
        if result.get("databaseDropAttempted") is not False:
            return fail("v293 must not drop a database")
        if result.get("alembicMutationAttempted") is not False:
            return fail("v293 must not run Alembic mutation")
        if not approved["reportPath"].is_file():
            return fail("verified restore report was not written")
        report = json.loads(approved["reportPath"].read_text(encoding="utf-8"))
        if report.get("targetAfter", {}).get("totalRows") != 748:
            return fail("restore report target total row count mismatch")

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        approved = evidence(root)
        runner = FakeRunner(approved["expectedTables"])
        non_empty = empty_target_state()
        non_empty.update(
            {
                "publicTableCount": 1,
                "publicTables": ["unexpected"],
                "tableCounts": {"unexpected": 1},
                "totalRows": 1,
            }
        )
        try:
            module.execute_restore(
                root,
                preflight_payload=ready_preflight(),
                evidence=approved,
                source_state_before=source_state(),
                target_state_before=non_empty,
                catalog_before=catalog(),
                run_process=runner,
            )
        except module.RestoreRehearsalError as exc:
            if "not empty" not in str(exc):
                return fail(f"non-empty target guard returned unclear error: {exc}")
        else:
            return fail("non-empty target must block restore")
        if runner.commands:
            return fail("non-empty target guard must run no pg_restore command")

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        approved = evidence(root)
        changed = source_state()
        changed["tableCounts"] = dict(changed["tableCounts"])
        changed["tableCounts"]["table_00"] += 1
        changed["totalRows"] += 1
        runner = FakeRunner(approved["expectedTables"])
        try:
            module.execute_restore(
                root,
                preflight_payload=ready_preflight(),
                evidence=approved,
                source_state_before=changed,
                target_state_before=empty_target_state(),
                catalog_before=catalog(),
                run_process=runner,
            )
        except module.RestoreRehearsalError as exc:
            if "row counts" not in str(exc) and "baseline" not in str(exc):
                return fail(f"source drift guard returned unclear error: {exc}")
        else:
            return fail("source row drift must block restore")
        if runner.commands:
            return fail("source drift guard must run no pg_restore command")

    # Simulate a pg_restore failure and prove the tool reports verified rollback.
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        approved = evidence(root)
        runner = FakeRunner(approved["expectedTables"], restore_exit=1)
        original_inspector = module.inspect_named_database
        module.inspect_named_database = lambda *_args, **_kwargs: empty_target_state()
        try:
            module.execute_restore(
                root,
                preflight_payload=ready_preflight(),
                evidence=approved,
                source_state_before=source_state(),
                target_state_before=empty_target_state(),
                catalog_before=catalog(),
                run_process=runner,
            )
        except module.RestoreRehearsalError as exc:
            if "rollback verified target remains empty" not in str(exc):
                return fail(f"failed restore rollback message is unclear: {exc}")
        else:
            return fail("failed restore must raise")
        finally:
            module.inspect_named_database = original_inspector
        if runner.restore_calls != 1:
            return fail("failed restore path must attempt pg_restore exactly once")

    print("OK: PostgreSQL restore rehearsal smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

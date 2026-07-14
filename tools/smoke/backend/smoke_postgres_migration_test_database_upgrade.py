#!/usr/bin/env python3
"""Smoke checks for the guarded v298 isolated migration DB upgrade boundary."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/upgrade_postgres_migration_test_database.py"


def load_tool() -> Any:
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location("upgrade_postgres_migration_test_database", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load v298 migration upgrade tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def table_counts(total: int = 0) -> dict[str, int]:
    values = {f"table_{index:02d}": 0 for index in range(22)}
    if total:
        values["table_00"] = total
    return values


def evidence() -> dict[str, Any]:
    values = table_counts(748)
    return {
        "expectedTables": tuple(sorted(values)),
        "expectedTableCounts": dict(sorted(values.items())),
        "expectedTotalRows": 748,
    }


def source_state() -> dict[str, Any]:
    values = table_counts(748)
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
        "tableCounts": values,
        "totalRows": 748,
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "existing-schema-without-alembic-baseline",
    }


def rehearsal_state() -> dict[str, Any]:
    state = source_state()
    state.update(
        {
            "database": "rpg_game_restore_rehearsal_v290",
            "schemaClassification": "structurally-equivalent",
            "differenceCount": 0,
        }
    )
    return state


def migration_before() -> dict[str, Any]:
    return {
        "connected": True,
        "database": "rpg_game_migration_empty_v290",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "modelTableCount": 22,
        "publicTableCount": 1,
        "publicTables": ["alembic_version"],
        "tableCountsCollected": True,
        "tableCounts": {"alembic_version": 0},
        "totalRows": 0,
        "alembicVersionTableExists": True,
        "alembicCurrentRevisions": [],
        "comparedTables": [],
        "differenceCount": 22,
        "differences": [],
        "schemaClassification": "review-required",
        "classification": "alembic-managed",
    }


def migration_after(module: Any) -> dict[str, Any]:
    tables = sorted([*(f"table_{index:02d}" for index in range(22)), "alembic_version"])
    counts = {name: 0 for name in tables}
    counts["alembic_version"] = 1
    return {
        "connected": True,
        "database": "rpg_game_migration_empty_v290",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "modelTableCount": 22,
        "publicTableCount": 23,
        "publicTables": tables,
        "tableCountsCollected": True,
        "tableCounts": dict(sorted(counts.items())),
        "totalRows": 1,
        "alembicVersionTableExists": True,
        "alembicCurrentRevisions": [module.REVISION_ID],
        "comparedTables": sorted(f"table_{index:02d}" for index in range(22)),
        "differenceCount": 0,
        "differences": [],
        "schemaClassification": "structurally-equivalent",
        "classification": "alembic-managed",
    }


class Runner:
    def __init__(self) -> None:
        self.calls = 0
        self.commands: list[list[str]] = []
        self.envs: list[dict[str, str]] = []

    def __call__(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        self.calls += 1
        self.commands.append(list(command))
        self.envs.append(dict(kwargs.get("env") or {}))
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=b"INFO [alembic.runtime.migration] Running upgrade -> v295_initial_schema\n",
            stderr=None,
        )


def main() -> None:
    module = load_tool()

    command = module.build_upgrade_command()
    joined = " ".join(command)
    if " upgrade head" not in joined:
        raise AssertionError(f"upgrade command mismatch: {command}")
    for forbidden in ("downgrade", "stamp", "revision", "createdb", "dropdb", "pg_restore"):
        if forbidden in command:
            raise AssertionError(f"forbidden command token present: {forbidden}")

    # The committed exact revision/manual review must remain valid.
    revision, manual, automated = module.reviewed_revision(ROOT)
    if revision.name != module.REVISION_FILENAME:
        raise AssertionError("reviewed revision filename mismatch")
    if manual.get("reviewResult") != "passed":
        raise AssertionError("manual review is not passed")
    if automated.get("tableCount") != 22 or automated.get("columnCount") != 209:
        raise AssertionError("automated review baseline changed")

    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory)
        (project / "backend").mkdir(parents=True)
        (project / "local-review-artifacts/alembic").mkdir(parents=True)
        fake_revision = project / "backend" / module.REVISION_FILENAME
        fake_revision.write_text("reviewed", encoding="utf-8")

        module.reviewed_revision = lambda root: (
            fake_revision,
            {
                "reviewResult": "passed",
                "manualConclusion": "approved-for-isolated-empty-migration-database-upgrade-only",
            },
            {
                "result": "initial-alembic-revision-automated-review-passed",
                "tableCount": 22,
                "columnCount": 209,
            },
        )
        module.target_database_url = lambda root: (
            "postgresql+asyncpg://rpg_user:secret@127.0.0.1:55432/"
            "rpg_game_migration_empty_v290"
        )

        runner = Runner()
        result = module.execute_upgrade(
            project,
            evidence=evidence(),
            source_before_raw=source_state(),
            source_after_raw=source_state(),
            rehearsal_before_raw=rehearsal_state(),
            rehearsal_after_raw=rehearsal_state(),
            migration_before_raw=migration_before(),
            migration_after_raw=migration_after(module),
            run_process=runner,
        )
        if result.get("result") != "migration-test-database-upgraded-and-verified":
            raise AssertionError("success classification mismatch")
        if runner.calls != 1:
            raise AssertionError("alembic upgrade must execute exactly once")
        if runner.envs[0].get("DATABASE_URL", "").split("/")[-1] != "rpg_game_migration_empty_v290":
            raise AssertionError("upgrade DATABASE_URL is not pinned to migration DB")
        report = project / module.UPGRADE_REPORT_RELATIVE_PATH
        if not report.is_file():
            raise AssertionError("upgrade verification report was not written")
        payload = json.loads(report.read_text(encoding="utf-8"))
        if payload.get("downgradeExecuted") is not False or payload.get("stampExecuted") is not False:
            raise AssertionError("report incorrectly claims forbidden Alembic actions")

        unsafe = migration_before()
        unsafe["alembicCurrentRevisions"] = [module.REVISION_ID]
        try:
            module.execute_upgrade(
                project,
                evidence=evidence(),
                source_before_raw=source_state(),
                source_after_raw=source_state(),
                rehearsal_before_raw=rehearsal_state(),
                rehearsal_after_raw=rehearsal_state(),
                migration_before_raw=unsafe,
                migration_after_raw=migration_after(module),
                run_process=Runner(),
            )
        except module.MigrationUpgradeError:
            pass
        else:
            raise AssertionError("existing revision row did not block upgrade")

        bad_after = migration_after(module)
        bad_after["differenceCount"] = 1
        bad_runner = Runner()
        try:
            module.execute_upgrade(
                project,
                evidence=evidence(),
                source_before_raw=source_state(),
                source_after_raw=source_state(),
                rehearsal_before_raw=rehearsal_state(),
                rehearsal_after_raw=rehearsal_state(),
                migration_before_raw=migration_before(),
                migration_after_raw=bad_after,
                run_process=bad_runner,
            )
        except module.MigrationUpgradeError:
            pass
        else:
            raise AssertionError("post-upgrade schema difference did not fail verification")
        if bad_runner.calls != 1:
            raise AssertionError("postcondition test should run upgrade once and never retry")

    source_text = TOOL.read_text(encoding="utf-8")
    for forbidden_fragment in (
        '"downgrade",',
        '"stamp",',
        '"createdb",',
        '"dropdb",',
        '"pg_restore",',
        "docker compose down",
        "setup_dev_db.py --reset",
    ):
        if forbidden_fragment in source_text:
            raise AssertionError(f"forbidden mutation command fragment found: {forbidden_fragment}")

    print("PostgreSQL migration test database upgrade smoke passed")
    print("- exact reviewed revision/manual review pinned")
    print("- command boundary: alembic upgrade head only")
    print("- target boundary: rpg_game_migration_empty_v290")
    print("- postcondition: 22 model tables + alembic_version / differences=0")
    print("- no automatic retry, downgrade, stamp, create/drop/restore")


if __name__ == "__main__":
    main()

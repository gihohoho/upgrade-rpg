#!/usr/bin/env python3
"""Smoke checks for the guarded v300 isolated migration round-trip re-upgrade."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/reupgrade_postgres_migration_test_database.py"


def load_tool() -> Any:
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location(
        "reupgrade_postgres_migration_test_database", TOOL
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load v300 round-trip re-upgrade tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def table_counts(total: int = 0) -> dict[str, int]:
    values = {f"table_{index:02d}": 0 for index in range(22)}
    if total:
        values["table_00"] = total
    return values


def restore_evidence() -> dict[str, Any]:
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


def migration_base() -> dict[str, Any]:
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


def migration_head(module: Any) -> dict[str, Any]:
    model_tables = sorted(f"table_{index:02d}" for index in range(22))
    tables = sorted([*model_tables, "alembic_version"])
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
        "comparedTables": model_tables,
        "differenceCount": 0,
        "differences": [],
        "schemaClassification": "structurally-equivalent",
        "classification": "alembic-managed",
    }


def first_upgrade_evidence(module: Any) -> dict[str, Any]:
    return {
        "result": "migration-test-database-upgraded-and-verified",
        "targetDatabase": "rpg_game_migration_empty_v290",
        "revisionId": module.REVISION_ID,
        "revisionSha256": module.REVISION_SHA256,
        "upgradeExecuted": True,
        "downgradeExecuted": False,
        "stampExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
        "migrationAfter": migration_head(module),
    }


def downgrade_evidence(module: Any) -> dict[str, Any]:
    return {
        "result": "migration-test-database-downgraded-to-base-and-verified",
        "targetDatabase": "rpg_game_migration_empty_v290",
        "revisionId": module.REVISION_ID,
        "revisionSha256": module.REVISION_SHA256,
        "upgradeExecuted": False,
        "downgradeExecuted": True,
        "stampExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
        "migrationBefore": migration_head(module),
        "migrationAfter": migration_base(),
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
    if command[-2:] != ["upgrade", "head"]:
        raise AssertionError(f"round-trip upgrade command mismatch: {command}")
    for forbidden in ("downgrade", "stamp", "revision", "createdb", "dropdb", "pg_restore"):
        if forbidden in command:
            raise AssertionError(f"forbidden command token present: {forbidden}")

    revision, manual, automated = module.reviewed_revision(ROOT)
    if revision.name != "v295_initial_schema_initial_postgresql_schema.py":
        raise AssertionError("reviewed revision filename mismatch")
    if manual.get("reviewResult") != "passed":
        raise AssertionError("manual review is not passed")
    if automated.get("tableCount") != 22 or automated.get("columnCount") != 209:
        raise AssertionError("automated review baseline changed")

    with tempfile.TemporaryDirectory() as directory:
        project = Path(directory)
        (project / "backend").mkdir(parents=True)
        fake_revision = project / "backend/v295_initial_schema_initial_postgresql_schema.py"
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
        # run_upgrade_command imports its target URL helper from the v298 module.
        import upgrade_postgres_migration_test_database as upgrade_module

        upgrade_module.target_database_url = lambda root: (
            "postgresql+asyncpg://rpg_user:secret@127.0.0.1:55432/"
            "rpg_game_migration_empty_v290"
        )

        runner = Runner()
        result = module.execute_roundtrip_upgrade(
            project,
            restore_evidence=restore_evidence(),
            first_upgrade_evidence=first_upgrade_evidence(module),
            downgrade_evidence=downgrade_evidence(module),
            source_before_raw=source_state(),
            source_after_raw=source_state(),
            rehearsal_before_raw=rehearsal_state(),
            rehearsal_after_raw=rehearsal_state(),
            migration_before_raw=migration_base(),
            migration_after_raw=migration_head(module),
            run_process=runner,
        )
        if result.get("result") != "migration-test-database-roundtrip-upgraded-and-verified":
            raise AssertionError("round-trip success classification mismatch")
        if result.get("roundTripEquivalent") is not True:
            raise AssertionError("round-trip equivalence was not recorded")
        if runner.calls != 1:
            raise AssertionError("round-trip upgrade must execute exactly once")
        if runner.commands[0][-2:] != ["upgrade", "head"]:
            raise AssertionError("unexpected Alembic command")
        if runner.envs[0].get("DATABASE_URL", "").split("/")[-1] != "rpg_game_migration_empty_v290":
            raise AssertionError("round-trip DATABASE_URL is not pinned to migration DB")
        report = project / module.ROUNDTRIP_REPORT_RELATIVE_PATH
        if not report.is_file():
            raise AssertionError("round-trip verification report was not written")
        payload = json.loads(report.read_text(encoding="utf-8"))
        if payload.get("downgradeExecutedInThisStep") is not False:
            raise AssertionError("report incorrectly records downgrade in v300 step")
        if payload.get("stampExecuted") is not False:
            raise AssertionError("report incorrectly records stamp")
        if payload.get("firstUpgradeSignature") != payload.get("secondUpgradeSignature"):
            raise AssertionError("report does not preserve identical upgrade signatures")

        bad_before = migration_base()
        bad_before["publicTables"] = ["alembic_version", "users"]
        bad_before["publicTableCount"] = 2
        blocked_runner = Runner()
        try:
            module.execute_roundtrip_upgrade(
                project,
                restore_evidence=restore_evidence(),
                first_upgrade_evidence=first_upgrade_evidence(module),
                downgrade_evidence=downgrade_evidence(module),
                source_before_raw=source_state(),
                source_after_raw=source_state(),
                rehearsal_before_raw=rehearsal_state(),
                rehearsal_after_raw=rehearsal_state(),
                migration_before_raw=bad_before,
                migration_after_raw=migration_head(module),
                run_process=blocked_runner,
            )
        except module.MigrationRoundTripError:
            pass
        else:
            raise AssertionError("non-empty precondition did not block re-upgrade")
        if blocked_runner.calls != 0:
            raise AssertionError("precondition failure executed Alembic")

        bad_downgrade = downgrade_evidence(module)
        bad_downgrade["revisionSha256"] = "wrong"
        evidence_runner = Runner()
        try:
            module.execute_roundtrip_upgrade(
                project,
                restore_evidence=restore_evidence(),
                first_upgrade_evidence=first_upgrade_evidence(module),
                downgrade_evidence=bad_downgrade,
                source_before_raw=source_state(),
                source_after_raw=source_state(),
                rehearsal_before_raw=rehearsal_state(),
                rehearsal_after_raw=rehearsal_state(),
                migration_before_raw=migration_base(),
                migration_after_raw=migration_head(module),
                run_process=evidence_runner,
            )
        except module.MigrationRoundTripError:
            pass
        else:
            raise AssertionError("invalid downgrade evidence did not block re-upgrade")
        if evidence_runner.calls != 0:
            raise AssertionError("invalid evidence executed Alembic")

        different_after = migration_head(module)
        different_after["tableCounts"] = dict(different_after["tableCounts"])
        different_after["tableCounts"]["table_00"] = 1
        different_after["totalRows"] = 2
        bad_runner = Runner()
        try:
            module.execute_roundtrip_upgrade(
                project,
                restore_evidence=restore_evidence(),
                first_upgrade_evidence=first_upgrade_evidence(module),
                downgrade_evidence=downgrade_evidence(module),
                source_before_raw=source_state(),
                source_after_raw=source_state(),
                rehearsal_before_raw=rehearsal_state(),
                rehearsal_after_raw=rehearsal_state(),
                migration_before_raw=migration_base(),
                migration_after_raw=different_after,
                run_process=bad_runner,
            )
        except module.MigrationRoundTripError:
            pass
        else:
            raise AssertionError("different second upgrade result did not fail verification")
        if bad_runner.calls != 1:
            raise AssertionError("postcondition failure must not retry upgrade")

    print("PostgreSQL migration round-trip re-upgrade smoke passed")
    print("- exact v298 first-upgrade and v299 downgrade evidence pinned")
    print("- command boundary: alembic upgrade head only")
    print("- target boundary: rpg_game_migration_empty_v290")
    print("- round-trip result: first and second upgrade signatures identical")
    print("- no retry, downgrade in this step, stamp, create/drop/restore, or source mutation")


if __name__ == "__main__":
    main()

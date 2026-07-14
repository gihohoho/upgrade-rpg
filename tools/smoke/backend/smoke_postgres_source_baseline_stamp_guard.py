#!/usr/bin/env python3
"""Smoke checks for the v304 exact-source baseline stamp final guard."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/stamp_postgres_source_database.py"


def load_tool() -> Any:
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location(
        "stamp_postgres_source_database", TOOL
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load v304 source stamp guard")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def counts(total: int = 748) -> dict[str, int]:
    values = {f"table_{index:02d}": 0 for index in range(22)}
    values["table_00"] = total
    return values


def evidence(module: Any) -> dict[str, Any]:
    values = counts()
    return {
        "backupRelativePath": (
            "local-backups/postgres/"
            "rpg_game_20260714_130403_KST_v290.custom.dump"
        ),
        "sha256": module.APPROVED_BACKUP_SHA256,
        "expectedTables": tuple(sorted(values)),
        "expectedTableCounts": dict(sorted(values.items())),
        "expectedTotalRows": 748,
    }


def source_pre() -> dict[str, Any]:
    values = counts()
    return {
        "connected": True,
        "database": "rpg_game",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "publicTableCount": 22,
        "publicTables": sorted(values),
        "missingModelTables": [],
        "extraPublicTables": [],
        "tableCountsCollected": True,
        "tableCounts": dict(sorted(values.items())),
        "totalRows": 748,
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "existing-schema-without-alembic-baseline",
    }


def source_post(module: Any) -> dict[str, Any]:
    values = counts()
    values["alembic_version"] = 1
    return {
        "connected": True,
        "database": "rpg_game",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "publicTableCount": 23,
        "publicTables": sorted(values),
        "missingModelTables": [],
        "extraPublicTables": [],
        "tableCountsCollected": True,
        "tableCounts": dict(sorted(values.items())),
        "totalRows": 749,
        "alembicVersionTableExists": True,
        "alembicCurrentRevisions": [module.REVISION_ID],
        "classification": "alembic-managed",
    }


def rehearsal_post(module: Any) -> dict[str, Any]:
    state = source_post(module)
    state.update(
        {
            "database": "rpg_game_restore_rehearsal_v290",
            "schemaClassification": "structurally-equivalent",
            "differenceCount": 0,
        }
    )
    return state


def migration_post(module: Any) -> dict[str, Any]:
    model_tables = sorted(f"table_{index:02d}" for index in range(22))
    values = {name: 0 for name in model_tables}
    values["alembic_version"] = 1
    return {
        "connected": True,
        "database": "rpg_game_migration_empty_v290",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "modelTableCount": 22,
        "publicTableCount": 23,
        "publicTables": sorted(values),
        "tableCountsCollected": True,
        "tableCounts": dict(sorted(values.items())),
        "totalRows": 1,
        "alembicVersionTableExists": True,
        "alembicCurrentRevisions": [module.REVISION_ID],
        "comparedTables": model_tables,
        "differenceCount": 0,
        "differences": [],
        "schemaClassification": "structurally-equivalent",
        "classification": "alembic-managed",
    }


def integrity(database: str, values: dict[str, int]) -> dict[str, Any]:
    tables = {
        name: {
            "schemaDigest": f"schema-{name}",
            "rowCount": count,
            "rowDigest": f"rows-{name}-{count}",
        }
        for name, count in sorted(values.items())
    }
    return {
        "database": database,
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "publicTables": sorted(values),
        "publicTableCount": len(values),
        "schemaDigest": f"schema-all-{database}",
        "dataDigest": f"data-all-{database}",
        "combinedDigest": f"combined-{database}",
        "tables": tables,
    }


def schema_state() -> dict[str, Any]:
    return {
        "connected": True,
        "classification": "structurally-equivalent",
        "modelTableCount": 22,
        "databaseTableCount": 22,
        "differenceCount": 0,
        "typeNormalization": "postgresql-float-aliases.v1",
    }


def rehearsal_report(
    module: Any,
    rehearsal: dict[str, Any],
    rehearsal_integrity: dict[str, Any],
    rehearsal_model: dict[str, Any],
    migration: dict[str, Any],
    migration_integrity: dict[str, Any],
) -> dict[str, Any]:
    placeholder_source_integrity = {"unchanged": True}
    return {
        "result": module.REHEARSAL_STAMP_SUCCESS_RESULT,
        "targetDatabase": "rpg_game_restore_rehearsal_v290",
        "revisionId": module.REVISION_ID,
        "revisionSha256": module.REVISION_SHA256,
        "stampExecuted": True,
        "upgradeExecuted": False,
        "downgradeExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
        "sourceDatabaseMutationExecuted": False,
        "migrationDatabaseMutationExecuted": False,
        "sourceBefore": {"unchanged": True},
        "sourceAfter": {"unchanged": True},
        "migrationBefore": migration,
        "migrationAfter": migration,
        "sourceIntegrityBefore": placeholder_source_integrity,
        "sourceIntegrityAfter": placeholder_source_integrity,
        "migrationIntegrityBefore": migration_integrity,
        "migrationIntegrityAfter": migration_integrity,
        "rehearsalModelIntegrityBefore": rehearsal_model,
        "rehearsalModelIntegrityAfter": rehearsal_model,
        "rehearsalAfter": rehearsal,
    }


def source_report(
    module: Any,
    source: dict[str, Any],
    source_integrity: dict[str, Any],
    source_model: dict[str, Any],
    rehearsal: dict[str, Any],
    rehearsal_integrity: dict[str, Any],
    migration: dict[str, Any],
    migration_integrity: dict[str, Any],
) -> dict[str, Any]:
    return {
        "result": module.SUCCESS_RESULT,
        "targetDatabase": "rpg_game",
        "revisionId": module.REVISION_ID,
        "revisionSha256": module.REVISION_SHA256,
        "verifiedBackupSha256": module.APPROVED_BACKUP_SHA256,
        "verifiedRehearsalResult": module.REHEARSAL_POST_STAMP_VERIFIED_RESULT,
        "stampExecuted": True,
        "upgradeExecuted": False,
        "downgradeExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
        "rehearsalDatabaseMutationExecuted": False,
        "migrationDatabaseMutationExecuted": False,
        "sourceBefore": source_pre(),
        "sourceAfter": source,
        "sourceIntegrityBefore": source_integrity,
        "sourceIntegrityAfter": source_integrity,
        "sourceModelIntegrityBefore": source_model,
        "sourceModelIntegrityAfter": source_model,
        "rehearsalBefore": rehearsal,
        "rehearsalAfter": rehearsal,
        "rehearsalIntegrityBefore": rehearsal_integrity,
        "rehearsalIntegrityAfter": rehearsal_integrity,
        "migrationBefore": migration,
        "migrationAfter": migration,
        "migrationIntegrityBefore": migration_integrity,
        "migrationIntegrityAfter": migration_integrity,
    }


def main() -> None:
    module = load_tool()
    verified = evidence(module)
    source_before = source_pre()
    source_after = source_post(module)
    rehearsal = rehearsal_post(module)
    migration = migration_post(module)

    source_after_validated = module.validate_source_after(source_after, verified)
    rehearsal_validated = module.validate_rehearsal_after(rehearsal, verified)
    migration_validated = module.validate_migration_after(
        migration, verified["expectedTables"]
    )

    source_before_integrity = integrity("rpg_game", counts())
    source_after_counts = counts()
    source_after_counts["alembic_version"] = 1
    source_after_integrity = integrity("rpg_game", source_after_counts)
    rehearsal_counts = counts()
    rehearsal_counts["alembic_version"] = 1
    rehearsal_integrity = integrity(
        "rpg_game_restore_rehearsal_v290", rehearsal_counts
    )
    migration_counts = {f"table_{index:02d}": 0 for index in range(22)}
    migration_counts["alembic_version"] = 1
    migration_integrity = integrity(
        "rpg_game_migration_empty_v290", migration_counts
    )

    approved_model = module.model_table_integrity_signature(
        source_before_integrity, verified["expectedTables"]
    )
    rehearsal_model = module.model_table_integrity_signature(
        rehearsal_integrity, verified["expectedTables"]
    )
    if approved_model != rehearsal_model:
        raise AssertionError("source/rehearsal mock application signatures differ")

    v302_report = rehearsal_report(
        module,
        rehearsal_validated,
        rehearsal_integrity,
        rehearsal_model,
        migration_validated,
        migration_integrity,
    )
    common = {
        "evidence": verified,
        "rehearsal_raw": rehearsal,
        "migration_raw": migration,
        "schema_raw": schema_state(),
        "rehearsal_integrity": rehearsal_integrity,
        "migration_integrity": migration_integrity,
        "roundtrip_evidence": {"migrationAfter": migration_validated},
        "rehearsal_report": v302_report,
        "approved_schema_digest": approved_model["schemaDigest"],
        "approved_data_digest": approved_model["dataDigest"],
    }

    before = module.inspect_readiness(
        ROOT,
        source_raw=source_before,
        source_integrity=source_before_integrity,
        source_report=None,
        **common,
    )
    if before["result"] != module.READY_RESULT:
        raise AssertionError("v304 pre-stamp readiness classification mismatch")
    if before["targetDatabase"] != "rpg_game":
        raise AssertionError("v304 exact source target boundary mismatch")
    if before["executionApproved"] is not False:
        raise AssertionError("v304 inspect must not approve source execution")
    if before["rehearsalVerification"]["reportStatus"] != "verified":
        raise AssertionError("v304 did not require the verified v302 rehearsal report")
    if before["readOnly"] is not True or before["mutationExecuted"] is not False:
        raise AssertionError("v304 inspection mutation boundary changed")

    after_model = module.model_table_integrity_signature(
        source_after_integrity, verified["expectedTables"]
    )
    v304_report = source_report(
        module,
        source_after_validated,
        source_after_integrity,
        after_model,
        rehearsal_validated,
        rehearsal_integrity,
        migration_validated,
        migration_integrity,
    )
    after = module.inspect_readiness(
        ROOT,
        source_raw=source_after,
        source_integrity=source_after_integrity,
        source_report=v304_report,
        **common,
    )
    if after["result"] != module.POST_STAMP_VERIFIED_RESULT:
        raise AssertionError("v304 post-stamp verification classification mismatch")
    if after["sourceStampReportStatus"] != "verified":
        raise AssertionError("v304 source execution report was not verified")
    if after["sourceModelIntegrity"] != before["sourceModelIntegrity"]:
        raise AssertionError("v304 source application digest changed after stamp")

    missing_report = module.inspect_readiness(
        ROOT,
        source_raw=source_after,
        source_integrity=source_after_integrity,
        source_report=None,
        **common,
    )
    if missing_report["result"] != module.POST_STAMP_REPORT_MISSING_RESULT:
        raise AssertionError("v304 post-stamp missing-report recovery mismatch")

    try:
        module.inspect_readiness(
            ROOT,
            source_raw=source_before,
            source_integrity=source_before_integrity,
            source_report=None,
            rehearsal_report=None,
            **{key: value for key, value in common.items() if key != "rehearsal_report"},
        )
    except module.SourceBaselineStampError:
        pass
    else:
        raise AssertionError("v304 allowed source planning without v302 report")

    changed_integrity = integrity("rpg_game", counts())
    changed_integrity["tables"]["table_00"]["rowDigest"] = "changed"
    try:
        module.inspect_readiness(
            ROOT,
            source_raw=source_before,
            source_integrity=changed_integrity,
            source_report=None,
            **common,
        )
    except module.SourceBaselineStampError:
        pass
    else:
        raise AssertionError("v304 allowed changed source application data")

    calls: list[dict[str, Any]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        calls.append({"command": command, **kwargs})
        if command[-2:] != ["stamp", "head"]:
            raise AssertionError(f"unexpected Alembic command: {command}")
        command_text = " ".join(command)
        if "upgrade" in command_text or "downgrade" in command_text:
            raise AssertionError("v304 source guard attempted upgrade/downgrade")
        database_url = str(kwargs["env"].get("DATABASE_URL") or "")
        if not database_url.endswith("/rpg_game"):
            raise AssertionError(f"v304 source target escaped rpg_game: {database_url}")
        if "restore_rehearsal" in database_url or "migration_empty" in database_url:
            raise AssertionError("v304 source target escaped into non-source DB")
        return subprocess.CompletedProcess(command, 0, stdout=b"stamp ok\n")

    original_url = module.source_database_url
    module.source_database_url = lambda root: "postgresql+psycopg://rpg_user:pw@localhost/rpg_game"
    try:
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            report_path = Path(temporary) / "source-stamp-report.json"
            executed = module.execute_stamp(
                ROOT,
                before_inspection=before,
                after_inspection=missing_report,
                run_process=fake_run,
                report_path=report_path,
            )
            if executed["result"] != module.SUCCESS_RESULT:
                raise AssertionError("v304 execute result mismatch")
            if not report_path.is_file():
                raise AssertionError("v304 source execution report was not written")
    finally:
        module.source_database_url = original_url

    if len(calls) != 1:
        raise AssertionError("v304 source guard did not execute exactly one command")

    source_text = TOOL.read_text(encoding="utf-8")
    if "revision --autogenerate" in source_text:
        raise AssertionError("v304 guard contains revision generation command")
    if "docker compose down -v" in source_text:
        raise AssertionError("v304 guard contains Docker volume deletion command")

    print("postgres source baseline stamp final guard smoke test passed")


if __name__ == "__main__":
    main()

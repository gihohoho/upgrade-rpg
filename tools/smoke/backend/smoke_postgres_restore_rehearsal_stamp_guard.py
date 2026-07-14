#!/usr/bin/env python3
"""Smoke checks for the v302 restored-copy Alembic stamp guard."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/stamp_postgres_restore_rehearsal_database.py"


def load_tool() -> Any:
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location(
        "stamp_postgres_restore_rehearsal_database", TOOL
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load v302 rehearsal stamp guard")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def counts(total: int = 748) -> dict[str, int]:
    values = {f"table_{index:02d}": 0 for index in range(22)}
    values["table_00"] = total
    return values


def evidence() -> dict[str, Any]:
    values = counts()
    return {
        "expectedTables": tuple(sorted(values)),
        "expectedTableCounts": dict(sorted(values.items())),
        "expectedTotalRows": 748,
    }


def source_state() -> dict[str, Any]:
    values = counts()
    return {
        "connected": True,
        "database": "rpg_game",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "publicTableCount": 22,
        "publicTables": sorted(values),
        "tableCountsCollected": True,
        "tableCounts": dict(sorted(values.items())),
        "totalRows": 748,
        "alembicVersionTableExists": False,
        "alembicCurrentRevisions": [],
        "classification": "existing-schema-without-alembic-baseline",
    }


def rehearsal_before_state() -> dict[str, Any]:
    state = source_state()
    state.update(
        {
            "database": "rpg_game_restore_rehearsal_v290",
            "schemaClassification": "structurally-equivalent",
            "differenceCount": 0,
        }
    )
    return state


def rehearsal_after_state(module: Any) -> dict[str, Any]:
    values = counts()
    values["alembic_version"] = 1
    return {
        "connected": True,
        "database": "rpg_game_restore_rehearsal_v290",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "publicTableCount": 23,
        "publicTables": sorted(values),
        "tableCountsCollected": True,
        "tableCounts": dict(sorted(values.items())),
        "totalRows": 749,
        "alembicVersionTableExists": True,
        "alembicCurrentRevisions": [module.REVISION_ID],
        "classification": "alembic-managed",
        "schemaClassification": "structurally-equivalent",
        "differenceCount": 0,
    }


def migration_state(module: Any) -> dict[str, Any]:
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


def preflight(module: Any) -> dict[str, Any]:
    return {
        "result": module.SOURCE_PREFLIGHT_READY_RESULT,
        "readOnly": True,
        "mutationExecuted": False,
        "sourceDatabase": "rpg_game",
        "revision": {
            "id": module.REVISION_ID,
            "sha256": module.REVISION_SHA256,
        },
    }


def main() -> None:
    module = load_tool()
    source = source_state()
    rehearsal_before = rehearsal_before_state()
    rehearsal_after = rehearsal_after_state(module)
    migration = migration_state(module)
    source_integrity = integrity("rpg_game", counts())
    rehearsal_before_integrity = integrity(
        "rpg_game_restore_rehearsal_v290", counts()
    )
    rehearsal_after_counts = counts()
    rehearsal_after_counts["alembic_version"] = 1
    rehearsal_after_integrity = integrity(
        "rpg_game_restore_rehearsal_v290", rehearsal_after_counts
    )
    migration_counts = {f"table_{index:02d}": 0 for index in range(22)}
    migration_counts["alembic_version"] = 1
    migration_integrity = integrity(
        "rpg_game_migration_empty_v290", migration_counts
    )

    inspected = module.inspect_readiness(
        ROOT,
        preflight_payload=preflight(module),
        evidence=evidence(),
        source_raw=source,
        rehearsal_raw=rehearsal_before,
        migration_raw=migration,
        source_integrity=source_integrity,
        rehearsal_integrity=rehearsal_before_integrity,
        migration_integrity=migration_integrity,
    )
    if inspected["result"] != module.READY_RESULT:
        raise AssertionError("v302 readiness classification mismatch")
    if inspected["readOnly"] is not True or inspected["mutationExecuted"] is not False:
        raise AssertionError("v302 inspection must remain read-only")
    if inspected["targetDatabase"] != "rpg_game_restore_rehearsal_v290":
        raise AssertionError("v302 exact target boundary mismatch")
    if inspected["executionApproved"] is not False:
        raise AssertionError("v302 inspection must not approve execution")
    if inspected["rehearsalModelIntegrity"]["rowCount"] != 748:
        raise AssertionError("v302 pre-stamp row integrity mismatch")

    calls: list[dict[str, Any]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[bytes]:
        calls.append({"command": command, **kwargs})
        if command[-2:] != ["stamp", "head"]:
            raise AssertionError(f"unexpected Alembic command: {command}")
        command_text = " ".join(command)
        if "upgrade" in command_text or "downgrade" in command_text:
            raise AssertionError("stamp guard attempted upgrade/downgrade")
        database_url = str(kwargs["env"].get("DATABASE_URL") or "")
        if not database_url.endswith("/rpg_game_restore_rehearsal_v290"):
            raise AssertionError(f"stamp target URL escaped rehearsal DB: {database_url}")
        if database_url.endswith("/rpg_game") or database_url.endswith(
            "/rpg_game_migration_empty_v290"
        ):
            raise AssertionError("stamp target escaped exact rehearsal boundary")
        return subprocess.CompletedProcess(command, 0, stdout=b"stamp simulated\n")

    original_report = module.STAMP_REPORT_RELATIVE_PATH
    original_writer = module.write_json_atomic
    captured: dict[str, Any] = {}
    module.STAMP_REPORT_RELATIVE_PATH = Path(
        "local-review-artifacts/alembic/smoke-v302-never-written.json"
    )
    module.write_json_atomic = lambda path, payload: captured.update(
        {"path": path, "payload": payload}
    )
    try:
        executed = module.execute_stamp(
            ROOT,
            preflight_payload=preflight(module),
            evidence=evidence(),
            source_before_raw=source,
            source_after_raw=source,
            rehearsal_before_raw=rehearsal_before,
            rehearsal_after_raw=rehearsal_after,
            migration_before_raw=migration,
            migration_after_raw=migration,
            source_before_integrity=source_integrity,
            source_after_integrity=source_integrity,
            rehearsal_before_integrity=rehearsal_before_integrity,
            rehearsal_after_integrity=rehearsal_after_integrity,
            migration_before_integrity=migration_integrity,
            migration_after_integrity=migration_integrity,
            run_process=fake_run,
        )
    finally:
        module.STAMP_REPORT_RELATIVE_PATH = original_report
        module.write_json_atomic = original_writer

    if len(calls) != 1:
        raise AssertionError("v302 simulated stamp must invoke exactly one subprocess")
    if executed["result"] != module.SUCCESS_RESULT:
        raise AssertionError("v302 simulated success classification mismatch")
    if executed["stampExecuted"] is not True:
        raise AssertionError("v302 simulated report must record stamp execution")
    if executed["upgradeExecuted"] or executed["downgradeExecuted"]:
        raise AssertionError("v302 simulated report recorded forbidden Alembic operations")
    if executed["rehearsalModelIntegrityBefore"] != executed[
        "rehearsalModelIntegrityAfter"
    ]:
        raise AssertionError("application schema/data signature was not preserved")
    if executed["rehearsalAfter"]["totalRows"] != 749:
        raise AssertionError("v302 post-stamp total must be 748 + one Alembic row")
    if not captured:
        raise AssertionError("v302 verified execution did not prepare its local report")

    bad_after_integrity = integrity(
        "rpg_game_restore_rehearsal_v290", rehearsal_after_counts
    )
    bad_after_integrity["tables"]["table_00"]["rowDigest"] = "changed"
    try:
        module.execute_stamp(
            ROOT,
            preflight_payload=preflight(module),
            evidence=evidence(),
            source_before_raw=source,
            source_after_raw=source,
            rehearsal_before_raw=rehearsal_before,
            rehearsal_after_raw=rehearsal_after,
            migration_before_raw=migration,
            migration_after_raw=migration,
            source_before_integrity=source_integrity,
            source_after_integrity=source_integrity,
            rehearsal_before_integrity=rehearsal_before_integrity,
            rehearsal_after_integrity=bad_after_integrity,
            migration_before_integrity=migration_integrity,
            migration_after_integrity=migration_integrity,
            run_process=fake_run,
        )
    except Exception:
        pass
    else:
        raise AssertionError("v302 must block changed application row content")

    bad_after = dict(rehearsal_after)
    bad_after["alembicCurrentRevisions"] = ["wrong_revision"]
    try:
        module.validate_rehearsal_after(bad_after, evidence())
    except Exception:
        pass
    else:
        raise AssertionError("v302 must block the wrong stamped revision")

    source_text = TOOL.read_text(encoding="utf-8")
    required_markers = [
        '"stamp",\n        "head"',
        "--confirm-target",
        "--confirm-revision",
        "collect_database_integrity_signature",
        "alembic_version",
    ]
    for marker in required_markers:
        if marker not in source_text:
            raise AssertionError(f"v302 stamp guard missing required marker: {marker}")
    forbidden_commands = [
        '"upgrade",\n        "head"',
        '"downgrade"',
        '"createdb"',
        '"dropdb"',
        '"pg_restore"',
        '"docker",\n        "compose"',
    ]
    for marker in forbidden_commands:
        if marker in source_text:
            raise AssertionError(f"v302 stamp guard contains forbidden command marker: {marker}")

    print("OK: PostgreSQL restore rehearsal stamp guard smoke passed")


if __name__ == "__main__":
    main()

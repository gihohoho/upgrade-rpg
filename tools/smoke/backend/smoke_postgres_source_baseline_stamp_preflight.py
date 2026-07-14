#!/usr/bin/env python3
"""Smoke checks for the v301 source baseline stamp read-only preflight."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_postgres_source_baseline_stamp_preflight.py"


def load_tool() -> Any:
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location(
        "check_postgres_source_baseline_stamp_preflight", TOOL
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load v301 source baseline preflight tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def counts(total: int = 748) -> dict[str, int]:
    values = {f"table_{index:02d}": 0 for index in range(22)}
    values["table_00"] = total
    return values


def restore_evidence() -> dict[str, Any]:
    values = counts()
    return {
        "backupRelativePath": "local-backups/postgres/rpg_game_test.custom.dump",
        "sha256": "b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481",
        "expectedTables": tuple(sorted(values)),
        "expectedTableCounts": dict(sorted(values.items())),
        "expectedTotalRows": 748,
    }


def source_state() -> dict[str, Any]:
    values = counts()
    tables = sorted(values)
    return {
        "connected": True,
        "database": "rpg_game",
        "user": "rpg_user",
        "schema": "public",
        "serverVersion": "16.14",
        "publicTableCount": 22,
        "publicTables": tables,
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


def migration_head(module: Any) -> dict[str, Any]:
    model_tables = sorted(f"table_{index:02d}" for index in range(22))
    tables = sorted([*model_tables, "alembic_version"])
    table_counts = {name: 0 for name in tables}
    table_counts["alembic_version"] = 1
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
        "tableCounts": dict(sorted(table_counts.items())),
        "totalRows": 1,
        "alembicVersionTableExists": True,
        "alembicCurrentRevisions": [module.REVISION_ID],
        "comparedTables": model_tables,
        "differenceCount": 0,
        "differences": [],
        "schemaClassification": "structurally-equivalent",
        "classification": "alembic-managed",
    }


def roundtrip_evidence(module: Any, source: dict[str, Any], rehearsal: dict[str, Any], migration: dict[str, Any]) -> dict[str, Any]:
    signature = module.migration_signature(migration)
    return {
        "result": "migration-test-database-roundtrip-upgraded-and-verified",
        "targetDatabase": "rpg_game_migration_empty_v290",
        "revisionId": module.REVISION_ID,
        "revisionSha256": module.REVISION_SHA256,
        "roundTripEquivalent": True,
        "upgradeExecuted": True,
        "downgradeExecutedInThisStep": False,
        "stampExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
        "sourceBefore": source,
        "sourceAfter": source,
        "rehearsalBefore": rehearsal,
        "rehearsalAfter": rehearsal,
        "migrationAfter": migration,
        "firstUpgradeSignature": signature,
        "secondUpgradeSignature": signature,
    }


def schema_state() -> dict[str, Any]:
    return {
        "connected": True,
        "classification": "structurally-equivalent",
        "typeNormalization": "postgresql-float-aliases.v1",
        "modelTableCount": 22,
        "databaseTableCount": 22,
        "differenceCount": 0,
        "differences": [],
    }


def main() -> None:
    module = load_tool()
    source = source_state()
    rehearsal = rehearsal_state()
    migration = migration_head(module)
    roundtrip = roundtrip_evidence(module, source, rehearsal, migration)

    result = module.inspect_readiness(
        ROOT,
        restore_evidence=restore_evidence(),
        roundtrip_evidence=roundtrip,
        source_raw=source,
        rehearsal_raw=rehearsal,
        migration_raw=migration,
        schema_raw=schema_state(),
    )
    if result["result"] != module.READY_RESULT:
        raise AssertionError("v301 preflight success classification mismatch")
    if result["readOnly"] is not True or result["mutationExecuted"] is not False:
        raise AssertionError("v301 preflight must remain read-only")
    if result["source"]["alembicVersionTableExists"] is not False:
        raise AssertionError("source must not already have an Alembic baseline")
    if result["migration"]["alembicCurrentRevisions"] != [module.REVISION_ID]:
        raise AssertionError("isolated migration round-trip head mismatch")
    if result["sourceSchema"]["differenceCount"] != 0:
        raise AssertionError("source schema difference count must be zero")

    bad_source = dict(source)
    bad_source["alembicVersionTableExists"] = True
    bad_source["alembicCurrentRevisions"] = [module.REVISION_ID]
    try:
        module.inspect_readiness(
            ROOT,
            restore_evidence=restore_evidence(),
            roundtrip_evidence=roundtrip,
            source_raw=bad_source,
            rehearsal_raw=rehearsal,
            migration_raw=migration,
            schema_raw=schema_state(),
        )
    except Exception:
        pass
    else:
        raise AssertionError("source with an existing Alembic baseline must be blocked")

    bad_schema = dict(schema_state())
    bad_schema.update({"classification": "review-required", "differenceCount": 1})
    try:
        module.inspect_readiness(
            ROOT,
            restore_evidence=restore_evidence(),
            roundtrip_evidence=roundtrip,
            source_raw=source,
            rehearsal_raw=rehearsal,
            migration_raw=migration,
            schema_raw=bad_schema,
        )
    except Exception:
        pass
    else:
        raise AssertionError("source schema drift must block baseline stamp readiness")

    bad_roundtrip = dict(roundtrip)
    bad_roundtrip["roundTripEquivalent"] = False
    try:
        module.inspect_readiness(
            ROOT,
            restore_evidence=restore_evidence(),
            roundtrip_evidence=bad_roundtrip,
            source_raw=source,
            rehearsal_raw=rehearsal,
            migration_raw=migration,
            schema_raw=schema_state(),
        )
    except Exception:
        pass
    else:
        raise AssertionError("failed round-trip evidence must block baseline stamp readiness")

    source_text = TOOL.read_text(encoding="utf-8")
    forbidden_runtime_markers = [
        'subprocess.run(',
        'create_engine(',
        'write_json_atomic(',
        '"--execute"',
        "'--execute'",
    ]
    for marker in forbidden_runtime_markers:
        if marker in source_text:
            raise AssertionError(f"v301 read-only preflight contains forbidden runtime marker: {marker}")

    print("OK: PostgreSQL source baseline stamp read-only preflight smoke passed")


if __name__ == "__main__":
    main()

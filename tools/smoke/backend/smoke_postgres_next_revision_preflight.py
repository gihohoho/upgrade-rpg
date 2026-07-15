#!/usr/bin/env python3
"""Smoke checks for the v306 next-revision read-only preflight."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools"
MODULE_PATH = TOOLS / "check_postgres_next_revision_preflight.py"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def load_module():
    spec = importlib.util.spec_from_file_location("v306_next_revision_preflight", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load v306 next-revision preflight")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def completion_state(module):
    return {
        "result": module.BASELINE_COMPLETION_RESULT,
        "readOnly": True,
        "sourceCurrentRevision": [module.REVISION_ID],
        "revisionSha256": module.REVISION_SHA256,
        "revisionFiles": [module.EXPECTED_REVISION_FILE],
    }


def graph_state(module):
    return {
        "heads": [module.REVISION_ID],
        "bases": [module.REVISION_ID],
        "currentHead": module.REVISION_ID,
        "revisionIds": [module.REVISION_ID],
        "revisionFiles": [module.EXPECTED_REVISION_FILE],
    }


def schema_state():
    return {
        "readOnly": True,
        "connected": True,
        "classification": "structurally-equivalent",
        "differenceCount": 0,
        "modelTableCount": 22,
        "databaseTableCount": 22,
    }


def comparison_state():
    owners = [{"table": f"table_{index}", "column": "id"} for index in range(22)]
    return {
        "readOnlyTransaction": True,
        "sqlWriteGuard": True,
        "database": "rpg_game",
        "metadataTableCount": 22,
        "compareType": True,
        "compareServerDefault": True,
        "candidateOperationCount": 0,
        "operationCounts": {},
        "operations": [],
        "sequenceCount": 22,
        "sequenceOwners": owners,
        "expectedSequenceOwners": owners,
        "sequenceOwnershipMatches": True,
        "unownedSequences": [],
    }


def inspect(module, **overrides):
    values = {
        "completion_state": completion_state(module),
        "graph_state": graph_state(module),
        "model_source_hashes": dict(module.EXPECTED_MODEL_SOURCE_SHA256),
        "schema_equivalence": schema_state(),
        "autogenerate_comparison": comparison_state(),
    }
    values.update(overrides)
    return module.inspect_next_revision_preflight(ROOT, **values)


def expect_block(module, message: str, **overrides) -> None:
    try:
        inspect(module, **overrides)
    except module.NextRevisionPreflightError:
        return
    raise AssertionError(message)


def main() -> None:
    module = load_module()

    result = inspect(module)
    if result["result"] != module.NO_REVISION_RESULT:
        raise AssertionError("v306 no-revision result mismatch")
    if result["nextRevisionRequired"] is not False:
        raise AssertionError("v306 incorrectly requires a revision")
    if result["readOnly"] is not True or result["mutationExecuted"] is not False:
        raise AssertionError("v306 read-only boundary changed")
    for key in (
        "revisionGenerated",
        "autogenerateCommandExecuted",
        "upgradeExecuted",
        "downgradeExecuted",
        "stampExecuted",
        "nextRevisionApproved",
        "autogenerateApproved",
        "upgradeApproved",
        "downgradeApproved",
    ):
        if result[key] is not False:
            raise AssertionError(f"v306 unexpectedly enabled {key}")

    comparison = comparison_state()
    comparison["candidateOperationCount"] = 1
    comparison["operationCounts"] = {"add_column": 1}
    comparison["operations"] = [
        {
            "operation": "add_column",
            "schema": "public",
            "table": "users",
            "column": "example",
            "objectName": None,
        }
    ]
    review = inspect(module, autogenerate_comparison=comparison)
    if review["result"] != module.REVIEW_RESULT:
        raise AssertionError("v306 did not classify candidate operations for review")
    if review["nextRevisionRequired"] is not True:
        raise AssertionError("v306 review state did not require explicit design review")
    if review["autogenerateApproved"] is not False:
        raise AssertionError("v306 review state automatically approved autogenerate")

    graph = graph_state(module)
    graph["heads"] = [module.REVISION_ID, "v306_unapproved"]
    expect_block(module, "v306 allowed multiple heads", graph_state=graph)

    hashes = dict(module.EXPECTED_MODEL_SOURCE_SHA256)
    hashes["backend/app/models/user.py"] = "0" * 64
    expect_block(module, "v306 allowed changed model source", model_source_hashes=hashes)

    schema = schema_state()
    schema["differenceCount"] = 1
    schema["classification"] = "review-required"
    expect_block(module, "v306 ignored canonical schema drift", schema_equivalence=schema)

    comparison = comparison_state()
    comparison["database"] = "rpg_game_restore_rehearsal_v290"
    expect_block(module, "v306 allowed a non-source DB", autogenerate_comparison=comparison)

    comparison = comparison_state()
    comparison["sequenceOwnershipMatches"] = False
    expect_block(module, "v306 allowed sequence ownership drift", autogenerate_comparison=comparison)

    comparison = comparison_state()
    comparison["unownedSequences"] = ["unexpected_sequence"]
    expect_block(module, "v306 allowed an unowned sequence", autogenerate_comparison=comparison)

    actual_hashes = module.collect_model_source_hashes(ROOT)
    if actual_hashes != module.EXPECTED_MODEL_SOURCE_SHA256:
        raise AssertionError("v306 embedded model source snapshot does not match project files")

    try:
        module._read_only_sql_guard(None, None, "ALTER TABLE users ADD COLUMN x int", None, None, False)
    except module.NextRevisionPreflightError:
        pass
    else:
        raise AssertionError("v306 SQL guard allowed ALTER TABLE")
    module._read_only_sql_guard(None, None, "SELECT 1", None, None, False)
    module._read_only_sql_guard(None, None, "SET TRANSACTION READ ONLY", None, None, False)

    source = MODULE_PATH.read_text(encoding="utf-8")
    forbidden = (
        "subprocess.run(",
        "os.system(",
        "command.revision(",
        "alembic.command",
        "upgrade(",
        "downgrade(",
        "stamp(",
    )
    for marker in forbidden:
        if marker in source:
            raise AssertionError(f"v306 checker contains forbidden execution marker: {marker}")

    print("OK: PostgreSQL next revision read-only preflight smoke passed")


if __name__ == "__main__":
    main()

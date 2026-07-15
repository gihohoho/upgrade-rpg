#!/usr/bin/env python3
"""Smoke checks for the v305 PostgreSQL baseline completion state lock."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools"
MODULE_PATH = TOOLS / "check_postgres_baseline_completion_state.py"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))


def load_module():
    spec = importlib.util.spec_from_file_location("v305_baseline_completion", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load v305 baseline completion checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_state(module):
    model = {
        "tableCount": 22,
        "rowCount": 748,
        "schemaDigest": "schema-digest",
        "dataDigest": "data-digest",
        "combinedDigest": "combined-digest",
        "tables": {},
    }
    return {
        "result": module.POST_STAMP_VERIFIED_RESULT,
        "readOnly": True,
        "mutationExecuted": False,
        "lifecycleState": "post-stamp",
        "targetDatabase": "rpg_game",
        "revisionId": module.REVISION_ID,
        "revisionSha256": module.REVISION_SHA256,
        "sourceStampReportStatus": "verified",
        "source": {
            "database": "rpg_game",
            "publicTableCount": 23,
            "totalRows": 749,
            "alembicVersionTableExists": True,
            "alembicCurrentRevisions": [module.REVISION_ID],
            "classification": "alembic-managed",
        },
        "sourceModelIntegrity": model,
        "rehearsalVerification": {
            "result": "restore-rehearsal-stamp-current-state-verified",
            "reportStatus": "verified",
            "rehearsal": {
                "database": "rpg_game_restore_rehearsal_v290",
                "publicTableCount": 23,
                "totalRows": 749,
                "alembicCurrentRevisions": [module.REVISION_ID],
            },
            "rehearsalModelIntegrity": dict(model),
            "migration": {
                "database": "rpg_game_migration_empty_v290",
                "publicTableCount": 23,
                "totalRows": 1,
                "alembicCurrentRevisions": [module.REVISION_ID],
            },
        },
    }


def expect_block(module, state, message, revision_files=None):
    try:
        module.inspect_completion_state(
            ROOT,
            source_stamp_state=state,
            revision_files=(
                revision_files
                if revision_files is not None
                else [module.EXPECTED_REVISION_FILE]
            ),
        )
    except module.BaselineCompletionStateError:
        return
    raise AssertionError(message)


def main() -> None:
    module = load_module()
    state = valid_state(module)
    result = module.inspect_completion_state(
        ROOT,
        source_stamp_state=state,
        revision_files=[module.EXPECTED_REVISION_FILE],
    )
    if result["result"] != module.SUCCESS_RESULT:
        raise AssertionError("v305 completion result mismatch")
    if result["classification"] != "alembic-managed-baseline-complete":
        raise AssertionError("v305 completed classification mismatch")
    if result["readOnly"] is not True or result["mutationExecuted"] is not False:
        raise AssertionError("v305 read-only boundary changed")
    for key in (
        "nextRevisionApproved",
        "autogenerateApproved",
        "upgradeApproved",
        "downgradeApproved",
        "stampRetryApproved",
    ):
        if result[key] is not False:
            raise AssertionError(f"v305 unexpectedly approved {key}")

    changed = valid_state(module)
    changed["lifecycleState"] = "pre-stamp"
    expect_block(module, changed, "v305 allowed pre-stamp source state")

    changed = valid_state(module)
    changed["sourceStampReportStatus"] = "missing"
    expect_block(module, changed, "v305 allowed missing v304 execution report")

    changed = valid_state(module)
    changed["source"]["classification"] = "existing-schema-without-alembic-baseline"
    expect_block(module, changed, "v305 allowed legacy source classification")

    changed = valid_state(module)
    changed["rehearsalVerification"]["migration"]["totalRows"] = 2
    expect_block(module, changed, "v305 allowed changed migration endpoint")

    expect_block(
        module,
        valid_state(module),
        "v305 allowed an unreviewed second revision",
        revision_files=[
            module.EXPECTED_REVISION_FILE,
            "backend/alembic/versions/v306_unapproved.py",
        ],
    )

    source = MODULE_PATH.read_text(encoding="utf-8")
    forbidden_calls = (
        "subprocess.run(",
        "os.system(",
        "write_json_atomic(",
        "execute_stamp(",
    )
    for marker in forbidden_calls:
        if marker in source:
            raise AssertionError(f"v305 checker contains forbidden call: {marker}")

    print("OK: PostgreSQL baseline completion state smoke passed")


if __name__ == "__main__":
    main()

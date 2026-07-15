#!/usr/bin/env python3
"""Verify that the PostgreSQL/Alembic initial baseline is fully completed.

This v305 checker is intentionally read-only. It reuses the verified v304
source post-check and then locks the completed lifecycle state:

- source ``rpg_game`` is Alembic-managed at ``v295_initial_schema``;
- source/rehearsal application schema and all 748 rows are unchanged;
- v302 rehearsal and v304 source execution reports are verified;
- the isolated migration DB remains at the verified round-trip endpoint;
- exactly one reviewed Alembic revision exists;
- no next revision/autogenerate/upgrade/downgrade is approved.

The checker never runs Alembic, subprocesses, DB writes, revision generation,
DB create/drop/restore, Docker changes, seed, auth, or API writes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from check_postgres_backup_restore_preflight import (
    MIGRATION_TEST_DATABASE,
    RESTORE_REHEARSAL_DATABASE,
    SOURCE_DATABASE,
)
from stamp_postgres_source_database import (
    POST_STAMP_VERIFIED_RESULT,
    SOURCE_STAMP_REPORT_RELATIVE_PATH,
    inspect_readiness as inspect_source_stamp_state,
)
from upgrade_postgres_migration_test_database import (
    REVISION_ID,
    REVISION_SHA256,
)

TOOL_VERSION = "v305.postgres-baseline-completion-state-lock"
SUCCESS_RESULT = "postgres-baseline-completion-state-verified"
COMPLETED_CLASSIFICATION = "alembic-managed-baseline-complete"
EXPECTED_REVISION_FILE = (
    "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py"
)


class BaselineCompletionStateError(RuntimeError):
    """Raised when the completed baseline lifecycle state is not preserved."""


def current_revision_files(root: Path) -> list[str]:
    versions = root / "backend/alembic/versions"
    if not versions.is_dir():
        raise BaselineCompletionStateError("Alembic versions directory is missing")
    return sorted(
        path.relative_to(root).as_posix()
        for path in versions.glob("*.py")
        if path.is_file() and path.name != "__init__.py"
    )


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BaselineCompletionStateError(message)


def inspect_completion_state(
    root: Path,
    *,
    source_stamp_state: dict[str, Any] | None = None,
    revision_files: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Return the read-only v305 baseline completion state."""
    root = root.resolve()
    state = source_stamp_state or inspect_source_stamp_state(root)

    _require(
        state.get("result") == POST_STAMP_VERIFIED_RESULT,
        "source baseline post-check is not fully verified",
    )
    _require(
        state.get("lifecycleState") == "post-stamp",
        "source is not in the post-stamp lifecycle state",
    )
    _require(
        state.get("targetDatabase") == SOURCE_DATABASE,
        "source database boundary differs from rpg_game",
    )
    _require(
        state.get("revisionId") == REVISION_ID,
        "source revision differs from the reviewed initial revision",
    )
    _require(
        state.get("revisionSha256") == REVISION_SHA256,
        "reviewed revision SHA-256 changed",
    )
    _require(
        state.get("sourceStampReportStatus") == "verified",
        "v304 source execution report is not verified",
    )
    _require(state.get("readOnly") is True, "v304 post-check is not read-only")
    _require(
        state.get("mutationExecuted") is False,
        "v304 post-check unexpectedly reports a mutation",
    )

    source = state.get("source") or {}
    source_model = state.get("sourceModelIntegrity") or {}
    _require(
        source.get("database") == SOURCE_DATABASE,
        "source state database name mismatch",
    )
    _require(
        source.get("publicTableCount") == 23 and source.get("totalRows") == 749,
        "source must remain at 23 public tables / 749 total rows",
    )
    _require(
        source.get("alembicVersionTableExists") is True,
        "source alembic_version table is missing",
    )
    _require(
        source.get("alembicCurrentRevisions") == [REVISION_ID],
        "source current revision is not v295_initial_schema",
    )
    _require(
        source.get("classification") == "alembic-managed",
        "source runtime classification is not alembic-managed",
    )
    _require(
        source_model.get("tableCount") == 22
        and source_model.get("rowCount") == 748,
        "source application baseline is not 22 tables / 748 rows",
    )

    related = state.get("rehearsalVerification") or {}
    _require(
        related.get("result") == "restore-rehearsal-stamp-current-state-verified",
        "restore rehearsal post-check is not verified",
    )
    _require(
        related.get("reportStatus") == "verified",
        "v302 rehearsal execution report is not verified",
    )
    rehearsal = related.get("rehearsal") or {}
    rehearsal_model = related.get("rehearsalModelIntegrity") or {}
    _require(
        rehearsal.get("database") == RESTORE_REHEARSAL_DATABASE,
        "restore rehearsal database boundary changed",
    )
    _require(
        rehearsal.get("publicTableCount") == 23
        and rehearsal.get("totalRows") == 749,
        "restore rehearsal must remain at 23 public tables / 749 total rows",
    )
    _require(
        rehearsal.get("alembicCurrentRevisions") == [REVISION_ID],
        "restore rehearsal revision changed",
    )
    _require(
        source_model == rehearsal_model,
        "source/rehearsal application integrity signatures differ",
    )

    migration = related.get("migration") or {}
    _require(
        migration.get("database") == MIGRATION_TEST_DATABASE,
        "migration test database boundary changed",
    )
    _require(
        migration.get("publicTableCount") == 23
        and migration.get("totalRows") == 1,
        "migration test DB is not at the verified 23-table / 1-row endpoint",
    )
    _require(
        migration.get("alembicCurrentRevisions") == [REVISION_ID],
        "migration test DB revision changed",
    )

    observed_revision_files = sorted(
        str(item)
        for item in (
            revision_files
            if revision_files is not None
            else current_revision_files(root)
        )
    )
    _require(
        observed_revision_files == [EXPECTED_REVISION_FILE],
        "Alembic revision set changed; v305 requires exactly the reviewed initial revision",
    )

    return {
        "toolVersion": TOOL_VERSION,
        "result": SUCCESS_RESULT,
        "readOnly": True,
        "mutationExecuted": False,
        "classification": COMPLETED_CLASSIFICATION,
        "sourceDatabase": SOURCE_DATABASE,
        "sourcePublicTables": source["publicTableCount"],
        "sourceTotalRows": source["totalRows"],
        "sourceApplicationTables": source_model["tableCount"],
        "sourceApplicationRows": source_model["rowCount"],
        "sourceCurrentRevision": source["alembicCurrentRevisions"],
        "sourceSchemaDigest": source_model.get("schemaDigest"),
        "sourceDataDigest": source_model.get("dataDigest"),
        "sourceStampReport": {
            "status": state["sourceStampReportStatus"],
            "relativePath": SOURCE_STAMP_REPORT_RELATIVE_PATH.as_posix(),
        },
        "rehearsalDatabase": RESTORE_REHEARSAL_DATABASE,
        "rehearsalPublicTables": rehearsal["publicTableCount"],
        "rehearsalTotalRows": rehearsal["totalRows"],
        "rehearsalCurrentRevision": rehearsal["alembicCurrentRevisions"],
        "rehearsalReportStatus": related["reportStatus"],
        "migrationDatabase": MIGRATION_TEST_DATABASE,
        "migrationPublicTables": migration["publicTableCount"],
        "migrationTotalRows": migration["totalRows"],
        "migrationCurrentRevision": migration["alembicCurrentRevisions"],
        "revisionId": REVISION_ID,
        "revisionSha256": REVISION_SHA256,
        "revisionFiles": observed_revision_files,
        "nextRevisionApproved": False,
        "autogenerateApproved": False,
        "upgradeApproved": False,
        "downgradeApproved": False,
        "stampRetryApproved": False,
        "nextSafeStage": "separate-read-only-next-revision-preflight",
    }


def render_text(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "PostgreSQL/Alembic baseline completion state lock (read-only)",
            "No stamp, retry, revision generation, autogenerate, upgrade, downgrade, DB create/drop/restore, or row write was executed.",
            "",
            f"- classification: {result['classification']}",
            f"- source DB: {result['sourceDatabase']}",
            f"- source public tables/rows: {result['sourcePublicTables']}/{result['sourceTotalRows']}",
            f"- source application tables/rows: {result['sourceApplicationTables']}/{result['sourceApplicationRows']}",
            f"- source current revision: {result['sourceCurrentRevision']}",
            f"- source application schema digest: {result['sourceSchemaDigest']}",
            f"- source application data digest: {result['sourceDataDigest']}",
            f"- v304 source execution report: {result['sourceStampReport']['status']}",
            f"- rehearsal DB tables/rows: {result['rehearsalPublicTables']}/{result['rehearsalTotalRows']}",
            f"- rehearsal current revision: {result['rehearsalCurrentRevision']}",
            f"- v302 rehearsal execution report: {result['rehearsalReportStatus']}",
            f"- migration DB tables/rows: {result['migrationPublicTables']}/{result['migrationTotalRows']}",
            f"- migration current revision: {result['migrationCurrentRevision']}",
            f"- reviewed revision files: {result['revisionFiles']}",
            "- source/rehearsal application integrity identical: yes",
            "- next revision/autogenerate/upgrade/downgrade approved: no",
            f"- result: {result['result']}",
            f"- next safe stage: {result['nextSafeStage']}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when the completed baseline state is not preserved",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = inspect_completion_state(root)
        print(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
            if args.json
            else render_text(result)
        )
        return 0
    except Exception as exc:
        print("PostgreSQL/Alembic baseline completion state lock")
        print("- result: blocked-or-failed")
        print(f"- reason: {type(exc).__name__}: {exc}")
        print("- no automatic retry or DB/Alembic mutation was attempted.")
        return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())

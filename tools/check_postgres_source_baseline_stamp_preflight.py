#!/usr/bin/env python3
"""Read-only preflight for a future baseline stamp on the existing source DB.

This v301 tool proves that the existing `rpg_game` schema/data still matches the
verified backup baseline and SQLAlchemy metadata, and that the isolated Alembic
round-trip completed successfully. It never runs Alembic stamp/upgrade/
downgrade, never creates or drops a database, and never writes a report or row.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from check_postgres_backup_restore_preflight import (
    MIGRATION_TEST_DATABASE,
    RESTORE_REHEARSAL_DATABASE,
    SOURCE_DATABASE,
)
from check_postgres_runtime_readonly_state import inspect_database
from check_postgres_schema_equivalence import collect as collect_schema_equivalence
from create_postgres_migration_test_database import (
    MigrationTestDatabaseError,
    load_verified_restore_evidence,
    validate_rehearsal_state,
    validate_source_state,
)
from restore_postgres_rehearsal_database import inspect_named_database
from reupgrade_postgres_migration_test_database import (
    ROUNDTRIP_REPORT_RELATIVE_PATH,
    migration_signature,
)
from upgrade_postgres_migration_test_database import (
    REVISION_ID,
    REVISION_SHA256,
    MigrationUpgradeError,
    reviewed_revision,
    validate_migration_after,
)

TOOL_VERSION = "v301.postgres-source-baseline-stamp-readonly-preflight"
READY_RESULT = "ready-for-separate-restore-rehearsal-stamp-approval"


class SourceBaselinePreflightError(RuntimeError):
    """Raised when any source baseline stamp readiness gate fails."""


def ensure_under(root: Path, path: Path) -> Path:
    root_resolved = root.resolve()
    resolved = path.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise SourceBaselinePreflightError(f"unsafe path outside project: {path}")
    return resolved


def validate_roundtrip_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    required = {
        "result": "migration-test-database-roundtrip-upgraded-and-verified",
        "targetDatabase": MIGRATION_TEST_DATABASE,
        "revisionId": REVISION_ID,
        "revisionSha256": REVISION_SHA256,
        "roundTripEquivalent": True,
        "upgradeExecuted": True,
        "downgradeExecutedInThisStep": False,
        "stampExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
    }
    for key, expected in required.items():
        if payload.get(key) != expected:
            raise SourceBaselinePreflightError(
                f"v300 round-trip evidence mismatch: {key}={payload.get(key)!r}, expected={expected!r}"
            )

    if payload.get("sourceBefore") != payload.get("sourceAfter"):
        raise SourceBaselinePreflightError("v300 report source before/after differs")
    if payload.get("rehearsalBefore") != payload.get("rehearsalAfter"):
        raise SourceBaselinePreflightError("v300 report rehearsal before/after differs")
    if payload.get("firstUpgradeSignature") != payload.get("secondUpgradeSignature"):
        raise SourceBaselinePreflightError("v300 first/second upgrade signatures differ")

    migration_after = payload.get("migrationAfter") or {}
    if migration_after.get("database") != MIGRATION_TEST_DATABASE:
        raise SourceBaselinePreflightError("v300 migration target database mismatch")
    if migration_after.get("publicTableCount") != 23:
        raise SourceBaselinePreflightError("v300 migration public table count is not 23")
    if migration_after.get("totalRows") != 1:
        raise SourceBaselinePreflightError("v300 migration total row count is not 1")
    if migration_after.get("alembicCurrentRevisions") != [REVISION_ID]:
        raise SourceBaselinePreflightError("v300 migration current revision mismatch")
    if migration_after.get("schemaClassification") != "structurally-equivalent":
        raise SourceBaselinePreflightError("v300 migration schema is not structurally equivalent")
    if migration_after.get("differenceCount") != 0:
        raise SourceBaselinePreflightError("v300 migration schema difference count is not zero")
    return payload


def load_verified_roundtrip_evidence(root: Path) -> dict[str, Any]:
    path = ensure_under(root, root / ROUNDTRIP_REPORT_RELATIVE_PATH)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceBaselinePreflightError(
            f"verified v300 round-trip report cannot be read: {path}: {exc}"
        ) from exc
    return validate_roundtrip_evidence(payload)


def validate_source_schema_equivalence(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("connected") is not True:
        raise SourceBaselinePreflightError(
            f"source schema comparison failed: {payload.get('error', 'unknown error')}"
        )
    if payload.get("classification") != "structurally-equivalent":
        raise SourceBaselinePreflightError("source schema classification is not structurally-equivalent")
    if payload.get("modelTableCount") != 22 or payload.get("databaseTableCount") != 22:
        raise SourceBaselinePreflightError("source schema table baseline is not 22 / 22")
    if payload.get("differenceCount") != 0:
        raise SourceBaselinePreflightError("source schema difference count is not zero")
    return {
        "classification": payload["classification"],
        "modelTableCount": payload["modelTableCount"],
        "databaseTableCount": payload["databaseTableCount"],
        "differenceCount": payload["differenceCount"],
        "typeNormalization": payload.get("typeNormalization"),
    }


def inspect_readiness(
    root: Path,
    *,
    restore_evidence: dict[str, Any] | None = None,
    roundtrip_evidence: dict[str, Any] | None = None,
    source_raw: dict[str, Any] | None = None,
    rehearsal_raw: dict[str, Any] | None = None,
    migration_raw: dict[str, Any] | None = None,
    schema_raw: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    revision_path, manual_review, automated_review = reviewed_revision(root)
    try:
        verified_restore = (
            restore_evidence if restore_evidence is not None else load_verified_restore_evidence(root)
        )
        source = validate_source_state(
            source_raw if source_raw is not None else inspect_database(root, include_counts=True),
            verified_restore,
        )
        rehearsal = validate_rehearsal_state(
            rehearsal_raw
            if rehearsal_raw is not None
            else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
            verified_restore,
        )
    except MigrationTestDatabaseError as exc:
        raise SourceBaselinePreflightError(str(exc)) from exc

    if source.get("database") != SOURCE_DATABASE:
        raise SourceBaselinePreflightError("source database boundary mismatch")
    if source.get("alembicVersionTableExists") is not False:
        raise SourceBaselinePreflightError("source database already has alembic_version")
    if source.get("alembicCurrentRevisions") not in ([], (None,), None):
        raise SourceBaselinePreflightError("source database already records an Alembic revision")

    schema = validate_source_schema_equivalence(
        schema_raw if schema_raw is not None else collect_schema_equivalence(root)
    )
    roundtrip = validate_roundtrip_evidence(
        roundtrip_evidence
        if roundtrip_evidence is not None
        else load_verified_roundtrip_evidence(root)
    )

    try:
        migration = validate_migration_after(
            migration_raw
            if migration_raw is not None
            else inspect_named_database(root, MIGRATION_TEST_DATABASE),
            verified_restore["expectedTables"],
        )
    except MigrationUpgradeError as exc:
        raise SourceBaselinePreflightError(str(exc)) from exc

    roundtrip_after = roundtrip.get("migrationAfter") or {}
    if migration_signature(migration) != migration_signature(roundtrip_after):
        raise SourceBaselinePreflightError(
            "current migration DB does not match the verified v300 round-trip endpoint"
        )

    return {
        "toolVersion": TOOL_VERSION,
        "readOnly": True,
        "mutationExecuted": False,
        "result": READY_RESULT,
        "sourceDatabase": SOURCE_DATABASE,
        "source": source,
        "sourceSchema": schema,
        "rehearsal": rehearsal,
        "migration": migration,
        "revision": {
            "id": REVISION_ID,
            "relativePath": revision_path.relative_to(root).as_posix(),
            "sha256": REVISION_SHA256,
            "manualReview": manual_review["manualConclusion"],
            "automatedReview": automated_review["result"],
        },
        "verifiedBackup": {
            "relativePath": str(verified_restore.get("backupRelativePath")),
            "sha256": str(verified_restore.get("sha256")),
            "expectedTables": len(verified_restore["expectedTables"]),
            "expectedRows": verified_restore["expectedTotalRows"],
        },
        "roundTrip": {
            "result": roundtrip["result"],
            "equivalent": roundtrip["roundTripEquivalent"],
            "reportRelativePath": ROUNDTRIP_REPORT_RELATIVE_PATH.as_posix(),
        },
        "approvedMutation": None,
        "nextApprovalBoundary": "restore-rehearsal-rpg_game_restore_rehearsal_v290-stamp-head-only",
    }


def render_text(payload: dict[str, Any]) -> str:
    source = payload["source"]
    migration = payload["migration"]
    revision = payload["revision"]
    backup = payload["verifiedBackup"]
    return "\n".join(
        [
            "PostgreSQL source baseline stamp preflight (read-only)",
            "No stamp, upgrade, downgrade, revision generation, DB create/drop/restore, or row write was executed.",
            "",
            f"- source DB: {payload['sourceDatabase']}",
            f"- source tables/rows: {source.get('publicTableCount')}/{source.get('totalRows')}",
            f"- source alembic_version: {source.get('alembicVersionTableExists')}",
            f"- source schema: {payload['sourceSchema']['classification']} / differences={payload['sourceSchema']['differenceCount']}",
            f"- verified backup: {backup['relativePath']}",
            f"- backup SHA-256: {backup['sha256']}",
            f"- reviewed revision: {revision['id']}",
            f"- revision SHA-256: {revision['sha256']}",
            f"- isolated round-trip: {payload['roundTrip']['result']}",
            f"- migration test current revision: {migration.get('alembicCurrentRevisions')}",
            f"- migration test schema: {migration.get('schemaClassification')} / differences={migration.get('differenceCount')}",
            f"- result: {payload['result']}",
            "- next mutation must be a separate stamp rehearsal on the restored copy; the source DB remains unapproved.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when any readiness gate fails")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    try:
        payload = inspect_readiness(root)
        print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else render_text(payload))
        return 0
    except Exception as exc:
        payload = {
            "toolVersion": TOOL_VERSION,
            "readOnly": True,
            "mutationExecuted": False,
            "result": "blocked",
            "reason": f"{type(exc).__name__}: {exc}",
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("PostgreSQL source baseline stamp preflight (read-only)")
            print(f"- result: {payload['result']}")
            print(f"- reason: {payload['reason']}")
            print("- no DB schema/data mutation was executed.")
        return 1 if args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())

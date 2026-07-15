#!/usr/bin/env python3
"""Re-apply the reviewed revision after a verified downgrade round trip.

Approved mutation boundary for v300:
- MAY run exactly `alembic upgrade head` against
  `rpg_game_migration_empty_v290` after the verified v299 downgrade.
- MUST use the exact reviewed revision file/SHA-256.
- MUST compare the second upgrade result with the verified first v298 upgrade.
- MUST preserve `rpg_game` and `rpg_game_restore_rehearsal_v290` unchanged.
- MUST NOT edit `.env`, create/drop/restore databases, run downgrade/stamp,
  write seed data, or target the source/rehearsal databases.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from check_postgres_backup_restore_preflight import (
    MIGRATION_TEST_DATABASE,
    RESTORE_REHEARSAL_DATABASE,
)
from check_postgres_runtime_readonly_state import inspect_database
from create_postgres_migration_test_database import (
    MigrationTestDatabaseError,
    load_verified_restore_evidence,
    validate_rehearsal_state,
    validate_source_state,
)
from downgrade_postgres_migration_test_database import (
    DOWNGRADE_REPORT_RELATIVE_PATH,
    load_verified_upgrade_evidence,
)
from restore_postgres_rehearsal_database import inspect_named_database
from upgrade_postgres_migration_test_database import (
    REVISION_ID,
    REVISION_SHA256,
    MigrationUpgradeError,
    build_upgrade_command,
    reviewed_revision,
    run_upgrade_command,
    validate_migration_after,
    validate_migration_before,
)

TOOL_VERSION = "v300.postgres-migration-roundtrip-reupgrade-ready"
ROUNDTRIP_REPORT_RELATIVE_PATH = Path(
    "local-review-artifacts/alembic/v295_initial_schema.roundtrip-upgrade-v300.json"
)
DEFAULT_TIMEOUT_SECONDS = 300


class MigrationRoundTripError(RuntimeError):
    """Raised when round-trip re-upgrade safety gates or checks fail."""


def ensure_under(root: Path, path: Path) -> Path:
    root_resolved = root.resolve()
    resolved = path.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise MigrationRoundTripError(f"unsafe path outside project: {path}")
    return resolved


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.partial")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)



def validate_first_upgrade_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "result": "migration-test-database-upgraded-and-verified",
        "targetDatabase": MIGRATION_TEST_DATABASE,
        "revisionId": REVISION_ID,
        "revisionSha256": REVISION_SHA256,
        "upgradeExecuted": True,
        "downgradeExecuted": False,
        "stampExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise MigrationRoundTripError(
                f"v298 first-upgrade evidence mismatch: {key}={payload.get(key)!r}, expected={value!r}"
            )
    after = payload.get("migrationAfter") or {}
    if after.get("alembicCurrentRevisions") != [REVISION_ID]:
        raise MigrationRoundTripError("v298 first-upgrade report does not record the reviewed revision")
    if after.get("publicTableCount") != 23 or after.get("differenceCount") != 0:
        raise MigrationRoundTripError("v298 first-upgrade report postcondition is incomplete")
    if after.get("totalRows") != 1:
        raise MigrationRoundTripError("v298 first-upgrade report total row count is not 1")
    return payload


def validate_downgrade_evidence(payload: dict[str, Any]) -> dict[str, Any]:
    expected = {
        "result": "migration-test-database-downgraded-to-base-and-verified",
        "targetDatabase": MIGRATION_TEST_DATABASE,
        "revisionId": REVISION_ID,
        "revisionSha256": REVISION_SHA256,
        "upgradeExecuted": False,
        "downgradeExecuted": True,
        "stampExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise MigrationRoundTripError(
                f"v299 downgrade evidence mismatch: {key}={payload.get(key)!r}, expected={value!r}"
            )

    before = payload.get("migrationBefore") or {}
    after = payload.get("migrationAfter") or {}
    if before.get("alembicCurrentRevisions") != [REVISION_ID]:
        raise MigrationRoundTripError("v299 report does not start from the reviewed revision")
    if before.get("publicTableCount") != 23 or before.get("differenceCount") != 0:
        raise MigrationRoundTripError("v299 report pre-downgrade state is incomplete")
    if after.get("alembicCurrentRevisions") not in ([], ()):
        raise MigrationRoundTripError("v299 report still records an Alembic revision")
    if after.get("publicTables") != ["alembic_version"]:
        raise MigrationRoundTripError("v299 report does not end at the empty Alembic placeholder")
    if after.get("publicTableCount") != 1 or after.get("totalRows") != 0:
        raise MigrationRoundTripError("v299 report empty-workspace row/table counts are invalid")
    if after.get("differenceCount") != 22:
        raise MigrationRoundTripError("v299 report model difference count is not 22")
    return payload


def load_verified_downgrade_evidence(root: Path) -> dict[str, Any]:
    path = ensure_under(root, root / DOWNGRADE_REPORT_RELATIVE_PATH)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationRoundTripError(
            f"verified v299 downgrade report cannot be read: {path}: {exc}"
        ) from exc

    return validate_downgrade_evidence(payload)


def migration_signature(state: dict[str, Any]) -> dict[str, Any]:
    """Return stable schema/row fields used to compare both upgrade passes."""
    keys = (
        "database",
        "user",
        "publicTableCount",
        "publicTables",
        "tableCounts",
        "totalRows",
        "alembicVersionTableExists",
        "alembicCurrentRevisions",
        "differenceCount",
        "schemaClassification",
    )
    return {key: state.get(key) for key in keys}


def execute_roundtrip_upgrade(
    root: Path,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    restore_evidence: dict[str, Any] | None = None,
    first_upgrade_evidence: dict[str, Any] | None = None,
    downgrade_evidence: dict[str, Any] | None = None,
    source_before_raw: dict[str, Any] | None = None,
    source_after_raw: dict[str, Any] | None = None,
    rehearsal_before_raw: dict[str, Any] | None = None,
    rehearsal_after_raw: dict[str, Any] | None = None,
    migration_before_raw: dict[str, Any] | None = None,
    migration_after_raw: dict[str, Any] | None = None,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    root = root.resolve()
    revision_path, manual_review, automated_review = reviewed_revision(root)
    verified_first_upgrade = validate_first_upgrade_evidence(
        first_upgrade_evidence
        if first_upgrade_evidence is not None
        else load_verified_upgrade_evidence(root)
    )
    verified_downgrade = validate_downgrade_evidence(
        downgrade_evidence
        if downgrade_evidence is not None
        else load_verified_downgrade_evidence(root)
    )

    try:
        verified_restore = (
            restore_evidence
            if restore_evidence is not None
            else load_verified_restore_evidence(root)
        )
        source_before = validate_source_state(
            source_before_raw
            if source_before_raw is not None
            else inspect_database(root, include_counts=True),
            verified_restore,
        )
        rehearsal_before = validate_rehearsal_state(
            rehearsal_before_raw
            if rehearsal_before_raw is not None
            else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
            verified_restore,
        )
    except MigrationTestDatabaseError as exc:
        raise MigrationRoundTripError(str(exc)) from exc

    try:
        migration_before = validate_migration_before(
            migration_before_raw
            if migration_before_raw is not None
            else inspect_named_database(root, MIGRATION_TEST_DATABASE)
        )
    except MigrationUpgradeError as exc:
        raise MigrationRoundTripError(str(exc)) from exc

    if migration_signature(migration_before) != migration_signature(
        verified_downgrade.get("migrationAfter") or {}
    ):
        raise MigrationRoundTripError(
            "current migration DB does not match the verified v299 downgrade endpoint"
        )

    command_output = run_upgrade_command(root, timeout=timeout, run_process=run_process)

    try:
        source_after = validate_source_state(
            source_after_raw
            if source_after_raw is not None
            else inspect_database(root, include_counts=True),
            verified_restore,
        )
        rehearsal_after = validate_rehearsal_state(
            rehearsal_after_raw
            if rehearsal_after_raw is not None
            else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
            verified_restore,
        )
    except MigrationTestDatabaseError as exc:
        raise MigrationRoundTripError(str(exc)) from exc

    try:
        migration_after = validate_migration_after(
            migration_after_raw
            if migration_after_raw is not None
            else inspect_named_database(root, MIGRATION_TEST_DATABASE),
            verified_restore["expectedTables"],
        )
    except MigrationUpgradeError as exc:
        raise MigrationRoundTripError(str(exc)) from exc

    first_upgrade_after = verified_first_upgrade.get("migrationAfter") or {}
    first_signature = migration_signature(first_upgrade_after)
    second_signature = migration_signature(migration_after)
    if second_signature != first_signature:
        raise MigrationRoundTripError(
            "second upgrade result differs from the verified first v298 upgrade result"
        )
    if source_before != source_after:
        raise MigrationRoundTripError("source DB changed during round-trip re-upgrade")
    if rehearsal_before != rehearsal_after:
        raise MigrationRoundTripError("restore rehearsal DB changed during round-trip re-upgrade")

    report_path = ensure_under(root, root / ROUNDTRIP_REPORT_RELATIVE_PATH)
    result = {
        "toolVersion": TOOL_VERSION,
        "result": "migration-test-database-roundtrip-upgraded-and-verified",
        "targetDatabase": MIGRATION_TEST_DATABASE,
        "revisionId": REVISION_ID,
        "revisionRelativePath": revision_path.relative_to(root).as_posix(),
        "revisionSha256": REVISION_SHA256,
        "manualReview": {
            "result": manual_review["reviewResult"],
            "conclusion": manual_review["manualConclusion"],
        },
        "automatedReview": automated_review,
        "verifiedFirstUpgradeReport": {
            "result": verified_first_upgrade["result"],
            "revisionId": verified_first_upgrade["revisionId"],
            "revisionSha256": verified_first_upgrade["revisionSha256"],
        },
        "verifiedDowngradeReport": {
            "result": verified_downgrade["result"],
            "revisionId": verified_downgrade["revisionId"],
            "revisionSha256": verified_downgrade["revisionSha256"],
        },
        "alembicCommand": build_upgrade_command()[1:],
        "alembicCommandOutput": command_output,
        "sourceBefore": source_before,
        "sourceAfter": source_after,
        "rehearsalBefore": rehearsal_before,
        "rehearsalAfter": rehearsal_after,
        "migrationBefore": migration_before,
        "migrationAfter": migration_after,
        "firstUpgradeSignature": first_signature,
        "secondUpgradeSignature": second_signature,
        "roundTripEquivalent": True,
        "upgradeExecuted": True,
        "downgradeExecutedInThisStep": False,
        "stampExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
    }
    write_json_atomic(report_path, result)
    result["reportRelativePath"] = report_path.relative_to(root).as_posix()
    return result


def inspect_readiness(root: Path) -> dict[str, Any]:
    revision_path, manual_review, automated_review = reviewed_revision(root)
    first_upgrade = validate_first_upgrade_evidence(load_verified_upgrade_evidence(root))
    downgrade = validate_downgrade_evidence(load_verified_downgrade_evidence(root))
    restore = load_verified_restore_evidence(root)
    source = validate_source_state(inspect_database(root, include_counts=True), restore)
    rehearsal = validate_rehearsal_state(
        inspect_named_database(root, RESTORE_REHEARSAL_DATABASE), restore
    )
    try:
        migration = validate_migration_before(
            inspect_named_database(root, MIGRATION_TEST_DATABASE)
        )
    except MigrationUpgradeError as exc:
        raise MigrationRoundTripError(str(exc)) from exc
    if migration_signature(migration) != migration_signature(
        downgrade.get("migrationAfter") or {}
    ):
        raise MigrationRoundTripError(
            "current migration DB does not match the verified v299 downgrade endpoint"
        )
    return {
        "ready": True,
        "revision": revision_path.relative_to(root).as_posix(),
        "revisionSha256": REVISION_SHA256,
        "manualReview": manual_review["manualConclusion"],
        "automatedReview": automated_review["result"],
        "firstUpgradeEvidence": first_upgrade["result"],
        "downgradeEvidence": downgrade["result"],
        "source": source,
        "rehearsal": rehearsal,
        "migration": migration,
    }


def render_inspection(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "PostgreSQL migration round-trip re-upgrade readiness (read-only)",
            f"- target DB: {MIGRATION_TEST_DATABASE}",
            f"- revision: {REVISION_ID}",
            f"- revision SHA-256: {result['revisionSha256']}",
            f"- verified first upgrade: {result['firstUpgradeEvidence']}",
            f"- verified downgrade: {result['downgradeEvidence']}",
            f"- migration tables: {result['migration'].get('publicTables')}",
            f"- recorded revisions: {result['migration'].get('alembicCurrentRevisions')}",
            "- result: ready-for-approved-roundtrip-reupgrade",
            "- no DB schema/data mutation was executed.",
        ]
    )


def render_success(result: dict[str, Any]) -> str:
    after = result["migrationAfter"]
    return "\n".join(
        [
            "PostgreSQL isolated migration round-trip re-upgrade",
            "The reviewed revision was re-applied only to the isolated migration DB.",
            "",
            f"- result: {result['result']}",
            f"- target DB: {result['targetDatabase']}",
            f"- revision: {result['revisionId']}",
            f"- revision SHA-256: {result['revisionSha256']}",
            f"- target public tables: {after.get('publicTableCount')}",
            "- target model tables: 22",
            f"- target total rows including Alembic control row: {after.get('totalRows')}",
            f"- target current revision: {after.get('alembicCurrentRevisions')}",
            f"- target schema: {after.get('schemaClassification')} / differences={after.get('differenceCount')}",
            "- first/second upgrade signatures: identical",
            "- round-trip sequence: upgrade -> downgrade base -> upgrade verified",
            "- source tables/rows preserved: 22/748",
            "- rehearsal tables/rows preserved: 22/748",
            f"- verification report: {result['reportRelativePath']}",
            "- downgrade in this step, stamp, DB create/drop/restore, .env/Docker changes, and source writes were not executed.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--inspect", action="store_true", help="Read-only round-trip readiness inspection")
    group.add_argument("--execute", action="store_true", help="Re-apply upgrade head to the isolated migration DB")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    try:
        if args.inspect:
            print(render_inspection(inspect_readiness(root)))
            return 0
        if not args.execute:
            print("PostgreSQL isolated migration round-trip re-upgrade - execution guard")
            print(f"- target DB: {MIGRATION_TEST_DATABASE}")
            print(f"- approved revision: {REVISION_ID}")
            print("- --execute is required; no DB mutation was attempted.")
            return 2
        result = execute_roundtrip_upgrade(root, timeout=args.timeout)
        print(render_success(result))
        return 0
    except Exception as exc:
        print("PostgreSQL isolated migration round-trip re-upgrade")
        print("- result: blocked-or-failed")
        print(f"- reason: {type(exc).__name__}: {exc}")
        print("- no automatic retry, downgrade, stamp, DB create/drop/restore, or source mutation was attempted.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

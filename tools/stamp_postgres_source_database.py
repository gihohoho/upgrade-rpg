#!/usr/bin/env python3
"""Guard and verify the final Alembic baseline stamp on the source PostgreSQL DB.

v304 is intentionally split into two approval boundaries:

1. ``--inspect`` is fully read-only and proves that the exact source database
   ``rpg_game`` is still the approved 22-table / 748-row application snapshot,
   the reviewed revision and backup are unchanged, the restored rehearsal copy
   is already stamped and verified, and the isolated migration DB still matches
   the verified v300 round-trip endpoint.
2. ``--execute`` exists behind exact target/revision/backup/rehearsal
   confirmations, but it must not be run until the user separately approves the
   source mutation. Its only allowed mutation is ``alembic stamp head`` against
   ``rpg_game``. It must preserve every application schema/data digest and leave
   the rehearsal and migration databases unchanged.

Inspection never runs subprocesses, stamp, upgrade, downgrade, DB
create/drop/restore, or row writes.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from sqlalchemy.engine import make_url

from _safe_subprocess import decode_output
from check_postgres_backup_restore_preflight import (
    MIGRATION_TEST_DATABASE,
    RESTORE_REHEARSAL_DATABASE,
    SOURCE_DATABASE,
)
from check_postgres_runtime_readonly_state import inspect_database, load_backend_objects
from check_postgres_schema_equivalence import collect as collect_schema_equivalence
from check_postgres_source_baseline_stamp_preflight import (
    load_verified_roundtrip_evidence,
    validate_source_schema_equivalence,
)
from create_postgres_migration_test_database import (
    MigrationTestDatabaseError,
    load_verified_restore_evidence,
    sanitize_database_state,
    validate_source_state,
)
from create_postgres_restore_rehearsal_database import (
    APPROVED_BACKUP_SHA256,
    SOURCE_DATABASE_USER,
)
from restore_postgres_rehearsal_database import inspect_named_database
from reupgrade_postgres_migration_test_database import migration_signature
from stamp_postgres_restore_rehearsal_database import (
    APPROVED_PRE_STAMP_DATA_DIGEST,
    APPROVED_PRE_STAMP_SCHEMA_DIGEST,
    POST_STAMP_VERIFIED_RESULT as REHEARSAL_POST_STAMP_VERIFIED_RESULT,
    SUCCESS_RESULT as REHEARSAL_STAMP_SUCCESS_RESULT,
    STAMP_REPORT_RELATIVE_PATH as REHEARSAL_STAMP_REPORT_RELATIVE_PATH,
    collect_database_integrity_signature,
    load_existing_stamp_report as load_rehearsal_stamp_report,
    model_table_integrity_signature,
    validate_existing_stamp_report as validate_rehearsal_stamp_report,
    validate_rehearsal_after,
    write_json_atomic,
)
from upgrade_postgres_migration_test_database import (
    REVISION_ID,
    REVISION_SHA256,
    MigrationUpgradeError,
    reviewed_revision,
    validate_migration_after,
)

TOOL_VERSION = "v304.postgres-source-baseline-stamp-final-guard"
READY_RESULT = "ready-for-separate-source-baseline-stamp-execution-approval"
SUCCESS_RESULT = "source-baseline-stamped-and-verified"
POST_STAMP_VERIFIED_RESULT = "source-baseline-stamp-current-state-verified"
POST_STAMP_REPORT_MISSING_RESULT = (
    "source-baseline-stamp-current-state-verified-report-missing"
)
SOURCE_STAMP_REPORT_RELATIVE_PATH = Path(
    "local-review-artifacts/alembic/v295_initial_schema.source-stamp-v304.json"
)
DEFAULT_TIMEOUT_SECONDS = 120


class SourceBaselineStampError(RuntimeError):
    """Raised when a source stamp safety gate or postcondition fails."""


def ensure_under(root: Path, path: Path) -> Path:
    root_resolved = root.resolve()
    resolved = path.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise SourceBaselineStampError(f"unsafe path outside project: {path}")
    return resolved


def source_database_url(root: Path) -> str:
    settings, _ = load_backend_objects(root)
    source_url = make_url(settings.database_url)
    if source_url.database != SOURCE_DATABASE:
        raise SourceBaselineStampError(
            f"configured source DB mismatch: expected={SOURCE_DATABASE}, actual={source_url.database}"
        )
    return source_url.render_as_string(hide_password=False)


def build_stamp_command() -> list[str]:
    return [
        sys.executable,
        "-m",
        "alembic",
        "--config",
        "alembic.ini",
        "stamp",
        "head",
    ]


def run_stamp_command(
    root: Path,
    *,
    timeout: int,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> str:
    backend = root / "backend"
    env = os.environ.copy()
    env["DATABASE_URL"] = source_database_url(root)
    env["PYTHONPATH"] = str(backend.resolve()) + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        completed = run_process(
            build_stamp_command(),
            cwd=backend,
            env=env,
            text=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise SourceBaselineStampError(
            f"Alembic source stamp timed out after {timeout} seconds; no retry was attempted"
        ) from exc
    output = decode_output(completed.stdout).strip()
    if completed.returncode != 0:
        raise SourceBaselineStampError(
            f"Alembic source stamp failed with exit={completed.returncode}: "
            f"{output or 'no output'}"
        )
    return output


def validate_source_after(
    state: dict[str, Any], evidence: dict[str, Any]
) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise SourceBaselineStampError(
            f"post-stamp source connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != SOURCE_DATABASE:
        raise SourceBaselineStampError("post-stamp source database boundary mismatch")
    if state.get("user") != SOURCE_DATABASE_USER:
        raise SourceBaselineStampError("post-stamp source user boundary mismatch")

    expected_tables = sorted((*evidence["expectedTables"], "alembic_version"))
    observed_tables = sorted(str(item) for item in (state.get("publicTables") or []))
    if observed_tables != expected_tables or state.get("publicTableCount") != 23:
        raise SourceBaselineStampError(
            "post-stamp source table set is not 22 application tables + alembic_version"
        )

    expected_counts = dict(evidence["expectedTableCounts"])
    expected_counts["alembic_version"] = 1
    observed_counts = {
        str(name): int(value) for name, value in (state.get("tableCounts") or {}).items()
    }
    if dict(sorted(observed_counts.items())) != dict(sorted(expected_counts.items())):
        raise SourceBaselineStampError("post-stamp source table row counts changed unexpectedly")
    if state.get("totalRows") != evidence["expectedTotalRows"] + 1:
        raise SourceBaselineStampError("post-stamp source rows must be 748 + one Alembic row")
    if state.get("alembicVersionTableExists") is not True:
        raise SourceBaselineStampError("post-stamp source alembic_version table is missing")
    if state.get("alembicCurrentRevisions") != [REVISION_ID]:
        raise SourceBaselineStampError(
            f"post-stamp source revision mismatch: {state.get('alembicCurrentRevisions')}"
        )
    if state.get("classification") != "alembic-managed":
        raise SourceBaselineStampError("post-stamp source classification is not alembic-managed")
    if state.get("missingModelTables") or state.get("extraPublicTables"):
        raise SourceBaselineStampError("post-stamp source model/public boundary changed")
    return sanitize_database_state(state)


def load_source_stamp_report(root: Path) -> dict[str, Any] | None:
    path = ensure_under(root, root / SOURCE_STAMP_REPORT_RELATIVE_PATH)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceBaselineStampError(
            f"existing v304 source stamp report cannot be read: {path}: {exc}"
        ) from exc


def validate_source_stamp_report(payload: dict[str, Any]) -> dict[str, Any]:
    required = {
        "result": SUCCESS_RESULT,
        "targetDatabase": SOURCE_DATABASE,
        "revisionId": REVISION_ID,
        "revisionSha256": REVISION_SHA256,
        "verifiedBackupSha256": APPROVED_BACKUP_SHA256,
        "verifiedRehearsalResult": REHEARSAL_POST_STAMP_VERIFIED_RESULT,
        "stampExecuted": True,
        "upgradeExecuted": False,
        "downgradeExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
        "rehearsalDatabaseMutationExecuted": False,
        "migrationDatabaseMutationExecuted": False,
    }
    for key, expected in required.items():
        if payload.get(key) != expected:
            raise SourceBaselineStampError(
                f"v304 source stamp report mismatch: {key}={payload.get(key)!r}, "
                f"expected={expected!r}"
            )
    if payload.get("sourceModelIntegrityBefore") != payload.get(
        "sourceModelIntegrityAfter"
    ):
        raise SourceBaselineStampError("v304 report source application integrity changed")
    if payload.get("rehearsalBefore") != payload.get("rehearsalAfter"):
        raise SourceBaselineStampError("v304 report rehearsal before/after differs")
    if payload.get("migrationBefore") != payload.get("migrationAfter"):
        raise SourceBaselineStampError("v304 report migration before/after differs")
    if payload.get("rehearsalIntegrityBefore") != payload.get(
        "rehearsalIntegrityAfter"
    ):
        raise SourceBaselineStampError("v304 report rehearsal integrity before/after differs")
    if payload.get("migrationIntegrityBefore") != payload.get(
        "migrationIntegrityAfter"
    ):
        raise SourceBaselineStampError("v304 report migration integrity before/after differs")
    return payload


def validate_rehearsal_and_migration(
    root: Path,
    *,
    verified: dict[str, Any],
    rehearsal_raw: dict[str, Any] | None,
    migration_raw: dict[str, Any] | None,
    rehearsal_integrity: dict[str, Any] | None,
    migration_integrity: dict[str, Any] | None,
    roundtrip_evidence: dict[str, Any] | None,
    rehearsal_report: dict[str, Any] | None | object,
    approved_schema_digest: str,
    approved_data_digest: str,
) -> dict[str, Any]:
    rehearsal = validate_rehearsal_after(
        rehearsal_raw
        if rehearsal_raw is not None
        else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
        verified,
    )
    roundtrip = roundtrip_evidence or load_verified_roundtrip_evidence(root)
    try:
        migration = validate_migration_after(
            migration_raw
            if migration_raw is not None
            else inspect_named_database(root, MIGRATION_TEST_DATABASE),
            verified["expectedTables"],
        )
    except MigrationUpgradeError as exc:
        raise SourceBaselineStampError(str(exc)) from exc
    if migration_signature(migration) != migration_signature(
        roundtrip.get("migrationAfter") or {}
    ):
        raise SourceBaselineStampError(
            "current migration DB does not match the verified v300 round-trip endpoint"
        )

    rehearsal_sig = rehearsal_integrity or collect_database_integrity_signature(
        root, RESTORE_REHEARSAL_DATABASE
    )
    migration_sig = migration_integrity or collect_database_integrity_signature(
        root, MIGRATION_TEST_DATABASE
    )
    rehearsal_model = model_table_integrity_signature(
        rehearsal_sig, verified["expectedTables"]
    )
    if rehearsal_model["tableCount"] != 22 or rehearsal_model["rowCount"] != 748:
        raise SourceBaselineStampError(
            "rehearsal application integrity baseline is not 22 tables / 748 rows"
        )
    if rehearsal_model["schemaDigest"] != approved_schema_digest:
        raise SourceBaselineStampError(
            "rehearsal application schema digest differs from approved v302 digest"
        )
    if rehearsal_model["dataDigest"] != approved_data_digest:
        raise SourceBaselineStampError(
            "rehearsal application data digest differs from approved v302 digest"
        )

    if rehearsal_report is ...:
        existing_report = load_rehearsal_stamp_report(root)
    else:
        existing_report = rehearsal_report
    if existing_report is None:
        raise SourceBaselineStampError(
            "verified v302 rehearsal stamp report is required before source stamp planning"
        )
    report = validate_rehearsal_stamp_report(existing_report)
    if report.get("rehearsalAfter") != rehearsal:
        raise SourceBaselineStampError(
            "current rehearsal state differs from the verified v302 report"
        )
    if report.get("rehearsalModelIntegrityAfter") != rehearsal_model:
        raise SourceBaselineStampError(
            "current rehearsal application integrity differs from the verified v302 report"
        )
    if report.get("migrationAfter") != migration:
        raise SourceBaselineStampError(
            "current migration state differs from the verified v302 report"
        )
    if report.get("migrationIntegrityAfter") != migration_sig:
        raise SourceBaselineStampError(
            "current migration integrity differs from the verified v302 report"
        )

    return {
        "result": REHEARSAL_POST_STAMP_VERIFIED_RESULT,
        "reportStatus": "verified",
        "reportRelativePath": REHEARSAL_STAMP_REPORT_RELATIVE_PATH.as_posix(),
        "rehearsal": rehearsal,
        "rehearsalIntegrity": rehearsal_sig,
        "rehearsalModelIntegrity": rehearsal_model,
        "migration": migration,
        "migrationIntegrity": migration_sig,
    }


def inspect_readiness(
    root: Path,
    *,
    evidence: dict[str, Any] | None = None,
    source_raw: dict[str, Any] | None = None,
    rehearsal_raw: dict[str, Any] | None = None,
    migration_raw: dict[str, Any] | None = None,
    schema_raw: dict[str, Any] | None = None,
    source_integrity: dict[str, Any] | None = None,
    rehearsal_integrity: dict[str, Any] | None = None,
    migration_integrity: dict[str, Any] | None = None,
    roundtrip_evidence: dict[str, Any] | None = None,
    rehearsal_report: dict[str, Any] | None | object = ...,
    source_report: dict[str, Any] | None | object = ...,
    approved_schema_digest: str = APPROVED_PRE_STAMP_SCHEMA_DIGEST,
    approved_data_digest: str = APPROVED_PRE_STAMP_DATA_DIGEST,
) -> dict[str, Any]:
    """Read-only pre/post inspection for the exact source baseline stamp."""
    root = root.resolve()
    revision_path, manual_review, automated_review = reviewed_revision(root)
    try:
        verified = evidence if evidence is not None else load_verified_restore_evidence(root)
    except MigrationTestDatabaseError as exc:
        raise SourceBaselineStampError(str(exc)) from exc

    raw_source = (
        source_raw
        if source_raw is not None
        else inspect_database(root, include_counts=True)
    )
    if raw_source.get("alembicVersionTableExists") is False:
        try:
            source = validate_source_state(raw_source, verified)
        except MigrationTestDatabaseError as exc:
            raise SourceBaselineStampError(str(exc)) from exc
        lifecycle_state = "pre-stamp"
        result_value = READY_RESULT
    elif raw_source.get("alembicVersionTableExists") is True:
        source = validate_source_after(raw_source, verified)
        lifecycle_state = "post-stamp"
        result_value = POST_STAMP_VERIFIED_RESULT
    else:
        raise SourceBaselineStampError("source Alembic lifecycle state is ambiguous")

    source_schema = validate_source_schema_equivalence(
        schema_raw if schema_raw is not None else collect_schema_equivalence(root)
    )
    related = validate_rehearsal_and_migration(
        root,
        verified=verified,
        rehearsal_raw=rehearsal_raw,
        migration_raw=migration_raw,
        rehearsal_integrity=rehearsal_integrity,
        migration_integrity=migration_integrity,
        roundtrip_evidence=roundtrip_evidence,
        rehearsal_report=rehearsal_report,
        approved_schema_digest=approved_schema_digest,
        approved_data_digest=approved_data_digest,
    )

    source_sig = source_integrity or collect_database_integrity_signature(
        root, SOURCE_DATABASE
    )
    source_model = model_table_integrity_signature(
        source_sig, verified["expectedTables"]
    )
    if source_model["tableCount"] != 22 or source_model["rowCount"] != 748:
        raise SourceBaselineStampError(
            "source application integrity baseline is not 22 tables / 748 rows"
        )
    if source_model["schemaDigest"] != approved_schema_digest:
        raise SourceBaselineStampError(
            "source application schema digest differs from approved v302 digest"
        )
    if source_model["dataDigest"] != approved_data_digest:
        raise SourceBaselineStampError(
            "source application data digest differs from approved v302 digest"
        )
    if source_model != related["rehearsalModelIntegrity"]:
        raise SourceBaselineStampError(
            "source and verified rehearsal application integrity signatures differ"
        )

    if source_report is ...:
        existing_source_report = load_source_stamp_report(root)
    else:
        existing_source_report = source_report
    source_report_status = "not-applicable"
    if lifecycle_state == "pre-stamp":
        if existing_source_report is not None:
            raise SourceBaselineStampError(
                "v304 source stamp report exists while source DB is still pre-stamp"
            )
    else:
        if existing_source_report is None:
            source_report_status = "missing"
            result_value = POST_STAMP_REPORT_MISSING_RESULT
        else:
            report = validate_source_stamp_report(existing_source_report)
            if report.get("sourceAfter") != source:
                raise SourceBaselineStampError(
                    "current source state differs from the verified v304 report"
                )
            if report.get("sourceIntegrityAfter") != source_sig:
                raise SourceBaselineStampError(
                    "current source integrity differs from the verified v304 report"
                )
            if report.get("sourceModelIntegrityAfter") != source_model:
                raise SourceBaselineStampError(
                    "current source application integrity differs from the v304 report"
                )
            if report.get("rehearsalAfter") != related["rehearsal"]:
                raise SourceBaselineStampError(
                    "current rehearsal state differs from the verified v304 report"
                )
            if report.get("migrationAfter") != related["migration"]:
                raise SourceBaselineStampError(
                    "current migration state differs from the verified v304 report"
                )
            source_report_status = "verified"

    return {
        "toolVersion": TOOL_VERSION,
        "result": result_value,
        "readOnly": True,
        "mutationExecuted": False,
        "lifecycleState": lifecycle_state,
        "targetDatabase": SOURCE_DATABASE,
        "revisionId": REVISION_ID,
        "revisionRelativePath": revision_path.relative_to(root).as_posix(),
        "revisionSha256": REVISION_SHA256,
        "manualReview": manual_review["manualConclusion"],
        "automatedReview": automated_review["result"],
        "verifiedBackup": {
            "relativePath": str(verified.get("backupRelativePath")),
            "sha256": str(verified.get("sha256")),
            "expectedTables": len(verified["expectedTables"]),
            "expectedRows": verified["expectedTotalRows"],
        },
        "sourceSchema": source_schema,
        "source": source,
        "sourceIntegrity": source_sig,
        "sourceModelIntegrity": source_model,
        "approvedApplicationDigests": {
            "schemaDigest": approved_schema_digest,
            "dataDigest": approved_data_digest,
        },
        "rehearsalVerification": related,
        "sourceStampReportStatus": source_report_status,
        "sourceStampReportRelativePath": SOURCE_STAMP_REPORT_RELATIVE_PATH.as_posix(),
        "plannedAlembicCommand": build_stamp_command()[1:],
        "allowedPostcondition": {
            "applicationTables": 22,
            "applicationRows": 748,
            "newControlTable": "alembic_version",
            "newControlRows": 1,
            "recordedRevision": REVISION_ID,
            "publicTablesAfter": 23,
            "totalRowsAfter": 749,
        },
        "executionApproved": False,
        "nextApprovalBoundary": (
            "explicit-v304-source-rpg_game-stamp-head-approval"
            if lifecycle_state == "pre-stamp"
            else "review-source-post-stamp-evidence-without-retry"
        ),
    }


def execute_stamp(
    root: Path,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    before_inspection: dict[str, Any] | None = None,
    after_inspection: dict[str, Any] | None = None,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
    report_path: Path | None = None,
) -> dict[str, Any]:
    """Execute the exact source stamp after a separate explicit approval."""
    root = root.resolve()
    existing_report = load_source_stamp_report(root)
    if existing_report is not None:
        raise SourceBaselineStampError(
            "v304 source stamp report already exists; source stamp will not be repeated"
        )

    before = before_inspection or inspect_readiness(root)
    if before.get("result") != READY_RESULT or before.get("lifecycleState") != "pre-stamp":
        raise SourceBaselineStampError("source is not in the approved pre-stamp state")
    if before.get("executionApproved") is not False:
        raise SourceBaselineStampError("read-only guard unexpectedly approved execution")

    command_output = run_stamp_command(
        root, timeout=timeout, run_process=run_process
    )

    after = after_inspection or inspect_readiness(root, source_report=None)
    if after.get("lifecycleState") != "post-stamp":
        raise SourceBaselineStampError("source did not reach the expected post-stamp state")
    if after.get("result") not in {
        POST_STAMP_VERIFIED_RESULT,
        POST_STAMP_REPORT_MISSING_RESULT,
    }:
        raise SourceBaselineStampError("source post-stamp current state was not verified")
    if before.get("sourceModelIntegrity") != after.get("sourceModelIntegrity"):
        raise SourceBaselineStampError(
            "source application schema/data integrity changed during stamp"
        )

    before_related = before["rehearsalVerification"]
    after_related = after["rehearsalVerification"]
    for key in ("rehearsal", "rehearsalIntegrity", "migration", "migrationIntegrity"):
        if before_related.get(key) != after_related.get(key):
            raise SourceBaselineStampError(
                f"{key} changed during source stamp"
            )

    revision_path, manual_review, automated_review = reviewed_revision(root)
    result = {
        "toolVersion": TOOL_VERSION,
        "result": SUCCESS_RESULT,
        "targetDatabase": SOURCE_DATABASE,
        "revisionId": REVISION_ID,
        "revisionRelativePath": revision_path.relative_to(root).as_posix(),
        "revisionSha256": REVISION_SHA256,
        "manualReview": manual_review["manualConclusion"],
        "automatedReview": automated_review["result"],
        "verifiedBackupSha256": APPROVED_BACKUP_SHA256,
        "verifiedRehearsalResult": REHEARSAL_POST_STAMP_VERIFIED_RESULT,
        "alembicCommand": build_stamp_command()[1:],
        "alembicCommandOutput": command_output,
        "sourceBefore": before["source"],
        "sourceAfter": after["source"],
        "sourceIntegrityBefore": before["sourceIntegrity"],
        "sourceIntegrityAfter": after["sourceIntegrity"],
        "sourceModelIntegrityBefore": before["sourceModelIntegrity"],
        "sourceModelIntegrityAfter": after["sourceModelIntegrity"],
        "rehearsalBefore": before_related["rehearsal"],
        "rehearsalAfter": after_related["rehearsal"],
        "rehearsalIntegrityBefore": before_related["rehearsalIntegrity"],
        "rehearsalIntegrityAfter": after_related["rehearsalIntegrity"],
        "migrationBefore": before_related["migration"],
        "migrationAfter": after_related["migration"],
        "migrationIntegrityBefore": before_related["migrationIntegrity"],
        "migrationIntegrityAfter": after_related["migrationIntegrity"],
        "stampExecuted": True,
        "upgradeExecuted": False,
        "downgradeExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
        "rehearsalDatabaseMutationExecuted": False,
        "migrationDatabaseMutationExecuted": False,
    }
    destination = ensure_under(
        root,
        report_path if report_path is not None else root / SOURCE_STAMP_REPORT_RELATIVE_PATH,
    )
    write_json_atomic(destination, result)
    result["reportRelativePath"] = destination.relative_to(root).as_posix()
    return result


def render_inspection(result: dict[str, Any]) -> str:
    source = result["source"]
    model = result["sourceModelIntegrity"]
    backup = result["verifiedBackup"]
    rehearsal = result["rehearsalVerification"]
    rehearsal_state = rehearsal["rehearsal"]
    migration = rehearsal["migration"]
    title = (
        "PostgreSQL source baseline stamp final guard (read-only inspection)"
        if result["lifecycleState"] == "pre-stamp"
        else "PostgreSQL source baseline stamp post-check (read-only)"
    )
    lines = [
        title,
        "No stamp, retry, rollback, upgrade, downgrade, DB create/drop/restore, or row write was executed.",
        "",
        f"- lifecycle state: {result['lifecycleState']}",
        f"- exact target DB: {result['targetDatabase']}",
        f"- exact revision: {result['revisionId']}",
        f"- revision SHA-256: {result['revisionSha256']}",
        f"- source public tables/rows: {source.get('publicTableCount')}/{source.get('totalRows')}",
        f"- source current revision: {source.get('alembicCurrentRevisions')}",
        f"- source application tables/rows: {model['tableCount']}/{model['rowCount']}",
        f"- source application schema digest: {model['schemaDigest']}",
        f"- source application data digest: {model['dataDigest']}",
        f"- verified backup: {backup['relativePath']}",
        f"- backup SHA-256: {backup['sha256']}",
        f"- rehearsal post-stamp: {rehearsal['reportStatus']} / "
        f"{rehearsal_state.get('publicTableCount')}/{rehearsal_state.get('totalRows')}",
        f"- migration test current revision: {migration.get('alembicCurrentRevisions')}",
        "- source/rehearsal application digests identical: yes",
    ]
    if result["lifecycleState"] == "pre-stamp":
        lines.extend(
            [
                "- allowed mutation: alembic_version table 1 + revision row 1 only",
                f"- planned command: {' '.join(result['plannedAlembicCommand'])}",
                f"- result: {result['result']}",
                "- actual source stamp still requires separate user approval and exact confirmation flags.",
            ]
        )
    else:
        lines.extend(
            [
                f"- v304 execution report: {result['sourceStampReportStatus']}",
                f"- result: {result['result']}",
                "- do not retry source stamp; review this post-check result first.",
            ]
        )
    return "\n".join(lines)


def render_success(result: dict[str, Any]) -> str:
    after = result["sourceAfter"]
    model = result["sourceModelIntegrityAfter"]
    return "\n".join(
        [
            "PostgreSQL source baseline stamp",
            "The Alembic baseline was stamped only on the exact source database.",
            "",
            f"- result: {result['result']}",
            f"- target DB: {result['targetDatabase']}",
            f"- revision: {result['revisionId']}",
            f"- revision SHA-256: {result['revisionSha256']}",
            f"- public tables/rows after: {after.get('publicTableCount')}/{after.get('totalRows')}",
            f"- current revision: {after.get('alembicCurrentRevisions')}",
            f"- application schema/data digest preserved: {model['combinedDigest']}",
            "- rehearsal DB preserved: yes",
            "- migration test DB preserved: yes",
            f"- verification report: {result['reportRelativePath']}",
            "- upgrade, downgrade, DB create/drop/restore, .env/Docker, seed, auth, API, and application writes were not executed.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--inspect", action="store_true", help="Read-only source pre/post verification")
    group.add_argument("--execute", action="store_true", help="Stamp only the exact source DB")
    parser.add_argument("--confirm-target", default="")
    parser.add_argument("--confirm-revision", default="")
    parser.add_argument("--confirm-backup-sha256", default="")
    parser.add_argument("--confirm-rehearsal-result", default="")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    try:
        if args.inspect:
            print(render_inspection(inspect_readiness(root)))
            return 0
        if not args.execute:
            print("PostgreSQL source baseline stamp - final execution guard")
            print(f"- exact target DB: {SOURCE_DATABASE}")
            print(f"- exact revision: {REVISION_ID}")
            print(f"- exact backup SHA-256: {APPROVED_BACKUP_SHA256}")
            print(f"- required rehearsal result: {REHEARSAL_POST_STAMP_VERIFIED_RESULT}")
            print("- --inspect is safe; --execute requires separate approval and every exact confirmation.")
            print("- no DB mutation was attempted.")
            return 2
        if args.confirm_target != SOURCE_DATABASE:
            raise SourceBaselineStampError(
                f"exact target confirmation required: --confirm-target {SOURCE_DATABASE}"
            )
        if args.confirm_revision != REVISION_ID:
            raise SourceBaselineStampError(
                f"exact revision confirmation required: --confirm-revision {REVISION_ID}"
            )
        if args.confirm_backup_sha256 != APPROVED_BACKUP_SHA256:
            raise SourceBaselineStampError(
                "exact approved backup SHA-256 confirmation is required"
            )
        if args.confirm_rehearsal_result != REHEARSAL_POST_STAMP_VERIFIED_RESULT:
            raise SourceBaselineStampError(
                "exact verified rehearsal result confirmation is required"
            )
        result = execute_stamp(root, timeout=args.timeout)
        print(render_success(result))
        return 0
    except Exception as exc:
        print("PostgreSQL source baseline stamp")
        print("- result: blocked-or-failed")
        print(f"- reason: {type(exc).__name__}: {exc}")
        print("- no automatic retry, rollback, upgrade, downgrade, DB create/drop/restore, or rehearsal/migration mutation was attempted.")
        if args.execute:
            print("- do not retry automatically; source stamp may already have run before a post-check/report failure. Run read-only inspection first.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

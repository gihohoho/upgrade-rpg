#!/usr/bin/env python3
"""Guard and verify the Alembic baseline stamp on the restored rehearsal DB.

The user approved and ran the v302 rehearsal-only ``stamp head``. The original
v302 ``--inspect`` path incorrectly reused a pre-stamp validator after the
``alembic_version`` control table had been added. v303 fixes that post-check:

- ``--inspect`` is fully read-only and recognizes both pre-stamp and post-stamp.
- Post-stamp success requires exactly 22 application tables / 748 application
  rows plus ``alembic_version`` 1 table / 1 row at ``v295_initial_schema``.
- The application schema/data digests are pinned to the actual user-confirmed
  v302 pre-stamp values and must remain identical.
- Source ``rpg_game`` and the isolated migration test DB are independently
  revalidated and, when present, matched to the local v302 execution report.
- No automatic retry, rollback, upgrade, downgrade, DB create/drop/restore,
  source stamp, or application row write is performed by inspection.

The historical ``--execute`` route remains protected by exact target/revision
confirmation and refuses an already-stamped or already-reported workspace.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import sys
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable
from uuid import UUID

from sqlalchemy import MetaData, Table, create_engine, inspect, select
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from _safe_subprocess import decode_output
from check_postgres_backup_restore_preflight import (
    MIGRATION_TEST_DATABASE,
    RESTORE_REHEARSAL_DATABASE,
    SOURCE_DATABASE,
)
from check_postgres_runtime_readonly_state import (
    inspect_database,
    load_backend_objects,
    to_sync_url,
)
from check_postgres_schema_equivalence import (
    collect as collect_schema_equivalence,
    reflected_signature,
)
from check_postgres_source_baseline_stamp_preflight import (
    READY_RESULT as SOURCE_PREFLIGHT_READY_RESULT,
    inspect_readiness as inspect_source_preflight,
    load_verified_roundtrip_evidence,
    validate_source_schema_equivalence,
)
from create_postgres_migration_test_database import (
    MigrationTestDatabaseError,
    load_verified_restore_evidence,
    sanitize_database_state,
    validate_rehearsal_state,
    validate_source_state,
)
from create_postgres_restore_rehearsal_database import SOURCE_DATABASE_USER
from restore_postgres_rehearsal_database import inspect_named_database
from reupgrade_postgres_migration_test_database import migration_signature
from upgrade_postgres_migration_test_database import (
    REVISION_ID,
    REVISION_SHA256,
    MigrationUpgradeError,
    reviewed_revision,
    validate_migration_after,
)

TOOL_VERSION = "v303.postgres-restore-rehearsal-stamp-postcheck-recovery"
READY_RESULT = "ready-for-separate-restore-rehearsal-stamp-execution-approval"
SUCCESS_RESULT = "restore-rehearsal-stamped-and-verified"
POST_STAMP_VERIFIED_RESULT = "restore-rehearsal-stamp-current-state-verified"
POST_STAMP_REPORT_MISSING_RESULT = (
    "restore-rehearsal-stamp-current-state-verified-report-missing"
)
APPROVED_PRE_STAMP_SCHEMA_DIGEST = (
    "7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921"
)
APPROVED_PRE_STAMP_DATA_DIGEST = (
    "ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244"
)
STAMP_REPORT_RELATIVE_PATH = Path(
    "local-review-artifacts/alembic/v295_initial_schema.restore-rehearsal-stamp-v302.json"
)
DEFAULT_TIMEOUT_SECONDS = 120
ALLOWED_DATABASES = {
    SOURCE_DATABASE,
    RESTORE_REHEARSAL_DATABASE,
    MIGRATION_TEST_DATABASE,
}


class RestoreRehearsalStampError(RuntimeError):
    """Raised when a rehearsal stamp safety gate or postcondition fails."""


def ensure_under(root: Path, path: Path) -> Path:
    root_resolved = root.resolve()
    resolved = path.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise RestoreRehearsalStampError(f"unsafe path outside project: {path}")
    return resolved


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.partial")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def canonical_value(value: Any) -> Any:
    """Convert DB values to deterministic JSON-safe values for row hashing."""
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return {"type": "float", "value": repr(value)}
    if isinstance(value, Decimal):
        return {"type": "decimal", "value": format(value, "f")}
    if isinstance(value, (datetime, date, time)):
        return {"type": type(value).__name__, "value": value.isoformat()}
    if isinstance(value, UUID):
        return {"type": "uuid", "value": str(value)}
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {
            "type": "bytes",
            "value": base64.b64encode(bytes(value)).decode("ascii"),
        }
    if isinstance(value, dict):
        return {
            str(key): canonical_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [canonical_value(item) for item in value]
    return {"type": type(value).__name__, "value": str(value)}


def sha256_json(payload: Any) -> str:
    encoded = json.dumps(
        canonical_value(payload),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def target_database_url(root: Path, database_name: str) -> str:
    if database_name not in ALLOWED_DATABASES:
        raise RestoreRehearsalStampError(f"database is outside the fixed allowlist: {database_name}")
    settings, _ = load_backend_objects(root)
    source_url = make_url(settings.database_url)
    if source_url.database != SOURCE_DATABASE:
        raise RestoreRehearsalStampError(
            f"configured source DB mismatch: expected={SOURCE_DATABASE}, actual={source_url.database}"
        )
    return source_url.set(database=database_name).render_as_string(hide_password=False)


def collect_database_integrity_signature(root: Path, database_name: str) -> dict[str, Any]:
    """Read schema and all row contents, returning deterministic SHA-256 signatures."""
    target_url = to_sync_url(target_database_url(root, database_name))
    engine = create_engine(target_url, poolclass=NullPool, future=True)
    try:
        with engine.connect() as connection:
            inspector = inspect(connection)
            identity = connection.exec_driver_sql(
                "SELECT current_database(), current_user, current_schema(), current_setting('server_version')"
            ).one()
            if str(identity[0]) != database_name:
                raise RestoreRehearsalStampError(
                    f"integrity target mismatch: expected={database_name}, actual={identity[0]}"
                )
            if str(identity[1]) != SOURCE_DATABASE_USER:
                raise RestoreRehearsalStampError(
                    f"integrity user mismatch: expected={SOURCE_DATABASE_USER}, actual={identity[1]}"
                )

            table_names = sorted(inspector.get_table_names(schema="public"))
            schema_payload: dict[str, Any] = {}
            data_payload: dict[str, Any] = {}
            metadata = MetaData()
            for table_name in table_names:
                schema_payload[table_name] = reflected_signature(inspector, table_name)
                table = Table(
                    table_name,
                    metadata,
                    schema="public",
                    autoload_with=connection,
                    extend_existing=True,
                )
                column_names = [column.name for column in table.columns]
                rows: list[str] = []
                for row in connection.execute(select(*table.columns)).mappings():
                    row_payload = [canonical_value(row[name]) for name in column_names]
                    rows.append(
                        json.dumps(
                            row_payload,
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                        )
                    )
                rows.sort()
                data_payload[table_name] = {
                    "rowCount": len(rows),
                    "rowDigest": hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest(),
                }

            schema_digest = sha256_json(schema_payload)
            data_digest = sha256_json(data_payload)
            return {
                "database": database_name,
                "user": str(identity[1]),
                "schema": str(identity[2]),
                "serverVersion": str(identity[3]),
                "publicTables": table_names,
                "publicTableCount": len(table_names),
                "schemaDigest": schema_digest,
                "dataDigest": data_digest,
                "combinedDigest": sha256_json(
                    {"schemaDigest": schema_digest, "dataDigest": data_digest}
                ),
                "tables": {
                    name: {
                        "schemaDigest": sha256_json(schema_payload[name]),
                        **data_payload[name],
                    }
                    for name in table_names
                },
            }
    finally:
        engine.dispose()


def model_table_integrity_signature(
    signature: dict[str, Any], expected_tables: tuple[str, ...]
) -> dict[str, Any]:
    tables = signature.get("tables") or {}
    expected = tuple(sorted(expected_tables))
    missing = [name for name in expected if name not in tables]
    if missing:
        raise RestoreRehearsalStampError(f"integrity signature is missing model tables: {missing}")
    selected = {name: tables[name] for name in expected}
    schema_digest = sha256_json({name: item["schemaDigest"] for name, item in selected.items()})
    data_digest = sha256_json(
        {
            name: {"rowCount": item["rowCount"], "rowDigest": item["rowDigest"]}
            for name, item in selected.items()
        }
    )
    return {
        "tables": list(expected),
        "tableCount": len(expected),
        "rowCount": sum(int(item["rowCount"]) for item in selected.values()),
        "schemaDigest": schema_digest,
        "dataDigest": data_digest,
        "combinedDigest": sha256_json(
            {"schemaDigest": schema_digest, "dataDigest": data_digest}
        ),
    }


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
    env["DATABASE_URL"] = target_database_url(root, RESTORE_REHEARSAL_DATABASE)
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
        raise RestoreRehearsalStampError(
            f"Alembic stamp timed out after {timeout} seconds; no retry was attempted"
        ) from exc
    output = decode_output(completed.stdout).strip()
    if completed.returncode != 0:
        raise RestoreRehearsalStampError(
            f"Alembic stamp failed with exit={completed.returncode}: {output or 'no output'}"
        )
    return output


def validate_rehearsal_after(
    state: dict[str, Any], evidence: dict[str, Any]
) -> dict[str, Any]:
    if state.get("connected") is not True:
        raise RestoreRehearsalStampError(
            f"post-stamp rehearsal connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != RESTORE_REHEARSAL_DATABASE:
        raise RestoreRehearsalStampError("post-stamp rehearsal database boundary mismatch")
    if state.get("user") != SOURCE_DATABASE_USER:
        raise RestoreRehearsalStampError("post-stamp rehearsal user boundary mismatch")

    expected_tables = sorted((*evidence["expectedTables"], "alembic_version"))
    observed_tables = sorted(str(item) for item in (state.get("publicTables") or []))
    if observed_tables != expected_tables or state.get("publicTableCount") != 23:
        raise RestoreRehearsalStampError(
            "post-stamp table set is not 22 application tables + alembic_version"
        )

    expected_counts = dict(evidence["expectedTableCounts"])
    expected_counts["alembic_version"] = 1
    observed_counts = {
        str(name): int(value) for name, value in (state.get("tableCounts") or {}).items()
    }
    if dict(sorted(observed_counts.items())) != dict(sorted(expected_counts.items())):
        raise RestoreRehearsalStampError("post-stamp table row counts changed unexpectedly")
    if state.get("totalRows") != evidence["expectedTotalRows"] + 1:
        raise RestoreRehearsalStampError("post-stamp total rows must be 748 + one Alembic row")
    if state.get("alembicVersionTableExists") is not True:
        raise RestoreRehearsalStampError("post-stamp alembic_version table is missing")
    if state.get("alembicCurrentRevisions") != [REVISION_ID]:
        raise RestoreRehearsalStampError(
            f"post-stamp revision mismatch: {state.get('alembicCurrentRevisions')}"
        )
    if state.get("schemaClassification") != "structurally-equivalent":
        raise RestoreRehearsalStampError("post-stamp application schema is not structurally equivalent")
    if state.get("differenceCount") != 0:
        raise RestoreRehearsalStampError("post-stamp application schema difference count is not zero")
    if state.get("classification") != "alembic-managed":
        raise RestoreRehearsalStampError("post-stamp rehearsal classification is not alembic-managed")
    return sanitize_database_state(state)


def validate_preflight_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("result") != SOURCE_PREFLIGHT_READY_RESULT:
        raise RestoreRehearsalStampError("v301 source baseline stamp preflight is not ready")
    if payload.get("readOnly") is not True or payload.get("mutationExecuted") is not False:
        raise RestoreRehearsalStampError("v301 preflight mutation boundary changed")
    if payload.get("sourceDatabase") != SOURCE_DATABASE:
        raise RestoreRehearsalStampError("v301 preflight source database boundary changed")
    revision = payload.get("revision") or {}
    if revision.get("id") != REVISION_ID or revision.get("sha256") != REVISION_SHA256:
        raise RestoreRehearsalStampError("v301 preflight reviewed revision boundary changed")
    return payload


def load_existing_stamp_report(root: Path) -> dict[str, Any] | None:
    path = ensure_under(root, root / STAMP_REPORT_RELATIVE_PATH)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RestoreRehearsalStampError(
            f"existing v302 stamp report cannot be read: {path}: {exc}"
        ) from exc
    return payload


def validate_existing_stamp_report(payload: dict[str, Any]) -> dict[str, Any]:
    required = {
        "result": SUCCESS_RESULT,
        "targetDatabase": RESTORE_REHEARSAL_DATABASE,
        "revisionId": REVISION_ID,
        "revisionSha256": REVISION_SHA256,
        "stampExecuted": True,
        "upgradeExecuted": False,
        "downgradeExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
        "sourceDatabaseMutationExecuted": False,
        "migrationDatabaseMutationExecuted": False,
    }
    for key, expected in required.items():
        if payload.get(key) != expected:
            raise RestoreRehearsalStampError(
                f"v302 stamp report mismatch: {key}={payload.get(key)!r}, expected={expected!r}"
            )
    if payload.get("sourceBefore") != payload.get("sourceAfter"):
        raise RestoreRehearsalStampError("v302 report source before/after differs")
    if payload.get("migrationBefore") != payload.get("migrationAfter"):
        raise RestoreRehearsalStampError("v302 report migration before/after differs")
    if payload.get("sourceIntegrityBefore") != payload.get("sourceIntegrityAfter"):
        raise RestoreRehearsalStampError("v302 report source integrity before/after differs")
    if payload.get("migrationIntegrityBefore") != payload.get("migrationIntegrityAfter"):
        raise RestoreRehearsalStampError("v302 report migration integrity before/after differs")
    if payload.get("rehearsalModelIntegrityBefore") != payload.get(
        "rehearsalModelIntegrityAfter"
    ):
        raise RestoreRehearsalStampError(
            "v302 report rehearsal application integrity before/after differs"
        )
    return payload


def validate_current_source_and_migration(
    root: Path,
    *,
    verified: dict[str, Any],
    source_raw: dict[str, Any] | None,
    migration_raw: dict[str, Any] | None,
    schema_raw: dict[str, Any] | None,
    roundtrip_evidence: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    try:
        source = validate_source_state(
            source_raw
            if source_raw is not None
            else inspect_database(root, include_counts=True),
            verified,
        )
    except MigrationTestDatabaseError as exc:
        raise RestoreRehearsalStampError(str(exc)) from exc
    schema = validate_source_schema_equivalence(
        schema_raw if schema_raw is not None else collect_schema_equivalence(root)
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
        raise RestoreRehearsalStampError(str(exc)) from exc
    if migration_signature(migration) != migration_signature(
        roundtrip.get("migrationAfter") or {}
    ):
        raise RestoreRehearsalStampError(
            "current migration DB does not match the verified v300 round-trip endpoint"
        )
    return source, schema, migration


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
    stamp_report: dict[str, Any] | None | object = ...,
    approved_schema_digest: str = APPROVED_PRE_STAMP_SCHEMA_DIGEST,
    approved_data_digest: str = APPROVED_PRE_STAMP_DATA_DIGEST,
) -> dict[str, Any]:
    """Inspect either the approved pre-stamp state or the verified post-stamp state.

    The v301 preflight itself is intentionally pre-stamp-only because it requires
    the rehearsal copy to have no ``alembic_version`` table. After the approved
    rehearsal stamp, this v303 inspector independently revalidates source,
    migration, revision, backup evidence, and the pinned application digests.
    """
    root = root.resolve()
    revision_path, manual_review, automated_review = reviewed_revision(root)
    try:
        verified = evidence if evidence is not None else load_verified_restore_evidence(root)
    except MigrationTestDatabaseError as exc:
        raise RestoreRehearsalStampError(str(exc)) from exc

    source, source_schema, migration = validate_current_source_and_migration(
        root,
        verified=verified,
        source_raw=source_raw,
        migration_raw=migration_raw,
        schema_raw=schema_raw,
        roundtrip_evidence=roundtrip_evidence,
    )

    raw_rehearsal = (
        rehearsal_raw
        if rehearsal_raw is not None
        else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE)
    )
    if raw_rehearsal.get("alembicVersionTableExists") is False:
        try:
            rehearsal = validate_rehearsal_state(raw_rehearsal, verified)
        except MigrationTestDatabaseError as exc:
            raise RestoreRehearsalStampError(str(exc)) from exc
        lifecycle_state = "pre-stamp"
        result_value = READY_RESULT
    elif raw_rehearsal.get("alembicVersionTableExists") is True:
        rehearsal = validate_rehearsal_after(raw_rehearsal, verified)
        lifecycle_state = "post-stamp"
        result_value = POST_STAMP_VERIFIED_RESULT
    else:
        raise RestoreRehearsalStampError("rehearsal Alembic lifecycle state is ambiguous")

    source_sig = source_integrity or collect_database_integrity_signature(
        root, SOURCE_DATABASE
    )
    rehearsal_sig = rehearsal_integrity or collect_database_integrity_signature(
        root, RESTORE_REHEARSAL_DATABASE
    )
    migration_sig = migration_integrity or collect_database_integrity_signature(
        root, MIGRATION_TEST_DATABASE
    )
    source_model_sig = model_table_integrity_signature(
        source_sig, verified["expectedTables"]
    )
    rehearsal_model_sig = model_table_integrity_signature(
        rehearsal_sig, verified["expectedTables"]
    )
    if rehearsal_model_sig["tableCount"] != 22 or rehearsal_model_sig["rowCount"] != 748:
        raise RestoreRehearsalStampError("rehearsal integrity baseline is not 22 tables / 748 rows")
    if source_model_sig["tableCount"] != 22 or source_model_sig["rowCount"] != 748:
        raise RestoreRehearsalStampError("source integrity baseline is not 22 tables / 748 rows")
    for label, signature in (
        ("source", source_model_sig),
        ("rehearsal", rehearsal_model_sig),
    ):
        if signature["schemaDigest"] != approved_schema_digest:
            raise RestoreRehearsalStampError(
                f"{label} application schema digest differs from approved v302 pre-stamp digest"
            )
        if signature["dataDigest"] != approved_data_digest:
            raise RestoreRehearsalStampError(
                f"{label} application data digest differs from approved v302 pre-stamp digest"
            )
    if source_model_sig != rehearsal_model_sig:
        raise RestoreRehearsalStampError(
            "source and rehearsal application integrity signatures differ"
        )

    if stamp_report is ...:
        existing_report = load_existing_stamp_report(root)
    else:
        existing_report = stamp_report
    report_status = "not-applicable"
    if lifecycle_state == "pre-stamp":
        if existing_report is not None:
            raise RestoreRehearsalStampError(
                "v302 stamp report exists while rehearsal DB is still pre-stamp"
            )
    else:
        if existing_report is None:
            report_status = "missing"
            result_value = POST_STAMP_REPORT_MISSING_RESULT
        else:
            report = validate_existing_stamp_report(existing_report)
            if report.get("sourceIntegrityAfter") != source_sig:
                raise RestoreRehearsalStampError(
                    "current source integrity differs from the verified v302 execution report"
                )
            if report.get("migrationIntegrityAfter") != migration_sig:
                raise RestoreRehearsalStampError(
                    "current migration integrity differs from the verified v302 execution report"
                )
            if report.get("rehearsalModelIntegrityAfter") != rehearsal_model_sig:
                raise RestoreRehearsalStampError(
                    "current rehearsal application integrity differs from the v302 execution report"
                )
            if report.get("rehearsalAfter") != rehearsal:
                raise RestoreRehearsalStampError(
                    "current rehearsal state differs from the verified v302 execution report"
                )
            report_status = "verified"

    return {
        "toolVersion": TOOL_VERSION,
        "result": result_value,
        "readOnly": True,
        "mutationExecuted": False,
        "lifecycleState": lifecycle_state,
        "targetDatabase": RESTORE_REHEARSAL_DATABASE,
        "revisionId": REVISION_ID,
        "revisionRelativePath": revision_path.relative_to(root).as_posix(),
        "revisionSha256": REVISION_SHA256,
        "manualReview": manual_review["manualConclusion"],
        "automatedReview": automated_review["result"],
        "sourceBaseline": "source-and-v300-roundtrip-current-state-verified",
        "sourceSchema": source_schema,
        "source": source,
        "rehearsal": rehearsal,
        "migration": migration,
        "sourceIntegrity": source_sig,
        "sourceModelIntegrity": source_model_sig,
        "rehearsalIntegrity": rehearsal_sig,
        "rehearsalModelIntegrity": rehearsal_model_sig,
        "migrationIntegrity": migration_sig,
        "approvedPreStampDigests": {
            "schemaDigest": approved_schema_digest,
            "dataDigest": approved_data_digest,
        },
        "stampReportStatus": report_status,
        "stampReportRelativePath": STAMP_REPORT_RELATIVE_PATH.as_posix(),
        "plannedAlembicCommand": build_stamp_command()[1:],
        "allowedPostcondition": {
            "applicationTables": 22,
            "applicationRows": 748,
            "newControlTable": "alembic_version",
            "newControlRows": 1,
            "recordedRevision": REVISION_ID,
        },
        "executionApproved": False,
        "nextApprovalBoundary": (
            "explicit-v302-restore-rehearsal-stamp-execute-approval"
            if lifecycle_state == "pre-stamp"
            else "review-v303-post-stamp-evidence-before-source-stamp-planning"
        ),
    }


def execute_stamp(
    root: Path,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    preflight_payload: dict[str, Any] | None = None,
    evidence: dict[str, Any] | None = None,
    source_before_raw: dict[str, Any] | None = None,
    source_after_raw: dict[str, Any] | None = None,
    rehearsal_before_raw: dict[str, Any] | None = None,
    rehearsal_after_raw: dict[str, Any] | None = None,
    migration_before_raw: dict[str, Any] | None = None,
    migration_after_raw: dict[str, Any] | None = None,
    source_before_integrity: dict[str, Any] | None = None,
    source_after_integrity: dict[str, Any] | None = None,
    rehearsal_before_integrity: dict[str, Any] | None = None,
    rehearsal_after_integrity: dict[str, Any] | None = None,
    migration_before_integrity: dict[str, Any] | None = None,
    migration_after_integrity: dict[str, Any] | None = None,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    root = root.resolve()
    revision_path, manual_review, automated_review = reviewed_revision(root)
    preflight = validate_preflight_payload(
        preflight_payload if preflight_payload is not None else inspect_source_preflight(root)
    )
    try:
        verified = evidence if evidence is not None else load_verified_restore_evidence(root)
        source_before = validate_source_state(
            source_before_raw
            if source_before_raw is not None
            else inspect_database(root, include_counts=True),
            verified,
        )
        rehearsal_before = validate_rehearsal_state(
            rehearsal_before_raw
            if rehearsal_before_raw is not None
            else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
            verified,
        )
    except MigrationTestDatabaseError as exc:
        raise RestoreRehearsalStampError(str(exc)) from exc
    try:
        migration_before = validate_migration_after(
            migration_before_raw
            if migration_before_raw is not None
            else inspect_named_database(root, MIGRATION_TEST_DATABASE),
            verified["expectedTables"],
        )
    except MigrationUpgradeError as exc:
        raise RestoreRehearsalStampError(str(exc)) from exc

    source_before_sig = source_before_integrity or collect_database_integrity_signature(
        root, SOURCE_DATABASE
    )
    rehearsal_before_sig = (
        rehearsal_before_integrity
        or collect_database_integrity_signature(root, RESTORE_REHEARSAL_DATABASE)
    )
    migration_before_sig = (
        migration_before_integrity
        or collect_database_integrity_signature(root, MIGRATION_TEST_DATABASE)
    )
    rehearsal_model_before = model_table_integrity_signature(
        rehearsal_before_sig, verified["expectedTables"]
    )
    if rehearsal_model_before["tableCount"] != 22 or rehearsal_model_before["rowCount"] != 748:
        raise RestoreRehearsalStampError("pre-stamp rehearsal integrity is not 22 tables / 748 rows")

    report_path = ensure_under(root, root / STAMP_REPORT_RELATIVE_PATH)
    if report_path.exists():
        raise RestoreRehearsalStampError(
            f"v302 stamp report already exists; refusing repeated execution: {report_path}"
        )

    command_output = run_stamp_command(root, timeout=timeout, run_process=run_process)

    try:
        source_after = validate_source_state(
            source_after_raw
            if source_after_raw is not None
            else inspect_database(root, include_counts=True),
            verified,
        )
    except MigrationTestDatabaseError as exc:
        raise RestoreRehearsalStampError(str(exc)) from exc
    rehearsal_after = validate_rehearsal_after(
        rehearsal_after_raw
        if rehearsal_after_raw is not None
        else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
        verified,
    )
    try:
        migration_after = validate_migration_after(
            migration_after_raw
            if migration_after_raw is not None
            else inspect_named_database(root, MIGRATION_TEST_DATABASE),
            verified["expectedTables"],
        )
    except MigrationUpgradeError as exc:
        raise RestoreRehearsalStampError(str(exc)) from exc

    source_after_sig = source_after_integrity or collect_database_integrity_signature(
        root, SOURCE_DATABASE
    )
    rehearsal_after_sig = (
        rehearsal_after_integrity
        or collect_database_integrity_signature(root, RESTORE_REHEARSAL_DATABASE)
    )
    migration_after_sig = (
        migration_after_integrity
        or collect_database_integrity_signature(root, MIGRATION_TEST_DATABASE)
    )
    rehearsal_model_after = model_table_integrity_signature(
        rehearsal_after_sig, verified["expectedTables"]
    )

    if source_before != source_after or source_before_sig != source_after_sig:
        raise RestoreRehearsalStampError("source DB changed during rehearsal stamp")
    if migration_before != migration_after or migration_before_sig != migration_after_sig:
        raise RestoreRehearsalStampError("migration test DB changed during rehearsal stamp")
    if rehearsal_model_before != rehearsal_model_after:
        raise RestoreRehearsalStampError(
            "rehearsal application schema/data integrity changed during stamp"
        )
    if sorted(rehearsal_after_sig.get("publicTables") or []) != sorted(
        (*verified["expectedTables"], "alembic_version")
    ):
        raise RestoreRehearsalStampError("rehearsal integrity signature contains unexpected tables")
    alembic_sig = (rehearsal_after_sig.get("tables") or {}).get("alembic_version") or {}
    if alembic_sig.get("rowCount") != 1:
        raise RestoreRehearsalStampError("alembic_version integrity signature is not one row")

    result = {
        "toolVersion": TOOL_VERSION,
        "result": SUCCESS_RESULT,
        "targetDatabase": RESTORE_REHEARSAL_DATABASE,
        "revisionId": REVISION_ID,
        "revisionRelativePath": revision_path.relative_to(root).as_posix(),
        "revisionSha256": REVISION_SHA256,
        "manualReview": manual_review["manualConclusion"],
        "automatedReview": automated_review["result"],
        "sourcePreflight": preflight["result"],
        "alembicCommand": build_stamp_command()[1:],
        "alembicCommandOutput": command_output,
        "sourceBefore": source_before,
        "sourceAfter": source_after,
        "rehearsalBefore": rehearsal_before,
        "rehearsalAfter": rehearsal_after,
        "migrationBefore": migration_before,
        "migrationAfter": migration_after,
        "sourceIntegrityBefore": source_before_sig,
        "sourceIntegrityAfter": source_after_sig,
        "rehearsalIntegrityBefore": rehearsal_before_sig,
        "rehearsalIntegrityAfter": rehearsal_after_sig,
        "rehearsalModelIntegrityBefore": rehearsal_model_before,
        "rehearsalModelIntegrityAfter": rehearsal_model_after,
        "migrationIntegrityBefore": migration_before_sig,
        "migrationIntegrityAfter": migration_after_sig,
        "stampExecuted": True,
        "upgradeExecuted": False,
        "downgradeExecuted": False,
        "databaseCreateDropRestoreExecuted": False,
        "environmentFileChanged": False,
        "sourceDatabaseMutationExecuted": False,
        "migrationDatabaseMutationExecuted": False,
    }
    write_json_atomic(report_path, result)
    result["reportRelativePath"] = report_path.relative_to(root).as_posix()
    return result


def render_inspection(result: dict[str, Any]) -> str:
    model_sig = result["rehearsalModelIntegrity"]
    if result["lifecycleState"] == "pre-stamp":
        return "\n".join(
            [
                "PostgreSQL restore rehearsal baseline stamp guard (read-only inspection)",
                "No stamp, upgrade, downgrade, DB create/drop/restore, or row write was executed.",
                "",
                f"- lifecycle state: {result['lifecycleState']}",
                f"- exact target DB: {result['targetDatabase']}",
                f"- exact revision: {result['revisionId']}",
                f"- revision SHA-256: {result['revisionSha256']}",
                f"- source baseline: {result['sourceBaseline']}",
                f"- rehearsal application tables/rows: {model_sig['tableCount']}/{model_sig['rowCount']}",
                f"- rehearsal schema digest: {model_sig['schemaDigest']}",
                f"- rehearsal data digest: {model_sig['dataDigest']}",
                "- allowed mutation: alembic_version table 1 + revision row 1 only",
                f"- planned command: {' '.join(result['plannedAlembicCommand'])}",
                f"- result: {result['result']}",
                "- actual stamp still requires separate user approval and exact confirmation flags.",
            ]
        )
    rehearsal = result["rehearsal"]
    return "\n".join(
        [
            "PostgreSQL restore rehearsal baseline stamp post-check (read-only)",
            "No stamp, retry, rollback, upgrade, downgrade, DB create/drop/restore, or row write was executed.",
            "",
            f"- lifecycle state: {result['lifecycleState']}",
            f"- exact target DB: {result['targetDatabase']}",
            f"- exact revision: {result['revisionId']}",
            f"- revision SHA-256: {result['revisionSha256']}",
            f"- public tables/rows: {rehearsal.get('publicTableCount')}/{rehearsal.get('totalRows')}",
            f"- current revision: {rehearsal.get('alembicCurrentRevisions')}",
            f"- application tables/rows: {model_sig['tableCount']}/{model_sig['rowCount']}",
            f"- application schema digest: {model_sig['schemaDigest']}",
            f"- application data digest: {model_sig['dataDigest']}",
            "- approved pre-stamp application digests preserved: yes",
            "- source DB current state preserved: yes",
            "- migration test DB current state preserved: yes",
            f"- v302 execution report: {result['stampReportStatus']}",
            f"- result: {result['result']}",
            "- source rpg_game remains unstamped and unapproved.",
        ]
    )

def render_success(result: dict[str, Any]) -> str:
    after = result["rehearsalAfter"]
    model_sig = result["rehearsalModelIntegrityAfter"]
    return "\n".join(
        [
            "PostgreSQL restore rehearsal baseline stamp",
            "The Alembic baseline was stamped only on the restored rehearsal copy.",
            "",
            f"- result: {result['result']}",
            f"- target DB: {result['targetDatabase']}",
            f"- revision: {result['revisionId']}",
            f"- revision SHA-256: {result['revisionSha256']}",
            f"- public tables/rows after: {after.get('publicTableCount')}/{after.get('totalRows')}",
            f"- current revision: {after.get('alembicCurrentRevisions')}",
            f"- application schema/data digest preserved: {model_sig['combinedDigest']}",
            "- source DB preserved: yes",
            "- migration test DB preserved: yes",
            f"- verification report: {result['reportRelativePath']}",
            "- upgrade, downgrade, DB create/drop/restore, .env/Docker, seed, auth, API, and source writes were not executed.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--inspect", action="store_true", help="Read-only pre/post-stamp verification")
    group.add_argument("--execute", action="store_true", help="Stamp only the restored rehearsal DB")
    parser.add_argument("--confirm-target", default="")
    parser.add_argument("--confirm-revision", default="")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    try:
        if args.inspect:
            print(render_inspection(inspect_readiness(root)))
            return 0
        if not args.execute:
            print("PostgreSQL restore rehearsal baseline stamp - execution guard")
            print(f"- exact target DB: {RESTORE_REHEARSAL_DATABASE}")
            print(f"- exact revision: {REVISION_ID}")
            print("- --inspect is safe; --execute requires separate approval and exact confirmations.")
            print("- no DB mutation was attempted.")
            return 2
        if args.confirm_target != RESTORE_REHEARSAL_DATABASE:
            raise RestoreRehearsalStampError(
                f"exact target confirmation required: --confirm-target {RESTORE_REHEARSAL_DATABASE}"
            )
        if args.confirm_revision != REVISION_ID:
            raise RestoreRehearsalStampError(
                f"exact revision confirmation required: --confirm-revision {REVISION_ID}"
            )
        result = execute_stamp(root, timeout=args.timeout)
        print(render_success(result))
        return 0
    except Exception as exc:
        print("PostgreSQL restore rehearsal baseline stamp")
        print("- result: blocked-or-failed")
        print(f"- reason: {type(exc).__name__}: {exc}")
        print("- no automatic retry, rollback, upgrade, downgrade, DB create/drop/restore, or source mutation was attempted.")
        if args.execute:
            print("- do not retry automatically; a rehearsal stamp may already have run before a post-check/report failure. Run read-only inspection first.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

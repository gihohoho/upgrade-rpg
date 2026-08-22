#!/usr/bin/env python3
"""Fresh-backup and exact-upgrade guard for local/Neon v377 targets.

The default mode performs no connection or mutation. ``--inspect`` is read-only.
``--backup`` creates one new local custom-format dump from an exact v295 target.
``--apply`` accepts only a fresh verified backup and runs exactly
``alembic upgrade v377_auth_email_public_security`` in one synchronous database
transaction. It first takes deterministic SHARE ROW EXCLUSIVE locks on all 22
legacy tables, then checks the backup/fingerprint, migrates through the same
connection, checks schema/data parity, and commits. There is deliberately no
production downgrade, stamp, restore, retry, cleanup, seed, or database
create/drop path.

Both mutation modes require the fixed completed isolated-roundtrip report from
the same pushed source SHA. The apply path also hashes every legacy table in PK
order before and after the additive migration without recording any row value.
Backup/apply each create a durable exclusive attempt marker before their first
client/file or database mutation, so a failed attempt cannot be replayed.
"""
from __future__ import annotations

import argparse
import asyncio
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import ssl
import subprocess
import sys
from typing import Any

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import MetaData, Table, create_engine, inspect, select
from sqlalchemy.engine import Connection, Engine, URL, make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from check_postgres_runtime_readonly_state import load_backend_objects
from check_postgres_schema_equivalence import reflected_signature
from postgres_client_safety import (
    PostgresClientSafetyError,
    filtered_libpq_environment,
    guard_sqlalchemy_libpq_engine,
    trusted_posix_executable,
    without_libpq_environment,
)
from private_artifacts import (
    PrivatePathError,
    create_private_file,
    ensure_private_path_location,
    harden_private_directory,
    harden_private_tree,
    verify_private_directory,
    verify_private_file,
    write_private_text_atomic,
    write_private_text_exclusive,
)
from run_v377_auth_security_migration_roundtrip import (
    ALEMBIC_GUARD_MODE,
    BACKEND,
    BASE_REVISION,
    HEAD_REVISION,
    ISOLATED_DATABASE,
    LOCK_TIMEOUT_MS,
    PROCESS_TIMEOUT_SECONDS,
    REVISION_SHA256,
    REPORT_PATH as ROUNDTRIP_REPORT_PATH,
    ROOT,
    SHA_PATTERN,
    SOURCE_DATABASE,
    SOURCE_DATABASE_PORT,
    SOURCE_DATABASE_USER,
    STATEMENT_TIMEOUT_MS,
    TOOL_VERSION as ROUNDTRIP_TOOL_VERSION,
    V377RoundTripError,
    git_output,
    model_table_differences,
    require,
    sha256_file,
    sha256_json,
    validate_revision_contract,
)


LOCAL_ENV_FILE = ROOT / "backend/.env"
NEON_ENV_FILE = ROOT / "deploy/.env.production"
NEON_CA_BUNDLE = ROOT / "local-review-artifacts/neon/windows-system-ca-roots.pem"
BACKUP_DIRECTORY = ROOT / "local-backups/postgres"
REPORT_DIRECTORY = ROOT / "local-review-artifacts/alembic"
BACKUP_ARTIFACT_ROOT = ROOT / "local-backups"
REVIEW_ARTIFACT_ROOT = ROOT / "local-review-artifacts"
EXPECTED_NEON_HOST_SUFFIX = ".ap-southeast-1.aws.neon.tech"
EXPECTED_NEON_DATABASE = "neondb"
EXPECTED_NEON_ROLE = "neondb_owner"
EXPECTED_POSTGRES_MAJOR = 16
EXPECTED_BASE_APPLICATION_TABLES = 22
EXPECTED_BASE_PUBLIC_TABLES = EXPECTED_BASE_APPLICATION_TABLES + 1
EXPECTED_HEAD_APPLICATION_TABLES = 25
EXPECTED_HEAD_PUBLIC_TABLES = EXPECTED_HEAD_APPLICATION_TABLES + 1
EXPECTED_V295_APPLICATION_SCHEMA_DIGEST = (
    "7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921"
)
BACKUP_MAX_AGE_SECONDS = 4 * 60 * 60
TOOL_VERSION = "v377.auth-security-target-backup-apply-guard.v2"
BACKUP_ACTION = "create-fresh-v295-custom-backup-for-v377"
APPLY_ACTION = "apply-exact-v377-upgrade-once-no-downgrade"
ALEMBIC_TARGET_APPLICATION_NAME = "upgrade-rpg-v377-target-migration"
DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ROUNDTRIP_MTIME_TOLERANCE_SECONDS = 60
ROUNDTRIP_COMPLETED_STAGES = [
    "isolated-database-created-empty",
    "v295-synthetic-baseline-created",
    "first-v377-upgrade-verified",
    "downgrade-to-exact-v295-verified",
    "second-v377-upgrade-verified",
]
LEGACY_WRITE_LOCK_MODE = "SHARE ROW EXCLUSIVE"
LEGACY_WRITE_LOCK_TABLES = (
    "admin_change_logs",
    "admin_roles",
    "admin_user_roles",
    "bosses",
    "character_skills",
    "characters",
    "drop_table_items",
    "drop_tables",
    "enhancement_groups",
    "enhancement_levels",
    "field_zones",
    "item_instances",
    "item_templates",
    "skill_levels",
    "skills",
    "user_character_skills",
    "user_equipment_slots",
    "user_inventory_slots",
    "user_mailbox_messages",
    "user_profiles",
    "user_save_snapshots",
    "users",
)


class V377ApplyError(V377RoundTripError):
    """Raised when a local/Neon backup or exact-upgrade boundary fails."""


@dataclass(frozen=True)
class TargetSpec:
    label: str
    database: str
    role: str
    host: str
    port: int
    password: str
    async_url: URL
    tls: bool


def _verify_private_input(path: Path, label: str) -> None:
    try:
        ensure_private_path_location(ROOT, path)
        verify_private_file(path)
    except PrivatePathError:
        raise V377ApplyError(f"{label} private-permission verification failed") from None


def _prepare_private_artifact_storage() -> None:
    """Harden only ignored backup/evidence trees in mutation modes."""
    try:
        for parent in (BACKUP_ARTIFACT_ROOT, REVIEW_ARTIFACT_ROOT):
            ensure_private_path_location(ROOT, parent)
            if not os.path.lexists(os.fspath(parent)):
                harden_private_directory(parent, create=True)
            elif not parent.is_dir():
                raise PrivatePathError("private artifact parent type is unsafe")
            else:
                harden_private_directory(parent)
            verify_private_directory(parent)
        for directory in (
            BACKUP_DIRECTORY,
            REPORT_DIRECTORY,
            NEON_CA_BUNDLE.parent,
        ):
            ensure_private_path_location(ROOT, directory)
            harden_private_tree(directory, create=True)
            verify_private_directory(directory)
    except PrivatePathError:
        raise V377ApplyError("private migration artifact storage is unavailable") from None


def _attempt_marker_path(target: TargetSpec, action: str) -> Path:
    kinds = {BACKUP_ACTION: "backup", APPLY_ACTION: "apply"}
    require(action in kinds, "migration attempt action differs")
    require(target.label in {"local", "neon"}, "migration attempt target differs")
    return REPORT_DIRECTORY / (
        f"v377_auth_security.{target.label}.{kinds[action]}-attempt.json"
    )


def _write_attempt_marker(
    target: TargetSpec,
    *,
    source_sha: str,
    action: str,
) -> str:
    path = _attempt_marker_path(target, action)
    payload = {
        "schemaVersion": TOOL_VERSION,
        "result": "v377-target-attempt-started",
        "startedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "preparationCommitSha": source_sha,
        "target": target.label,
        "database": target.database,
        "action": action,
        "automaticRetry": False,
        "secretOrEndpointRecorded": False,
    }
    try:
        ensure_private_path_location(ROOT, path)
        verify_private_directory(REPORT_DIRECTORY)
        write_private_text_exclusive(
            path,
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        verify_private_file(path)
    except PrivatePathError:
        raise V377ApplyError(
            f"{target.label} {action} attempt marker already exists or could not be "
            "written; retry is forbidden"
        ) from None
    return path.relative_to(ROOT).as_posix()


def _load_env_keys(path: Path) -> dict[str, str]:
    _verify_private_input(path, "ignored Neon environment")
    require(path.is_file(), "ignored Neon environment file is missing")
    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise V377ApplyError(f"cannot read ignored Neon environment file ({type(exc).__name__})") from None
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        selected_key = key.strip()
        require(selected_key != "", "ignored Neon environment contains an empty key")
        if selected_key != "NEON_DIRECT_DATABASE_URL":
            continue
        require(
            selected_key not in values,
            "ignored Neon environment contains a duplicate key",
        )
        selected = value.strip()
        if len(selected) >= 2 and selected[0] == selected[-1] and selected[0] in {'"', "'"}:
            selected = selected[1:-1]
        values[selected_key] = selected
    return values


def _normalize_async_url(raw: str) -> URL:
    try:
        parsed = make_url(raw)
    except Exception:
        raise V377ApplyError("database URL is invalid; value withheld") from None
    require(parsed.drivername.startswith("postgresql"), "database URL must use PostgreSQL")
    require(bool(parsed.host and parsed.username and parsed.password and parsed.database), "database URL is incomplete")
    return parsed.set(drivername="postgresql+asyncpg")


def _strip_verified_neon_query(parsed: URL) -> URL:
    query = {str(key): str(value) for key, value in parsed.query.items()}
    require(
        set(query) == {"sslmode", "channel_binding"},
        "Neon direct URL query boundary differs",
    )
    require(
        query["sslmode"].lower() in {"require", "verify-full"},
        "Neon direct URL must require TLS",
    )
    require(
        query["channel_binding"].lower() == "require",
        "Neon direct URL must require channel binding",
    )
    return parsed.set(query={})


def load_target(label: str) -> TargetSpec:
    if label == "local":
        _verify_private_input(LOCAL_ENV_FILE, "local environment")
        settings, _base = load_backend_objects(ROOT)
        try:
            configured = make_url(settings.database_url)
        except Exception:
            raise V377ApplyError("local database URL is invalid; value withheld") from None
        require(
            configured.drivername == "postgresql+asyncpg",
            "local database driver differs",
        )
        parsed = _normalize_async_url(settings.database_url)
        require(parsed.database == SOURCE_DATABASE, "local database must remain exact rpg_game")
        require(parsed.username == SOURCE_DATABASE_USER, "local database role differs")
        require((parsed.host or "").lower() in {"127.0.0.1", "localhost"}, "local database host differs")
        require(int(parsed.port or 5432) == SOURCE_DATABASE_PORT, "local database port differs")
        require(not parsed.query, "local database URL must not contain query parameters")
        return TargetSpec(
            label="local",
            database=SOURCE_DATABASE,
            role=SOURCE_DATABASE_USER,
            host=str(parsed.host),
            port=SOURCE_DATABASE_PORT,
            password=str(parsed.password),
            async_url=parsed,
            tls=False,
        )
    require(label == "neon", "target must be local or neon")
    values = _load_env_keys(NEON_ENV_FILE)
    raw = values.get("NEON_DIRECT_DATABASE_URL", "").strip()
    require(raw != "", "NEON_DIRECT_DATABASE_URL is missing")
    parsed = _strip_verified_neon_query(_normalize_async_url(raw))
    host = str(parsed.host or "").lower()
    require(host.endswith(EXPECTED_NEON_HOST_SUFFIX), "Neon target region/host differs")
    require("-pooler" not in host, "Neon migration must use the direct endpoint")
    require(parsed.database == EXPECTED_NEON_DATABASE, "Neon database must remain neondb")
    require(parsed.username == EXPECTED_NEON_ROLE, "Neon role must remain neondb_owner")
    require(int(parsed.port or 5432) == 5432, "Neon direct database port differs")
    require(not parsed.query, "normalized Neon target URL must not contain query parameters")
    return TargetSpec(
        label="neon",
        database=EXPECTED_NEON_DATABASE,
        role=EXPECTED_NEON_ROLE,
        host=host,
        port=5432,
        password=str(parsed.password),
        async_url=parsed,
        tls=True,
    )


def verified_ssl_context() -> ssl.SSLContext:
    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    require(context.cert_store_stats().get("x509_ca", 0) > 0, "system CA trust store is empty")
    return context


def _stable_json_default(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray, memoryview)):
        return {
            "type": "bytes",
            "sha256": hashlib.sha256(bytes(value)).hexdigest(),
        }
    isoformat = getattr(value, "isoformat", None)
    if callable(isoformat):
        return {"type": type(value).__name__, "value": isoformat()}
    return {"type": type(value).__name__, "value": str(value)}


def _stable_row_bytes(row: Any) -> bytes:
    return json.dumps(
        list(row),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=_stable_json_default,
    ).encode("utf-8")


def _legacy_contract(inspector: Any, table_names: list[str]) -> dict[str, Any]:
    tables: dict[str, Any] = {}
    for table_name in sorted(table_names):
        columns = sorted(
            str(item["name"])
            for item in inspector.get_columns(table_name, schema="public")
        )
        primary_key = list(
            (inspector.get_pk_constraint(table_name, schema="public") or {}).get(
                "constrained_columns"
            )
            or []
        )
        require(bool(primary_key), "legacy application table is missing a primary key")
        require(
            set(primary_key) <= set(columns),
            "legacy application primary key contract differs",
        )
        tables[table_name] = {
            "columns": columns,
            "primaryKey": primary_key,
        }
    return {"tableNames": sorted(table_names), "tables": tables}


def _legacy_data_fingerprint(
    connection: Any,
    inspector: Any,
    application_tables: list[str],
    contract: dict[str, Any] | None,
) -> dict[str, Any]:
    observed_contract = contract or _legacy_contract(inspector, application_tables)
    table_names = list(observed_contract.get("tableNames") or [])
    table_contracts = observed_contract.get("tables") or {}
    require(
        set(table_names) == set(table_contracts),
        "legacy table fingerprint contract differs",
    )
    require(
        set(table_names) <= set(application_tables),
        "head is missing a legacy application table",
    )

    table_fingerprints: dict[str, Any] = {}
    aggregate_row_count = 0
    for table_name in sorted(table_names):
        expected = table_contracts[table_name]
        column_names = list(expected.get("columns") or [])
        primary_key = list(expected.get("primaryKey") or [])
        actual_columns = {
            str(item["name"])
            for item in inspector.get_columns(table_name, schema="public")
        }
        actual_primary_key = list(
            (inspector.get_pk_constraint(table_name, schema="public") or {}).get(
                "constrained_columns"
            )
            or []
        )
        require(column_names and set(column_names) <= actual_columns, "legacy columns differ")
        require(primary_key == actual_primary_key, "legacy primary key differs")

        table = Table(
            table_name,
            MetaData(),
            schema="public",
            autoload_with=connection,
        )
        statement = select(*(table.c[name] for name in column_names)).order_by(
            *(table.c[name] for name in primary_key)
        )
        digest = hashlib.sha256()
        digest.update(
            json.dumps(
                {
                    "table": table_name,
                    "columns": column_names,
                    "primaryKey": primary_key,
                },
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("ascii")
        )
        row_count = 0
        for row in connection.execute(statement):
            encoded = _stable_row_bytes(row)
            digest.update(len(encoded).to_bytes(8, byteorder="big"))
            digest.update(encoded)
            row_count += 1
        aggregate_row_count += row_count
        table_fingerprints[table_name] = {
            "columns": column_names,
            "primaryKey": primary_key,
            "rowCount": row_count,
            "contentSha256": digest.hexdigest(),
        }

    aggregate = sha256_json(table_fingerprints)
    return {
        "tableNames": sorted(table_names),
        "tables": table_fingerprints,
        "tableCount": len(table_names),
        "rowCount": aggregate_row_count,
        "aggregateSha256": aggregate,
    }


def compare_legacy_data(
    before: dict[str, Any],
    after: dict[str, Any],
) -> dict[str, Any]:
    before_tables = before.get("tables") or {}
    after_tables = after.get("tables") or {}
    require(set(before_tables) == set(after_tables), "legacy application table set differs")
    differences = sum(
        before_tables[name] != after_tables[name]
        for name in before_tables
    )
    require(differences == 0, "legacy application table data differs")
    require(
        before.get("aggregateSha256") == after.get("aggregateSha256"),
        "legacy aggregate data digest differs",
    )
    return {
        "legacyApplicationTableCount": int(before.get("tableCount") or 0),
        "legacyRowCount": int(before.get("rowCount") or 0),
        "legacyDataAggregateSha256": str(before.get("aggregateSha256") or ""),
        "legacyDataDifferenceCount": 0,
    }


def _state_from_connection(
    connection: Any,
    target: TargetSpec,
    legacy_contract: dict[str, Any] | None = None,
    read_only: bool = True,
) -> dict[str, Any]:
    identity = connection.exec_driver_sql(
        "SELECT current_database(), current_user, "
        "current_setting('server_version'), current_setting('transaction_read_only')"
    ).one()
    require(identity[0] == target.database, "connected database differs from exact target")
    require(identity[1] == target.role, "connected database role differs from exact target")
    require(str(identity[2]).split(".", 1)[0] == str(EXPECTED_POSTGRES_MAJOR), "PostgreSQL major differs")
    expected_read_only = "on" if read_only else "off"
    require(
        identity[3] == expected_read_only,
        "target transaction read-only mode differs",
    )

    inspector = inspect(connection)
    public_tables = sorted(inspector.get_table_names(schema="public"))
    revisions = (
        sorted(
            str(value)
            for value in connection.exec_driver_sql(
                "SELECT version_num FROM public.alembic_version"
            ).scalars()
        )
        if "alembic_version" in public_tables
        else []
    )
    application_tables = [name for name in public_tables if name != "alembic_version"]
    table_schema_digests = {
        name: sha256_json(reflected_signature(inspector, name))
        for name in application_tables
    }
    legacy_data = _legacy_data_fingerprint(
        connection,
        inspector,
        application_tables,
        legacy_contract,
    )
    return {
        "label": target.label,
        "database": target.database,
        "roleVerified": True,
        "postgresMajor": EXPECTED_POSTGRES_MAJOR,
        "tlsVerified": target.tls,
        "readOnly": read_only,
        "currentRevision": revisions,
        "applicationTables": application_tables,
        "applicationTableCount": len(application_tables),
        "publicTableCount": len(public_tables),
        "applicationSchemaDigest": sha256_json(table_schema_digests),
        "legacyData": legacy_data,
        "secretOrEndpointRecorded": False,
    }


async def _collect_target_state(target: TargetSpec) -> dict[str, Any]:
    connect_args: dict[str, Any] = {
        "timeout": 20,
        "server_settings": {
            "application_name": "upgrade-rpg-v377-target-readonly",
            "statement_timeout": f"{STATEMENT_TIMEOUT_MS}ms",
        }
    }
    if target.tls:
        connect_args["ssl"] = verified_ssl_context()
    engine = create_async_engine(
        target.async_url,
        poolclass=NullPool,
        connect_args=connect_args,
    )
    try:
        async with engine.connect() as connection:
            async with connection.begin():
                await connection.exec_driver_sql(
                    "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"
                )
                return await connection.run_sync(_state_from_connection, target)
    except V377ApplyError:
        raise
    except V377RoundTripError:
        raise
    except Exception as exc:
        raise V377ApplyError(
            f"{target.label} read-only inspection failed ({type(exc).__name__}); details withheld"
        ) from None
    finally:
        await engine.dispose()


def collect_target_state(target: TargetSpec) -> dict[str, Any]:
    try:
        return asyncio.run(
            asyncio.wait_for(
                _collect_target_state(target),
                timeout=PROCESS_TIMEOUT_SECONDS,
            )
        )
    except TimeoutError:
        raise V377ApplyError(
            "target read-only verification timed out; do not retry automatically"
        ) from None


def validate_base_target(state: dict[str, Any], target: TargetSpec) -> None:
    require(state.get("label") == target.label, "target label differs")
    require(state.get("database") == target.database, "target database differs")
    require(state.get("currentRevision") == [BASE_REVISION], "target current revision must be exact v295")
    require(state.get("applicationTableCount") == EXPECTED_BASE_APPLICATION_TABLES, "v295 application table count differs")
    require(state.get("publicTableCount") == EXPECTED_BASE_PUBLIC_TABLES, "v295 public table count differs")
    require(
        state.get("applicationSchemaDigest") == EXPECTED_V295_APPLICATION_SCHEMA_DIGEST,
        "target v295 application schema digest differs",
    )
    legacy_data = state.get("legacyData") or {}
    require(
        legacy_data.get("tableCount") == EXPECTED_BASE_APPLICATION_TABLES,
        "v295 legacy data table count differs",
    )
    require(
        DIGEST_PATTERN.fullmatch(str(legacy_data.get("aggregateSha256") or ""))
        is not None,
        "v295 legacy aggregate digest differs",
    )


def inspect_target_readiness(target: TargetSpec) -> dict[str, Any]:
    contract = validate_revision_contract(ROOT)
    state = collect_target_state(target)
    if state.get("currentRevision") == [BASE_REVISION]:
        validate_base_target(state, target)
        classification = "ready-for-fresh-v377-backup"
        model_parity: dict[str, int] | None = None
    elif state.get("currentRevision") == [HEAD_REVISION]:
        verified = verify_head(target, state["legacyData"])
        model_parity = verified["modelParity"]
        classification = "v377-already-applied-execution-refused"
    else:
        raise V377ApplyError("target revision is neither exact v295 nor exact v377")
    return {
        "toolVersion": TOOL_VERSION,
        "result": classification,
        "readOnly": True,
        "mutationExecuted": False,
        "target": target.label,
        "database": target.database,
        "currentRevision": state["currentRevision"],
        "revisionContract": contract,
        "modelParity": model_parity,
        "tlsVerified": state["tlsVerified"],
        "secretOrEndpointRecorded": False,
    }


def validate_execution_confirmation(
    *,
    source_sha: str,
    target: TargetSpec,
    target_database: str,
    current_revision: str,
    head_revision: str,
    head_sha256: str,
    action: str,
    expected_action: str,
) -> None:
    require(SHA_PATTERN.fullmatch(source_sha) is not None, "source SHA must be 40 lowercase hex")
    require(target_database == target.database, "target database confirmation differs")
    require(current_revision == BASE_REVISION, "current revision confirmation differs")
    require(head_revision == HEAD_REVISION, "head revision confirmation differs")
    require(head_sha256 == REVISION_SHA256[HEAD_REVISION], "v377 source hash confirmation differs")
    require(action == expected_action, "execution action confirmation differs")
    require(git_output(ROOT, "branch", "--show-current") == "main", "execution branch must be main")
    require(git_output(ROOT, "rev-parse", "HEAD") == source_sha, "confirmed source SHA is not HEAD")
    require(
        git_output(ROOT, "rev-parse", "--verify", "origin/main") == source_sha,
        "confirmed source SHA is not pushed origin/main",
    )
    require(git_output(ROOT, "status", "--porcelain") == "", "working tree must be clean")


def _ensure_inside(root: Path, path: Path) -> Path:
    try:
        ensure_private_path_location(ROOT, root)
        ensure_private_path_location(root, path)
        root_resolved = root.resolve(strict=True)
        resolved = path.resolve(strict=False)
    except (OSError, PrivatePathError):
        raise V377ApplyError("unsafe artifact path boundary") from None
    require(root_resolved in resolved.parents, "unsafe artifact path outside approved directory")
    return resolved


def _utc_timestamp(value: Any, label: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} timestamp differs")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise V377ApplyError(f"{label} timestamp differs") from None
    require(parsed.utcoffset() == timedelta(0), f"{label} timestamp is not UTC")
    return parsed


def validate_roundtrip_payload(
    payload: dict[str, Any],
    *,
    source_sha: str,
) -> datetime:
    expected_keys = {
        "toolVersion",
        "result",
        "startedAtUtc",
        "preparationCommitSha",
        "sourceDatabase",
        "sourceCurrentRevision",
        "targetDatabase",
        "revisionContract",
        "syntheticFixtureOnly",
        "restoreExecuted",
        "dropDatabaseExecuted",
        "automaticRetry",
        "completedStages",
        "completedAtUtc",
        "alembicCommands",
        "baselineFixtureDigest",
        "firstHeadSchemaDigest",
        "secondHeadSchemaDigest",
        "firstModelParity",
        "secondModelParity",
        "syntheticHeadRowsBeforeDowngrade",
        "syntheticHeadRowsAfterReupgrade",
        "sourcePreserved",
        "finalTargetRevision",
    }
    require(set(payload) == expected_keys, "round-trip report field boundary differs")
    expected = {
        "toolVersion": ROUNDTRIP_TOOL_VERSION,
        "result": "v377-isolated-upgrade-downgrade-reupgrade-verified",
        "preparationCommitSha": source_sha,
        "sourceDatabase": SOURCE_DATABASE,
        "sourceCurrentRevision": BASE_REVISION,
        "targetDatabase": ISOLATED_DATABASE,
        "revisionContract": validate_revision_contract(ROOT),
        "syntheticFixtureOnly": True,
        "restoreExecuted": False,
        "dropDatabaseExecuted": False,
        "automaticRetry": False,
        "completedStages": ROUNDTRIP_COMPLETED_STAGES,
        "firstModelParity": {
            "modelTableCount": EXPECTED_HEAD_APPLICATION_TABLES,
            "differenceCount": 0,
        },
        "secondModelParity": {
            "modelTableCount": EXPECTED_HEAD_APPLICATION_TABLES,
            "differenceCount": 0,
        },
        "syntheticHeadRowsBeforeDowngrade": {
            "authRateLimitBuckets": 1,
            "authEmailOutbox": 1,
        },
        "syntheticHeadRowsAfterReupgrade": {
            "authRateLimitBuckets": 0,
            "authEmailOutbox": 0,
        },
        "sourcePreserved": True,
        "finalTargetRevision": HEAD_REVISION,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"round-trip report contract differs: {key}")

    expected_commands = [
        f"alembic upgrade {BASE_REVISION}",
        f"alembic upgrade {HEAD_REVISION}",
        f"alembic downgrade {BASE_REVISION}",
        f"alembic upgrade {HEAD_REVISION}",
    ]
    commands = payload.get("alembicCommands")
    require(isinstance(commands, list) and len(commands) == 4, "round-trip command evidence differs")
    for item, expected_command in zip(commands, expected_commands, strict=True):
        require(
            isinstance(item, dict)
            and set(item) == {"command", "exitCode", "outputSha256"},
            "round-trip command evidence fields differ",
        )
        require(item.get("command") == expected_command, "round-trip command differs")
        require(item.get("exitCode") == 0, "round-trip command did not succeed")
        require(
            DIGEST_PATTERN.fullmatch(str(item.get("outputSha256") or ""))
            is not None,
            "round-trip command output digest differs",
        )

    for key in (
        "baselineFixtureDigest",
        "firstHeadSchemaDigest",
        "secondHeadSchemaDigest",
    ):
        require(
            DIGEST_PATTERN.fullmatch(str(payload.get(key) or "")) is not None,
            f"round-trip digest differs: {key}",
        )
    require(
        payload["firstHeadSchemaDigest"] == payload["secondHeadSchemaDigest"],
        "round-trip schema digests differ",
    )
    started = _utc_timestamp(payload.get("startedAtUtc"), "round-trip start")
    completed = _utc_timestamp(payload.get("completedAtUtc"), "round-trip completion")
    require(started <= completed, "round-trip timestamp order differs")
    return completed


def load_verified_roundtrip_evidence(
    report_argument: str,
    *,
    source_sha: str,
) -> dict[str, Any]:
    require(report_argument != "", "completed isolated round-trip report is required")
    path = _ensure_inside(ROUNDTRIP_REPORT_PATH.parent, ROOT / report_argument)
    require(
        path == ROUNDTRIP_REPORT_PATH.resolve(),
        "round-trip report must use the fixed ignored path",
    )
    _verify_private_input(path, "completed isolated round-trip report")
    require(path.is_file(), "completed isolated round-trip report is missing")
    before_stat = path.stat()
    require(0 < before_stat.st_size <= 1_000_000, "round-trip report size differs")
    try:
        raw = path.read_bytes()
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise V377ApplyError(f"round-trip report is invalid ({type(exc).__name__})") from None
    after_stat = path.stat()
    require(
        (before_stat.st_size, before_stat.st_mtime_ns)
        == (after_stat.st_size, after_stat.st_mtime_ns),
        "round-trip report changed during verification",
    )
    require(isinstance(payload, dict), "round-trip report root differs")
    completed = validate_roundtrip_payload(payload, source_sha=source_sha)
    modified = datetime.fromtimestamp(after_stat.st_mtime, timezone.utc)
    require(
        abs((modified - completed).total_seconds())
        <= ROUNDTRIP_MTIME_TOLERANCE_SECONDS,
        "round-trip report mtime does not match completion",
    )
    require(
        modified <= datetime.now(timezone.utc) + timedelta(seconds=5),
        "round-trip report mtime is in the future",
    )
    return {
        "roundTripReportRelativePath": path.relative_to(ROOT).as_posix(),
        "roundTripReportSha256": hashlib.sha256(raw).hexdigest(),
        "roundTripReportMtimeNs": after_stat.st_mtime_ns,
        "roundTripCompletedAtUtc": payload["completedAtUtc"],
    }


def _postgres_tool(name: str) -> Path:
    if os.name == "nt":
        require(
            re.fullmatch(r"pg_(?:dump|restore)", name) is not None,
            "PostgreSQL client tool name differs",
        )
        path = Path(r"C:\Program Files\PostgreSQL\16\bin") / f"{name}.exe"
    else:
        try:
            path = trusted_posix_executable(name)
        except PostgresClientSafetyError:
            raise V377ApplyError(
                f"PostgreSQL client tool path is unsafe: {name}"
            ) from None
    require(path.is_file(), f"PostgreSQL 16 client tool is missing: {name}")
    try:
        completed = subprocess.run(
            [str(path), "--version"],
            capture_output=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise V377ApplyError(f"cannot inspect PostgreSQL client ({type(exc).__name__})") from None
    output = completed.stdout.decode("utf-8", errors="replace")
    require(completed.returncode == 0 and f"{EXPECTED_POSTGRES_MAJOR}." in output, "PostgreSQL client major differs")
    return path


def _ensure_neon_ca_bundle() -> Path:
    context = verified_ssl_context()
    certificates = context.get_ca_certs(binary_form=True)
    require(bool(certificates), "system CA certificate export is empty")
    pem = "".join(ssl.DER_cert_to_PEM_cert(item) for item in certificates)
    try:
        ensure_private_path_location(ROOT, NEON_CA_BUNDLE)
        verify_private_directory(NEON_CA_BUNDLE.parent)
        write_private_text_atomic(NEON_CA_BUNDLE, pem, encoding="ascii")
        verify_private_file(NEON_CA_BUNDLE)
    except PrivatePathError:
        raise V377ApplyError("private Neon CA bundle write failed") from None
    return NEON_CA_BUNDLE


def pg_environment(target: TargetSpec) -> dict[str, str]:
    environment = filtered_libpq_environment(
        {
            "PGHOST": target.host,
            "PGPORT": str(target.port),
            "PGDATABASE": target.database,
            "PGUSER": target.role,
            "PGPASSWORD": target.password,
            "PGAPPNAME": "upgrade-rpg-v377-fresh-backup",
            "PGCONNECT_TIMEOUT": "20",
        },
    )
    if target.tls:
        environment.update(
            {
                "PGSSLMODE": "verify-full",
                "PGSSLROOTCERT": str(_ensure_neon_ca_bundle()),
                "PGCHANNELBINDING": "require",
            }
        )
    else:
        environment["PGSSLMODE"] = "disable"
        environment.pop("PGSSLROOTCERT", None)
        environment.pop("PGCHANNELBINDING", None)
    return environment


def _run_backup_command(command: list[str], *, environment: dict[str, str], label: str) -> bytes:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        raise V377ApplyError(f"{label} timed out; do not retry automatically") from None
    except (OSError, subprocess.SubprocessError) as exc:
        raise V377ApplyError(f"{label} failed ({type(exc).__name__}); details withheld") from None
    require(completed.returncode == 0, f"{label} failed with exit={completed.returncode}; output withheld")
    return completed.stdout


def create_fresh_backup(
    target: TargetSpec,
    *,
    source_sha: str,
    roundtrip_report: str,
) -> dict[str, Any]:
    _prepare_private_artifact_storage()
    validate_revision_contract(ROOT)
    roundtrip_evidence = load_verified_roundtrip_evidence(
        roundtrip_report,
        source_sha=source_sha,
    )
    before = collect_target_state(target)
    validate_base_target(before, target)
    timestamp = datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d_%H%M%S_KST")
    base_name = f"{target.label}_{target.database}_{timestamp}_pre_v377.custom.dump"
    dump_path = _ensure_inside(BACKUP_DIRECTORY, BACKUP_DIRECTORY / base_name)
    partial_dump_path = dump_path.with_name(f".{dump_path.name}.partial")
    checksum_path = dump_path.with_name(f"{dump_path.name}.sha256")
    manifest_path = dump_path.with_name(f"{dump_path.name}.manifest.json")
    verify_private_directory(BACKUP_DIRECTORY)
    for path in (dump_path, partial_dump_path, checksum_path, manifest_path):
        require(not path.exists(), "fresh backup artifact collision; no overwrite allowed")

    pg_dump = _postgres_tool("pg_dump")
    pg_restore = _postgres_tool("pg_restore")
    attempt_marker = _write_attempt_marker(
        target,
        source_sha=source_sha,
        action=BACKUP_ACTION,
    )
    environment = pg_environment(target)
    try:
        descriptor = create_private_file(partial_dump_path)
        os.close(descriptor)
        verify_private_file(partial_dump_path)
    except (OSError, PrivatePathError):
        raise V377ApplyError("private backup staging file creation failed") from None
    _run_backup_command(
        [
            str(pg_dump),
            "--format=custom",
            "--no-owner",
            "--no-privileges",
            "--file",
            str(partial_dump_path),
        ],
        environment=environment,
        label="fresh PostgreSQL custom backup",
    )
    require(
        partial_dump_path.is_file() and partial_dump_path.stat().st_size > 0,
        "pg_dump produced no archive",
    )
    verify_private_file(partial_dump_path)
    toc = _run_backup_command(
        [str(pg_restore), "--list", str(partial_dump_path)],
        environment=environment,
        label="fresh backup TOC verification",
    ).decode("utf-8", errors="replace")
    for required in (" TABLE public users ", " TABLE DATA public users ", " TABLE DATA public alembic_version "):
        require(required in toc, "fresh backup TOC is missing a required entry")

    after = collect_target_state(target)
    validate_base_target(after, target)
    require(
        after["applicationSchemaDigest"] == before["applicationSchemaDigest"],
        "target schema changed during fresh backup",
    )
    legacy_preservation = compare_legacy_data(
        before["legacyData"],
        after["legacyData"],
    )

    try:
        os.replace(partial_dump_path, dump_path)
        verify_private_file(dump_path)
    except (OSError, PrivatePathError):
        raise V377ApplyError("private backup archive finalization failed") from None
    backup_sha = sha256_file(dump_path)
    try:
        write_private_text_atomic(
            checksum_path,
            f"{backup_sha}  {dump_path.name}\n",
            encoding="ascii",
        )
    except PrivatePathError:
        raise V377ApplyError("private backup checksum write failed") from None
    manifest = {
        "schemaVersion": TOOL_VERSION,
        "result": "fresh-v295-backup-created-and-verified-for-v377",
        "createdAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "preparationCommitSha": source_sha,
        "target": target.label,
        "database": target.database,
        "currentRevision": BASE_REVISION,
        "targetRevision": HEAD_REVISION,
        "revisionSha256": dict(REVISION_SHA256),
        **roundtrip_evidence,
        "backupAttemptMarkerRelativePath": attempt_marker,
        "applicationSchemaDigest": before["applicationSchemaDigest"],
        "legacyApplicationTableCount": legacy_preservation[
            "legacyApplicationTableCount"
        ],
        "legacyRowCount": legacy_preservation["legacyRowCount"],
        "legacyDataAggregateSha256": legacy_preservation[
            "legacyDataAggregateSha256"
        ],
        "legacyDataDifferenceCount": 0,
        "backupRelativePath": dump_path.relative_to(ROOT).as_posix(),
        "backupSizeBytes": dump_path.stat().st_size,
        "backupSha256": backup_sha,
        "format": "PostgreSQL custom",
        "tocRequiredEntriesVerified": True,
        "databaseMutationExecuted": False,
        "restoreExecuted": False,
        "secretOrEndpointRecorded": False,
        "tlsCertificateAndHostnameVerified": target.tls,
    }
    try:
        write_private_text_atomic(
            manifest_path,
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        for path in (dump_path, checksum_path, manifest_path):
            verify_private_file(path)
    except PrivatePathError:
        raise V377ApplyError("private backup manifest finalization failed") from None
    return {**manifest, "manifestRelativePath": manifest_path.relative_to(ROOT).as_posix()}


def load_verified_backup(
    target: TargetSpec,
    manifest_argument: str,
    *,
    source_sha: str,
    roundtrip_evidence: dict[str, Any],
) -> dict[str, Any]:
    require(manifest_argument != "", "backup manifest path is required")
    manifest_path = _ensure_inside(BACKUP_DIRECTORY, ROOT / manifest_argument)
    _verify_private_input(manifest_path, "backup manifest")
    require(manifest_path.is_file(), "backup manifest is missing")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise V377ApplyError(f"backup manifest is invalid ({type(exc).__name__})") from None
    require(isinstance(manifest, dict), "backup manifest root differs")
    expected_keys = {
        "schemaVersion",
        "result",
        "createdAtUtc",
        "preparationCommitSha",
        "target",
        "database",
        "currentRevision",
        "targetRevision",
        "revisionSha256",
        "roundTripReportRelativePath",
        "roundTripReportSha256",
        "roundTripReportMtimeNs",
        "roundTripCompletedAtUtc",
        "backupAttemptMarkerRelativePath",
        "applicationSchemaDigest",
        "legacyApplicationTableCount",
        "legacyRowCount",
        "legacyDataAggregateSha256",
        "legacyDataDifferenceCount",
        "backupRelativePath",
        "backupSizeBytes",
        "backupSha256",
        "format",
        "tocRequiredEntriesVerified",
        "databaseMutationExecuted",
        "restoreExecuted",
        "secretOrEndpointRecorded",
        "tlsCertificateAndHostnameVerified",
    }
    require(set(manifest) == expected_keys, "backup manifest field boundary differs")
    expected = {
        "schemaVersion": TOOL_VERSION,
        "result": "fresh-v295-backup-created-and-verified-for-v377",
        "preparationCommitSha": source_sha,
        "target": target.label,
        "database": target.database,
        "currentRevision": BASE_REVISION,
        "targetRevision": HEAD_REVISION,
        "revisionSha256": REVISION_SHA256,
        **roundtrip_evidence,
        "backupAttemptMarkerRelativePath": _attempt_marker_path(
            target,
            BACKUP_ACTION,
        ).relative_to(ROOT).as_posix(),
        "applicationSchemaDigest": EXPECTED_V295_APPLICATION_SCHEMA_DIGEST,
        "format": "PostgreSQL custom",
        "tocRequiredEntriesVerified": True,
        "databaseMutationExecuted": False,
        "restoreExecuted": False,
        "secretOrEndpointRecorded": False,
        "tlsCertificateAndHostnameVerified": target.tls,
    }
    for key, value in expected.items():
        require(manifest.get(key) == value, f"backup manifest contract differs: {key}")
    require(
        manifest.get("legacyApplicationTableCount")
        == EXPECTED_BASE_APPLICATION_TABLES,
        "backup legacy table count differs",
    )
    require(
        isinstance(manifest.get("legacyRowCount"), int)
        and manifest["legacyRowCount"] >= 0,
        "backup legacy row count differs",
    )
    require(
        DIGEST_PATTERN.fullmatch(
            str(manifest.get("legacyDataAggregateSha256") or "")
        )
        is not None,
        "backup legacy data digest differs",
    )
    require(
        manifest.get("legacyDataDifferenceCount") == 0,
        "backup legacy data verification differs",
    )
    require(
        isinstance(manifest.get("backupSizeBytes"), int)
        and manifest["backupSizeBytes"] > 0,
        "backup size contract differs",
    )
    require(
        DIGEST_PATTERN.fullmatch(str(manifest.get("backupSha256") or ""))
        is not None,
        "backup SHA-256 contract differs",
    )
    created = datetime.fromisoformat(str(manifest["createdAtUtc"]).replace("Z", "+00:00"))
    age = (datetime.now(timezone.utc) - created).total_seconds()
    require(0 <= age <= BACKUP_MAX_AGE_SECONDS, "backup is not fresh enough for target apply")
    dump_path = _ensure_inside(BACKUP_DIRECTORY, ROOT / str(manifest.get("backupRelativePath") or ""))
    require(
        manifest_path == dump_path.with_name(f"{dump_path.name}.manifest.json"),
        "backup manifest/archive path relationship differs",
    )
    _verify_private_input(dump_path, "backup archive")
    require(dump_path.is_file(), "verified backup archive is missing")
    require(dump_path.stat().st_size == int(manifest.get("backupSizeBytes", -1)), "backup size differs")
    require(sha256_file(dump_path) == manifest.get("backupSha256"), "backup SHA-256 differs")
    checksum_path = dump_path.with_name(f"{dump_path.name}.sha256")
    _verify_private_input(checksum_path, "backup checksum")
    require(checksum_path.is_file(), "backup checksum sidecar is missing")
    try:
        checksum = checksum_path.read_text(encoding="ascii")
    except OSError as exc:
        raise V377ApplyError(f"backup checksum is unreadable ({type(exc).__name__})") from None
    require(
        checksum == f"{manifest['backupSha256']}  {dump_path.name}\n",
        "backup checksum sidecar differs",
    )
    return {
        **manifest,
        "verifiedManifestRelativePath": manifest_path.relative_to(ROOT).as_posix(),
    }


def validate_backup_matches_target(
    backup: dict[str, Any],
    state: dict[str, Any],
) -> None:
    legacy_data = state.get("legacyData") or {}
    require(
        backup.get("applicationSchemaDigest") == state.get("applicationSchemaDigest"),
        "fresh backup schema no longer matches target",
    )
    require(
        backup.get("legacyApplicationTableCount") == legacy_data.get("tableCount"),
        "fresh backup legacy table count no longer matches target",
    )
    require(
        backup.get("legacyRowCount") == legacy_data.get("rowCount"),
        "fresh backup legacy row count no longer matches target",
    )
    require(
        backup.get("legacyDataAggregateSha256")
        == legacy_data.get("aggregateSha256"),
        "fresh backup legacy data digest no longer matches target",
    )


def alembic_database_url(target: TargetSpec) -> str:
    require(not target.async_url.query, "target database URL query boundary changed")
    return target.async_url.render_as_string(hide_password=False)


def alembic_environment(target: TargetSpec) -> dict[str, str]:
    environment = filtered_libpq_environment()
    environment.update(
        {
            "DATABASE_URL": alembic_database_url(target),
            "DEBUG": "false",
            "OWNER_ADMIN_BOOTSTRAP_ENABLED": "false",
            "ALEMBIC_GUARD_MODE": ALEMBIC_GUARD_MODE,
            "ALEMBIC_LOCK_TIMEOUT_MS": str(LOCK_TIMEOUT_MS),
            "ALEMBIC_STATEMENT_TIMEOUT_MS": str(STATEMENT_TIMEOUT_MS),
            "ALEMBIC_APPLICATION_NAME": ALEMBIC_TARGET_APPLICATION_NAME,
        }
    )
    if target.tls:
        # Process-only non-production credentials satisfy the shared Settings
        # validator without reading or exposing unrelated Render secrets.
        environment.update(
            {
                "ENVIRONMENT": "production",
                "JWT_SECRET_KEY": "v377-migration-process-only-jwt-" + ("j" * 32),
                "ADMIN_WRITE_DEV_KEY": "v377-migration-process-only-admin-" + ("a" * 32),
                "EMAIL_PROVIDER": "brevo",
                "BREVO_API_KEY": "v377-migration-process-only-unused",
                "BREVO_FROM_EMAIL": "migration-only@example.invalid",
                "BREVO_FROM_NAME": "Upgrade RPG Migration",
                "EMAIL_TOKEN_SECRET": "v377-migration-process-only-email-" + ("e" * 32),
                "AUTH_ABUSE_SECRET": "v377-migration-process-only-abuse-" + ("r" * 32),
                "AUTH_TRUSTED_PROXY_MODE": "render",
                "EMAIL_OUTBOX_WORKER_ENABLED": "true",
                "REQUEST_BODY_LIMIT_BYTES": "2100000",
                "AUTH_REQUEST_BODY_LIMIT_BYTES": "16384",
                "AUTH_DISCOVERY_RESPONSE_FLOOR_MS": "350",
                "AUTH_DISCOVERY_RESPONSE_JITTER_MS": "100",
                "PUBLIC_FRONTEND_ORIGIN": "https://example.invalid",
                "CORS_ORIGINS": "[]",
                "DB_POOL_SIZE": "1",
                "DB_MAX_OVERFLOW": "0",
            }
        )
    else:
        environment["ENVIRONMENT"] = "local"
    return environment


def _alembic_environment_overrides(target: TargetSpec) -> dict[str, str]:
    environment = alembic_environment(target)
    keys = {
        "DATABASE_URL",
        "DEBUG",
        "OWNER_ADMIN_BOOTSTRAP_ENABLED",
        "ALEMBIC_GUARD_MODE",
        "ALEMBIC_LOCK_TIMEOUT_MS",
        "ALEMBIC_STATEMENT_TIMEOUT_MS",
        "ALEMBIC_APPLICATION_NAME",
        "ENVIRONMENT",
    }
    if target.tls:
        keys.update(
            {
                "JWT_SECRET_KEY",
                "ADMIN_WRITE_DEV_KEY",
                "EMAIL_PROVIDER",
                "BREVO_API_KEY",
                "BREVO_FROM_EMAIL",
                "BREVO_FROM_NAME",
                "EMAIL_TOKEN_SECRET",
                "AUTH_ABUSE_SECRET",
                "AUTH_TRUSTED_PROXY_MODE",
                "EMAIL_OUTBOX_WORKER_ENABLED",
                "REQUEST_BODY_LIMIT_BYTES",
                "AUTH_REQUEST_BODY_LIMIT_BYTES",
                "AUTH_DISCOVERY_RESPONSE_FLOOR_MS",
                "AUTH_DISCOVERY_RESPONSE_JITTER_MS",
                "PUBLIC_FRONTEND_ORIGIN",
                "CORS_ORIGINS",
                "DB_POOL_SIZE",
                "DB_MAX_OVERFLOW",
            }
        )
    return {key: environment[key] for key in keys}


@contextmanager
def _temporary_alembic_environment(target: TargetSpec) -> Iterator[None]:
    overrides = _alembic_environment_overrides(target)
    missing = object()
    previous: dict[str, str | object] = {
        key: os.environ.get(key, missing)
        for key in overrides
    }
    with without_libpq_environment():
        os.environ.update(overrides)
        try:
            yield
        finally:
            for key, value in previous.items():
                if value is missing:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = str(value)


def sync_database_url(target: TargetSpec) -> URL:
    require(not target.async_url.query, "target database URL query boundary changed")
    return target.async_url.set(drivername="postgresql+psycopg")


def target_sync_connect_args(target: TargetSpec) -> dict[str, Any]:
    connect_args: dict[str, Any] = {
        "connect_timeout": 20,
        "application_name": ALEMBIC_TARGET_APPLICATION_NAME,
        "options": (
            f"-c lock_timeout={LOCK_TIMEOUT_MS}ms "
            f"-c statement_timeout={STATEMENT_TIMEOUT_MS}ms"
        ),
    }
    if target.tls:
        connect_args.update(
            {
                "sslmode": "verify-full",
                "sslrootcert": str(_ensure_neon_ca_bundle()),
                "channel_binding": "require",
            }
        )
    else:
        connect_args["sslmode"] = "disable"
    return connect_args


def build_target_sync_engine(target: TargetSpec) -> Engine:
    return guard_sqlalchemy_libpq_engine(
        create_engine(
            sync_database_url(target),
            poolclass=NullPool,
            connect_args=target_sync_connect_args(target),
        )
    )


def legacy_write_lock_statements() -> tuple[str, ...]:
    require(
        len(LEGACY_WRITE_LOCK_TABLES) == EXPECTED_BASE_APPLICATION_TABLES,
        "legacy write-lock table count differs",
    )
    require(
        tuple(sorted(LEGACY_WRITE_LOCK_TABLES)) == LEGACY_WRITE_LOCK_TABLES,
        "legacy write-lock table order differs",
    )
    require(
        all(re.fullmatch(r"[a-z][a-z0-9_]*", name) for name in LEGACY_WRITE_LOCK_TABLES),
        "legacy write-lock identifier differs",
    )
    return tuple(
        f'LOCK TABLE "public"."{name}" IN {LEGACY_WRITE_LOCK_MODE} MODE'
        for name in LEGACY_WRITE_LOCK_TABLES
    )


def prepare_quiescent_apply_transaction(connection: Connection) -> None:
    # These transaction-control statements do not take an MVCC snapshot. The
    # first fingerprint SELECT therefore sees all writes that completed before
    # the deterministic lock set was fully acquired.
    connection.exec_driver_sql("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
    connection.exec_driver_sql(f"SET LOCAL lock_timeout = '{LOCK_TIMEOUT_MS}ms'")
    connection.exec_driver_sql(
        f"SET LOCAL statement_timeout = '{STATEMENT_TIMEOUT_MS}ms'"
    )
    for statement in legacy_write_lock_statements():
        connection.exec_driver_sql(statement)


def run_exact_upgrade(
    connection: Connection,
    target: TargetSpec,
) -> dict[str, Any]:
    output = io.StringIO()
    config = AlembicConfig(str(BACKEND / "alembic.ini"), stdout=output)
    config.set_main_option("script_location", str(BACKEND / "alembic"))
    config.set_main_option("prepend_sys_path", str(BACKEND))
    config.attributes["connection"] = connection
    try:
        with _temporary_alembic_environment(target):
            alembic_command.upgrade(config, HEAD_REVISION)
    except (V377ApplyError, V377RoundTripError):
        raise
    except Exception as exc:
        raise V377ApplyError(
            f"exact v377 upgrade failed ({type(exc).__name__}); details withheld"
        ) from None
    return {
        "command": f"alembic upgrade {HEAD_REVISION}",
        "exitCode": 0,
        "outputSha256": hashlib.sha256(output.getvalue().encode("utf-8")).hexdigest(),
        "existingSyncConnection": True,
    }


def _model_parity_from_connection(connection: Any) -> dict[str, int]:
    _verify_private_input(LOCAL_ENV_FILE, "local environment")
    _settings, Base = load_backend_objects(ROOT)
    model_tables = {table.name: table for table in Base.metadata.sorted_tables}
    require(len(model_tables) == EXPECTED_HEAD_APPLICATION_TABLES, "model table count differs")
    inspector = inspect(connection)
    actual = set(inspector.get_table_names(schema="public")) - {"alembic_version"}
    require(actual == set(model_tables), "target/model application table set differs")
    differences = []
    for name in sorted(model_tables):
        differences.extend(
            model_table_differences(
                inspector,
                name,
                model_tables[name],
            )
        )
    require(not differences, "target/model schema parity differs after v377")
    return {"modelTableCount": len(model_tables), "differenceCount": 0}


def _verified_head_from_connection(
    connection: Any,
    target: TargetSpec,
    legacy_contract: dict[str, Any],
    read_only: bool = True,
) -> dict[str, Any]:
    state = _state_from_connection(
        connection,
        target,
        legacy_contract,
        read_only,
    )
    parity = _model_parity_from_connection(connection)
    require(state["currentRevision"] == [HEAD_REVISION], "target did not reach exact v377")
    require(state["applicationTableCount"] == EXPECTED_HEAD_APPLICATION_TABLES, "v377 table count differs")
    require(state["publicTableCount"] == EXPECTED_HEAD_PUBLIC_TABLES, "v377 public table count differs")
    return {"state": state, "modelParity": parity}


async def _verify_head(
    target: TargetSpec,
    legacy_contract: dict[str, Any],
) -> dict[str, Any]:
    connect_args: dict[str, Any] = {
        "timeout": 20,
        "server_settings": {
            "application_name": "upgrade-rpg-v377-postcheck",
            "statement_timeout": f"{STATEMENT_TIMEOUT_MS}ms",
        }
    }
    if target.tls:
        connect_args["ssl"] = verified_ssl_context()
    engine = create_async_engine(target.async_url, poolclass=NullPool, connect_args=connect_args)
    try:
        async with engine.connect() as connection:
            async with connection.begin():
                await connection.exec_driver_sql(
                    "SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"
                )
                verified = await connection.run_sync(
                    _verified_head_from_connection,
                    target,
                    legacy_contract,
                )
    except (V377ApplyError, V377RoundTripError):
        raise
    except Exception as exc:
        raise V377ApplyError(f"v377 post-check failed ({type(exc).__name__}); details withheld") from None
    finally:
        await engine.dispose()
    return verified


def verify_head(
    target: TargetSpec,
    legacy_contract: dict[str, Any],
) -> dict[str, Any]:
    try:
        return asyncio.run(
            asyncio.wait_for(
                _verify_head(target, legacy_contract),
                timeout=PROCESS_TIMEOUT_SECONDS,
            )
        )
    except TimeoutError:
        raise V377ApplyError(
            "v377 post-check timed out; inspect target and do not retry"
        ) from None


def execute_quiescent_upgrade(
    target: TargetSpec,
    backup: dict[str, Any],
) -> dict[str, Any]:
    """Lock, fingerprint, migrate, verify, and commit as one transaction."""
    engine = build_target_sync_engine(target)
    try:
        with engine.begin() as connection:
            prepare_quiescent_apply_transaction(connection)
            before = _state_from_connection(
                connection,
                target,
                None,
                False,
            )
            validate_base_target(before, target)
            validate_backup_matches_target(backup, before)
            migration = run_exact_upgrade(connection, target)
            verified = _verified_head_from_connection(
                connection,
                target,
                before["legacyData"],
                False,
            )
            legacy_preservation = compare_legacy_data(
                before["legacyData"],
                verified["state"]["legacyData"],
            )
            result = {
                "before": before,
                "migration": migration,
                "verified": verified,
                "legacyPreservation": legacy_preservation,
            }
        return result
    except (V377ApplyError, V377RoundTripError):
        raise
    except Exception as exc:
        raise V377ApplyError(
            f"transactional v377 apply failed ({type(exc).__name__}); details withheld; "
            "the database transaction was rolled back"
        ) from None
    finally:
        engine.dispose()


def apply_exact_upgrade(
    target: TargetSpec,
    *,
    source_sha: str,
    roundtrip_report: str,
    backup_manifest: str,
) -> dict[str, Any]:
    _prepare_private_artifact_storage()
    contract = validate_revision_contract(ROOT)
    roundtrip_evidence = load_verified_roundtrip_evidence(
        roundtrip_report,
        source_sha=source_sha,
    )
    backup = load_verified_backup(
        target,
        backup_manifest,
        source_sha=source_sha,
        roundtrip_evidence=roundtrip_evidence,
    )
    attempt_marker = _write_attempt_marker(
        target,
        source_sha=source_sha,
        action=APPLY_ACTION,
    )
    transaction = execute_quiescent_upgrade(target, backup)
    command = transaction["migration"]
    verified = transaction["verified"]
    legacy_preservation = transaction["legacyPreservation"]
    result = {
        "schemaVersion": TOOL_VERSION,
        "result": "exact-v377-upgrade-applied-and-verified",
        "completedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "preparationCommitSha": source_sha,
        "target": target.label,
        "database": target.database,
        "previousRevision": BASE_REVISION,
        "currentRevision": HEAD_REVISION,
        "revisionContract": contract,
        **roundtrip_evidence,
        "backupSha256": backup["backupSha256"],
        "backupManifest": backup["verifiedManifestRelativePath"],
        "applyAttemptMarkerRelativePath": attempt_marker,
        "alembicCommand": command,
        "modelParity": verified["modelParity"],
        **legacy_preservation,
        "lockTimeoutMs": LOCK_TIMEOUT_MS,
        "statementTimeoutMs": STATEMENT_TIMEOUT_MS,
        "legacyWriteLockMode": LEGACY_WRITE_LOCK_MODE,
        "legacyWriteLockTableCount": len(LEGACY_WRITE_LOCK_TABLES),
        "singleTransaction": True,
        "downgradeExecuted": False,
        "stampExecuted": False,
        "restoreExecuted": False,
        "automaticRetry": False,
        "secretOrEndpointRecorded": False,
    }
    path = REPORT_DIRECTORY / f"v377_auth_security.{target.label}.apply.json"
    try:
        ensure_private_path_location(ROOT, path)
        verify_private_directory(REPORT_DIRECTORY)
        write_private_text_atomic(
            path,
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        verify_private_file(path)
    except PrivatePathError:
        raise V377ApplyError("private migration apply report write failed") from None
    return {**result, "reportRelativePath": path.relative_to(ROOT).as_posix()}


def render_plan() -> str:
    return "\n".join(
        [
            "v377 local/Neon fresh-backup and exact-upgrade guard",
            "- default action: no file, DB, provider, or network mutation",
            f"- exact current/head: {BASE_REVISION} -> {HEAD_REVISION}",
            f"- lock/statement/process timeouts: {LOCK_TIMEOUT_MS}ms/{STATEMENT_TIMEOUT_MS}ms/{PROCESS_TIMEOUT_SECONDS}s",
            "- backup: new PostgreSQL custom archive, checksum, TOC, manifest; no overwrite",
            "- backup/apply: fixed completed isolated-roundtrip report for the same source SHA",
            "- one attempt: exclusive local/Neon backup/apply markers; manual and automatic retry forbidden",
            "- apply: exact 22-table SHARE ROW EXCLUSIVE lock, fingerprint, Alembic, and parity check in one transaction",
            "- Neon: direct endpoint + system CA hostname verification; pooler forbidden",
            "- PostgreSQL clients: inherited PG* defaults removed; trusted absolute executable only",
            "- upgrade only: no downgrade/stamp/restore/retry/reset/seed/create/drop path",
            "- modes: --inspect, --backup, or --apply with every exact confirmation",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--inspect", action="store_true", help="read-only exact-target inspection")
    modes.add_argument("--backup", action="store_true", help="create one fresh verified local backup")
    modes.add_argument("--apply", action="store_true", help="apply exact v377 after fresh backup")
    parser.add_argument("--target", choices=("local", "neon"))
    parser.add_argument("--roundtrip-report", default="")
    parser.add_argument("--backup-manifest", default="")
    parser.add_argument("--confirm-source-sha", default="")
    parser.add_argument("--confirm-target-database", default="")
    parser.add_argument("--confirm-current-revision", default="")
    parser.add_argument("--confirm-head-revision", default="")
    parser.add_argument("--confirm-v377-sha256", default="")
    parser.add_argument("--confirm-action", default="")
    args = parser.parse_args()

    if not args.inspect and not args.backup and not args.apply:
        print(render_plan())
        return 0
    if not args.target:
        print("ERROR: --target local|neon is required", file=sys.stderr)
        return 2
    try:
        target = load_target(args.target)
        if args.inspect:
            result = inspect_target_readiness(target)
            print("v377 target readiness (read-only)")
            print(f"- target/current: {result['target']} / {result['currentRevision']}")
            print(f"- result: {result['result']}")
            print("- DB/file mutation attempted: no")
            return 0

        expected_action = BACKUP_ACTION if args.backup else APPLY_ACTION
        validate_execution_confirmation(
            source_sha=args.confirm_source_sha,
            target=target,
            target_database=args.confirm_target_database,
            current_revision=args.confirm_current_revision,
            head_revision=args.confirm_head_revision,
            head_sha256=args.confirm_v377_sha256,
            action=args.confirm_action,
            expected_action=expected_action,
        )
        if args.backup:
            result = create_fresh_backup(
                target,
                source_sha=args.confirm_source_sha,
                roundtrip_report=args.roundtrip_report,
            )
            print("v377 fresh backup")
            print(f"- target/current: {target.label} / {BASE_REVISION}")
            print(f"- result: {result['result']}")
            print(f"- backup SHA-256: {result['backupSha256']}")
            print(f"- manifest: {result['manifestRelativePath']}")
            print("- database mutation attempted: no")
            return 0

        result = apply_exact_upgrade(
            target,
            source_sha=args.confirm_source_sha,
            roundtrip_report=args.roundtrip_report,
            backup_manifest=args.backup_manifest,
        )
        print("v377 exact target upgrade")
        print(f"- target/current: {target.label} / {result['currentRevision']}")
        print(f"- result: {result['result']}")
        print(f"- sanitized local evidence: {result['reportRelativePath']}")
        return 0
    except (V377ApplyError, V377RoundTripError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - environment safety net
        print(f"ERROR: v377 target guard failed ({type(exc).__name__}); sensitive output withheld", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

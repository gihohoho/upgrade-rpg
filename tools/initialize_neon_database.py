#!/usr/bin/env python3
"""Read-only completion guard for the initialized Neon database.

The approved v343 execution restored the pinned archive once.  The approved
v344 recovery reverified the UTC-canonical application digest and stamped only
``v295_initial_schema``.  The final state is 22 application tables / 748 rows
plus one ``alembic_version`` table / row.

The default path is static and ``--inspect`` is read-only.  Both historical
mutation paths, ``--execute`` and ``--resume-stamp``, are disabled so neither
the restore nor the stamp can be repeated.  There is no automatic cleanup,
reset, truncate, migration upgrade, or Render action.  Connection values are
loaded from a Git-ignored local file and are never included in commands,
reports, or displayed errors.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import json
import os
import re
import ssl
import subprocess
import sys
from datetime import date, datetime, time, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import MetaData, Table, URL, create_engine, inspect, select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Connection

from check_neon_readonly_connectivity import (
    ConnectionTarget,
    _load_local_values,
    _validate_pair,
    _verified_ssl_context,
)
from check_postgres_schema_equivalence import reflected_signature


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
PLAN_FILE = ROOT / "deploy/neon-database-initialization-migration.example.json"
ENV_FILE = ROOT / "deploy/.env.production"
BACKUP_FILE = (
    ROOT
    / "local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump"
)
REVISION_FILE = (
    BACKEND / "alembic/versions/v295_initial_schema_initial_postgresql_schema.py"
)
PYTHON = BACKEND / ".venv/Scripts/python.exe"
PG_BIN = Path(r"C:\Program Files\PostgreSQL\16\bin")
PG_RESTORE = PG_BIN / "pg_restore.exe"
PSQL = PG_BIN / "psql.exe"
LOCAL_REPORT_DIR = ROOT / "local-review-artifacts/neon"
LOCAL_CA_BUNDLE = LOCAL_REPORT_DIR / "windows-system-ca-roots.pem"

TOOL_VERSION = "v345.neon-initialization-completed-readonly-guard"
PLAN_VERSION = "v345.neon-initialization-completed-verified-render-preparation-required"
READY_RESULT = "neon-database-initialization-completed-verified-render-preparation-required"
INSPECT_RESULT = "neon-database-initialization-readonly-current-state-verified"
SUCCESS_RESULT = "neon-database-restored-stamped-and-verified"
NEXT_STAGE = "prepare-render-service-creation-exact-sha-approval"

EXPECTED_DATABASE = "neondb"
EXPECTED_ROLE = "neondb_owner"
EXPECTED_POSTGRES_MAJOR = 16
EXPECTED_BACKUP_SHA256 = (
    "b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481"
)
EXPECTED_BACKUP_SIZE = 129635
EXPECTED_REVISION = "v295_initial_schema"
EXPECTED_REVISION_SHA256 = (
    "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa"
)
EXPECTED_SCHEMA_DIGEST = (
    "7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921"
)
EXPECTED_DATA_DIGEST = (
    "4ea23cfd2446b522cc9e85e2a8520160427cf8e3987d9b6ab04f4b99fbf6c00c"
)
LEGACY_SESSION_TIMEZONE_DATA_DIGEST = (
    "ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244"
)
EXPECTED_APP_ROWS = 748
EXPECTED_APP_TABLES = (
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
EXPECTED_ACTION = "verify-restored-and-stamp-once"
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class NeonInitializationError(RuntimeError):
    """Safe-to-display initialization guard failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise NeonInitializationError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_value(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        return {"type": "float", "value": repr(value)}
    if isinstance(value, Decimal):
        return {"type": "decimal", "value": format(value, "f")}
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc)
        return {"type": "datetime", "value": value.isoformat()}
    if isinstance(value, (date, time)):
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


def load_plan() -> dict[str, Any]:
    require(PLAN_FILE.is_file(), "Neon initialization plan is missing")
    try:
        plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise NeonInitializationError(
            f"Neon initialization plan is invalid ({type(exc).__name__})"
        ) from None
    require(isinstance(plan, dict), "Neon initialization plan root must be an object")
    require(plan.get("schemaVersion") == PLAN_VERSION, "Neon plan version differs")
    require(plan.get("result") == READY_RESULT, "Neon plan result differs")
    require(plan.get("nextSafeStage") == NEXT_STAGE, "Neon plan next stage differs")
    require(plan.get("productionResourcesMutated") is True, "restore mutation marker differs")

    gate = plan.get("executionGate") or {}
    require(gate.get("preparationToolReviewed") is True, "preparation tool review is incomplete")
    require(gate.get("readOnlyPreflightRequired") is True, "read-only preflight must be required")
    require(gate.get("stampRecoveryPreparationReady") is True, "stamp recovery preparation record differs")
    require(
        gate.get("restoreVerifiedWithUtcCanonicalDigest") is True,
        "restored data UTC-canonical verification is incomplete",
    )
    require(
        gate.get("exactPreparationShaApprovalRequired") is True,
        "exact preparation SHA approval must be required",
    )
    for key in (
        "databaseInitializationApproved",
        "restoreExecuted",
        "stampExecuted",
        "stampRecoveryApproved",
    ):
        require(gate.get(key) is True, f"completed execution gate must be true: {key}")
    require(gate.get("renderServiceExists") is False, "Render service must not exist yet")
    return plan


def validate_local_artifacts() -> dict[str, str]:
    require(BACKUP_FILE.is_file(), "pinned local backup is missing")
    require(BACKUP_FILE.stat().st_size == EXPECTED_BACKUP_SIZE, "backup size differs")
    require(sha256_file(BACKUP_FILE) == EXPECTED_BACKUP_SHA256, "backup SHA-256 differs")
    require(REVISION_FILE.is_file(), "reviewed Alembic revision is missing")
    require(
        sha256_file(REVISION_FILE) == EXPECTED_REVISION_SHA256,
        "reviewed Alembic revision SHA-256 differs",
    )
    for path in (PYTHON, PG_RESTORE, PSQL):
        require(path.is_file(), f"required existing executable is missing: {path.name}")
    return {
        "backupSha256": EXPECTED_BACKUP_SHA256,
        "revisionSha256": EXPECTED_REVISION_SHA256,
    }


def load_direct_target() -> ConnectionTarget:
    values = _load_local_values(ENV_FILE)
    direct, pooled = _validate_pair(values)
    require(direct.pooled is False, "restore target must be the direct Neon endpoint")
    require(pooled.pooled is True, "local pooled URL classification differs")
    require(direct.database == EXPECTED_DATABASE, "direct target database differs")
    require(direct.user == EXPECTED_ROLE, "direct target role differs")
    return direct


def sqlalchemy_url(target: ConnectionTarget) -> URL:
    return URL.create(
        "postgresql+asyncpg",
        username=target.user,
        password=target.password,
        host=target.host,
        port=target.port,
        database=target.database,
    )


def asyncpg_url(target: ConnectionTarget) -> str:
    return sqlalchemy_url(target).render_as_string(hide_password=False)


def export_windows_system_ca_bundle() -> Path:
    """Export public system trust roots for PostgreSQL 16/OpenSSL on Windows."""
    context = _verified_ssl_context()
    certificates = context.get_ca_certs(binary_form=True)
    require(bool(certificates), "Windows system CA trust store is empty")
    pem = "".join(ssl.DER_cert_to_PEM_cert(item) for item in certificates)
    require("BEGIN CERTIFICATE" in pem, "Windows system CA export is empty")

    LOCAL_CA_BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    partial = LOCAL_CA_BUNDLE.with_name(f".{LOCAL_CA_BUNDLE.name}.partial")
    partial.write_text(pem, encoding="ascii")
    partial.replace(LOCAL_CA_BUNDLE)
    return LOCAL_CA_BUNDLE


def pg_environment(target: ConnectionTarget) -> dict[str, str]:
    ca_bundle = export_windows_system_ca_bundle()
    environment = os.environ.copy()
    environment.update(
        {
            "PGHOST": target.host,
            "PGPORT": str(target.port),
            "PGDATABASE": target.database,
            "PGUSER": target.user,
            "PGPASSWORD": target.password,
            "PGSSLMODE": "verify-full",
            "PGSSLROOTCERT": str(ca_bundle),
            "PGAPPNAME": "upgrade-rpg-neon-initialization",
        }
    )
    return environment


def run_version(executable: Path) -> str:
    try:
        completed = subprocess.run(
            [str(executable), "--version"],
            cwd=ROOT,
            capture_output=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise NeonInitializationError(
            f"cannot inspect {executable.name} ({type(exc).__name__})"
        ) from None
    require(completed.returncode == 0, f"{executable.name} version check failed")
    output = completed.stdout.decode("utf-8", errors="replace").strip()
    match = re.search(r"(\d+)(?:\.\d+)*", output)
    require(match is not None, f"{executable.name} version is unreadable")
    require(
        int(match.group(1)) == EXPECTED_POSTGRES_MAJOR,
        f"{executable.name} major version must remain {EXPECTED_POSTGRES_MAJOR}",
    )
    return output


def build_psql_readonly_command() -> list[str]:
    return [
        str(PSQL),
        "--no-psqlrc",
        "--set=ON_ERROR_STOP=1",
        "--tuples-only",
        "--no-align",
        "--command",
        (
            "BEGIN TRANSACTION READ ONLY; "
            "SELECT current_database(), current_user, "
            "current_setting('server_version'), current_setting('ssl'); "
            "ROLLBACK;"
        ),
    ]


def run_libpq_readonly_preflight(target: ConnectionTarget) -> None:
    run_guarded_subprocess(
        build_psql_readonly_command(),
        environment=pg_environment(target),
        label="PostgreSQL 16 libpq verify-full read-only preflight",
        cwd=ROOT,
        timeout=30,
    )


def collect_integrity_from_connection(connection: Connection) -> dict[str, Any]:
    identity = connection.exec_driver_sql(
        "SELECT current_database(), current_user, "
        "current_setting('server_version'), "
        "current_setting('transaction_read_only')"
    ).one()
    require(identity[0] == EXPECTED_DATABASE, "connected database differs")
    require(identity[1] == EXPECTED_ROLE, "connected role differs")
    require(
        str(identity[2]).split(".", 1)[0] == str(EXPECTED_POSTGRES_MAJOR),
        "connected PostgreSQL major differs",
    )
    require(identity[3] == "on", "inspection transaction is not read-only")

    inspector = inspect(connection)
    table_names = sorted(inspector.get_table_names(schema="public"))
    alembic_revisions = (
        sorted(
            str(value)
            for value in connection.exec_driver_sql(
                "SELECT version_num FROM public.alembic_version"
            ).scalars()
        )
        if "alembic_version" in table_names
        else []
    )
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
            rows.append(
                json.dumps(
                    [canonical_value(row[name]) for name in column_names],
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
            )
        rows.sort()
        data_payload[table_name] = {
            "rowCount": len(rows),
            "rowDigest": hashlib.sha256(
                "\n".join(rows).encode("utf-8")
            ).hexdigest(),
        }

    return {
        "database": EXPECTED_DATABASE,
        "role": EXPECTED_ROLE,
        "serverMajor": EXPECTED_POSTGRES_MAJOR,
        "readOnly": True,
        "publicTables": table_names,
        "alembicRevisions": alembic_revisions,
        "tables": {
            name: {
                "schemaDigest": sha256_json(schema_payload[name]),
                **data_payload[name],
            }
            for name in table_names
        },
    }


async def collect_integrity_async(target: ConnectionTarget) -> dict[str, Any]:
    engine = create_async_engine(
        sqlalchemy_url(target),
        pool_size=1,
        max_overflow=0,
        connect_args={
            "ssl": _verified_ssl_context(),
            "server_settings": {
                "application_name": "upgrade-rpg-neon-initialization-readonly"
            },
        },
    )
    try:
        async with engine.connect() as connection:
            async with connection.begin():
                await connection.exec_driver_sql("SET TRANSACTION READ ONLY")
                return await connection.run_sync(collect_integrity_from_connection)
    except NeonInitializationError:
        raise
    except Exception as exc:
        # Driver messages can contain connection details, so never include them.
        raise NeonInitializationError(
            f"Neon read-only inspection failed ({type(exc).__name__})"
        ) from None
    finally:
        await engine.dispose()


def collect_integrity(target: ConnectionTarget) -> dict[str, Any]:
    return asyncio.run(collect_integrity_async(target))


def application_signature(signature: dict[str, Any]) -> dict[str, Any]:
    tables = signature.get("tables") or {}
    expected = tuple(sorted(EXPECTED_APP_TABLES))
    missing = [name for name in expected if name not in tables]
    require(not missing, f"application tables are missing: {missing}")
    selected = {name: tables[name] for name in expected}
    schema_digest = sha256_json(
        {name: item["schemaDigest"] for name, item in selected.items()}
    )
    data_digest = sha256_json(
        {
            name: {"rowCount": item["rowCount"], "rowDigest": item["rowDigest"]}
            for name, item in selected.items()
        }
    )
    return {
        "tableCount": len(expected),
        "rowCount": sum(int(item["rowCount"]) for item in selected.values()),
        "schemaDigest": schema_digest,
        "dataDigest": data_digest,
    }


def require_empty_target(signature: dict[str, Any]) -> None:
    require(signature.get("publicTables") == [], "Neon target is no longer empty")


def require_application_restore(signature: dict[str, Any], *, stamped: bool) -> None:
    expected_tables = sorted(
        [*EXPECTED_APP_TABLES, *(["alembic_version"] if stamped else [])]
    )
    require(
        signature.get("publicTables") == expected_tables,
        "restored public table inventory differs",
    )
    model = application_signature(signature)
    require(model["tableCount"] == len(EXPECTED_APP_TABLES), "application table count differs")
    require(model["rowCount"] == EXPECTED_APP_ROWS, "application row count differs")
    require(model["schemaDigest"] == EXPECTED_SCHEMA_DIGEST, "application schema digest differs")
    require(model["dataDigest"] == EXPECTED_DATA_DIGEST, "application data digest differs")

    alembic = (signature.get("tables") or {}).get("alembic_version")
    if stamped:
        require(isinstance(alembic, dict), "alembic_version table is missing")
        require(alembic.get("rowCount") == 1, "alembic_version row count differs")
        require(
            signature.get("alembicRevisions") == [EXPECTED_REVISION],
            "alembic current revision differs",
        )
    else:
        require(alembic is None, "backup unexpectedly restored alembic_version")
        require(signature.get("alembicRevisions") == [], "pre-stamp Alembic revision differs")


def git_output(*args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise NeonInitializationError(f"Git check failed ({type(exc).__name__})") from None
    require(completed.returncode == 0, f"Git check failed: {' '.join(args)}")
    return completed.stdout.decode("utf-8", errors="replace").strip()


def require_exact_approval(
    *,
    preparation_sha: str,
    target: str,
    backup_sha: str,
    revision: str,
    action: str,
) -> None:
    require(SHA_PATTERN.fullmatch(preparation_sha) is not None, "preparation SHA must be 40 lowercase hex characters")
    require(target == EXPECTED_DATABASE, f"target confirmation must be {EXPECTED_DATABASE}")
    require(backup_sha == EXPECTED_BACKUP_SHA256, "backup SHA confirmation differs")
    require(revision == EXPECTED_REVISION, "revision confirmation differs")
    require(action == EXPECTED_ACTION, f"action confirmation must be {EXPECTED_ACTION}")
    require(git_output("branch", "--show-current") == "main", "execution branch must be main")
    require(git_output("rev-parse", "HEAD") == preparation_sha, "approved SHA is not current HEAD")
    require(
        git_output("rev-parse", "--verify", "origin/main") == preparation_sha,
        "approved SHA is not pushed origin/main",
    )
    require(git_output("status", "--porcelain") == "", "working tree must be clean")


def build_restore_command() -> list[str]:
    command = [
        str(PG_RESTORE),
        "--exit-on-error",
        "--single-transaction",
        "--no-owner",
        "--no-privileges",
        f"--dbname={EXPECTED_DATABASE}",
        str(BACKUP_FILE),
    ]
    require("--create" not in command and "--clean" not in command, "unsafe restore flag detected")
    return command


def run_guarded_subprocess(
    command: list[str],
    *,
    environment: dict[str, str],
    label: str,
    cwd: Path,
    timeout: int,
) -> None:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise NeonInitializationError(f"{label} failed ({type(exc).__name__})") from None
    require(completed.returncode == 0, f"{label} failed (exit={completed.returncode})")


def build_alembic_environment(target: ConnectionTarget) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "DATABASE_URL": asyncpg_url(target),
            "JWT_SECRET_KEY": "neon-initialization-process-only-" + ("j" * 32),
            "ADMIN_WRITE_DEV_KEY": "neon-initialization-process-only-" + ("a" * 32),
            "CORS_ORIGINS": "[]",
            "DB_POOL_SIZE": "1",
            "DB_MAX_OVERFLOW": "0",
        }
    )
    return environment


def build_stamp_command() -> list[str]:
    return [
        str(PYTHON),
        "-m",
        "alembic",
        "--config",
        "alembic.ini",
        "stamp",
        EXPECTED_REVISION,
    ]


def write_success_report(
    *,
    preparation_sha: str,
    before: dict[str, Any],
    after: dict[str, Any],
) -> Path:
    model = application_signature(after)
    report = {
        "schemaVersion": TOOL_VERSION,
        "completedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "preparationCommitSha": preparation_sha,
        "provider": "Neon Free",
        "region": "aws-ap-southeast-1",
        "database": EXPECTED_DATABASE,
        "role": EXPECTED_ROLE,
        "backupSha256": EXPECTED_BACKUP_SHA256,
        "reviewedRevision": EXPECTED_REVISION,
        "recoveryMode": "verify-restored-and-stamp-once",
        "preStampPublicTableCount": len(before["publicTables"]),
        "applicationTableCount": model["tableCount"],
        "applicationRowCount": model["rowCount"],
        "applicationSchemaDigest": model["schemaDigest"],
        "applicationDataDigest": model["dataDigest"],
        "finalPublicTableCount": len(after["publicTables"]),
        "alembicVersionRows": after["tables"]["alembic_version"]["rowCount"],
        "alembicCurrentRevision": after["alembicRevisions"][0],
        "directConnectionOnly": True,
        "tlsCertificateAndHostnameVerified": True,
        "automaticRetryOrCleanup": False,
        "secretOrEndpointRecorded": False,
        "result": SUCCESS_RESULT,
        "nextSafeStage": "review-neon-initialization-evidence-and-prepare-render-service-exact-sha-approval",
    }
    LOCAL_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = LOCAL_REPORT_DIR / f"neon-initialization-{preparation_sha}.json"
    partial = path.with_name(f".{path.name}.partial")
    partial.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    partial.replace(path)
    return path


def print_preparation_summary(*, connected: bool) -> None:
    print("Neon database initialization completion guard")
    print("- target: Neon Free / AWS Singapore / PostgreSQL 16 / neondb / neondb_owner")
    print("- current state: 22 application tables / 748 rows / exact v295 Alembic stamp")
    print("- restore retry and stamp retry: forbidden")
    print("- next mutation: none; Render preparation requires a separate exact-SHA approval")
    print("- automatic retry/cleanup/reset/Render action: no")
    print("- secret/endpoint printed or recorded: no")
    print(f"- read-only target inspection: {'yes' if connected else 'no'}")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--inspect", action="store_true", help="perform the read-only target preflight")
    mode.add_argument("--execute", action="store_true", help="disabled after the completed restore")
    mode.add_argument(
        "--resume-stamp",
        action="store_true",
        help="verify the restored state and perform only the exact approved stamp",
    )
    parser.add_argument("--confirm-preparation-sha", default="")
    parser.add_argument("--confirm-target", default="")
    parser.add_argument("--confirm-backup-sha", default="")
    parser.add_argument("--confirm-revision", default="")
    parser.add_argument("--confirm-action", default="")
    args = parser.parse_args()

    try:
        load_plan()
        validate_local_artifacts()
        run_version(PG_RESTORE)
        run_version(PSQL)
        target = load_direct_target()

        if not args.inspect and not args.execute and not args.resume_stamp:
            print_preparation_summary(connected=False)
            print("- database mutation attempted: no")
            print(f"- result: {READY_RESULT}")
            print(f"- next safe stage: {NEXT_STAGE}")
            return 0

        if args.inspect:
            state = collect_integrity(target)
            require_application_restore(state, stamped=True)
            run_libpq_readonly_preflight(target)
            print_preparation_summary(connected=True)
            print("- current public tables/rows: 23/749; Alembic: exact v295_initial_schema")
            print("- PostgreSQL 16 libpq + exported Windows system CA + verify-full: passed")
            print("- database mutation attempted: no")
            print(f"- result: {INSPECT_RESULT}")
            print(f"- next safe stage: {NEXT_STAGE}")
            return 0

        if args.execute or args.resume_stamp:
            raise NeonInitializationError(
                "Neon initialization is complete; restore and stamp retries are disabled"
            )

        require_exact_approval(
            preparation_sha=args.confirm_preparation_sha,
            target=args.confirm_target,
            backup_sha=args.confirm_backup_sha,
            revision=args.confirm_revision,
            action=args.confirm_action,
        )
        before = collect_integrity(target)
        require_application_restore(before, stamped=False)
        run_libpq_readonly_preflight(target)

        run_guarded_subprocess(
            build_stamp_command(),
            environment=build_alembic_environment(target),
            label="exact Neon Alembic stamp",
            cwd=BACKEND,
            timeout=180,
        )
        stamped = collect_integrity(target)
        require_application_restore(stamped, stamped=True)
        report = write_success_report(
            preparation_sha=args.confirm_preparation_sha,
            before=before,
            after=stamped,
        )

        print_preparation_summary(connected=True)
        print("- existing restore: application integrity reverified; no restore retry")
        print(f"- Alembic: exact {EXPECTED_REVISION} stamped and verified")
        print(f"- sanitized local report: {report.relative_to(ROOT)}")
        print(f"- result: {SUCCESS_RESULT}")
        print("- next safe stage: review-neon-initialization-evidence-and-prepare-render-service-exact-sha-approval")
        return 0
    except NeonInitializationError as exc:
        print(f"Neon database initialization stopped: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        # Imported parsers and database libraries may include a DSN in messages.
        print(
            f"Neon database initialization stopped safely ({type(exc).__name__})",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())

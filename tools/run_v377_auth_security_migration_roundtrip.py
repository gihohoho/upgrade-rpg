#!/usr/bin/env python3
"""Guard one synthetic PostgreSQL round trip for the v377 auth migrations.

The default mode only prints the immutable execution boundary. ``--inspect``
performs read-only source/catalog checks. ``--execute`` is the only mutation
path and is intentionally limited to one new fixed isolated database:

    v295_initial_schema -> v377_auth_email_public_security
    -> v295_initial_schema -> v377_auth_email_public_security

It never restores real data, targets the source/Neon databases, stamps, drops a
database, retries automatically, or prints a DSN or synthetic row value.
The fixed private report is created exclusively before database creation and
remains as the durable no-retry marker even when the attempt fails.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Callable

from sqlalchemy import CheckConstraint, create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from _safe_subprocess import decode_output
from check_postgres_runtime_readonly_state import load_backend_objects, to_sync_url
from check_postgres_schema_equivalence import (
    compare_table,
    model_signature,
    reflected_signature,
)
from postgres_client_safety import (
    filtered_libpq_environment,
    guard_sqlalchemy_libpq_engine,
)
from private_artifacts import (
    PrivatePathError,
    ensure_private_path_location,
    harden_private_directory,
    harden_private_tree,
    verify_private_directory,
    verify_private_file,
    write_private_text_atomic,
    write_private_text_exclusive,
)


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
LOCAL_ENV_FILE = BACKEND / ".env"
PYTHON = BACKEND / ".venv/Scripts/python.exe"
POSTGRES_CONTAINER = "upgrade_rpg_postgres"
SOURCE_DATABASE = "rpg_game"
SOURCE_DATABASE_USER = "rpg_user"
SOURCE_DATABASE_PORT = 55432
ISOLATED_DATABASE = "rpg_game_v377_auth_security_roundtrip"
BASE_REVISION = "v295_initial_schema"
EMAIL_REVISION = "v371_email_identity_lifecycle"
HEAD_REVISION = "v377_auth_email_public_security"
REVISION_FILES = {
    BASE_REVISION: "v295_initial_schema_initial_postgresql_schema.py",
    EMAIL_REVISION: "v371_email_identity_lifecycle.py",
    HEAD_REVISION: "v377_auth_email_public_security.py",
}
REVISION_SHA256 = {
    BASE_REVISION: "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa",
    EMAIL_REVISION: "2fcff40ada290f7896b5744491921406cdd359ef6090647653c2ec2fd0b4f9e4",
    HEAD_REVISION: "3792de23c53b57e9d2c08dd83889e84a22e98d7dfb9e9dfdd25314bfa56f6eb4",
}
EXPECTED_BASE_APPLICATION_TABLES = 22
EXPECTED_BASE_PUBLIC_TABLES = EXPECTED_BASE_APPLICATION_TABLES + 1
EXPECTED_HEAD_APPLICATION_TABLES = 25
EXPECTED_HEAD_PUBLIC_TABLES = EXPECTED_HEAD_APPLICATION_TABLES + 1
EXPECTED_V295_APPLICATION_SCHEMA_DIGEST = (
    "7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921"
)
LOCK_TIMEOUT_MS = 5_000
STATEMENT_TIMEOUT_MS = 120_000
PROCESS_TIMEOUT_SECONDS = 150
CONNECT_TIMEOUT_SECONDS = 20
ALEMBIC_GUARD_MODE = "v377"
ALEMBIC_ISOLATED_APPLICATION_NAME = "upgrade-rpg-v377-isolated-migration"
TOOL_VERSION = "v377.auth-security-isolated-roundtrip-guard.v1"
REPORT_PATH = ROOT / "local-review-artifacts/alembic/v377_auth_security.roundtrip.json"
REVIEW_ARTIFACT_ROOT = ROOT / "local-review-artifacts"
EXECUTION_ACTION = "create-synthetic-v295-upgrade-downgrade-v295-reupgrade-v377-once"
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class V377RoundTripError(RuntimeError):
    """Raised when a v377 isolated migration safety boundary fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise V377RoundTripError(message)


def verify_local_environment_file() -> None:
    """Fail closed before reading the ignored local database credential file."""
    try:
        ensure_private_path_location(ROOT, LOCAL_ENV_FILE)
        verify_private_file(LOCAL_ENV_FILE)
    except PrivatePathError:
        raise V377RoundTripError(
            "local environment private-permission verification failed"
        ) from None


def validate_roundtrip_report_absent(
    root: Path = ROOT,
    report_path: Path = REPORT_PATH,
) -> None:
    """Enforce the fixed report as the durable one-attempt marker."""
    try:
        ensure_private_path_location(root, report_path)
    except PrivatePathError:
        raise V377RoundTripError("round-trip report path is unsafe") from None
    require(
        not os.path.lexists(os.fspath(report_path)),
        "fixed round-trip report already exists; automatic retry is forbidden",
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_revision_contract(root: Path = ROOT) -> dict[str, Any]:
    """Validate the exact three-revision source graph without opening a DB."""
    versions = root / "backend/alembic/versions"
    observed_files = sorted(
        path.name for path in versions.glob("*.py") if path.name != "__init__.py"
    )
    expected_files = sorted(REVISION_FILES.values())
    require(observed_files == expected_files, "Alembic revision file boundary changed")

    observed_hashes: dict[str, str] = {}
    for revision_id, filename in REVISION_FILES.items():
        observed = sha256_file(versions / filename)
        require(
            observed == REVISION_SHA256[revision_id],
            f"revision source hash changed: {revision_id}",
        )
        observed_hashes[revision_id] = observed

    try:
        from alembic.config import Config  # noqa: PLC0415
        from alembic.script import ScriptDirectory  # noqa: PLC0415

        config = Config(str(root / "backend/alembic.ini"))
        config.set_main_option("script_location", str(root / "backend/alembic"))
        scripts = ScriptDirectory.from_config(config)
        revisions = list(scripts.walk_revisions(base="base", head="heads"))
    except Exception as exc:
        raise V377RoundTripError(
            f"Alembic graph inspection failed ({type(exc).__name__})"
        ) from None

    parents = {item.revision: item.down_revision for item in revisions}
    require(scripts.get_heads() == [HEAD_REVISION], "v377 must be the only Alembic head")
    require(scripts.get_bases() == [BASE_REVISION], "v295 must remain the only Alembic base")
    require(
        set(parents) == set(REVISION_FILES),
        "Alembic graph contains an unexpected revision",
    )
    require(parents[BASE_REVISION] is None, "v295 base parent changed")
    require(parents[EMAIL_REVISION] == BASE_REVISION, "v371 parent changed")
    require(parents[HEAD_REVISION] == EMAIL_REVISION, "v377 must directly revise v371")
    return {
        "head": HEAD_REVISION,
        "base": BASE_REVISION,
        "revisionIds": [BASE_REVISION, EMAIL_REVISION, HEAD_REVISION],
        "revisionSha256": observed_hashes,
    }


def git_output(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise V377RoundTripError(f"Git preflight failed ({type(exc).__name__})") from None
    require(completed.returncode == 0, "Git preflight command failed")
    return decode_output(completed.stdout).strip()


def validate_execution_confirmation(
    *,
    root: Path,
    source_sha: str,
    target_database: str,
    base_revision: str,
    head_revision: str,
    head_sha256: str,
    action: str,
) -> None:
    require(SHA_PATTERN.fullmatch(source_sha) is not None, "source SHA must be 40 lowercase hex")
    require(target_database == ISOLATED_DATABASE, "isolated database confirmation differs")
    require(base_revision == BASE_REVISION, "base revision confirmation differs")
    require(head_revision == HEAD_REVISION, "head revision confirmation differs")
    require(head_sha256 == REVISION_SHA256[HEAD_REVISION], "v377 source hash confirmation differs")
    require(action == EXECUTION_ACTION, "round-trip action confirmation differs")
    require(git_output(root, "branch", "--show-current") == "main", "execution branch must be main")
    require(git_output(root, "rev-parse", "HEAD") == source_sha, "confirmed source SHA is not HEAD")
    require(
        git_output(root, "rev-parse", "--verify", "origin/main") == source_sha,
        "confirmed source SHA is not pushed origin/main",
    )
    require(git_output(root, "status", "--porcelain") == "", "working tree must be clean")


def local_database_url(database: str) -> str:
    verify_local_environment_file()
    settings, _base = load_backend_objects(ROOT)
    source = make_url(settings.database_url)
    require(source.drivername == "postgresql+asyncpg", "configured local DB driver differs")
    require(source.database == SOURCE_DATABASE, "configured local source database differs")
    require((source.host or "").lower() in {"127.0.0.1", "localhost"}, "local DB host differs")
    require(source.username == SOURCE_DATABASE_USER, "local DB role differs")
    require(int(source.port or 5432) == SOURCE_DATABASE_PORT, "local DB port differs")
    require(not source.query, "configured local DB URL query parameters are forbidden")
    return source.set(database=database).render_as_string(hide_password=False)


def build_alembic_command(command: str, revision: str) -> list[str]:
    require(command in {"upgrade", "downgrade"}, "unsupported Alembic command")
    if command == "upgrade":
        require(revision in {BASE_REVISION, HEAD_REVISION}, "unsafe upgrade target")
    else:
        require(revision == BASE_REVISION, "isolated downgrade must stop at exact v295")
    return [
        str(PYTHON),
        "-m",
        "alembic",
        "--config",
        "alembic.ini",
        command,
        revision,
    ]


def isolated_alembic_environment() -> dict[str, str]:
    environment = filtered_libpq_environment()
    environment.update(
        {
            "DATABASE_URL": local_database_url(ISOLATED_DATABASE),
            "ENVIRONMENT": "local",
            "DEBUG": "false",
            "ALEMBIC_GUARD_MODE": ALEMBIC_GUARD_MODE,
            "ALEMBIC_LOCK_TIMEOUT_MS": str(LOCK_TIMEOUT_MS),
            "ALEMBIC_STATEMENT_TIMEOUT_MS": str(STATEMENT_TIMEOUT_MS),
            "ALEMBIC_APPLICATION_NAME": ALEMBIC_ISOLATED_APPLICATION_NAME,
        }
    )
    return environment


def run_alembic(command: str, revision: str) -> dict[str, Any]:
    environment = isolated_alembic_environment()
    argv = build_alembic_command(command, revision)
    try:
        completed = subprocess.run(
            argv,
            cwd=BACKEND,
            env=environment,
            capture_output=True,
            check=False,
            timeout=PROCESS_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        raise V377RoundTripError(
            f"exact Alembic {command} timed out; inspect the isolated DB and do not retry"
        ) from None
    except (OSError, subprocess.SubprocessError) as exc:
        raise V377RoundTripError(
            f"exact Alembic {command} failed ({type(exc).__name__}); do not retry"
        ) from None
    combined = completed.stdout + b"\n" + completed.stderr
    require(
        completed.returncode == 0,
        f"exact Alembic {command} failed with exit={completed.returncode}; output withheld",
    )
    return {
        "command": f"alembic {command} {revision}",
        "exitCode": completed.returncode,
        "outputSha256": hashlib.sha256(combined).hexdigest(),
    }


def catalog_query() -> str:
    return (
        "SELECT COALESCE(json_agg(row_to_json(q)), '[]'::json)::text FROM ("
        'SELECT datname AS "database", pg_get_userbyid(datdba) AS "owner", '
        'pg_encoding_to_char(encoding) AS "encoding", datcollate AS "collate", '
        'datctype AS "ctype", datlocprovider::text AS "locale_provider", '
        "COALESCE(daticulocale, '') AS \"icu_locale\" FROM pg_database "
        f"WHERE datname IN ('{SOURCE_DATABASE}', '{ISOLATED_DATABASE}') ORDER BY datname"
        ") q;"
    )


def catalog_command() -> list[str]:
    return [
        "docker",
        "exec",
        POSTGRES_CONTAINER,
        "psql",
        "--dbname=postgres",
        f"--username={SOURCE_DATABASE_USER}",
        "--no-password",
        "--tuples-only",
        "--no-align",
        "--set=ON_ERROR_STOP=1",
        f"--command={catalog_query()}",
    ]


def run_catalog(
    *,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, dict[str, Any]]:
    try:
        completed = run_process(
            catalog_command(),
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise V377RoundTripError(f"database catalog inspection failed ({type(exc).__name__})") from None
    require(completed.returncode == 0, "database catalog inspection failed; output withheld")
    try:
        rows = json.loads(decode_output(completed.stdout).strip())
    except json.JSONDecodeError:
        raise V377RoundTripError("database catalog returned invalid JSON") from None
    require(isinstance(rows, list), "database catalog result must be a list")
    return {str(item.get("database")): item for item in rows if isinstance(item, dict)}


def build_create_command(source: dict[str, Any]) -> list[str]:
    require(source.get("owner") == SOURCE_DATABASE_USER, "local source DB owner differs")
    encoding = str(source.get("encoding") or "")
    collate = str(source.get("collate") or "")
    ctype = str(source.get("ctype") or "")
    provider = str(source.get("locale_provider") or "")
    require(encoding and collate and ctype, "local source locale metadata is incomplete")
    require(provider in {"c", "i"}, "unsupported PostgreSQL locale provider")
    command = [
        "docker",
        "exec",
        POSTGRES_CONTAINER,
        "createdb",
        f"--username={SOURCE_DATABASE_USER}",
        "--no-password",
        "--maintenance-db=postgres",
        f"--owner={SOURCE_DATABASE_USER}",
        "--template=template0",
        f"--encoding={encoding}",
        f"--lc-collate={collate}",
        f"--lc-ctype={ctype}",
    ]
    if provider == "i":
        icu_locale = str(source.get("icu_locale") or "")
        require(icu_locale != "", "source ICU locale is missing")
        command.extend(["--locale-provider=icu", f"--icu-locale={icu_locale}"])
    command.append(ISOLATED_DATABASE)
    return command


def create_isolated_database(source: dict[str, Any]) -> None:
    try:
        completed = subprocess.run(
            build_create_command(source),
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise V377RoundTripError(f"isolated database creation failed ({type(exc).__name__})") from None
    require(
        completed.returncode == 0,
        "isolated database creation failed; inspect catalog and do not retry",
    )


def validate_isolated_catalog(
    catalog: dict[str, dict[str, Any]],
    source: dict[str, Any],
) -> None:
    """Require the created fixed target to inherit only source locale metadata."""
    require(
        set(catalog) == {SOURCE_DATABASE, ISOLATED_DATABASE},
        "source/fixed-target catalog boundary differs",
    )
    isolated = catalog[ISOLATED_DATABASE]
    require(isolated.get("owner") == SOURCE_DATABASE_USER, "isolated DB owner differs")
    for key in ("encoding", "collate", "ctype", "locale_provider", "icu_locale"):
        require(isolated.get(key) == source.get(key), f"isolated DB {key} differs")


def isolated_sync_connect_args() -> dict[str, Any]:
    return {
        "connect_timeout": CONNECT_TIMEOUT_SECONDS,
        "application_name": "upgrade-rpg-v377-isolated-verification",
        "options": (
            f"-c lock_timeout={LOCK_TIMEOUT_MS}ms "
            f"-c statement_timeout={STATEMENT_TIMEOUT_MS}ms"
        ),
    }


def engine_for(database: str):  # type: ignore[no-untyped-def]
    return guard_sqlalchemy_libpq_engine(
        create_engine(
            to_sync_url(local_database_url(database)),
            poolclass=NullPool,
            connect_args=isolated_sync_connect_args(),
            future=True,
            hide_parameters=True,
        )
    )


def collect_state(database: str) -> dict[str, Any]:
    """Collect schema/revision facts and only a digest of the synthetic row."""
    engine = engine_for(database)
    try:
        with engine.connect() as connection:
            identity = connection.exec_driver_sql(
                "SELECT current_database(), current_user"
            ).one()
            require(identity[0] == database, "connected database differs from fixed target")
            require(identity[1] == SOURCE_DATABASE_USER, "connected database role differs")
            inspector = inspect(connection)
            tables = sorted(inspector.get_table_names(schema="public"))
            revisions = (
                sorted(
                    str(value)
                    for value in connection.exec_driver_sql(
                        "SELECT version_num FROM public.alembic_version"
                    ).scalars()
                )
                if "alembic_version" in tables
                else []
            )
            table_schema_digests = {
                table: sha256_json(reflected_signature(inspector, table))
                for table in tables
                if table != "alembic_version"
            }
            fixture = connection.execute(
                text(
                    "SELECT id, username, password_hash, is_active, is_admin, "
                    "created_at, updated_at FROM users "
                    "WHERE username = :username ORDER BY id"
                ),
                {"username": "v377_synthetic_legacy_user"},
            ).mappings().all() if "users" in tables else []
            return {
                "database": database,
                "revision": revisions,
                "publicTables": tables,
                "publicTableCount": len(tables),
                "schemaDigest": sha256_json(table_schema_digests),
                "fixtureCount": len(fixture),
                "fixtureDigest": sha256_json([dict(row) for row in fixture]),
            }
    except V377RoundTripError:
        raise
    except Exception as exc:
        raise V377RoundTripError(
            f"isolated database inspection failed ({type(exc).__name__})"
        ) from None
    finally:
        engine.dispose()


def validate_source_state(state: dict[str, Any]) -> None:
    require(state.get("database") == SOURCE_DATABASE, "source DB identity differs")
    require(state.get("revision") == [BASE_REVISION], "source DB must remain at exact v295")
    require(
        state.get("publicTableCount") == EXPECTED_BASE_PUBLIC_TABLES,
        "source v295 public table count differs",
    )
    require(
        len(state.get("publicTables") or []) == EXPECTED_BASE_PUBLIC_TABLES,
        "source v295 public table list differs",
    )
    require(
        state.get("schemaDigest") == EXPECTED_V295_APPLICATION_SCHEMA_DIGEST,
        "source v295 application schema digest differs",
    )
    for table in (
        "user_email_action_tokens",
        "auth_email_outbox",
        "auth_rate_limit_buckets",
    ):
        require(
            table not in (state.get("publicTables") or []),
            f"source v295 unexpectedly contains {table}",
        )


def validate_base_state(state: dict[str, Any], *, fixture_required: bool) -> None:
    require(state.get("database") == ISOLATED_DATABASE, "isolated DB identity differs")
    require(state.get("revision") == [BASE_REVISION], "isolated DB is not exact v295")
    require(
        state.get("publicTableCount") == EXPECTED_BASE_PUBLIC_TABLES,
        "v295 public table boundary differs",
    )
    require(
        len(state.get("publicTables") or []) == EXPECTED_BASE_PUBLIC_TABLES,
        "v295 public table list differs",
    )
    require(
        state.get("schemaDigest") == EXPECTED_V295_APPLICATION_SCHEMA_DIGEST,
        "isolated v295 application schema digest differs",
    )
    for table in ("user_email_action_tokens", "auth_email_outbox", "auth_rate_limit_buckets"):
        require(table not in (state.get("publicTables") or []), f"v295 unexpectedly contains {table}")
    require(
        state.get("fixtureCount") == (1 if fixture_required else 0),
        "synthetic fixture boundary differs",
    )


def validate_head_state(state: dict[str, Any]) -> None:
    require(state.get("database") == ISOLATED_DATABASE, "isolated DB identity differs")
    require(state.get("revision") == [HEAD_REVISION], "isolated DB is not exact v377")
    require(
        state.get("publicTableCount") == EXPECTED_HEAD_PUBLIC_TABLES,
        "v377 public table boundary differs",
    )
    for table in ("user_email_action_tokens", "auth_email_outbox", "auth_rate_limit_buckets"):
        require(table in (state.get("publicTables") or []), f"v377 is missing {table}")
    require(state.get("fixtureCount") == 1, "synthetic legacy fixture was not preserved")


def model_table_differences(
    inspector: Any,
    table_name: str,
    model_table: Any,
) -> list[dict[str, str]]:
    """Compare structure while avoiding PostgreSQL CHECK text re-rendering drift.

    The immutable revision hashes and DB-free source parity smoke validate each
    CHECK expression. PostgreSQL rewrites varchar ``IN`` expressions during
    reflection, so the live check verifies the exact source-controlled names.
    """
    differences = [
        item.__dict__
        for item in compare_table(
            table_name,
            model_signature(model_table),
            reflected_signature(inspector, table_name),
        )
        if item.category != "check"
    ]
    expected_checks = sorted(
        str(constraint.name or "")
        for constraint in model_table.constraints
        if isinstance(constraint, CheckConstraint)
    )
    observed_checks = sorted(
        str(item.get("name") or "")
        for item in inspector.get_check_constraints(table_name, schema="public")
    )
    if expected_checks != observed_checks:
        differences.append(
            {
                "category": "check-name",
                "table": table_name,
                "detail": "model/database named CHECK boundary differs",
            }
        )
    return differences


def validate_model_parity(database: str) -> dict[str, Any]:
    verify_local_environment_file()
    settings, Base = load_backend_objects(ROOT)
    del settings
    model_tables = {table.name: table for table in Base.metadata.sorted_tables}
    require(len(model_tables) == EXPECTED_HEAD_APPLICATION_TABLES, "model table count differs")
    engine = engine_for(database)
    try:
        with engine.connect() as connection:
            inspector = inspect(connection)
            actual = set(inspector.get_table_names(schema="public")) - {"alembic_version"}
            require(actual == set(model_tables), "v377 DB/model table set differs")
            differences: list[dict[str, str]] = []
            for name in sorted(model_tables):
                differences.extend(
                    model_table_differences(
                        inspector,
                        name,
                        model_tables[name],
                    )
                )
            require(not differences, "v377 DB/model schema parity differs")
            fixture = connection.execute(
                text(
                    "SELECT email_original, email_canonical, email_verified_at, auth_version "
                    "FROM users WHERE username = :username"
                ),
                {"username": "v377_synthetic_legacy_user"},
            ).one()
            require(tuple(fixture[:3]) == (None, None, None), "legacy email columns were backfilled")
            require(int(fixture[3]) == 0, "legacy auth_version default differs")
            return {"modelTableCount": len(model_tables), "differenceCount": 0}
    except V377RoundTripError:
        raise
    except Exception as exc:
        raise V377RoundTripError(f"v377 model parity failed ({type(exc).__name__})") from None
    finally:
        engine.dispose()


def insert_synthetic_base_fixture() -> None:
    engine = engine_for(ISOLATED_DATABASE)
    try:
        with engine.begin() as connection:
            existing = connection.execute(text("SELECT count(*) FROM users")).scalar_one()
            require(int(existing) == 0, "isolated v295 users table is not empty")
            connection.execute(
                text(
                    "INSERT INTO users "
                    "(username, password_hash, is_active, is_admin, created_at, updated_at) "
                    "VALUES (:username, :password_hash, true, false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                ),
                {
                    "username": "v377_synthetic_legacy_user",
                    "password_hash": "synthetic-not-a-real-password-hash",
                },
            )
    finally:
        engine.dispose()


def insert_synthetic_head_rows() -> dict[str, int]:
    engine = engine_for(ISOLATED_DATABASE)
    try:
        with engine.begin() as connection:
            user_id = connection.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {"username": "v377_synthetic_legacy_user"},
            ).scalar_one()
            connection.execute(
                text(
                    "INSERT INTO auth_rate_limit_buckets "
                    "(scope, subject_digest, window_started_at, request_count, failure_count, "
                    "created_at, updated_at) VALUES "
                    "('register:email', :digest, CURRENT_TIMESTAMP, 1, 0, "
                    "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                ),
                {"digest": "a" * 64},
            )
            connection.execute(
                text(
                    "INSERT INTO auth_email_outbox "
                    "(user_id, purpose, target_digest, status, available_at, attempt_count, "
                    "created_at, updated_at) VALUES "
                    "(:user_id, 'verify_email', :digest, 'pending', CURRENT_TIMESTAMP, 0, "
                    "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                ),
                {"user_id": user_id, "digest": "b" * 64},
            )
            rate_count = connection.execute(
                text("SELECT count(*) FROM auth_rate_limit_buckets")
            ).scalar_one()
            outbox_count = connection.execute(
                text("SELECT count(*) FROM auth_email_outbox")
            ).scalar_one()
            require(int(rate_count) == 1 and int(outbox_count) == 1, "synthetic head rows differ")
            return {"authRateLimitBuckets": 1, "authEmailOutbox": 1}
    finally:
        engine.dispose()


def prepare_private_report_storage() -> None:
    """Prepare only the dedicated ignored evidence directory during execution."""
    try:
        ensure_private_path_location(ROOT, REVIEW_ARTIFACT_ROOT)
        if not os.path.lexists(os.fspath(REVIEW_ARTIFACT_ROOT)):
            harden_private_directory(REVIEW_ARTIFACT_ROOT, create=True)
        elif not REVIEW_ARTIFACT_ROOT.is_dir():
            raise PrivatePathError("private artifact parent type is unsafe")
        else:
            harden_private_directory(REVIEW_ARTIFACT_ROOT)
        verify_private_directory(REVIEW_ARTIFACT_ROOT)
        ensure_private_path_location(ROOT, REPORT_PATH.parent)
        harden_private_tree(REPORT_PATH.parent, create=True)
        verify_private_directory(REPORT_PATH.parent)
    except PrivatePathError:
        raise V377RoundTripError("private round-trip evidence storage is unavailable") from None


def write_report(payload: dict[str, Any], *, create_only: bool = False) -> None:
    try:
        ensure_private_path_location(ROOT, REPORT_PATH)
        verify_private_directory(REPORT_PATH.parent)
        content = json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"
        if create_only:
            write_private_text_exclusive(
                REPORT_PATH,
                content,
                encoding="utf-8",
            )
        else:
            write_private_text_atomic(
                REPORT_PATH,
                content,
                encoding="utf-8",
            )
    except PrivatePathError:
        raise V377RoundTripError("private round-trip evidence write failed") from None


def inspect_readiness(
    *,
    catalog: dict[str, dict[str, Any]] | None = None,
    source_state: dict[str, Any] | None = None,
    report_root: Path = ROOT,
    report_path: Path = REPORT_PATH,
) -> dict[str, Any]:
    contract = validate_revision_contract(ROOT)
    validate_roundtrip_report_absent(report_root, report_path)
    observed_catalog = catalog if catalog is not None else run_catalog()
    require(SOURCE_DATABASE in observed_catalog, "local source database is missing")
    require(ISOLATED_DATABASE not in observed_catalog, "fixed isolated database already exists")
    observed_source = source_state if source_state is not None else collect_state(SOURCE_DATABASE)
    validate_source_state(observed_source)
    return {
        "toolVersion": TOOL_VERSION,
        "result": "ready-for-v377-isolated-roundtrip-execution",
        "readOnly": True,
        "mutationExecuted": False,
        "sourceDatabase": SOURCE_DATABASE,
        "sourceCurrentRevision": BASE_REVISION,
        "targetDatabase": ISOLATED_DATABASE,
        "targetAbsent": True,
        "revisionContract": contract,
        "syntheticFixtureOnly": True,
        "restoreExecuted": False,
        "dropDatabaseAllowed": False,
        "automaticRetry": False,
    }


def execute_roundtrip(*, source_sha: str) -> dict[str, Any]:
    """Execute the exact approved isolated sequence; never call automatically."""
    require(
        SHA_PATTERN.fullmatch(source_sha) is not None,
        "round-trip source SHA must be 40 lowercase hex",
    )
    readiness = inspect_readiness()
    prepare_private_report_storage()
    source_before = collect_state(SOURCE_DATABASE)
    catalog_before = run_catalog()
    source_metadata = catalog_before[SOURCE_DATABASE]

    checkpoint: dict[str, Any] = {
        "toolVersion": TOOL_VERSION,
        "result": "v377-isolated-roundtrip-in-progress",
        "startedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "preparationCommitSha": source_sha,
        "sourceDatabase": SOURCE_DATABASE,
        "sourceCurrentRevision": BASE_REVISION,
        "targetDatabase": ISOLATED_DATABASE,
        "revisionContract": readiness["revisionContract"],
        "syntheticFixtureOnly": True,
        "restoreExecuted": False,
        "dropDatabaseExecuted": False,
        "automaticRetry": False,
        "completedStages": [],
    }
    write_report(checkpoint, create_only=True)

    create_isolated_database(source_metadata)
    created_catalog = run_catalog()
    validate_isolated_catalog(created_catalog, source_metadata)
    checkpoint["completedStages"].append("isolated-database-created-empty")
    write_report(checkpoint)

    first_base = run_alembic("upgrade", BASE_REVISION)
    insert_synthetic_base_fixture()
    baseline = collect_state(ISOLATED_DATABASE)
    validate_base_state(baseline, fixture_required=True)
    baseline_digest = baseline["fixtureDigest"]
    checkpoint["completedStages"].append("v295-synthetic-baseline-created")
    write_report(checkpoint)

    first_upgrade = run_alembic("upgrade", HEAD_REVISION)
    first_head = collect_state(ISOLATED_DATABASE)
    validate_head_state(first_head)
    first_parity = validate_model_parity(ISOLATED_DATABASE)
    synthetic_head_rows = insert_synthetic_head_rows()
    checkpoint["completedStages"].append("first-v377-upgrade-verified")
    write_report(checkpoint)

    downgrade = run_alembic("downgrade", BASE_REVISION)
    downgraded = collect_state(ISOLATED_DATABASE)
    validate_base_state(downgraded, fixture_required=True)
    require(downgraded["fixtureDigest"] == baseline_digest, "v295 fixture changed after downgrade")
    checkpoint["completedStages"].append("downgrade-to-exact-v295-verified")
    write_report(checkpoint)

    second_upgrade = run_alembic("upgrade", HEAD_REVISION)
    second_head = collect_state(ISOLATED_DATABASE)
    validate_head_state(second_head)
    second_parity = validate_model_parity(ISOLATED_DATABASE)
    require(second_head["schemaDigest"] == first_head["schemaDigest"], "round-trip schema differs")
    require(second_head["fixtureDigest"] == baseline_digest, "fixture changed after re-upgrade")

    engine = engine_for(ISOLATED_DATABASE)
    try:
        with engine.connect() as connection:
            remaining = {
                "authRateLimitBuckets": int(
                    connection.execute(text("SELECT count(*) FROM auth_rate_limit_buckets")).scalar_one()
                ),
                "authEmailOutbox": int(
                    connection.execute(text("SELECT count(*) FROM auth_email_outbox")).scalar_one()
                ),
            }
    finally:
        engine.dispose()
    require(remaining == {"authRateLimitBuckets": 0, "authEmailOutbox": 0}, "new tables were not recreated empty")

    source_after = collect_state(SOURCE_DATABASE)
    validate_source_state(source_after)
    require(source_after["schemaDigest"] == source_before["schemaDigest"], "source schema changed")
    require(source_after["fixtureDigest"] == source_before["fixtureDigest"], "source fixture digest changed")
    catalog_after = run_catalog()
    validate_isolated_catalog(catalog_after, source_metadata)
    require(
        catalog_after[SOURCE_DATABASE] == source_metadata,
        "source catalog metadata changed",
    )

    result = {
        **checkpoint,
        "result": "v377-isolated-upgrade-downgrade-reupgrade-verified",
        "completedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "completedStages": [
            *checkpoint["completedStages"],
            "second-v377-upgrade-verified",
        ],
        "alembicCommands": [first_base, first_upgrade, downgrade, second_upgrade],
        "baselineFixtureDigest": baseline_digest,
        "firstHeadSchemaDigest": first_head["schemaDigest"],
        "secondHeadSchemaDigest": second_head["schemaDigest"],
        "firstModelParity": first_parity,
        "secondModelParity": second_parity,
        "syntheticHeadRowsBeforeDowngrade": synthetic_head_rows,
        "syntheticHeadRowsAfterReupgrade": remaining,
        "sourcePreserved": True,
        "finalTargetRevision": HEAD_REVISION,
    }
    write_report(result)
    return result


def render_plan() -> str:
    return "\n".join(
        [
            "v377 auth security isolated PostgreSQL round-trip guard",
            "- default action: no DB connection or mutation",
            f"- fixed target: {ISOLATED_DATABASE}",
            f"- exact sequence: {BASE_REVISION} -> {HEAD_REVISION} -> {BASE_REVISION} -> {HEAD_REVISION}",
            "- fixture: synthetic values only; no backup restore or production row copy",
            f"- lock/statement/process timeouts: {LOCK_TIMEOUT_MS}ms/{STATEMENT_TIMEOUT_MS}ms/{PROCESS_TIMEOUT_SECONDS}s",
            "- stamp/drop/reset/seed/automatic retry: forbidden",
            "- use --inspect for read-only readiness; --execute requires every exact confirmation",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--inspect", action="store_true", help="read-only source/catalog readiness")
    modes.add_argument("--execute", action="store_true", help="execute the exact isolated round trip once")
    parser.add_argument("--confirm-source-sha", default="")
    parser.add_argument("--confirm-target-database", default="")
    parser.add_argument("--confirm-base-revision", default="")
    parser.add_argument("--confirm-head-revision", default="")
    parser.add_argument("--confirm-v377-sha256", default="")
    parser.add_argument("--confirm-action", default="")
    args = parser.parse_args()

    if not args.inspect and not args.execute:
        print(render_plan())
        return 0
    try:
        if args.inspect:
            result = inspect_readiness()
            print("v377 isolated migration readiness (read-only)")
            print(f"- result: {result['result']}")
            print(f"- source current / target head: {BASE_REVISION} / {HEAD_REVISION}")
            print("- DB mutation attempted: no")
            return 0

        validate_revision_contract(ROOT)
        validate_execution_confirmation(
            root=ROOT,
            source_sha=args.confirm_source_sha,
            target_database=args.confirm_target_database,
            base_revision=args.confirm_base_revision,
            head_revision=args.confirm_head_revision,
            head_sha256=args.confirm_v377_sha256,
            action=args.confirm_action,
        )
        result = execute_roundtrip(source_sha=args.confirm_source_sha)
        print("v377 isolated migration round trip")
        print(f"- result: {result['result']}")
        print(f"- final target revision: {result['finalTargetRevision']}")
        print(f"- sanitized local evidence: {REPORT_PATH.relative_to(ROOT)}")
        return 0
    except V377RoundTripError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - environment safety net
        print(f"ERROR: v377 guard failed ({type(exc).__name__}); sensitive output withheld", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Inspect PostgreSQL/FastAPI deployment runtime readiness without changing state.

v307 is a read-only deployment/runtime preflight. It verifies the completed
PostgreSQL baseline, confirms that the current schema still needs no next
revision, inspects the FastAPI database/session/health paths, inventories the
local environment file by key name only, checks Docker Compose safety markers,
reads the live PostgreSQL identity/revision in a read-only transaction, and
optionally calls the FastAPI DB health endpoint with GET.

It never edits ``.env``, starts/stops Docker, removes volumes, creates revisions,
or runs Alembic stamp/upgrade/downgrade. Secret values are never printed.
"""
from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Iterator
import urllib.error
import urllib.request

from _safe_subprocess import run_captured
from check_postgres_backup_restore_preflight import SOURCE_DATABASE
from check_postgres_next_revision_preflight import (
    NO_REVISION_RESULT,
    inspect_next_revision_preflight,
)
from check_postgres_runtime_readonly_state import load_backend_objects, to_sync_url
from upgrade_postgres_migration_test_database import REVISION_ID, REVISION_SHA256

TOOL_VERSION = "v307.postgres-deployment-runtime-readiness-readonly"
READY_RESULT = "local-runtime-readiness-verified-production-hardening-required"
PRODUCTION_READY_RESULT = "deployment-runtime-readiness-verified"
BLOCKED_RESULT = "blocked-or-failed"
RUNTIME_ENGINE_BINDING_INSPECTOR = "v309.ast-create-async-engine-binding"

REQUIRED_ENV_KEYS = {
    "APP_NAME",
    "ENVIRONMENT",
    "DEBUG",
    "API_PREFIX",
    "DATABASE_URL",
    "JWT_SECRET_KEY",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "ADMIN_WRITE_DEV_KEY",
    "CORS_ORIGINS",
}

LOCAL_SECRET_DEFAULTS = {
    "jwt": "change-me-before-production",
    "adminWrite": "local-admin-dev-key",
}


class DeploymentRuntimeReadinessError(RuntimeError):
    """Raised when a safety-critical v307 runtime condition is not satisfied."""


@dataclass(frozen=True)
class CommandSnapshot:
    command: str
    ok: bool
    returncode: int
    output: str


@dataclass(frozen=True)
class HealthSnapshot:
    url: str
    ok: bool
    status_code: int | None
    output: str


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DeploymentRuntimeReadinessError(message)


@contextmanager
def working_directory(path: Path) -> Iterator[None]:
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _read(path: Path) -> str:
    if not path.is_file():
        raise DeploymentRuntimeReadinessError(
            f"required runtime file is missing: {path.as_posix()}"
        )
    return path.read_text(encoding="utf-8")


def _is_settings_database_url(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "database_url"
        and isinstance(node.value, ast.Name)
        and node.value.id == "settings"
    )


def _create_async_engine_call_uses_settings_database_url(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    function = node.func
    is_create_async_engine = (
        isinstance(function, ast.Name)
        and function.id == "create_async_engine"
    ) or (
        isinstance(function, ast.Attribute)
        and function.attr == "create_async_engine"
    )
    if not is_create_async_engine:
        return False

    candidates: list[ast.AST] = []
    if node.args:
        candidates.append(node.args[0])
    candidates.extend(
        keyword.value
        for keyword in node.keywords
        if keyword.arg in {"url", "database_url"}
    )
    return any(_is_settings_database_url(candidate) for candidate in candidates)


def _call_uses_settings_database_url(source: str) -> bool:
    """Detect the runtime ``engine`` binding independent of source formatting."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise DeploymentRuntimeReadinessError(
            f"runtime session source is not valid Python: {exc}"
        ) from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            binds_runtime_engine = any(
                isinstance(target, ast.Name) and target.id == "engine"
                for target in node.targets
            )
            if binds_runtime_engine and _create_async_engine_call_uses_settings_database_url(node.value):
                return True
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "engine"
            and node.value is not None
            and _create_async_engine_call_uses_settings_database_url(node.value)
        ):
            return True
    return False


def _env_key_inventory(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {
            "exists": False,
            "keys": [],
            "requiredKeysPresent": False,
            "missingRequiredKeys": sorted(REQUIRED_ENV_KEYS),
        }

    keys: set[str] = set()
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key = line.split("=", 1)[0].strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            keys.add(key)

    missing = sorted(REQUIRED_ENV_KEYS - keys)
    return {
        "exists": True,
        "keys": sorted(keys),
        "requiredKeysPresent": not missing,
        "missingRequiredKeys": missing,
    }


def inspect_runtime_sources(root: Path) -> dict[str, Any]:
    backend = root / "backend"
    config_text = _read(backend / "app/core/config.py")
    session_text = _read(backend / "app/db/session.py")
    main_text = _read(backend / "app/main.py")
    health_text = _read(backend / "app/api/routes/health.py")
    alembic_env_text = _read(backend / "alembic/env.py")
    setup_text = _read(backend / "scripts/setup_dev_db.py")

    app_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((backend / "app").rglob("*.py"))
    )
    startup_mutation_markers = {
        "Base.metadata.create_all": "Base.metadata.create_all" in app_sources,
        "Base.metadata.drop_all": "Base.metadata.drop_all" in app_sources,
        "alembic.command.upgrade": "alembic.command.upgrade" in app_sources,
        "alembic.command.stamp": "alembic.command.stamp" in app_sources,
        "DROP SCHEMA": "DROP SCHEMA" in app_sources,
    }
    startup_mutations = sorted(
        marker for marker, present in startup_mutation_markers.items() if present
    )

    explicit_pool_options = {
        "poolPrePing": "pool_pre_ping=" in session_text,
        "poolSize": "pool_size=" in session_text,
        "maxOverflow": "max_overflow=" in session_text,
        "poolTimeout": "pool_timeout=" in session_text,
        "poolRecycle": "pool_recycle=" in session_text,
    }

    return {
        "databaseUrlFromSettings": _call_uses_settings_database_url(session_text),
        "databaseUrlBindingInspection": RUNTIME_ENGINE_BINDING_INSPECTOR,
        "asyncEngine": "create_async_engine" in session_text,
        "asyncSession": "AsyncSession" in session_text and "async_sessionmaker" in session_text,
        "sessionDependency": "async with AsyncSessionLocal() as session" in session_text,
        "engineEchoUsesDebug": "echo=settings.debug" in session_text,
        "explicitPoolOptions": explicit_pool_options,
        "explicitPoolOptionCount": sum(explicit_pool_options.values()),
        "engineDisposeLifecycle": "engine.dispose" in app_sources,
        "startupMutationMarkers": startup_mutations,
        "startupMutationFree": not startup_mutations,
        "healthDbGetRoute": '@router.get("/health/db")' in health_text,
        "healthDbSelectOne": 'text("SELECT 1")' in health_text,
        "healthDbCommitFree": ".commit(" not in health_text,
        "healthDbResponseSafe": "database_url" not in health_text.lower()
        and "password" not in health_text.lower(),
        "mainIncludesOnlyRouters": "app.include_router" in main_text,
        "mainHasStartupHook": "on_event(\"startup\")" in main_text
        or "lifespan=" in main_text,
        "alembicUsesSettingsDatabaseUrl": "settings.database_url" in alembic_env_text,
        "alembicUsesNullPool": "poolclass=pool.NullPool" in alembic_env_text,
        "setupResetIsSeparateCli": "DROP SCHEMA IF EXISTS public CASCADE" in setup_text
        and "argparse" in setup_text,
        "configUsesEnvFile": 'env_file=".env"' in config_text,
        "configHasEnvironment": "environment: str" in config_text,
        "configHasDebug": "debug: bool" in config_text,
        "configHasDatabaseUrl": "database_url: str" in config_text,
        "sqliteRuntimeMarkers": sorted(
            {
                marker
                for marker in ("sqlite://", "sqlite+aiosqlite://")
                if marker in app_sources.lower()
            }
        ),
    }


def inspect_runtime_settings(root: Path) -> dict[str, Any]:
    try:
        from sqlalchemy.engine import make_url  # noqa: PLC0415

        settings, _Base = load_backend_objects(root)
        url = make_url(str(settings.database_url))
        driver = url.drivername
        database = url.database or ""
        environment = str(settings.environment).strip().lower()
        debug = bool(settings.debug)
        jwt_is_local_default = str(settings.jwt_secret_key) == LOCAL_SECRET_DEFAULTS["jwt"]
        admin_key_is_local_default = (
            str(settings.admin_write_dev_key) == LOCAL_SECRET_DEFAULTS["adminWrite"]
        )
        is_production = environment in {"prod", "production"}
        production_secret_policy_ok = not is_production or (
            not jwt_is_local_default and not admin_key_is_local_default and debug is False
        )
        exact_source = database == SOURCE_DATABASE
        unsafe_target = database in {
            "rpg_game_restore_rehearsal_v290",
            "rpg_game_migration_empty_v290",
        }
        return {
            "loaded": True,
            "environment": environment,
            "debug": debug,
            "driver": driver,
            "database": database,
            "host": url.host,
            "port": url.port,
            "usernameConfigured": bool(url.username),
            "passwordConfigured": url.password is not None,
            "postgresAsyncpg": driver == "postgresql+asyncpg",
            "exactSourceDatabase": exact_source,
            "unsafeNonRuntimeTarget": unsafe_target,
            "jwtUsesLocalDefault": jwt_is_local_default,
            "adminWriteKeyUsesLocalDefault": admin_key_is_local_default,
            "productionSecretPolicyOk": production_secret_policy_ok,
            "corsOriginCount": len(settings.cors_origins),
            "apiPrefix": str(settings.api_prefix),
        }
    except Exception as exc:
        return {
            "loaded": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def inspect_database_runtime(root: Path) -> dict[str, Any]:
    try:
        from sqlalchemy import create_engine, text  # noqa: PLC0415
        from sqlalchemy.pool import NullPool  # noqa: PLC0415

        settings, _Base = load_backend_objects(root)
        engine = create_engine(
            to_sync_url(str(settings.database_url)), poolclass=NullPool, future=True
        )
        try:
            with engine.connect() as connection:
                transaction = connection.begin()
                try:
                    connection.execute(text("SET TRANSACTION READ ONLY"))
                    identity = connection.execute(
                        text(
                            "SELECT current_database(), current_user, current_schema(), "
                            "current_setting('server_version'), "
                            "current_setting('max_connections')::int, pg_is_in_recovery()"
                        )
                    ).one()
                    select_one = int(connection.execute(text("SELECT 1")).scalar_one())
                    revisions = [
                        str(row[0])
                        for row in connection.execute(
                            text(
                                "SELECT version_num FROM public.alembic_version "
                                "ORDER BY version_num"
                            )
                        ).all()
                    ]
                    default_read_only = str(
                        connection.execute(text("SHOW default_transaction_read_only")).scalar_one()
                    )
                finally:
                    transaction.rollback()
            return {
                "connected": True,
                "readOnlyTransaction": True,
                "database": str(identity[0]),
                "user": str(identity[1]),
                "schema": str(identity[2]),
                "serverVersion": str(identity[3]),
                "maxConnections": int(identity[4]),
                "inRecovery": bool(identity[5]),
                "selectOne": select_one,
                "currentRevisions": revisions,
                "defaultTransactionReadOnly": default_read_only,
            }
        finally:
            engine.dispose()
    except Exception as exc:
        return {
            "connected": False,
            "readOnlyTransaction": True,
            "error": f"{type(exc).__name__}: {exc}",
        }


def inspect_docker_static(root: Path) -> dict[str, Any]:
    compose = _read(root / "docker-compose.yml")
    return {
        "postgres16": "image: postgres:16-alpine" in compose,
        "postgresImage": "postgres:16-alpine" if "postgres:16-alpine" in compose else "unknown",
        "restartUnlessStopped": "restart: unless-stopped" in compose,
        "healthcheck": "healthcheck:" in compose and "pg_isready" in compose,
        "namedVolume": "rpg_postgres_data:/var/lib/postgresql/data" in compose
        and "rpg_postgres_data:" in compose,
        "hostPort55432": '"55432:5432"' in compose,
        "adminerEnabled": "image: adminer:4" in compose,
        "adminerPublished": '"8081:8080"' in compose,
        "hardcodedLocalPassword": "POSTGRES_PASSWORD: rpg_password" in compose,
        "imageDigestPinned": "postgres@sha256:" in compose,
        "tlsConfigured": "sslmode" in compose.lower() or "ssl:" in compose.lower(),
        "dockerfileExists": any(root.glob("**/Dockerfile*")),
    }


def run_readonly_command(root: Path, command: list[str], timeout: float = 20) -> CommandSnapshot:
    allowed = {
        ("docker", "compose", "ps", "--format", "json"),
        ("docker", "compose", "config", "--format", "json"),
    }
    if tuple(command) not in allowed:
        raise DeploymentRuntimeReadinessError(
            f"blocked unapproved Docker inspection command: {' '.join(command)}"
        )
    try:
        completed, output = run_captured(command, cwd=root, timeout=timeout, check=False)
        return CommandSnapshot(
            command=" ".join(command),
            ok=completed.returncode == 0,
            returncode=completed.returncode,
            output=output,
        )
    except Exception as exc:  # pragma: no cover - host installation dependent
        return CommandSnapshot(
            command=" ".join(command),
            ok=False,
            returncode=1,
            output=f"{type(exc).__name__}: {exc}",
        )


def _parse_compose_ps(output: str) -> list[dict[str, Any]]:
    if not output.strip():
        return []
    try:
        parsed = json.loads(output)
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)]
        if isinstance(parsed, dict):
            return [parsed]
    except json.JSONDecodeError:
        pass

    rows: list[dict[str, Any]] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            rows.append(item)
    return rows


def inspect_docker_live(root: Path) -> dict[str, Any]:
    ps = run_readonly_command(root, ["docker", "compose", "ps", "--format", "json"])
    config = run_readonly_command(
        root, ["docker", "compose", "config", "--format", "json"]
    )
    rows = _parse_compose_ps(ps.output) if ps.ok else []
    postgres = next(
        (
            row
            for row in rows
            if str(row.get("Service") or row.get("service") or "").lower() == "postgres"
            or "upgrade_rpg_postgres"
            in str(row.get("Name") or row.get("name") or "")
        ),
        None,
    )
    state = str((postgres or {}).get("State") or (postgres or {}).get("state") or "").lower()
    health = str((postgres or {}).get("Health") or (postgres or {}).get("health") or "").lower()
    return {
        # Never expose raw `docker compose config` output because it may contain
        # environment values. Only command/result metadata is retained.
        "commands": [
            {"command": ps.command, "ok": ps.ok, "returncode": ps.returncode},
            {"command": config.command, "ok": config.ok, "returncode": config.returncode},
        ],
        "commandOutputStored": False,
        "composePsOk": ps.ok,
        "composeConfigOk": config.ok,
        "postgresFound": postgres is not None,
        "postgresState": state or None,
        "postgresHealth": health or None,
        "postgresRunning": state == "running",
        "postgresHealthy": health == "healthy",
    }


def fetch_health(url: str, timeout: float) -> HealthSnapshot:
    request = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace").strip()
            return HealthSnapshot(url, 200 <= response.status < 300, response.status, body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        return HealthSnapshot(url, False, exc.code, body or str(exc))
    except Exception as exc:  # pragma: no cover - server may intentionally be stopped
        return HealthSnapshot(url, False, None, f"{type(exc).__name__}: {exc}")


def inspect_operations_policy(root: Path) -> dict[str, Any]:
    required_docs = [
        root / "docs/current/POSTGRES_BASELINE_COMPLETION_STATE.md",
        root / "docs/current/POSTGRES_NEXT_REVISION_PREFLIGHT.md",
        root / "docs/archive/postgres-baseline/POSTGRES_BACKUP_CREATION.md",
        root / "docs/archive/postgres-baseline/POSTGRES_RESTORE_REHEARSAL.md",
        root / "docs/current/POSTGRES_DEPLOYMENT_MIGRATION_RUNBOOK.md",
    ]
    missing = [path.relative_to(root).as_posix() for path in required_docs if not path.is_file()]
    gitignore = _read(root / ".gitignore")
    dockerignore = _read(root / ".dockerignore")
    runbook_text = (
        (root / "docs/current/POSTGRES_DEPLOYMENT_MIGRATION_RUNBOOK.md").read_text(
            encoding="utf-8"
        )
        if not missing
        else ""
    )
    return {
        "requiredDocsPresent": not missing,
        "missingDocs": missing,
        "localBackupsGitIgnored": "/local-backups/" in gitignore,
        "localReviewArtifactsGitIgnored": "/local-review-artifacts/" in gitignore,
        "localBackupsDockerIgnored": "local-backups/" in dockerignore,
        "localReviewArtifactsDockerIgnored": "local-review-artifacts/" in dockerignore,
        "manualMigrationApprovalDocumented": "별도 승인" in runbook_text
        and "자동 migration" in runbook_text,
        "backupBeforeMigrationDocumented": "backup" in runbook_text.lower()
        and "migration 전" in runbook_text,
        "isolatedFirstDocumented": "isolated" in runbook_text.lower()
        and "원본 DB" in runbook_text,
        "startupMigrationForbiddenDocumented": "서버 시작" in runbook_text
        and "upgrade" in runbook_text,
    }


def _warning(key: str, message: str) -> dict[str, str]:
    return {"key": key, "message": message}


def inspect_deployment_runtime_readiness(
    root: Path,
    *,
    next_revision_state: dict[str, Any] | None = None,
    runtime_sources: dict[str, Any] | None = None,
    runtime_settings: dict[str, Any] | None = None,
    database_runtime: dict[str, Any] | None = None,
    docker_static: dict[str, Any] | None = None,
    docker_live: dict[str, Any] | None = None,
    env_example_inventory: dict[str, Any] | None = None,
    env_inventory: dict[str, Any] | None = None,
    operations_policy: dict[str, Any] | None = None,
    health: dict[str, Any] | None = None,
    require_health: bool = False,
) -> dict[str, Any]:
    """Return the v307 readiness classification without mutating runtime state."""
    root = root.resolve()
    next_revision = next_revision_state or inspect_next_revision_preflight(root)
    sources = runtime_sources or inspect_runtime_sources(root)
    settings_state = runtime_settings or inspect_runtime_settings(root)
    database = database_runtime or inspect_database_runtime(root)
    docker_config = docker_static or inspect_docker_static(root)
    docker_state = docker_live or inspect_docker_live(root)
    example_env = env_example_inventory or _env_key_inventory(root / "backend/.env.example")
    local_env = env_inventory or _env_key_inventory(root / "backend/.env")
    ops = operations_policy or inspect_operations_policy(root)
    raw_health = health or asdict(
        fetch_health("http://127.0.0.1:8000/api/v1/health/db", 2.0)
    )
    # The endpoint body is intentionally discarded even though the checked
    # contract is safe. This keeps JSON/report output metadata-only.
    health_state = {
        "url": raw_health.get("url"),
        "ok": bool(raw_health.get("ok")),
        "status_code": raw_health.get("status_code"),
        "responseBodyStored": False,
    }

    _require(
        next_revision.get("result") == NO_REVISION_RESULT,
        "v306 next-revision preflight is not in the no-revision-required state",
    )
    _require(next_revision.get("readOnly") is True, "v306 state is not read-only")
    _require(
        next_revision.get("sourceCurrentRevision") == [REVISION_ID],
        "source current revision differs from the reviewed baseline",
    )
    _require(
        next_revision.get("revisionSha256") == REVISION_SHA256,
        "reviewed baseline revision SHA-256 changed",
    )

    _require(sources.get("databaseUrlFromSettings") is True, "runtime engine bypasses settings.database_url")
    _require(sources.get("asyncEngine") is True, "FastAPI runtime is not using an async SQLAlchemy engine")
    _require(sources.get("asyncSession") is True, "FastAPI runtime AsyncSession setup is missing")
    _require(sources.get("sessionDependency") is True, "FastAPI DB dependency lifecycle changed")
    _require(sources.get("startupMutationFree") is True, "FastAPI startup contains a DB mutation path")
    _require(not sources.get("sqliteRuntimeMarkers"), "SQLite runtime marker detected")
    _require(sources.get("healthDbGetRoute") is True, "GET /health/db contract is missing")
    _require(sources.get("healthDbSelectOne") is True, "DB health contract no longer uses SELECT 1")
    _require(sources.get("healthDbCommitFree") is True, "DB health route may commit")
    _require(sources.get("healthDbResponseSafe") is True, "DB health route may expose connection details")
    _require(sources.get("alembicUsesSettingsDatabaseUrl") is True, "Alembic does not use the shared DATABASE_URL")
    _require(sources.get("alembicUsesNullPool") is True, "Alembic online environment no longer uses NullPool")
    _require(sources.get("setupResetIsSeparateCli") is True, "dangerous local reset path is not isolated in the CLI tool")

    _require(settings_state.get("loaded") is True, "backend settings could not be loaded")
    _require(settings_state.get("postgresAsyncpg") is True, "runtime DATABASE_URL is not postgresql+asyncpg")
    _require(settings_state.get("exactSourceDatabase") is True, "runtime DATABASE_URL does not target exact source rpg_game")
    _require(settings_state.get("unsafeNonRuntimeTarget") is False, "runtime DATABASE_URL targets a rehearsal/migration DB")
    _require(settings_state.get("productionSecretPolicyOk") is True, "production settings use debug or local default secrets")

    _require(database.get("connected") is True, "runtime PostgreSQL connection failed")
    _require(database.get("readOnlyTransaction") is True, "runtime DB inspection was not read-only")
    _require(database.get("database") == SOURCE_DATABASE, "live runtime DB is not exact source rpg_game")
    _require(database.get("selectOne") == 1, "runtime SELECT 1 failed")
    _require(database.get("currentRevisions") == [REVISION_ID], "live runtime DB revision is not the reviewed head")

    _require(docker_config.get("postgres16") is True, "Docker Compose PostgreSQL 16 service changed")
    _require(docker_config.get("restartUnlessStopped") is True, "PostgreSQL restart policy is missing")
    _require(docker_config.get("healthcheck") is True, "PostgreSQL healthcheck is missing")
    _require(docker_config.get("namedVolume") is True, "PostgreSQL named volume boundary is missing")
    _require(docker_state.get("composePsOk") is True, "docker compose ps read-only inspection failed")
    _require(docker_state.get("composeConfigOk") is True, "docker compose config read-only inspection failed")
    _require(docker_state.get("postgresFound") is True, "PostgreSQL container was not found")
    _require(docker_state.get("postgresRunning") is True, "PostgreSQL container is not running")
    _require(docker_state.get("postgresHealthy") is True, "PostgreSQL container is not healthy")

    _require(example_env.get("exists") is True, "backend/.env.example is missing")
    _require(example_env.get("requiredKeysPresent") is True, "backend/.env.example required key set is incomplete")
    _require(ops.get("requiredDocsPresent") is True, "deployment operations documents are incomplete")
    _require(ops.get("localBackupsGitIgnored") is True, "local backups are not Git-ignored")
    _require(ops.get("localReviewArtifactsGitIgnored") is True, "local review artifacts are not Git-ignored")
    _require(ops.get("localBackupsDockerIgnored") is True, "local backups are not Docker-ignored")
    _require(ops.get("localReviewArtifactsDockerIgnored") is True, "local review artifacts are not Docker-ignored")
    _require(ops.get("manualMigrationApprovalDocumented") is True, "manual migration approval policy is missing")
    _require(ops.get("backupBeforeMigrationDocumented") is True, "backup-before-migration policy is missing")
    _require(ops.get("isolatedFirstDocumented") is True, "isolated-first migration policy is missing")
    _require(ops.get("startupMigrationForbiddenDocumented") is True, "startup migration prohibition is missing")

    if require_health:
        _require(health_state.get("ok") is True, "FastAPI DB health endpoint is not reachable")

    warnings: list[dict[str, str]] = []
    if not local_env.get("exists"):
        warnings.append(_warning("env-file-missing", "backend/.env가 없어 기본값으로 실행될 수 있습니다."))
    elif not local_env.get("requiredKeysPresent"):
        warnings.append(_warning("env-key-set-incomplete", "backend/.env에 일부 권장 키가 없습니다."))
    if settings_state.get("environment") not in {"prod", "production"}:
        warnings.append(_warning("environment-not-production", "현재 환경은 production이 아닙니다."))
    if settings_state.get("debug") is True:
        warnings.append(_warning("debug-enabled", "현재 DEBUG=true입니다. 운영에서는 false가 필요합니다."))
    if settings_state.get("jwtUsesLocalDefault") is True:
        warnings.append(_warning("jwt-local-default", "JWT secret이 로컬 기본값입니다."))
    if settings_state.get("adminWriteKeyUsesLocalDefault") is True:
        warnings.append(_warning("admin-write-local-default", "관리자 쓰기 키가 로컬 기본값입니다."))
    if sources.get("explicitPoolOptionCount") == 0:
        warnings.append(_warning("pool-policy-implicit", "연결 풀 크기/timeout/pre-ping 정책이 명시되어 있지 않습니다."))
    if sources.get("engineDisposeLifecycle") is False:
        warnings.append(_warning("engine-dispose-lifecycle-missing", "앱 종료 시 engine.dispose() lifecycle이 없습니다."))
    if docker_config.get("hardcodedLocalPassword") is True:
        warnings.append(_warning("compose-local-password", "docker-compose.yml에 로컬 DB 비밀번호가 고정되어 있습니다."))
    if docker_config.get("adminerPublished") is True:
        warnings.append(_warning("adminer-published", "Adminer 8081 포트가 공개되어 있습니다."))
    if docker_config.get("hostPort55432") is True:
        warnings.append(_warning("postgres-host-port-published", "PostgreSQL 55432 포트가 host에 공개되어 있습니다."))
    if docker_config.get("imageDigestPinned") is False:
        warnings.append(_warning("postgres-image-not-digest-pinned", "PostgreSQL image가 digest로 고정되지 않았습니다."))
    if docker_config.get("tlsConfigured") is False:
        warnings.append(_warning("database-tls-not-configured", "운영 DB TLS 설정이 아직 없습니다."))
    if docker_config.get("dockerfileExists") is False:
        warnings.append(_warning("backend-container-image-missing", "FastAPI 배포용 Dockerfile이 아직 없습니다."))
    if health_state.get("ok") is not True:
        warnings.append(_warning("health-endpoint-not-running", "FastAPI 서버가 꺼져 있어 live health GET은 확인하지 못했습니다."))

    production_hardening_required = bool(warnings)
    result = READY_RESULT if production_hardening_required else PRODUCTION_READY_RESULT
    return {
        "toolVersion": TOOL_VERSION,
        "result": result,
        "readOnly": True,
        "mutationExecuted": False,
        "environmentFileChanged": False,
        "dockerMutationExecuted": False,
        "alembicCommandExecuted": False,
        "baselineCompletionResult": next_revision.get("baselineCompletionResult"),
        "nextRevisionResult": next_revision.get("result"),
        "nextRevisionRequired": False,
        "runtimeSources": sources,
        "runtimeSettings": settings_state,
        "databaseRuntime": database,
        "dockerStatic": docker_config,
        "dockerLive": docker_state,
        "envExample": example_env,
        "envFile": local_env,
        "operationsPolicy": ops,
        "health": health_state,
        "healthRequired": require_health,
        "productionHardeningRequired": production_hardening_required,
        "warningCount": len(warnings),
        "warnings": warnings,
        "nextSafeStage": (
            "separate-runtime-config-hardening-without-db-mutation"
            if production_hardening_required
            else "deployment-release-candidate-readiness-review"
        ),
    }


def render_text(result: dict[str, Any]) -> str:
    settings_state = result["runtimeSettings"]
    sources = result["runtimeSources"]
    database = result["databaseRuntime"]
    docker_static = result["dockerStatic"]
    docker_live = result["dockerLive"]
    env_file = result["envFile"]
    health = result["health"]
    lines = [
        "PostgreSQL/FastAPI deployment runtime readiness preflight (read-only)",
        "No .env edit, Docker start/stop/remove, volume mutation, revision generation, stamp, upgrade, downgrade, DB create/drop/restore, or row write was executed.",
        "",
        f"- baseline completion: {result['baselineCompletionResult']}",
        f"- next revision preflight: {result['nextRevisionResult']} / required=no",
        f"- exact runtime DB: {settings_state['database']}",
        f"- runtime driver: {settings_state['driver']}",
        f"- runtime environment/debug: {settings_state['environment']}/{settings_state['debug']}",
        f"- live PostgreSQL: {database['database']} / {database['serverVersion']} / revision={database['currentRevisions']}",
        f"- live DB inspection transaction: read-only={database['readOnlyTransaction']}",
        f"- FastAPI startup DB mutation markers: {sources['startupMutationMarkers'] or 'none'}",
        f"- FastAPI session: async engine/session={sources['asyncEngine']}/{sources['asyncSession']}",
        f"- explicit runtime pool options: {sources['explicitPoolOptionCount']}",
        f"- DB health contract: GET /api/v1/health/db / SELECT 1 / commit-free={sources['healthDbCommitFree']}",
        f"- Docker PostgreSQL: {docker_static['postgresImage']} / restart={docker_static['restartUnlessStopped']} / healthcheck={docker_static['healthcheck']} / named volume={docker_static['namedVolume']}",
        f"- Docker live PostgreSQL: running={docker_live['postgresRunning']} / healthy={docker_live['postgresHealthy']}",
        f"- backend/.env: {'present' if env_file['exists'] else 'missing'} / required keys={env_file['requiredKeysPresent']}",
        f"- FastAPI live DB health GET: {'ok' if health.get('ok') else 'not-confirmed'}",
        f"- production hardening warnings: {result['warningCount']}",
    ]
    for item in result["warnings"]:
        lines.append(f"    [{item['key']}] {item['message']}")
    lines.extend(
        [
            "- new revision/autogenerate/stamp/upgrade/downgrade approved: no",
            f"- result: {result['result']}",
            f"- next safe stage: {result['nextSafeStage']}",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return 1 only when a safety-critical runtime readiness condition fails",
    )
    parser.add_argument(
        "--require-health",
        action="store_true",
        help="Require the FastAPI DB health GET to be reachable",
    )
    parser.add_argument(
        "--health-url",
        default="http://127.0.0.1:8000/api/v1/health/db",
        help="FastAPI read-only DB health endpoint",
    )
    parser.add_argument("--health-timeout", type=float, default=2.0)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    try:
        result = inspect_deployment_runtime_readiness(
            root,
            health=asdict(fetch_health(args.health_url, args.health_timeout)),
            require_health=args.require_health,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render_text(result))
        return 0
    except Exception as exc:
        payload = {
            "toolVersion": TOOL_VERSION,
            "result": BLOCKED_RESULT,
            "readOnly": True,
            "mutationExecuted": False,
            "reason": f"{type(exc).__name__}: {exc}",
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("PostgreSQL/FastAPI deployment runtime readiness preflight (read-only)")
            print("- result: blocked-or-failed")
            print(f"- reason: {payload['reason']}")
            print("- no .env edit, Docker mutation, Alembic mutation, DB create/drop/restore, or row write was executed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

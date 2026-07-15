#!/usr/bin/env python3
"""Verify v309 runtime hardening after the source-binding inspector fix.

The checker reuses the v307 read-only live readiness inspection, then verifies
that SQLAlchemy pool policy, FastAPI engine disposal, production fail-closed
settings, and deployment templates are present. It never writes environment
files, runs Docker mutation commands, or executes Alembic operations.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
from typing import Any, Iterator

from check_postgres_deployment_runtime_readiness import (
    PRODUCTION_READY_RESULT,
    READY_RESULT as V307_READY_RESULT,
    fetch_health,
    inspect_deployment_runtime_readiness,
)

TOOL_VERSION = "v309.runtime-config-hardening-source-binding-fix-readonly-verification"
READY_RESULT = "runtime-config-hardening-verified-local-runtime-preserved"
BLOCKED_RESULT = "blocked-or-failed"

EXPECTED_POOL_POLICY = {
    "prePing": True,
    "size": 5,
    "maxOverflow": 10,
    "timeoutSeconds": 30,
    "recycleSeconds": 1800,
}


class RuntimeConfigHardeningError(RuntimeError):
    """Raised when a safety-critical v308 hardening condition is missing."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeConfigHardeningError(message)


def _read(path: Path) -> str:
    if not path.is_file():
        raise RuntimeConfigHardeningError(f"required file is missing: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


@contextmanager
def working_directory(path: Path) -> Iterator[None]:
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def inspect_static_hardening(root: Path) -> dict[str, Any]:
    backend = root / "backend"
    config = _read(backend / "app/core/config.py")
    session = _read(backend / "app/db/session.py")
    main = _read(backend / "app/main.py")
    env_example = _read(backend / ".env.example")
    dockerfile = _read(backend / "Dockerfile")
    production_compose = _read(root / "deploy/docker-compose.production.yml")
    deployment_readme = _read(root / "deploy/README.md")
    local_compose = _read(root / "docker-compose.yml")

    pool_markers = {
        "poolPrePing": "pool_pre_ping=settings.db_pool_pre_ping" in session,
        "poolSize": "pool_size=settings.db_pool_size" in session,
        "maxOverflow": "max_overflow=settings.db_max_overflow" in session,
        "poolTimeout": "pool_timeout=settings.db_pool_timeout_seconds" in session,
        "poolRecycle": "pool_recycle=settings.db_pool_recycle_seconds" in session,
    }
    config_pool_fields = {
        "prePing": "db_pool_pre_ping: bool = True" in config,
        "size": "db_pool_size: int = Field(default=5" in config,
        "maxOverflow": "db_max_overflow: int = Field(default=10" in config,
        "timeoutSeconds": "db_pool_timeout_seconds: int = Field(default=30" in config,
        "recycleSeconds": "db_pool_recycle_seconds: int = Field(default=1800" in config,
    }
    env_pool_keys = {
        "DB_POOL_PRE_PING",
        "DB_POOL_SIZE",
        "DB_MAX_OVERFLOW",
        "DB_POOL_TIMEOUT_SECONDS",
        "DB_POOL_RECYCLE_SECONDS",
    }
    env_example_keys = {
        line.split("=", 1)[0].strip()
        for line in env_example.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }

    dockerfile_command_line = next(
        (line.strip() for line in dockerfile.splitlines() if line.strip().startswith("CMD ")),
        "",
    )

    return {
        "configPoolFields": config_pool_fields,
        "sessionPoolOptions": pool_markers,
        "sessionPoolOptionCount": sum(pool_markers.values()),
        "engineDisposeLifecycle": all(
            marker in main
            for marker in (
                "@asynccontextmanager",
                "lifespan=lifespan",
                "await engine.dispose()",
            )
        ),
        "lifespanMutationFree": all(
            marker not in main
            for marker in (
                "alembic.command",
                "Base.metadata.create_all",
                "Base.metadata.drop_all",
                "DROP SCHEMA",
            )
        ),
        "productionGuard": all(
            marker in config
            for marker in (
                '@model_validator(mode="after")',
                "validate_production_runtime_guard",
                "DEBUG must be false in production",
                "JWT_SECRET_KEY must not use the local default in production",
                "ADMIN_WRITE_DEV_KEY must not use the local default in production",
                "at least 32 characters",
            )
        ),
        "envExamplePoolKeysPresent": env_pool_keys.issubset(env_example_keys),
        "envExamplePoolKeys": sorted(env_pool_keys & env_example_keys),
        "backendDockerfile": {
            "exists": True,
            "nonRootUser": "USER app" in dockerfile,
            "noAutomaticAlembic": "alembic" not in dockerfile_command_line.lower(),
            "uvicornCommand": "uvicorn" in dockerfile_command_line,
            "copyLocalEnv": "COPY backend/.env" in dockerfile,
        },
        "productionCompose": {
            "exists": True,
            "separateFromLocal": "production review template only" in production_compose.lower(),
            "productionEnvironment": "ENVIRONMENT: production" in production_compose,
            "debugFalse": 'DEBUG: "false"' in production_compose,
            "databaseUrlRequired": "DATABASE_URL:?" in production_compose,
            "managedPostgresServiceAbsent": "  postgres:" not in production_compose.lower(),
            "postgresCaSecret": "POSTGRES_CA_FILE" in production_compose and "postgres_ca:" in production_compose,
            "postgresHostPortPublished": "ports:" in production_compose,
            "adminerIncluded": "adminer:" in production_compose.lower(),
            "digestPinRequired": "approved digest-pinned backend image" in production_compose,
            "tlsUrlRequired": "managed PostgreSQL verify-full DATABASE_URL" in production_compose,
            "externalEdgeNetwork": "external: true" in production_compose and "EDGE_NETWORK_NAME" in production_compose,
            "singleReplica": "replicas: 1" in production_compose,
            "backendReadOnlyFilesystem": "read_only: true" in production_compose,
            "noNewPrivileges": "no-new-privileges:true" in production_compose,
            "automaticAlembic": "alembic" in production_compose.lower(),
        },
        "deploymentReadme": {
            "exists": True,
            "separateApproval": "아직 결정하지 않은 것" in deployment_readme,
            "tlsDocumented": "TLS" in deployment_readme,
            "poolSizingDocumented": "pool" in deployment_readme,
            "noAdminerHostPort": "Adminer" in deployment_readme and "host `ports:` 없음" in deployment_readme,
        },
        "localComposePreserved": all(
            marker in local_compose
            for marker in (
                'image: postgres:16-alpine',
                '"55432:5432"',
                '"8081:8080"',
                "rpg_postgres_data:/var/lib/postgresql/data",
            )
        ),
    }


def inspect_runtime_hardening_settings(root: Path) -> dict[str, Any]:
    backend = (root / "backend").resolve()
    backend_text = str(backend)
    sys.path[:] = [item for item in sys.path if str(Path(item or ".").resolve()) != backend_text]
    sys.path.insert(0, backend_text)

    with working_directory(backend):
        from app.core.config import (  # noqa: PLC0415
            LOCAL_ADMIN_WRITE_KEY,
            LOCAL_JWT_SECRET,
            Settings,
            settings,
        )

        pool_policy = {
            "prePing": bool(settings.db_pool_pre_ping),
            "size": int(settings.db_pool_size),
            "maxOverflow": int(settings.db_max_overflow),
            "timeoutSeconds": int(settings.db_pool_timeout_seconds),
            "recycleSeconds": int(settings.db_pool_recycle_seconds),
        }

        unsafe_blocked = False
        try:
            Settings(
                _env_file=None,
                environment="production",
                debug=True,
                jwt_secret_key=LOCAL_JWT_SECRET,
                admin_write_dev_key=LOCAL_ADMIN_WRITE_KEY,
                CORS_ORIGINS="https://example.invalid",
            )
        except ValueError:
            unsafe_blocked = True

        safe_loaded = Settings(
            _env_file=None,
            environment="production",
            debug=False,
            jwt_secret_key="j" * 40,
            admin_write_dev_key="a" * 40,
            database_url="postgresql+asyncpg://user:secret@db.internal:5432/rpg_game",
            CORS_ORIGINS="https://game.example.invalid",
        )

    return {
        "environment": str(settings.environment).strip().lower(),
        "debug": bool(settings.debug),
        "poolPolicy": pool_policy,
        "productionUnsafeDefaultsBlocked": unsafe_blocked,
        "productionSafeSettingsAccepted": safe_loaded.environment == "production"
        and safe_loaded.debug is False,
        "secretValuesStored": False,
    }


def inspect_runtime_config_hardening(
    root: Path,
    *,
    require_health: bool = False,
    v307_state: dict[str, Any] | None = None,
    static_state: dict[str, Any] | None = None,
    settings_state: dict[str, Any] | None = None,
    health_url: str = "http://127.0.0.1:8000/api/v1/health/db",
    health_timeout: float = 2.0,
) -> dict[str, Any]:
    root = root.resolve()
    health = fetch_health(health_url, health_timeout)
    runtime = v307_state or inspect_deployment_runtime_readiness(
        root,
        require_health=require_health,
        health={
            "url": health.url,
            "ok": health.ok,
            "status_code": health.status_code,
            "output": health.output,
        },
    )
    static = static_state or inspect_static_hardening(root)
    runtime_settings = settings_state or inspect_runtime_hardening_settings(root)

    _require(
        runtime.get("result") in {V307_READY_RESULT, PRODUCTION_READY_RESULT},
        "v307 deployment runtime readiness is not verified",
    )
    _require(runtime.get("readOnly") is True, "v307 readiness did not remain read-only")
    _require(runtime.get("mutationExecuted") is False, "v307 readiness reported a mutation")
    _require(runtime.get("nextRevisionRequired") is False, "a new Alembic revision is unexpectedly required")

    _require(all(static["configPoolFields"].values()), "runtime pool config fields are incomplete")
    _require(all(static["sessionPoolOptions"].values()), "async engine pool options are incomplete")
    _require(static["sessionPoolOptionCount"] == 5, "expected five explicit pool options")
    _require(static["engineDisposeLifecycle"] is True, "engine.dispose lifecycle is missing")
    _require(static["lifespanMutationFree"] is True, "FastAPI lifespan contains a DB mutation path")
    _require(static["productionGuard"] is True, "production fail-closed settings guard is incomplete")
    _require(static["envExamplePoolKeysPresent"] is True, "pool keys are missing from backend/.env.example")

    dockerfile = static["backendDockerfile"]
    _require(dockerfile["nonRootUser"] is True, "backend Dockerfile does not use a non-root user")
    _require(dockerfile["noAutomaticAlembic"] is True, "backend Dockerfile command contains Alembic")
    _require(dockerfile["uvicornCommand"] is True, "backend Dockerfile does not start Uvicorn")
    _require(dockerfile["copyLocalEnv"] is False, "backend Dockerfile copies backend/.env")

    production_compose = static["productionCompose"]
    _require(production_compose["separateFromLocal"] is True, "production Compose is not marked as a separate template")
    _require(production_compose["productionEnvironment"] is True, "production Compose does not force ENVIRONMENT=production")
    _require(production_compose["debugFalse"] is True, "production Compose does not force DEBUG=false")
    _require(production_compose["databaseUrlRequired"] is True, "production DATABASE_URL is not required")
    _require(production_compose["managedPostgresServiceAbsent"] is True, "bundled PostgreSQL service must be absent")
    _require(production_compose["postgresCaSecret"] is True, "managed PostgreSQL CA secret boundary is missing")
    _require(production_compose["postgresHostPortPublished"] is False, "production PostgreSQL host port is published")
    _require(production_compose["adminerIncluded"] is False, "production Compose includes Adminer")
    _require(production_compose["digestPinRequired"] is True, "production backend image digest pin is not required")
    _require(production_compose["tlsUrlRequired"] is True, "managed PostgreSQL verify-full DATABASE_URL is not required")
    _require(production_compose["externalEdgeNetwork"] is True, "external reverse proxy edge network is missing")
    _require(production_compose["singleReplica"] is True, "production backend replica count is not 1")
    _require(production_compose["backendReadOnlyFilesystem"] is True, "backend container filesystem is not read-only")
    _require(production_compose["noNewPrivileges"] is True, "backend container no-new-privileges is missing")
    _require(production_compose["automaticAlembic"] is False, "production Compose contains automatic Alembic")
    _require(static["localComposePreserved"] is True, "local docker-compose.yml behavior changed")

    _require(runtime_settings["poolPolicy"] == EXPECTED_POOL_POLICY, "local runtime pool defaults changed unexpectedly")
    _require(runtime_settings["productionUnsafeDefaultsBlocked"] is True, "unsafe production defaults are not blocked")
    _require(runtime_settings["productionSafeSettingsAccepted"] is True, "safe production settings are rejected")

    warning_keys = {item.get("key") for item in runtime.get("warnings", [])}
    removed_warnings = {
        "pool-policy-implicit",
        "engine-dispose-lifecycle-missing",
        "backend-container-image-missing",
    }
    _require(not (warning_keys & removed_warnings), "v307 still reports a completed v308 hardening item")

    return {
        "toolVersion": TOOL_VERSION,
        "result": READY_RESULT,
        "readOnly": True,
        "mutationExecuted": False,
        "environmentFileChanged": False,
        "dockerMutationExecuted": False,
        "databaseMutationExecuted": False,
        "alembicCommandExecuted": False,
        "runtimeReadinessResult": runtime.get("result"),
        "runtimeWarningCount": runtime.get("warningCount"),
        "remainingRuntimeWarningKeys": sorted(warning_keys),
        "staticHardening": static,
        "runtimeHardeningSettings": runtime_settings,
        "healthRequired": require_health,
        "healthConfirmed": runtime.get("health", {}).get("ok") is True,
        "nextRevisionRequired": False,
        "nextSafeStage": "separate-production-secrets-tls-and-container-validation",
    }


def render_text(result: dict[str, Any]) -> str:
    settings = result["runtimeHardeningSettings"]
    pool = settings["poolPolicy"]
    static = result["staticHardening"]
    lines = [
        "FastAPI/PostgreSQL runtime config hardening verification (read-only)",
        "No .env edit, Docker start/stop/build/remove, DB write, revision generation, stamp, upgrade, or downgrade was executed.",
        "",
        f"- v307 runtime readiness: {result['runtimeReadinessResult']}",
        f"- local environment/debug preserved: {settings['environment']}/{settings['debug']}",
        f"- explicit SQLAlchemy pool options: {static['sessionPoolOptionCount']} / pre_ping={pool['prePing']}",
        f"- pool size/max overflow: {pool['size']}/{pool['maxOverflow']}",
        f"- pool timeout/recycle seconds: {pool['timeoutSeconds']}/{pool['recycleSeconds']}",
        f"- FastAPI shutdown engine.dispose lifecycle: {static['engineDisposeLifecycle']}",
        f"- lifespan DB mutation markers: {'none' if static['lifespanMutationFree'] else 'detected'}",
        f"- unsafe production defaults blocked: {settings['productionUnsafeDefaultsBlocked']}",
        f"- safe production settings accepted: {settings['productionSafeSettingsAccepted']}",
        f"- backend Dockerfile: non-root={static['backendDockerfile']['nonRootUser']} / automatic Alembic={static['backendDockerfile']['noAutomaticAlembic'] is False}",
        f"- production Compose: separate template={static['productionCompose']['separateFromLocal']} / managed DB service absent={static['productionCompose']['managedPostgresServiceAbsent']} / host ports={static['productionCompose']['postgresHostPortPublished']}",
        f"- local docker-compose behavior preserved: {static['localComposePreserved']}",
        f"- live DB health required/confirmed: {result['healthRequired']}/{result['healthConfirmed']}",
        f"- remaining production warnings: {result['runtimeWarningCount']} / {result['remainingRuntimeWarningKeys']}",
        "- new revision/autogenerate/stamp/upgrade/downgrade approved: no",
        f"- result: {result['result']}",
        f"- next safe stage: {result['nextSafeStage']}",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--require-health", action="store_true")
    parser.add_argument(
        "--health-url",
        default="http://127.0.0.1:8000/api/v1/health/db",
    )
    parser.add_argument("--health-timeout", type=float, default=2.0)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    try:
        result = inspect_runtime_config_hardening(
            root,
            require_health=args.require_health,
            health_url=args.health_url,
            health_timeout=args.health_timeout,
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
            print("FastAPI/PostgreSQL runtime config hardening verification (read-only)")
            print("- result: blocked-or-failed")
            print(f"- reason: {payload['reason']}")
            print("- no .env, Docker, Alembic, or DB mutation was executed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

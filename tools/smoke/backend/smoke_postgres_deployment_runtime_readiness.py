#!/usr/bin/env python3
"""Smoke checks for the v307 deployment/runtime read-only preflight."""
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_postgres_deployment_runtime_readiness.py"
READINESS_DOC = ROOT / "docs/current/POSTGRES_DEPLOYMENT_RUNTIME_READINESS.md"
RUNBOOK_DOC = ROOT / "docs/current/POSTGRES_DEPLOYMENT_MIGRATION_RUNBOOK.md"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_tool():
    tools_dir = ROOT / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))
    spec = importlib.util.spec_from_file_location("v307_runtime_readiness", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v307 tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def ready_fixture() -> dict[str, Any]:
    return {
        "next_revision_state": {
            "result": "next-revision-not-required-current-schema-equivalent",
            "readOnly": True,
            "sourceCurrentRevision": ["v295_initial_schema"],
            "revisionSha256": "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa",
            "baselineCompletionResult": "postgres-baseline-completion-state-verified",
        },
        "runtime_sources": {
            "databaseUrlFromSettings": True,
            "asyncEngine": True,
            "asyncSession": True,
            "sessionDependency": True,
            "engineEchoUsesDebug": True,
            "explicitPoolOptions": {
                "poolPrePing": False,
                "poolSize": False,
                "maxOverflow": False,
                "poolTimeout": False,
                "poolRecycle": False,
            },
            "explicitPoolOptionCount": 0,
            "engineDisposeLifecycle": False,
            "startupMutationMarkers": [],
            "startupMutationFree": True,
            "healthDbGetRoute": True,
            "healthDbSelectOne": True,
            "healthDbCommitFree": True,
            "healthDbResponseSafe": True,
            "mainIncludesOnlyRouters": True,
            "mainHasStartupHook": False,
            "alembicUsesSettingsDatabaseUrl": True,
            "alembicUsesNullPool": True,
            "setupResetIsSeparateCli": True,
            "configUsesEnvFile": True,
            "configHasEnvironment": True,
            "configHasDebug": True,
            "configHasDatabaseUrl": True,
            "sqliteRuntimeMarkers": [],
        },
        "runtime_settings": {
            "loaded": True,
            "environment": "local",
            "debug": True,
            "driver": "postgresql+asyncpg",
            "database": "rpg_game",
            "host": "127.0.0.1",
            "port": 55432,
            "usernameConfigured": True,
            "passwordConfigured": True,
            "postgresAsyncpg": True,
            "exactSourceDatabase": True,
            "unsafeNonRuntimeTarget": False,
            "jwtUsesLocalDefault": True,
            "adminWriteKeyUsesLocalDefault": True,
            "productionSecretPolicyOk": True,
            "corsOriginCount": 7,
            "apiPrefix": "/api/v1",
        },
        "database_runtime": {
            "connected": True,
            "readOnlyTransaction": True,
            "database": "rpg_game",
            "user": "rpg_user",
            "schema": "public",
            "serverVersion": "16.14",
            "maxConnections": 100,
            "inRecovery": False,
            "selectOne": 1,
            "currentRevisions": ["v295_initial_schema"],
            "defaultTransactionReadOnly": "off",
        },
        "docker_static": {
            "postgres16": True,
            "postgresImage": "postgres:16-alpine",
            "restartUnlessStopped": True,
            "healthcheck": True,
            "namedVolume": True,
            "hostPort55432": True,
            "adminerEnabled": True,
            "adminerPublished": True,
            "hardcodedLocalPassword": True,
            "imageDigestPinned": False,
            "tlsConfigured": False,
            "dockerfileExists": False,
        },
        "docker_live": {
            "commands": [],
            "commandOutputStored": False,
            "composePsOk": True,
            "composeConfigOk": True,
            "postgresFound": True,
            "postgresState": "running",
            "postgresHealth": "healthy",
            "postgresRunning": True,
            "postgresHealthy": True,
        },
        "env_example_inventory": {
            "exists": True,
            "keys": [],
            "requiredKeysPresent": True,
            "missingRequiredKeys": [],
        },
        "env_inventory": {
            "exists": True,
            "keys": [],
            "requiredKeysPresent": True,
            "missingRequiredKeys": [],
        },
        "operations_policy": {
            "requiredDocsPresent": True,
            "missingDocs": [],
            "localBackupsGitIgnored": True,
            "localReviewArtifactsGitIgnored": True,
            "localBackupsDockerIgnored": True,
            "localReviewArtifactsDockerIgnored": True,
            "manualMigrationApprovalDocumented": True,
            "backupBeforeMigrationDocumented": True,
            "isolatedFirstDocumented": True,
            "startupMigrationForbiddenDocumented": True,
        },
        "health": {
            "url": "http://127.0.0.1:8000/api/v1/health/db",
            "ok": False,
            "status_code": None,
            "output": "server intentionally stopped",
        },
    }


def main() -> int:
    for path in (TOOL, READINESS_DOC, RUNBOOK_DOC):
        if not path.is_file():
            return fail(f"missing file: {path.relative_to(ROOT).as_posix()}")

    source = TOOL.read_text(encoding="utf-8")
    ast.parse(source, filename=str(TOOL))

    required_markers = [
        'TOOL_VERSION = "v307.postgres-deployment-runtime-readiness-readonly"',
        'READY_RESULT = "local-runtime-readiness-verified-production-hardening-required"',
        'SET TRANSACTION READ ONLY',
        '["docker", "compose", "ps", "--format", "json"]',
        '["docker", "compose", "config", "--format", "json"]',
        "startupMutationFree",
        "productionSecretPolicyOk",
        "Secret values are never printed",
        "commandOutputStored",
        "responseBodyStored",
        "alembicCommandExecuted\": False",
    ]
    for marker in required_markers:
        if marker not in source:
            return fail(f"v307 checker missing marker: {marker}")

    forbidden_markers = [
        '["docker", "compose", "up"]',
        '["docker", "compose", "down"]',
        '["docker", "volume", "rm"]',
        'subprocess.run(["alembic"',
        '"upgrade", "head"',
        '"stamp", "head"',
        '"revision", "--autogenerate"',
        "DROP SCHEMA IF EXISTS public CASCADE\")",
    ]
    for marker in forbidden_markers:
        if marker in source:
            return fail(f"v307 checker contains forbidden execution marker: {marker}")

    tool = load_tool()
    actual_sources = tool.inspect_runtime_sources(ROOT)
    if actual_sources.get("databaseUrlFromSettings") is not True:
        return fail("actual runtime engine must use settings.database_url")
    if actual_sources.get("databaseUrlBindingInspection") != tool.RUNTIME_ENGINE_BINDING_INSPECTOR:
        return fail("runtime engine binding inspector must use the v309 AST contract")

    fixture = ready_fixture()
    result = tool.inspect_deployment_runtime_readiness(ROOT, **fixture)
    if result.get("result") != tool.READY_RESULT:
        return fail(f"unexpected local readiness result: {result.get('result')}")
    if result.get("readOnly") is not True or result.get("mutationExecuted") is not False:
        return fail("v307 result must remain read-only and mutation-free")
    if result.get("productionHardeningRequired") is not True:
        return fail("local fixture must require production hardening")
    serialized = __import__("json").dumps(result, ensure_ascii=False)
    if "rpg_password" in serialized or "change-me-before-production" in serialized:
        return fail("v307 JSON result must not expose secret values")
    if "server intentionally stopped" in serialized or '{\"ok\":true}' in serialized:
        return fail("v307 JSON result must not retain health response bodies")
    warning_keys = {item.get("key") for item in result.get("warnings", [])}
    for key in (
        "pool-policy-implicit",
        "engine-dispose-lifecycle-missing",
        "compose-local-password",
        "adminer-published",
        "database-tls-not-configured",
        "backend-container-image-missing",
    ):
        if key not in warning_keys:
            return fail(f"expected hardening warning missing: {key}")

    production_fixture = ready_fixture()
    production_fixture["runtime_sources"] = dict(production_fixture["runtime_sources"])
    production_fixture["runtime_sources"].update(
        {
            "explicitPoolOptionCount": 5,
            "engineDisposeLifecycle": True,
        }
    )
    production_fixture["runtime_settings"] = dict(production_fixture["runtime_settings"])
    production_fixture["runtime_settings"].update(
        {
            "environment": "production",
            "debug": False,
            "jwtUsesLocalDefault": False,
            "adminWriteKeyUsesLocalDefault": False,
            "productionSecretPolicyOk": True,
        }
    )
    production_fixture["docker_static"] = dict(production_fixture["docker_static"])
    production_fixture["docker_static"].update(
        {
            "hostPort55432": False,
            "adminerPublished": False,
            "hardcodedLocalPassword": False,
            "imageDigestPinned": True,
            "tlsConfigured": True,
            "dockerfileExists": True,
        }
    )
    production_fixture["health"] = {
        "url": "https://example.invalid/api/v1/health/db",
        "ok": True,
        "status_code": 200,
        "output": '{"ok":true}',
    }
    production = tool.inspect_deployment_runtime_readiness(
        ROOT, require_health=True, **production_fixture
    )
    if production.get("result") != tool.PRODUCTION_READY_RESULT:
        return fail("production fixture should be fully ready")
    if production.get("warningCount") != 0:
        return fail("production fixture should not contain warnings")

    unsafe_fixture = ready_fixture()
    unsafe_fixture["runtime_settings"] = dict(unsafe_fixture["runtime_settings"])
    unsafe_fixture["runtime_settings"].update(
        {
            "database": "rpg_game_migration_empty_v290",
            "exactSourceDatabase": False,
            "unsafeNonRuntimeTarget": True,
        }
    )
    try:
        tool.inspect_deployment_runtime_readiness(ROOT, **unsafe_fixture)
    except tool.DeploymentRuntimeReadinessError:
        pass
    else:
        return fail("migration DB runtime target must be blocked")

    try:
        tool.run_readonly_command(ROOT, ["docker", "compose", "down"])
    except tool.DeploymentRuntimeReadinessError:
        pass
    else:
        return fail("unapproved Docker command must be blocked")

    readiness_text = READINESS_DOC.read_text(encoding="utf-8")
    for marker in (
        "운영·배포 runtime readiness — v307",
        "check_postgres_deployment_runtime_readiness.py --strict",
        "local-runtime-readiness-verified-production-hardening-required",
        "docker compose ps --format json",
        "비밀번호, JWT secret",
    ):
        if marker not in readiness_text:
            return fail(f"runtime readiness doc missing: {marker}")

    runbook_text = RUNBOOK_DOC.read_text(encoding="utf-8")
    for marker in (
        "배포 migration 운영 원칙 — v307",
        "서버 시작 시 자동 migration",
        "migration 전 source DB backup",
        "isolated migration DB",
        "별도 승인",
    ):
        if marker not in runbook_text:
            return fail(f"deployment migration runbook missing: {marker}")

    print("OK: PostgreSQL deployment runtime readiness smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Smoke checks for the v309 runtime hardening inspector-fix boundary."""
from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_runtime_config_hardening.py"
DOC = ROOT / "docs/current/POSTGRES_RUNTIME_CONFIG_HARDENING.md"
DEPLOY_DOC = ROOT / "docs/current/POSTGRES_PRODUCTION_DEPLOYMENT_TEMPLATE.md"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_tool():  # type: ignore[no-untyped-def]
    tools_path = str(ROOT / "tools")
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    spec = importlib.util.spec_from_file_location("v309_runtime_hardening", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v309 tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def ready_v307_fixture(tool):  # type: ignore[no-untyped-def]
    return {
        "result": tool.V307_READY_RESULT,
        "readOnly": True,
        "mutationExecuted": False,
        "nextRevisionRequired": False,
        "warningCount": 9,
        "warnings": [
            {"key": "environment-not-production", "message": "local"},
            {"key": "debug-enabled", "message": "local"},
            {"key": "jwt-local-default", "message": "local"},
            {"key": "admin-write-local-default", "message": "local"},
            {"key": "compose-local-password", "message": "local"},
            {"key": "adminer-published", "message": "local"},
            {"key": "postgres-host-port-published", "message": "local"},
            {"key": "postgres-image-not-digest-pinned", "message": "local"},
            {"key": "database-tls-not-configured", "message": "local"},
        ],
        "health": {"ok": True},
    }


def main() -> int:
    for path in (TOOL, DOC, DEPLOY_DOC, ROOT / "backend/Dockerfile", ROOT / "deploy/docker-compose.production.yml"):
        if not path.is_file():
            return fail(f"missing file: {path.relative_to(ROOT).as_posix()}")

    source = TOOL.read_text(encoding="utf-8")
    ast.parse(source, filename=str(TOOL))
    for marker in (
        'TOOL_VERSION = "v309.runtime-config-hardening-source-binding-fix-readonly-verification"',
        'READY_RESULT = "runtime-config-hardening-verified-local-runtime-preserved"',
        "pool_pre_ping=settings.db_pool_pre_ping",
        "await engine.dispose()",
        "productionUnsafeDefaultsBlocked",
        "dockerMutationExecuted\": False",
        "alembicCommandExecuted\": False",
    ):
        if marker not in source and marker not in (ROOT / "backend/app/db/session.py").read_text(encoding="utf-8") and marker not in (ROOT / "backend/app/main.py").read_text(encoding="utf-8"):
            return fail(f"v309 marker missing: {marker}")

    for forbidden in (
        'docker compose up',
        'docker compose down',
        'docker volume rm',
        'alembic upgrade head',
        'alembic stamp head',
        'DROP SCHEMA IF EXISTS public CASCADE',
    ):
        if forbidden in source:
            return fail(f"v309 checker contains forbidden mutation marker: {forbidden}")

    tool = load_tool()
    static = tool.inspect_static_hardening(ROOT)
    settings = tool.inspect_runtime_hardening_settings(ROOT)
    result = tool.inspect_runtime_config_hardening(
        ROOT,
        require_health=True,
        v307_state=ready_v307_fixture(tool),
        static_state=static,
        settings_state=settings,
    )
    if result.get("result") != tool.READY_RESULT:
        return fail(f"unexpected v309 result: {result.get('result')}")
    if result.get("readOnly") is not True or result.get("mutationExecuted") is not False:
        return fail("v309 checker must remain read-only and mutation-free")
    if settings.get("poolPolicy") != tool.EXPECTED_POOL_POLICY:
        return fail("local pool defaults differ from approved v308/v309 values")
    if settings.get("productionUnsafeDefaultsBlocked") is not True:
        return fail("unsafe production defaults were not blocked")
    if static.get("localComposePreserved") is not True:
        return fail("local docker-compose.yml behavior changed")
    if static["productionCompose"].get("adminerIncluded") is not False:
        return fail("production Compose must not include Adminer")
    if static["productionCompose"].get("postgresHostPortPublished") is not False:
        return fail("production PostgreSQL host port must not be published")

    serialized = json.dumps(result, ensure_ascii=False)
    for secret in ("rpg_password", "change-me-before-production", "local-admin-dev-key"):
        if secret in serialized:
            return fail("v309 result exposed a local secret value")

    bad_static = dict(static)
    bad_static["engineDisposeLifecycle"] = False
    try:
        tool.inspect_runtime_config_hardening(
            ROOT,
            v307_state=ready_v307_fixture(tool),
            static_state=bad_static,
            settings_state=settings,
        )
    except tool.RuntimeConfigHardeningError:
        pass
    else:
        return fail("missing engine.dispose lifecycle must be blocked")

    for path, markers in (
        (DOC, ("runtime config hardening — v308", "engine.dispose()", "DB_POOL_PRE_PING", "runtime-config-hardening-verified-local-runtime-preserved")),
        (DEPLOY_DOC, ("운영 배포 template — v312", "Adminer", "digest", "verify-full", "자동 Alembic")),
    ):
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                return fail(f"document missing marker: {path.name}: {marker}")

    print("OK: runtime config hardening smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

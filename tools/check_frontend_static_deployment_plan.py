#!/usr/bin/env python3
"""Fail-closed static validation for the v348 frontend deployment preparation."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "deploy/render-static-site.example.json"
DOC_PATH = ROOT / "docs/current/FRONTEND_STATIC_DEPLOYMENT_PLAN.md"
BUILDER_PATH = ROOT / "tools/build_legacy_static_site.mjs"
SMOKE_PATH = ROOT / "tools/smoke/frontend/smoke_legacy_static_deployment_preparation.js"
RUNTIME_CONFIG_PATH = ROOT / "src/api/runtime-config.js"
VERSION = "v348.frontend-static-deployment-preparation-ready-exact-sha-gated"
RESULT = "frontend-static-deployment-preparation-ready-exact-sha-gated"
NEXT_STAGE = "owner-approve-frontend-static-deployment-preparation-sha"
FRONTEND_ORIGIN = "https://gihohoho-upgrade-rpg.onrender.com"
BACKEND_API = "https://upgrade-rpg-api.onrender.com/api/v1"
STATE_FILES = (
    ROOT / "AGENTS.md",
    ROOT / "NEXT_CHAT_PROMPT.md",
    ROOT / "NEXT_CHAT_HANDOFF.md",
    ROOT / "docs/current/CURRENT_STATUS.md",
    ROOT / "docs/handoff/NEXT_CHAT_PROMPT.md",
    ROOT / "docs/handoff/NEXT_CHAT_HANDOFF.md",
)


class PlanError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing file: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanError(f"invalid JSON: {path.name} ({type(exc).__name__})") from None
    require(isinstance(value, dict), "plan root must be an object")
    return value


def flattened_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for child in value for item in flattened_strings(child)]
    if isinstance(value, dict):
        return [item for child in value.values() for item in flattened_strings(child)]
    return []


def verify_plan(plan: dict[str, Any]) -> None:
    require(plan.get("schemaVersion") == VERSION, "schemaVersion differs")
    require(plan.get("result") == RESULT, "result differs")
    require(plan.get("nextSafeStage") == NEXT_STAGE, "next safe stage differs")
    require(plan.get("productionResourcesMutated") is False, "provider mutation must remain false")

    site = plan.get("site") or {}
    require(site.get("provider") == "render" and site.get("type") == "static-site", "site type differs")
    require(site.get("plan") == "free", "site plan must remain free")
    require(site.get("recommendedName") == "gihohoho-upgrade-rpg", "site name differs")
    require(site.get("expectedOrigin") == FRONTEND_ORIGIN, "expected origin differs")
    require(site.get("autoDeploy") is False, "auto-deploy must remain disabled")
    require(site.get("customDomain") is False, "custom domain must remain disabled")

    source = plan.get("source") or {}
    require(source.get("repository") == "https://github.com/gihohoho/upgrade-rpg.git", "repository differs")
    require(source.get("visibility") == "private", "repository visibility differs")
    require(source.get("branch") == "main", "branch differs")
    require(source.get("buildCommand") == "node tools/build_legacy_static_site.mjs", "build command differs")
    require(source.get("publishDirectory") == "frontend/legacy-dist", "publish directory differs")
    require(source.get("cleanPushedExactShaRequired") is True, "exact SHA gate must remain enabled")

    runtime = plan.get("runtime") or {}
    require(runtime.get("productionApiBaseUrl") == BACKEND_API, "production API differs")
    require(runtime.get("localApiBaseUrl") == "http://127.0.0.1:8000/api/v1", "local API differs")
    require(runtime.get("localStaticOrigin") == "http://127.0.0.1:5500", "local origin differs")
    require(runtime.get("backendCorsExactOriginRequired") is True, "exact CORS origin is required")
    require(runtime.get("backendCorsExpectedValue") == f'["{FRONTEND_ORIGIN}"]', "CORS value differs")
    require(runtime.get("backendServiceId") == "srv-d9iro458nd3s73acgmsg", "backend service differs")

    admin = plan.get("adminBoundary") or {}
    require(admin.get("adminHtmlPublic") is True, "admin page publication must be explicit")
    require(admin.get("readOnlyApiAllowed") is True, "admin read-only boundary differs")
    require(admin.get("adminWriteKeyEmbedded") is False, "admin key must not be embedded")
    require(admin.get("adminWriteOperationApproved") is False, "admin write must remain unapproved")
    require(admin.get("futureProductionAuthenticationReviewRequired") is True, "future admin auth review is required")

    scope = plan.get("approvedExecutionScopeAfterExactShaApproval") or {}
    for key in (
        "verifyCleanPushedMainExactSha",
        "connectPrivateGitHubRepository",
        "createOneFreeStaticSite",
        "initialStaticDeployExactCommitOnce",
        "confirmExactStaticOrigin",
        "setBackendCorsToExactStaticOrigin",
        "deployBackendCorsConfigurationOnce",
        "verifyGameAndAdminHttp200",
        "verifyBrowserCorsAndReadOnlyApi",
        "recordSanitizedEvidence",
    ):
        require(scope.get(key) is True, f"approved scope marker differs: {key}")
    for key in (
        "databaseWrite",
        "alembic",
        "adminWrite",
        "secretEmbeddedInFrontend",
        "customDomainOrDns",
        "paymentMethodChange",
        "automaticDeployOrRetry",
    ):
        require(scope.get(key) is False, f"excluded scope marker differs: {key}")

    gate = plan.get("approvalGate") or {}
    require(gate.get("preparationReady") is True, "preparation must be ready")
    require(gate.get("exactPreparationShaApprovalRequired") is True, "exact SHA approval must be required")
    require(gate.get("exactPreparationShaApproved") is False, "exact SHA must not be pre-approved")
    require(gate.get("approvedPreparationSha") is None, "approved SHA must be empty")
    for key in (
        "staticSiteCreated",
        "staticDeployExecuted",
        "backendCorsApplied",
        "backendCorsDeployExecuted",
        "browserIntegrationVerified",
    ):
        require(gate.get(key) is False, f"execution gate must remain false: {key}")

    joined = "\n".join(flattened_strings(plan))
    for pattern in (
        r"\bnpg_[A-Za-z0-9]+",
        r"\bghp_[A-Za-z0-9]+",
        r"\bgithub_pat_[A-Za-z0-9_]+",
        r"\bep-[a-z0-9-]+\.(?:c-\d+\.)?ap-southeast-1\.aws\.neon\.tech\b",
        r"postgres(?:ql)?://",
    ):
        require(re.search(pattern, joined, re.IGNORECASE) is None, "plan contains secret-shaped text")


def verify_sources() -> None:
    for path in (DOC_PATH, BUILDER_PATH, SMOKE_PATH, RUNTIME_CONFIG_PATH):
        require(path.is_file(), f"missing file: {path.relative_to(ROOT)}")

    runtime = RUNTIME_CONFIG_PATH.read_text(encoding="utf-8")
    for marker in (VERSION.replace("-deployment-preparation-ready-exact-sha-gated", "-runtime-config"), BACKEND_API):
        require(marker in runtime, f"runtime config marker differs: {marker}")
    require("ADMIN_WRITE_DEV_KEY" not in runtime, "runtime config must not contain admin key")

    for entrypoint in ("index.html", "admin.html"):
        html = (ROOT / entrypoint).read_text(encoding="utf-8")
        config_index = html.find('src="src/api/runtime-config.js"')
        client_index = html.find('src="src/api/game-api-client.js"')
        require(config_index >= 0 and client_index > config_index, f"{entrypoint} load order differs")

    builder = BUILDER_PATH.read_text(encoding="utf-8")
    for marker in (
        'path.resolve(projectRoot, "frontend", "legacy-dist")',
        'publishedExtensions = new Set([".js", ".css"])',
        "outputDirectory !== expectedOutputDirectory",
        "forbiddenTextPatterns",
    ):
        require(marker in builder, f"builder safety marker differs: {marker}")

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")
    require("/frontend/legacy-dist/" in gitignore, "frontend output must be Git-ignored")
    require("frontend/legacy-dist/" in dockerignore, "frontend output must be Docker-ignored")

    doc = DOC_PATH.read_text(encoding="utf-8")
    for marker in (VERSION.split(".", 1)[0], FRONTEND_ORIGIN, BACKEND_API, "정확한 40자리 SHA"):
        require(marker in doc, f"frontend plan document marker differs: {marker}")

    for state_path in STATE_FILES:
        text = state_path.read_text(encoding="utf-8")
        for marker in (VERSION, RESULT, NEXT_STAGE):
            require(marker in text, f"{state_path.relative_to(ROOT)} marker differs: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    parser.parse_args()
    try:
        verify_plan(load_json(PLAN_PATH))
        verify_sources()
    except PlanError as exc:
        print(f"frontend static deployment plan verification failed: {exc}", file=sys.stderr)
        return 1
    print("frontend static deployment plan verification (static, no provider mutation)")
    print("- publish allowlist: index.html / admin.html / src/**/*.js / src/**/*.css")
    print("- local/public API: local preserved / Render backend pinned")
    print("- static site/backend CORS mutation: no/no")
    print(f"- result: {RESULT}")
    print(f"- next safe stage: {NEXT_STAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

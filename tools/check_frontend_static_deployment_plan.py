#!/usr/bin/env python3
"""Fail-closed static validation for the v350 CORS recovery record."""

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
EVIDENCE_PATH = ROOT / "deploy/review/render-backend-cors-recovery-v350.json"
VERSION = "v350.backend-cors-recovered-browser-timeout-followup-required"
RESULT = "backend-cors-recovered-browser-timeout-followup-required"
NEXT_STAGE = "prepare-frontend-master-data-timeout-fix-and-content-readiness-review"
APPROVED_SHA = "b13b1775093716800d7361ee1e8f94d8112eefc1"
RECOVERY_SHA = "e64d42d812d78de023dc6cbd7f960263bc1c2d15"
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
    require(plan.get("productionResourcesMutated") is True, "provider mutation record differs")

    site = plan.get("site") or {}
    require(site.get("provider") == "render" and site.get("type") == "static-site", "site type differs")
    require(site.get("plan") == "free", "site plan must remain free")
    require(site.get("recommendedName") == "gihohoho-upgrade-rpg", "site name differs")
    require(site.get("expectedOrigin") == FRONTEND_ORIGIN, "expected origin differs")
    require(site.get("serviceId") == "srv-d9iu337aqgkc73am4lh0", "static service id differs")
    require(site.get("deployId") == "dep-d9iu33faqgkc73am4m3g", "static deploy id differs")
    require(site.get("deployStatus") == "live", "static deploy status differs")
    require(site.get("autoDeploy") is False, "auto-deploy must remain disabled")
    require(site.get("customDomain") is False, "custom domain must remain disabled")

    source = plan.get("source") or {}
    require(source.get("repository") == "https://github.com/gihohoho/upgrade-rpg.git", "repository differs")
    require(source.get("visibility") == "private", "repository visibility differs")
    require(source.get("branch") == "main", "branch differs")
    require(source.get("approvedAndDeployedCommit") == APPROVED_SHA, "deployed commit differs")
    require(source.get("buildCommand") == "node tools/build_legacy_static_site.mjs", "build command differs")
    require(source.get("publishDirectory") == "frontend/legacy-dist", "publish directory differs")
    require(source.get("cleanPushedExactShaRequired") is True, "exact SHA gate must remain enabled")

    runtime = plan.get("runtime") or {}
    require(runtime.get("productionApiBaseUrl") == BACKEND_API, "production API differs")
    require(runtime.get("localApiBaseUrl") == "http://127.0.0.1:8000/api/v1", "local API differs")
    require(runtime.get("localStaticOrigin") == "http://127.0.0.1:5500", "local origin differs")
    require(runtime.get("backendCorsExactOriginRequired") is True, "exact CORS origin is required")
    require(runtime.get("backendCorsExpectedValue") == f'["{FRONTEND_ORIGIN}"]', "CORS value differs")
    require(runtime.get("backendCorsActualValueAfterDeploy") == f'["{FRONTEND_ORIGIN}"]', "actual CORS value differs")
    require(runtime.get("backendCorsApplied") is True, "CORS recovery must remain recorded")
    require(runtime.get("backendCorsDeployId") == "dep-d9ivfmvlk1mc73fbcv40", "backend deploy id differs")
    require(runtime.get("backendCorsDeployStatus") == "live", "backend deploy status differs")
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
    require(gate.get("exactPreparationShaApproved") is True, "exact SHA approval record differs")
    require(gate.get("approvedPreparationSha") == APPROVED_SHA, "approved SHA differs")
    require(gate.get("staticSiteCreated") is True, "static site creation record differs")
    require(gate.get("staticDeployExecuted") is True, "static deploy record differs")
    require(gate.get("backendCorsApplied") is True, "CORS recovery must remain recorded")
    require(gate.get("backendCorsDeployExecuted") is True, "backend deploy execution record differs")
    require(gate.get("browserIntegrationVerified") is False, "browser integration must remain fail-closed")
    require(gate.get("approvedOneShotBackendDeployConsumed") is True, "one-shot deploy must be consumed")
    require(gate.get("automaticRetryExecuted") is False, "automatic retry must remain false")
    require(gate.get("recoveryExactShaApprovalRequired") is True, "recovery exact SHA gate is required")
    require(gate.get("recoveryExactShaApproved") is True, "recovery approval record differs")
    require(gate.get("approvedRecoverySha") == RECOVERY_SHA, "recovery SHA differs")
    require(gate.get("recoveryDeployExecuted") is True, "recovery deploy record differs")
    require(gate.get("recoveryDeployId") == "dep-d9ivfmvlk1mc73fbcv40", "recovery deploy id differs")
    require(gate.get("recoveryDeployStatus") == "live", "recovery deploy status differs")
    require(gate.get("recoveryOneShotConsumed") is True, "recovery one-shot must be consumed")

    validation = plan.get("validation") or {}
    require(validation.get("gameHttp200") is True, "game HTTP validation differs")
    require(validation.get("adminHttp200") is True, "admin HTTP validation differs")
    require(validation.get("staticAssetRawBytesMatchApprovedSource") is True, "asset integrity differs")
    require(validation.get("corsPreflightStatus") == 200, "CORS preflight status differs")
    require(validation.get("corsBrowserIntegrationVerified") is True, "CORS browser validation differs")
    require(validation.get("gameReadOnlyApiIntegration") is False, "game integration must remain false")
    require(validation.get("gameFallbackReason") == "master-data-request-exceeded-1500ms-timeout", "game fallback reason differs")
    require(validation.get("masterDataHttpStatus") == 200, "master-data HTTP status differs")
    require(validation.get("masterDataResponseBytes") == 464098, "master-data response size differs")
    require(validation.get("masterDataMeasuredMilliseconds") == [1980, 1829], "master-data timings differ")
    require(validation.get("adminPreviousModuleErrorReproduced") is False, "admin browser result differs")
    require(validation.get("sanitizedEvidence") == EVIDENCE_PATH.relative_to(ROOT).as_posix(), "evidence path differs")

    joined = "\n".join(flattened_strings(plan))
    for pattern in (
        r"\bnpg_[A-Za-z0-9]+",
        r"\bghp_[A-Za-z0-9]+",
        r"\bgithub_pat_[A-Za-z0-9_]+",
        r"\bep-[a-z0-9-]+\.(?:c-\d+\.)?ap-southeast-1\.aws\.neon\.tech\b",
        r"postgres(?:ql)?://",
    ):
        require(re.search(pattern, joined, re.IGNORECASE) is None, "plan contains secret-shaped text")


def verify_evidence() -> None:
    evidence = load_json(EVIDENCE_PATH)
    require(evidence.get("schemaVersion") == VERSION, "evidence schema differs")
    require(evidence.get("result") == RESULT, "evidence result differs")
    require(evidence.get("nextSafeStage") == NEXT_STAGE, "evidence next stage differs")
    approval = evidence.get("approval") or {}
    require(approval.get("approvedRecoverySha") == RECOVERY_SHA, "evidence recovery SHA differs")
    require(approval.get("oneFocusedBackendCorsDeployConsumed") is True, "evidence deploy consumption differs")
    require(approval.get("secondRecoveryDeployOrRetryExecuted") is False, "evidence retry boundary differs")
    backend = evidence.get("backendCorsRecovery") or {}
    require(backend.get("corsOriginsBefore") == "[]", "evidence prior CORS differs")
    require(backend.get("corsOriginsAfter") == f'["{FRONTEND_ORIGIN}"]', "evidence recovered CORS differs")
    require(backend.get("exactOriginApplied") is True, "evidence CORS recovery differs")
    require(backend.get("deployStatus") == "live", "evidence deploy status differs")
    http = evidence.get("httpValidation") or {}
    require(http.get("healthStatus") == 200, "evidence health status differs")
    require(http.get("preflightStatus") == 200, "evidence preflight status differs")
    require(http.get("masterDataStatus") == 200, "evidence master-data status differs")
    require(http.get("masterDataMeasuredMilliseconds") == [1980, 1829], "evidence timing differs")
    browser = evidence.get("browserValidation") or {}
    require(browser.get("corsFetchFailureObserved") is False, "evidence CORS browser result differs")
    require(browser.get("masterDataTimeoutFallbackObserved") is True, "evidence timeout fallback differs")
    content = evidence.get("contentReadiness") or {}
    require(content.get("ready") is False, "content readiness must remain false")
    require(content.get("notifyOwnerWhenReady") is True, "content owner notification marker differs")
    safety = evidence.get("safety") or {}
    for key in ("databaseWrite", "alembicMutation", "adminWrite", "secretRecorded", "automaticDeployOrRetry"):
        require(safety.get(key) is False, f"evidence safety marker differs: {key}")


def verify_sources() -> None:
    for path in (DOC_PATH, BUILDER_PATH, SMOKE_PATH, RUNTIME_CONFIG_PATH, EVIDENCE_PATH):
        require(path.is_file(), f"missing file: {path.relative_to(ROOT)}")

    runtime = RUNTIME_CONFIG_PATH.read_text(encoding="utf-8")
    for marker in ("v348.frontend-static-runtime-config", BACKEND_API):
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
    for marker in (VERSION.split(".", 1)[0], FRONTEND_ORIGIN, BACKEND_API, RECOVERY_SHA, "정확한 40자리 SHA"):
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
        verify_evidence()
        verify_sources()
    except PlanError as exc:
        print(f"frontend static deployment plan verification failed: {exc}", file=sys.stderr)
        return 1
    print("frontend static deployment result verification (static, no provider mutation)")
    print("- publish allowlist: index.html / admin.html / src/**/*.js / src/**/*.css")
    print("- local/public API: local preserved / Render backend pinned")
    print("- static site/backend CORS deploy: live/executed-once")
    print(f'- backend CORS actual/applied: ["{FRONTEND_ORIGIN}"]/yes')
    print("- browser master-data: HTTP 200 but 1500ms timeout fallback")
    print("- automatic retry: no")
    print(f"- result: {RESULT}")
    print(f"- next safe stage: {NEXT_STAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

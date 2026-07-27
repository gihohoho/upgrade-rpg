#!/usr/bin/env python3
"""Fail-closed checker for the v351 backend/static provider release gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "deploy/v351-public-release-gates.example.json"
LIFECYCLE_PATH = ROOT / "deploy/github-actions-ghcr-publish-lifecycle.json"
ISOLATED_EVIDENCE_PATH = ROOT / "deploy/review/isolated-image-pull-validation-v353.json"
PROVIDER_EVIDENCE_PATH = ROOT / "deploy/review/render-v351-provider-release-v355.json"
BACKEND_POLICY_PATH = ROOT / "deploy/backend-image-ghcr-policy.example.json"
STATIC_PLAN_PATH = ROOT / "deploy/render-static-site.example.json"

VERSION = "v355.v351-provider-release-deployed-verified-content-ready"
RESULT = "v351-provider-release-deployed-verified-content-ready"
NEXT_STAGE = "select-first-content-and-balance-change-scope"
BASELINE = "81beaa0864c3422fb9fc2071b9c4965936ecafac"
PROVIDER_PREPARATION_SHA = "05f1af8ed1316e2cf0e0f39ac795b3ff60bccb62"
LIFECYCLE_VERSION = "v352.owner-only-publish-lifecycle-with-six-attempt-history"
PREPARATION_SHA = "b48dfd0751b12b1b3afb6474f9d35359ba2f8177"
AUTHORIZATION_SHA = "7578eb665c03ee0fcb9399929328ce684cdd1b31"
CLOSURE_SHA = "5d547126322dbe3c235e855cc9c2f7337342ae36"
RECORD_SHA = "5c842deec6d1f496679a144897f485b07428810b"
RUN_ID = 30226905547
OLD_IMAGE = (
    "ghcr.io/gihohoho/upgrade-rpg-backend@"
    "sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1"
)
NEW_DIGEST = "sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac"
NEW_IMAGE = f"ghcr.io/gihohoho/upgrade-rpg-backend@{NEW_DIGEST}"
EXPECTED_HASHES = {
    "backend/app/main.py": "61c34c329b19cea8568296317b2649ddfef191a7ff003348e845f37882d754d4",
    "src/api/master-data-boot-policy.js": "4c230b5adde411c5ca7710d8582f3ff0871521ab554c89be47eebc3e718a53ec",
    "src/api/master-data-runtime-switch.js": "701334af14edbb025389857a7802c07314ce18ac423fe28941dc2fa66f499a39",
    "tools/build_legacy_static_site.mjs": "e05dfcb7e3ddb3782463ec3064acc45c60c8d5db2df2dfeee2312a3486ff501c",
}
STATE_FILES = (
    ROOT / "AGENTS.md",
    ROOT / "NEXT_CHAT_PROMPT.md",
    ROOT / "NEXT_CHAT_HANDOFF.md",
    ROOT / "docs/current/CURRENT_STATUS.md",
    ROOT / "docs/handoff/NEXT_CHAT_PROMPT.md",
    ROOT / "docs/handoff/NEXT_CHAT_HANDOFF.md",
)


class ReleaseGateError(RuntimeError):
    """Safe static release-gate failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseGateError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON: {path.relative_to(ROOT)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseGateError(f"invalid JSON: {path.name} ({type(exc).__name__})") from None
    require(isinstance(payload, dict), f"JSON root must be object: {path.name}")
    return payload


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_contract(plan: dict[str, Any]) -> None:
    require(plan.get("schemaVersion") == VERSION, "release gate version differs")
    require(plan.get("result") == RESULT, "release gate result differs")
    require(plan.get("nextSafeStage") == NEXT_STAGE, "release next stage differs")
    require(plan.get("productionResourcesMutated") is True, "provider mutation completion flag must be true")
    require(plan.get("providerReleaseExecuted") is True, "provider release completion is missing")

    source = plan.get("source") or {}
    require(source.get("baselineCommit") == BASELINE, "v351 source baseline differs")
    require(source.get("branch") == "main", "release branch must be main")
    require(source.get("cleanPushedPreparationRequired") is True, "clean pushed preparation is required")
    require(source.get("cleanPushedPreparationSha") == PROVIDER_PREPARATION_SHA, "provider preparation SHA differs")
    require(source.get("runtimeFiles") == EXPECTED_HASHES, "runtime file hash contract differs")

    approval = plan.get("ownerApproval") or {}
    require(approval.get("approvedPreparationSha") == PROVIDER_PREPARATION_SHA, "provider approval SHA differs")
    require(approval.get("recordedByUserMessage") is True, "provider approval record is missing")
    require(approval.get("scopeConsumed") is True, "provider approval scope must be consumed")

    actions = plan.get("githubActions") or {}
    require(actions.get("trigger") == "workflow_dispatch-only", "workflow trigger differs")
    require(actions.get("lifecycleSchemaVersion") == LIFECYCLE_VERSION, "lifecycle version differs")
    require(actions.get("lifecycleState") == "attempt-recorded", "workflow attempt must be recorded")
    require(actions.get("publishReviewerGateReady") is False, "publish gate must be closed")
    require(actions.get("approvedPreparationSha") == PREPARATION_SHA, "approved preparation differs")
    require(actions.get("ownerApprovalRecorded") is True, "owner approval record is missing")
    require(actions.get("workflowRunId") == RUN_ID, "workflow run differs")
    require(actions.get("workflowRunAttempt") == 1, "workflow rerun is forbidden")
    require(actions.get("workflowConclusion") == "success", "workflow must have succeeded")
    require(actions.get("authorizationCommitSha") == AUTHORIZATION_SHA, "authorization SHA differs")
    require(actions.get("closureCommitSha") == CLOSURE_SHA, "closure SHA differs")
    require(actions.get("recordCommitSha") == RECORD_SHA, "record SHA differs")
    require(actions.get("registryMutationExecuted") is True, "registry result must be recorded")
    require(actions.get("signatureVerified") is True, "signature verification is required")
    require(actions.get("rerunForbidden") is True, "rerun must remain forbidden")

    backend = plan.get("backendRelease") or {}
    require(backend.get("serviceId") == "srv-d9iro458nd3s73acgmsg", "backend service differs")
    require(backend.get("previousLiveImage") == OLD_IMAGE, "previous live image differs")
    require(backend.get("currentLiveImage") == NEW_IMAGE, "current live image differs")
    require(backend.get("newImageReference") == NEW_IMAGE, "new exact image differs")
    require(backend.get("supplyChainValidationComplete") is True, "supply-chain validation is incomplete")
    require(backend.get("isolatedRuntimeValidationComplete") is True, "isolated validation is incomplete")
    require(
        backend.get("isolatedEvidence") == "deploy/review/isolated-image-pull-validation-v353.json",
        "isolated evidence path differs",
    )
    require(backend.get("renderExactImageDeployPreparationReady") is True, "backend deploy is not prepared")
    require(backend.get("renderDeployApproved") is True, "backend deploy approval is missing")
    require(backend.get("renderDeployExecuted") is True, "backend deploy completion is missing")
    require(backend.get("renderDeployId") == "dep-d9jeuf3eo5us73ba6cgg", "backend deploy ID differs")
    require(backend.get("renderDeployStatus") == "live", "backend deploy is not live")
    require(backend.get("renderDeployTrigger") == "image-updated", "backend deploy trigger differs")
    require(backend.get("renderDeployCount") == 1, "backend deploy count differs")
    require(backend.get("singleManualDeployOnly") is True, "backend deploy must be single/manual")
    require(backend.get("automaticRetry") is False, "backend automatic retry must be off")

    frontend = plan.get("frontendRelease") or {}
    require(frontend.get("serviceId") == "srv-d9iu337aqgkc73am4lh0", "static service differs")
    require(frontend.get("autoDeploy") is False, "static auto-deploy must remain off")
    require(frontend.get("releaseSourceBaseline") == BASELINE, "static release baseline differs")
    require(frontend.get("currentLiveSourceCommit") == BASELINE, "static live source differs")
    require(frontend.get("staticDeployPreparationReady") is True, "static deploy is not prepared")
    require(frontend.get("staticDeployApproved") is True, "static deploy approval is missing")
    require(frontend.get("staticDeployExecuted") is True, "static deploy completion is missing")
    require(frontend.get("staticDeployId") == "dep-d9jev7gu01pc73favje0", "static deploy ID differs")
    require(frontend.get("staticDeployStatus") == "live", "static deploy is not live")
    require(frontend.get("staticDeployTrigger") == "manual-specific-commit", "static deploy trigger differs")
    require(frontend.get("staticDeployCount") == 1, "static deploy count differs")
    require(frontend.get("singleManualDeployOnly") is True, "static deploy must be single/manual")
    require(frontend.get("automaticRetry") is False, "static automatic retry must be off")

    scope = plan.get("approvalScopeAfterExactSha") or {}
    for key in (
        "verifyCleanPushedMainExactSha",
        "updateExistingBackendServiceToExactImageOnce",
        "deployExistingStaticSiteFromExactSourceOnce",
        "verifyGameAndAdminHttp200",
        "verifyMasterDataWithoutFrontendFallback",
        "verifyAdminGuardedContentWorkflowWithoutWrite",
        "recordSanitizedEvidence",
    ):
        require(scope.get(key) is True, f"approved provider scope differs: {key}")
    for key in (
        "databaseWrite",
        "alembicMutation",
        "adminWrite",
        "contentOrBalanceChange",
        "customDomainOrDns",
        "paymentMethodChange",
        "automaticDeployOrRetry",
    ):
        require(scope.get(key) is False, f"forbidden provider scope differs: {key}")

    validation = plan.get("validation") or {}
    require(validation.get("evidence") == "deploy/review/render-v351-provider-release-v355.json", "provider evidence path differs")
    require(validation.get("backendHealthStatus") == 200, "backend health result differs")
    require(validation.get("databaseHealthStatus") == 200, "database health result differs")
    require(validation.get("databaseHealthRequestCount") == 1, "database health request count differs")
    require(validation.get("indexStatus") == 200 and validation.get("adminStatus") == 200, "public page status differs")
    require(validation.get("corsAllowOrigin") == "https://gihohoho-upgrade-rpg.onrender.com", "CORS origin differs")
    require(validation.get("masterDataStatus") == 200, "master-data status differs")
    require(validation.get("masterDataMilliseconds") == 1346, "master-data timing differs")
    require(validation.get("masterDataContentEncoding") == "gzip", "master-data encoding differs")
    for key in ("browserMasterDataAppliedWithoutFallback", "adminGuardedReadOnlyVerified", "contentReadiness"):
        require(validation.get(key) is True, f"provider validation differs: {key}")

    forbidden = plan.get("forbiddenBeforeExactShaApproval") or []
    for marker in (
        "Render backend image update or deploy",
        "Render Static Site deploy",
        "database or Alembic mutation",
        "admin write or game content change",
        "automatic deploy or retry",
        "additional GitHub Actions dispatch or rerun",
    ):
        require(marker in forbidden, f"missing forbidden boundary: {marker}")


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        check=False,
        timeout=20,
    )
    require(completed.returncode == 0, f"Git check failed: {' '.join(args)}")
    return completed.stdout.decode("utf-8", errors="replace").strip()


def verify_repository(plan: dict[str, Any]) -> None:
    require(re.fullmatch(r"[0-9a-f]{40}", BASELINE) is not None, "baseline SHA shape differs")
    require(git("merge-base", "--is-ancestor", BASELINE, "HEAD") == "", "v351 baseline is not an ancestor")
    require(
        git("merge-base", "--is-ancestor", PROVIDER_PREPARATION_SHA, "HEAD") == "",
        "provider preparation SHA is not an ancestor",
    )
    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.is_file(), f"missing pinned source: {relative}")
        require(sha256_file(path) == expected, f"pinned source hash differs: {relative}")

    lifecycle = load_json(LIFECYCLE_PATH)
    require(lifecycle.get("schemaVersion") == LIFECYCLE_VERSION, "live lifecycle schema differs")
    require(lifecycle.get("state") == "attempt-recorded", "live workflow attempt is not recorded")
    require(lifecycle.get("publishReviewerGateReady") is False, "live publish gate is open")
    require(lifecycle.get("approvedPreparationSha") == PREPARATION_SHA, "live approval differs")
    require((lifecycle.get("ownerApproval") or {}).get("recorded") is True, "live owner approval is missing")
    require((lifecycle.get("closure") or {}).get("authorizationSourceSha") == AUTHORIZATION_SHA, "live authorization differs")
    require((lifecycle.get("closure") or {}).get("closureCommitSha") == CLOSURE_SHA, "live closure differs")
    observed = lifecycle.get("observedAttempt") or {}
    require(observed.get("runId") == RUN_ID, "live run differs")
    require(observed.get("runAttempt") == 1, "live rerun differs")
    require(observed.get("status") == "completed", "live run is incomplete")
    require(observed.get("conclusion") == "success", "live run failed")
    require(observed.get("imageDigest") == NEW_DIGEST, "live image digest differs")
    require(observed.get("signatureVerified") is True, "live signature is unverified")

    evidence = load_json(ISOLATED_EVIDENCE_PATH)
    require(evidence.get("schemaVersion") == "v353.v351-image-isolated-runtime-validation", "evidence version differs")
    require(evidence.get("workflowRunId") == RUN_ID, "evidence run differs")
    require(evidence.get("workflowRunAttempt") == 1, "evidence run attempt differs")
    require(evidence.get("workflowConclusion") == "success", "evidence workflow failed")
    require(evidence.get("sourceCommitSha") == AUTHORIZATION_SHA, "evidence authorization differs")
    require(evidence.get("preparationCommitSha") == PREPARATION_SHA, "evidence preparation differs")
    require(evidence.get("closureCommitSha") == CLOSURE_SHA, "evidence closure differs")
    require(evidence.get("recordCommitSha") == RECORD_SHA, "evidence record differs")
    require(evidence.get("imageReference") == NEW_IMAGE, "evidence image differs")
    require(evidence.get("imageId") == NEW_DIGEST, "evidence image ID differs")
    require(evidence.get("platform") == "linux/amd64", "evidence platform differs")
    supply = evidence.get("supplyChainValidation") or {}
    require(supply.get("localTrivyHighCriticalFindings") == 0, "local vulnerabilities differ")
    require(supply.get("registryTrivyHighCriticalFindings") == 0, "registry vulnerabilities differ")
    require(supply.get("registryProvenanceVerified") is True, "provenance is unverified")
    require(supply.get("registrySbomFormat") == "SPDX-2.3", "SBOM format differs")
    require(supply.get("cosignVerified") is True, "Cosign is unverified")
    runtime = evidence.get("runtimeValidation") or {}
    require(runtime.get("healthStatus") == 200 and runtime.get("healthOk") is True, "isolated health failed")
    require(runtime.get("systemCaX509Count") == 119, "isolated CA count differs")
    require(runtime.get("pipPresent") is False, "pip must be absent")
    require(runtime.get("rootFilesystemWriteBlocked") is True, "rootfs write was not blocked")
    cleanup = evidence.get("cleanup") or {}
    for key in ("containerRemoved", "internalNetworkRemoved", "localImageRemoved", "existingPostgresContainerHealthyAfterCleanup"):
        require(cleanup.get(key) is True, f"isolated cleanup differs: {key}")
    for key in (
        "productionRuntimeApplied",
        "renderBackendDeployApproved",
        "renderBackendDeployExecuted",
        "renderStaticDeployApproved",
        "renderStaticDeployExecuted",
        "databaseWriteExecuted",
        "alembicMutationExecuted",
        "adminWriteExecuted",
        "contentOrBalanceChanged",
    ):
        require(evidence.get(key) is False, f"provider/mutation boundary differs: {key}")

    policy = load_json(BACKEND_POLICY_PATH)
    require(policy.get("publishLifecycleState") == "attempt-recorded", "backend policy lifecycle differs")
    require(policy.get("approvedPreparationSha") == PREPARATION_SHA, "backend policy approval differs")
    require(policy.get("exactPreparationShaApproved") is True, "backend image approval record is missing")
    require(policy.get("sourceControlledPublishGateReady") is False, "backend publish gate is open")
    require(policy.get("productionReference") == OLD_IMAGE, "backend live reference differs")
    require(policy.get("verifiedCandidateReference") == NEW_IMAGE, "backend verified candidate differs")
    require(policy.get("verifiedCandidateAppliedToRender") is True, "verified candidate Render application is missing")
    require(policy.get("renderLiveReference") == NEW_IMAGE, "Render live reference differs")
    require(policy.get("renderProviderReleaseApprovedPreparationSha") == PROVIDER_PREPARATION_SHA, "Render approval differs")
    require(policy.get("renderProviderReleaseDeployId") == "dep-d9jeuf3eo5us73ba6cgg", "Render deploy record differs")
    require(
        policy.get("renderProviderReleaseEvidence") == "deploy/review/render-v351-provider-release-v355.json",
        "Render provider evidence differs",
    )
    require(
        policy.get("isolatedValidationEvidence") == "deploy/review/isolated-image-pull-validation-v353.json",
        "backend isolated evidence differs",
    )
    require(policy.get("nextSafeStage") == NEXT_STAGE, "backend policy next stage differs")

    provider = load_json(PROVIDER_EVIDENCE_PATH)
    require(provider.get("schemaVersion") == VERSION, "provider evidence version differs")
    require(provider.get("result") == RESULT, "provider evidence result differs")
    require(provider.get("nextSafeStage") == NEXT_STAGE, "provider evidence next stage differs")
    owner = provider.get("ownerApproval") or {}
    require(owner.get("approvedPreparationSha") == PROVIDER_PREPARATION_SHA, "provider evidence approval differs")
    require(owner.get("scopeConsumed") is True, "provider evidence approval is not consumed")
    backend_live = provider.get("backend") or {}
    require(backend_live.get("liveImageReference") == NEW_IMAGE, "provider evidence backend image differs")
    require(backend_live.get("deployId") == "dep-d9jeuf3eo5us73ba6cgg", "provider evidence backend deploy differs")
    require(backend_live.get("status") == "live" and backend_live.get("deployCount") == 1, "provider backend deploy state differs")
    require((backend_live.get("health") or {}).get("status") == 200, "provider backend health differs")
    db_health = backend_live.get("databaseHealth") or {}
    require(db_health.get("status") == 200 and db_health.get("requestCount") == 1, "provider DB health differs")
    frontend_live = provider.get("frontend") or {}
    require(frontend_live.get("liveSourceCommit") == BASELINE, "provider frontend source differs")
    require(frontend_live.get("deployId") == "dep-d9jev7gu01pc73favje0", "provider frontend deploy differs")
    require(frontend_live.get("status") == "live" and frontend_live.get("deployCount") == 1, "provider frontend deploy state differs")
    require(frontend_live.get("autoDeploy") is False, "provider frontend auto-deploy is on")
    integration = provider.get("integration") or {}
    master = integration.get("masterData") or {}
    require(master.get("status") == 200 and master.get("contentEncoding") == "gzip", "provider master-data differs")
    require(master.get("browserRuntimeAppliedLogObserved") is True, "browser runtime apply evidence is missing")
    require(master.get("browserFallbackWarningObserved") is False, "browser fallback was observed")
    admin = integration.get("admin") or {}
    require(admin.get("readOnly") is True and admin.get("generalWriteUi") == "blocked", "admin guard differs")
    require(admin.get("writeActionExecuted") is False, "admin write was executed")
    rotation = provider.get("securityRotation") or {}
    require(rotation.get("backendDeployHookRotated") is True, "backend deploy hook was not rotated")
    require(rotation.get("staticSiteDeployHookRotated") is True, "static deploy hook was not rotated")
    require(rotation.get("rotatedValuesRecorded") is False, "rotated hook value must not be recorded")
    forbidden_results = provider.get("forbiddenMutationResults") or {}
    for key, value in forbidden_results.items():
        require(value is False, f"forbidden provider mutation executed: {key}")
    readiness = provider.get("contentReadiness") or {}
    require(readiness.get("readyToSelectFirstContentAndBalanceScope") is True, "content readiness differs")

    static = load_json(STATIC_PLAN_PATH)
    require((static.get("site") or {}).get("autoDeploy") is False, "provider static auto-deploy is on")
    require(
        (static.get("approvalGate") or {}).get("automaticRetryExecuted") is False,
        "provider static automatic retry record differs",
    )

    for state_file in STATE_FILES:
        require(state_file.is_file(), f"missing state file: {state_file.relative_to(ROOT)}")
        text = state_file.read_text(encoding="utf-8")
        for marker in (VERSION, RESULT, NEXT_STAGE):
            require(marker in text, f"{state_file.relative_to(ROOT)} is missing {marker}")
    require(
        (ROOT / "NEXT_CHAT_PROMPT.md").read_bytes()
        == (ROOT / "docs/handoff/NEXT_CHAT_PROMPT.md").read_bytes(),
        "prompt mirror differs",
    )
    require(
        (ROOT / "NEXT_CHAT_HANDOFF.md").read_bytes()
        == (ROOT / "docs/handoff/NEXT_CHAT_HANDOFF.md").read_bytes(),
        "handoff mirror differs",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    parser.parse_args()
    try:
        plan = load_json(PLAN_PATH)
        validate_contract(plan)
        verify_repository(plan)
    except ReleaseGateError as exc:
        print(f"v351 public release gate verification failed: {exc}", file=sys.stderr)
        return 1

    print("v351 provider release verification (completed, sanitized evidence)")
    print(f"- source baseline: {BASELINE}")
    print(f"- backend exact image: {NEW_IMAGE}")
    print(f"- workflow: run {RUN_ID} / attempt=1 / success / gate closed")
    print("- supply chain + isolated runtime + cleanup: verified")
    print("- backend/static provider deploy approved/executed/live: yes/yes/yes")
    print("- public integration: health/db/index/admin/CORS/master-data/admin guard verified")
    print(f"- result: {RESULT}")
    print(f"- next safe stage: {NEXT_STAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

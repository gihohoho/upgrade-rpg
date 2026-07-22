#!/usr/bin/env python3
"""Fail-closed validation for the v334 reviewed production deployment plan."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

VERSION = "v334.production-deploy-plan-reviewed-inputs-blocked"
RESULT = "production-deploy-plan-reviewed-inputs-blocked"
NEXT_STAGE = "select-production-targets-and-complete-executable-deploy-plan"
IMAGE = "ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2"
PLAN_PATH = "deploy/production-deploy-plan.example.json"
EVIDENCE_PATH = "deploy/review/isolated-image-pull-validation-v333.json"


class DeploymentPlanError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DeploymentPlanError(message)


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON file: {path.as_posix()}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DeploymentPlanError(f"invalid JSON: {path.as_posix()}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root must be an object: {path.as_posix()}")
    return value


def boolean(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    require(isinstance(value, bool), f"{key} must be boolean")
    return value


def inspect_plan(root: Path) -> dict[str, Any]:
    plan = read_json(root / PLAN_PATH)
    evidence = read_json(root / EVIDENCE_PATH)
    env_text = (root / "deploy/production.env.example").read_text(encoding="utf-8")
    compose = (root / "deploy/docker-compose.production.yml").read_text(encoding="utf-8")
    doc = (root / "docs/current/PRODUCTION_DEPLOYMENT_PLAN.md").read_text(encoding="utf-8")

    require(plan.get("schemaVersion") == VERSION, "deployment plan schemaVersion changed")
    require(
        set(plan) == {
            "schemaVersion", "reviewedAtUtc", "basedOnCommitSha", "planReview",
            "approvalContract", "image", "githubLiveReview", "architecture",
            "requiredInputs", "orderedExecution", "rollback", "nextSafeStage",
        },
        "deployment plan top-level schema changed",
    )
    require(re.fullmatch(r"[0-9a-f]{40}", str(plan.get("basedOnCommitSha"))) is not None, "basedOnCommitSha must be a full SHA")
    require(re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(plan.get("reviewedAtUtc"))) is not None, "reviewedAtUtc must be UTC")

    review = plan.get("planReview")
    require(isinstance(review, dict), "planReview must be an object")
    for key in ("requestedByOwner", "completed", "isolatedEvidenceReviewed"):
        require(boolean(review, key) is True, f"plan review flag must be true: {key}")
    require(boolean(review, "productionResourcesMutated") is False, "plan review must not mutate production resources")

    approval = plan.get("approvalContract")
    require(isinstance(approval, dict), "approvalContract must be an object")
    require(approval.get("model") == "owner-only-exact-preparation-sha", "approval model changed")
    require(approval.get("preparationCommitSha") is None, "unready plan cannot contain preparation approval SHA")
    for key in ("exactPreparationShaApprovalRecorded", "approvalReady", "productionDeploymentApproved", "productionDeploymentExecuted"):
        require(boolean(approval, key) is False, f"deployment approval must remain closed: {key}")
    require(boolean(approval, "requiresAllInputsResolved") is True, "all required inputs must be resolved before approval")
    excluded = approval.get("excludedScope")
    require(isinstance(excluded, list) and any("Alembic" in item for item in excluded), "Alembic exclusion is missing")
    require(any("down -v" in item for item in excluded), "volume deletion exclusion is missing")

    image = plan.get("image")
    require(isinstance(image, dict) and image.get("reference") == IMAGE, "exact production image changed")
    require(image.get("platform") == "linux/amd64", "production platform changed")
    require(boolean(image, "signatureVerified") is True, "signature must remain verified")
    require(image.get("exactDigestTrivyHighCriticalFindings") == 0, "exact digest vulnerability result changed")
    require(image.get("isolatedRuntimeEvidence") == EVIDENCE_PATH, "isolated evidence path changed")
    require(evidence.get("imageReference") == IMAGE, "isolated evidence image differs")
    require(evidence.get("runtimeValidation", {}).get("healthOk") is True, "isolated health evidence is not successful")
    cleanup = evidence.get("cleanup", {})
    for key in ("containerRemoved", "internalNetworkRemoved", "localImageRemoved"):
        require(cleanup.get(key) is True, f"isolated cleanup evidence missing: {key}")

    live = plan.get("githubLiveReview")
    require(isinstance(live, dict), "githubLiveReview must be an object")
    for key in ("actionsEnabled", "selectedActionsOnly", "fullLengthActionShaRequired", "publishEnvironmentExists", "publishEnvironmentMainOnly", "adminsCanBypassEnvironment"):
        require(boolean(live, key) is True, f"GitHub live marker changed: {key}")
    for key in ("actionsCanApprovePullRequests", "nativeRequiredReviewerConfigured"):
        require(boolean(live, key) is False, f"GitHub approval boundary changed: {key}")
    require(live.get("defaultWorkflowPermissions") == "read", "default workflow permission changed")

    architecture = plan.get("architecture")
    require(isinstance(architecture, dict), "architecture must be an object")
    for key in ("managedPostgresql", "providerCaVerifyFull", "externalReverseProxyHttps"):
        require(boolean(architecture, key) is True, f"architecture requirement changed: {key}")
    for key in ("backendHostPortPublished", "bundledDatabase", "automaticMigration"):
        require(boolean(architecture, key) is False, f"unsafe architecture option enabled: {key}")
    require(architecture.get("backendReplicas") == 1 and architecture.get("uvicornWorkers") == 1, "backend replicas/workers must remain 1/1")

    inputs = plan.get("requiredInputs")
    expected_keys = {
        "production-host", "managed-postgresql", "provider-ca", "reverse-proxy-and-domain",
        "secret-injection", "external-edge-network", "backup-and-first-deploy-rollback",
    }
    require(isinstance(inputs, list) and {item.get("key") for item in inputs if isinstance(item, dict)} == expected_keys, "required input inventory changed")
    require(all(item.get("status") == "unresolved" for item in inputs), "all production inputs must remain unresolved in v334")

    ordered = plan.get("orderedExecution")
    require(isinstance(ordered, list) and len(ordered) == 12, "deployment execution sequence changed")
    require(any("exact digest" in item for item in ordered), "exact digest verification step is missing")
    require(any("without host ports" in item for item in ordered), "no-host-port start boundary is missing")
    require(any("read-only connectivity" in item for item in ordered), "read-only DB health boundary is missing")
    require(all("down -v" not in item and "alembic" not in item.lower() for item in ordered), "unsafe deployment command entered execution sequence")

    rollback = plan.get("rollback")
    require(isinstance(rollback, dict), "rollback must be an object")
    require(boolean(rollback, "automaticRollback") is False, "automatic rollback must remain disabled")
    require(boolean(rollback, "firstDeploymentHasPreviousImage") is False, "first deployment cannot claim a prior image")
    require(boolean(rollback, "forbidComposeDownVolumes") is True, "volume deletion guard is missing")
    require(boolean(rollback, "forbidAutomaticRetry") is True, "automatic retry guard is missing")
    require("no schema or data mutation" in str(rollback.get("databaseRollback")), "database rollback boundary changed")

    require(f"BACKEND_IMAGE={IMAGE}" in env_text, "production env exact image differs")
    require("image: ${BACKEND_IMAGE:?" in compose, "Compose must require the exact image input")
    require(re.search(r"(?m)^\s+ports:\s*$", compose) is None, "production backend host ports must remain absent")
    require(re.search(r"(?m)^\s+build:\s*$", compose) is None, "production Compose must not build")
    require("plan review: complete" in doc and "approval ready: no" in doc, "deployment plan document approval boundary is missing")
    require(plan.get("nextSafeStage") == NEXT_STAGE and NEXT_STAGE in doc, "next safe stage changed")

    return {
        "toolVersion": VERSION,
        "imageReference": IMAGE,
        "planReviewCompleted": True,
        "requiredInputsResolved": False,
        "approvalReady": False,
        "productionDeploymentApproved": False,
        "productionDeploymentExecuted": False,
        "result": RESULT,
        "nextSafeStage": NEXT_STAGE,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = inspect_plan(root)
    except (DeploymentPlanError, OSError) as exc:
        if args.json:
            print(json.dumps({"toolVersion": VERSION, "result": "blocked-or-failed", "reason": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print("Production deployment plan verification")
            print("- result: blocked-or-failed")
            print(f"- reason: {exc}")
        return 1 if args.strict else 0
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Production deployment plan verification")
        print("- plan review: complete")
        print("- required production inputs: unresolved")
        print("- approval ready: no")
        print("- production deploy approved/executed: no/no")
        print(f"- result: {result['result']}")
        print(f"- next safe stage: {result['nextSafeStage']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

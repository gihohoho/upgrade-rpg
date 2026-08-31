#!/usr/bin/env python3
"""Validate the v334 reviewed production deploy plan and closed approval boundary."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
from typing import Any

TOOL_VERSION = "v334.production-deploy-plan-reviewed-inputs-blocked"
READY_RESULT = "production-deploy-plan-reviewed-inputs-blocked"
PREPARATION_READY_RESULT = "github-actions-ghcr-owner-only-provenance-path-preparation-ready-publish-gated"
AUTHORIZATION_OPEN_RESULT = "github-actions-ghcr-owner-only-authorization-open"
AUTHORIZATION_CLOSED_AWAITING_EVIDENCE_RESULT = (
    "github-actions-ghcr-owner-only-authorization-closed-awaiting-evidence"
)
ATTEMPT_RECORDED_RESULT = "github-actions-ghcr-owner-only-attempt-recorded-publish-gated"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "select-production-targets-and-complete-executable-deploy-plan"
ISOLATED_NEXT_SAFE_STAGE = "review-isolated-validation-and-approve-production-deploy-plan"
EXPECTED_REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
EXPECTED_NAMESPACE = "gihohoho"
EXPECTED_REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
EXPECTED_REFERENCE_TEMPLATE = EXPECTED_REPOSITORY + "@sha256:<approved-64-hex-digest>"
EXPECTED_REFERENCE = EXPECTED_REPOSITORY + "@sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1"
EXPECTED_BASE = "python:3.11.15-alpine3.23@sha256:ac0151f0eec4b7ba78bc47d337f328c6db706e7255b35b2327c2749f058c82fe"
WORKFLOW_PATH = ".github/workflows/publish-backend-ghcr.yml"
LIFECYCLE_PATH = "deploy/github-actions-ghcr-publish-lifecycle.json"
ISOLATED_EVIDENCE_PATH = "deploy/review/isolated-image-pull-validation-v353.json"
PROVIDER_RELEASE_EVIDENCE_PATH = "deploy/review/render-v351-provider-release-v355.json"
PRODUCTION_DEPLOY_PLAN_PATH = "deploy/production-deploy-plan.example.json"
LIFECYCLE_SCHEMA_VERSION = "v352.owner-only-publish-lifecycle-with-six-attempt-history"
PRIOR_APPROVED_PREPARATION_SHA = "36e8720a53ef7ff6a8334de6bc99646998d63fc9"
SECOND_APPROVED_PREPARATION_SHA = "2f77ebf0f60a39c936509df26f903995f0c62967"
PRIOR_ATTEMPT_EVIDENCE = {
    "preparationSha": PRIOR_APPROVED_PREPARATION_SHA,
    "authorizationSha": "26a11356e33c978afa8cd8a4881500fa62cdbc5c",
    "closureSha": "1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5",
    "recordCommitSha": "1f0340ddfcf3c8a74cf14110d5957627d4c5d38a",
    "runId": 29909291344,
    "runUrl": "https://github.com/gihohoho/upgrade-rpg/actions/runs/29909291344",
    "conclusion": "success",
    "registryLoginExecuted": True,
    "imageBuildExecuted": True,
    "imagePushExecuted": True,
}
ATTEMPT_HISTORY = [
    {
        "preparationSha": "350bbd085f1cf636810d75ddcbb5321e0791256c",
        "authorizationSha": "32e5102877851ace06e1c0ed3bcb48310b8d65b6",
        "closureSha": "362f5f1901d234b5b86f2a7cefdabd28ac61f896",
        "recordCommitSha": "1f12ea59eb54385337557e9754f86731ec53d253",
        "runId": 29716038891,
        "runUrl": "https://github.com/gihohoho/upgrade-rpg/actions/runs/29716038891",
        "conclusion": "failure",
        "registryLoginExecuted": False,
        "imageBuildExecuted": False,
        "imagePushExecuted": False,
        "artifactCount": 0,
        "imageDigest": None,
        "signatureVerified": False,
    },
    {
        "preparationSha": SECOND_APPROVED_PREPARATION_SHA,
        "authorizationSha": "7e69555b8b653c406b322fb5c8f23e550751d72c",
        "closureSha": "5479e6b14826b3a0f2b6d0c3beb0e2142ca22c94",
        "recordCommitSha": "c93a0327bc25941865f4ee8d600a4f903886a4fe",
        "runId": 29877813770,
        "runUrl": "https://github.com/gihohoho/upgrade-rpg/actions/runs/29877813770",
        "conclusion": "failure",
        "registryLoginExecuted": False,
        "imageBuildExecuted": True,
        "imagePushExecuted": False,
        "artifactCount": 0,
        "imageDigest": None,
        "signatureVerified": False,
    },
    {
        "preparationSha": "b35dfacf427162b348a6bd29eb030778edc7741c",
        "authorizationSha": "04e002060e576f19f4d8687b33635a414486206d",
        "closureSha": "64e5ae0f5e5385ba00df16bb10ac33789ca3760a",
        "recordCommitSha": "303a2ed01c69c29894efdcde4ead6c2291c3d8bc",
        "runId": 29883012957,
        "runUrl": "https://github.com/gihohoho/upgrade-rpg/actions/runs/29883012957",
        "conclusion": "failure",
        "registryLoginExecuted": False,
        "imageBuildExecuted": True,
        "imagePushExecuted": False,
        "artifactCount": 1,
        "imageDigest": None,
        "signatureVerified": False,
    },
    {
        "preparationSha": "13b15409929d77b4e6209481596e4f4550a22ba5",
        "authorizationSha": "4fb31f51ca0de15d77a73390b5a07e394ffce12a",
        "closureSha": "ddf475c1a2449feb50ef2af1a536e4150cf0ad59",
        "recordCommitSha": "f945214f2387b6aa191655d3740e18ef862bd6fb",
        "runId": 29886540317,
        "runUrl": "https://github.com/gihohoho/upgrade-rpg/actions/runs/29886540317",
        "conclusion": "failure",
        "registryLoginExecuted": True,
        "imageBuildExecuted": True,
        "imagePushExecuted": True,
        "artifactCount": 2,
        "imageDigest": "sha256:6e4aefad0cdf1767670b7f736477dd9e00f17bf49a03fa471828df6667c41149",
        "signatureVerified": False,
    },
    {
        **PRIOR_ATTEMPT_EVIDENCE,
        "artifactCount": 2,
        "imageDigest": "sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2",
        "signatureVerified": True,
    },
    {
        "preparationSha": "fb231afa5081f5bfd7b459081a58bc5acd6699df",
        "authorizationSha": "f5d69c1bbef101cc9124b9dede18c844ef80b59c",
        "closureSha": "ebb5ef46e3115bc358d62d93a64002b8711f4232",
        "recordCommitSha": "cf9e0bab121186d2ac51f889f807348cc46f192c",
        "runId": 30180738530,
        "runUrl": "https://github.com/gihohoho/upgrade-rpg/actions/runs/30180738530",
        "conclusion": "success",
        "registryLoginExecuted": True,
        "imageBuildExecuted": True,
        "imagePushExecuted": True,
        "artifactCount": 2,
        "imageDigest": "sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1",
        "signatureVerified": True,
    },
]
APPROVED_PREPARATION_SHA = "b48dfd0751b12b1b3afb6474f9d35359ba2f8177"
AUTHORIZATION_SHA = "7578eb665c03ee0fcb9399929328ce684cdd1b31"
CLOSURE_SHA = "5d547126322dbe3c235e855cc9c2f7337342ae36"
RECORD_COMMIT_SHA = "5c842deec6d1f496679a144897f485b07428810b"
CURRENT_RUN_ID = 30226905547
CURRENT_RUN_URL = f"https://github.com/gihohoho/upgrade-rpg/actions/runs/{CURRENT_RUN_ID}"
CURRENT_ARTIFACT_IDS = [8638838292, 8638825538]
CURRENT_ARTIFACT_DIGESTS = [
    "sha256:9d23b748aed34152afe979e678bc99d7246e47e4b95dae6d7da21be6f6f24ae3",
    "sha256:db7046ca2a94d8794e6aa56df7bb331049d1b9ed1bb2a4c189f33a7ffa3ed2e6",
]
CURRENT_IMAGE_DIGEST = "sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac"
VERIFIED_CANDIDATE_REFERENCE = EXPECTED_REPOSITORY + "@" + CURRENT_IMAGE_DIGEST
PROVIDER_RELEASE_PREPARATION_SHA = "05f1af8ed1316e2cf0e0f39ac795b3ff60bccb62"
PROVIDER_RELEASE_DEPLOY_ID = "dep-d9jeuf3eo5us73ba6cgg"
PROVIDER_RELEASE_NEXT_STAGE = "select-first-content-and-balance-change-scope"
LIFECYCLE_SUPPORTED_STATES = (
    "preparation-closed",
    "authorization-open",
    "authorization-closed-awaiting-evidence",
    "attempt-recorded",
)
REVISION_SHA256 = "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa"


class CodexHandoffError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CodexHandoffError(message)


def _read(path: Path) -> str:
    if not path.is_file():
        raise CodexHandoffError(f"required file is missing: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise CodexHandoffError(f"invalid JSON: {path.as_posix()}: {exc}") from exc
    _require(isinstance(value, dict), f"JSON root must be an object: {path.as_posix()}")
    return value


def _bool(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    _require(isinstance(value, bool), f"{key} must be a boolean")
    return value


def _full_sha_or_none(value: Any, field: str) -> None:
    _require(
        value is None or (isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None),
        f"{field} must be null or a lowercase full SHA",
    )


def _inspect_publish_lifecycle(root: Path) -> dict[str, Any]:
    lifecycle = _read_json(root / LIFECYCLE_PATH)
    _require(
        set(lifecycle) == {
            "schemaVersion",
            "state",
            "publishReviewerGateReady",
            "priorApprovedPreparationSha",
            "priorAttemptEvidence",
            "attemptHistory",
            "approvedPreparationSha",
            "ownerApproval",
            "githubLiveSettings",
            "authorizationPolicy",
            "closure",
            "observedAttempt",
        },
        "publish lifecycle top-level schema changed",
    )
    _require(lifecycle.get("schemaVersion") == LIFECYCLE_SCHEMA_VERSION, "publish lifecycle schemaVersion changed")
    _require(lifecycle.get("state") == "attempt-recorded", "root handoff lifecycle must be attempt-recorded")
    _require(_bool(lifecycle, "publishReviewerGateReady") is False, "root handoff publish lifecycle gate must be false")
    _require(
        lifecycle.get("priorApprovedPreparationSha") == PRIOR_APPROVED_PREPARATION_SHA,
        "prior exact-SHA approval record changed",
    )
    _require(lifecycle.get("priorAttemptEvidence") == PRIOR_ATTEMPT_EVIDENCE, "prior attempt evidence changed")
    _require(lifecycle.get("attemptHistory") == ATTEMPT_HISTORY, "prior six-attempt history changed")
    _require(
        lifecycle.get("approvedPreparationSha") == APPROVED_PREPARATION_SHA,
        "approved preparation SHA changed",
    )

    owner_approval = lifecycle.get("ownerApproval")
    _require(isinstance(owner_approval, dict), "ownerApproval must be an object")
    _require(
        set(owner_approval) == {"recorded", "recordedAtUtc", "evidence"},
        "ownerApproval schema changed",
    )
    _require(_bool(owner_approval, "recorded") is True, "recorded attempt must retain owner approval")
    _require(owner_approval.get("recordedAtUtc") == "2026-07-27T00:11:00Z", "owner approval timestamp changed")
    _require(
        owner_approval.get("evidence") == "exact-40-character-sha-user-message",
        "owner approval evidence type changed",
    )

    live = lifecycle.get("githubLiveSettings")
    _require(isinstance(live, dict), "githubLiveSettings must be an object")
    _require(
        set(live) == {
            "recheckedAtUtc",
            "actionsAllowlistMatchesPlan",
            "fullLengthActionShaRequired",
            "githubOwnedActionsBlanketAllowed",
            "verifiedCreatorsBlanketAllowed",
            "forkWriteTokensEnabled",
            "forkSecretsEnabled",
            "defaultWorkflowPermissions",
            "actionsCanApprovePullRequests",
            "environmentExists",
            "environmentMainOnly",
            "environmentSecretsCount",
            "environmentVariablesCount",
            "nativeRequiredReviewerConfigured",
            "preventSelfReviewConfigured",
        },
        "githubLiveSettings schema changed",
    )
    _require(
        isinstance(live.get("recheckedAtUtc"), str)
        and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", live["recheckedAtUtc"]) is not None,
        "GitHub live recheck timestamp must be UTC second precision",
    )
    expected_live = {
        "actionsAllowlistMatchesPlan": True,
        "fullLengthActionShaRequired": True,
        "githubOwnedActionsBlanketAllowed": False,
        "verifiedCreatorsBlanketAllowed": False,
        "forkWriteTokensEnabled": False,
        "forkSecretsEnabled": False,
        "defaultWorkflowPermissions": "read-contents-and-packages",
        "actionsCanApprovePullRequests": False,
        "environmentExists": True,
        "environmentMainOnly": True,
        "environmentSecretsCount": 0,
        "environmentVariablesCount": 0,
        "nativeRequiredReviewerConfigured": False,
        "preventSelfReviewConfigured": False,
    }
    for key, expected in expected_live.items():
        if isinstance(expected, bool):
            _require(_bool(live, key) is expected, f"GitHub live setting changed: {key}")
        elif isinstance(expected, int):
            actual = live.get(key)
            _require(
                isinstance(actual, int) and not isinstance(actual, bool) and actual == expected,
                f"GitHub live setting changed: {key}",
            )
        else:
            _require(live.get(key) == expected, f"GitHub live setting changed: {key}")

    authorization = lifecycle.get("authorizationPolicy")
    _require(isinstance(authorization, dict), "authorizationPolicy must be an object")
    _require(
        set(authorization) == {
            "authorizationCommitMustBeDirectChild",
            "authorizationChangedPaths",
            "workflowRunAttemptMustEqual",
            "singleDispatchApiCheckRequired",
            "rerunForbidden",
            "immediateClosureAfterRunAccepted",
        },
        "authorizationPolicy schema changed",
    )
    for key in (
        "authorizationCommitMustBeDirectChild",
        "singleDispatchApiCheckRequired",
        "rerunForbidden",
        "immediateClosureAfterRunAccepted",
    ):
        _require(_bool(authorization, key) is True, f"owner-only authorization rule weakened: {key}")
    _require(
        authorization.get("authorizationChangedPaths") == [LIFECYCLE_PATH],
        "authorization commit path allowlist changed",
    )
    run_attempt = authorization.get("workflowRunAttemptMustEqual")
    _require(
        isinstance(run_attempt, int) and not isinstance(run_attempt, bool) and run_attempt == 1,
        "workflow run_attempt must equal 1",
    )

    closure = lifecycle.get("closure")
    _require(isinstance(closure, dict), "closure must be an object")
    _require(
        set(closure) == {"authorizationSourceSha", "closureCommitSha", "preparedAtUtc"},
        "closure schema changed",
    )
    _require(closure == {
        "authorizationSourceSha": AUTHORIZATION_SHA,
        "closureCommitSha": CLOSURE_SHA,
        "preparedAtUtc": "2026-07-27T00:12:23Z",
    }, "verified attempt closure evidence changed")

    observed = lifecycle.get("observedAttempt")
    _require(isinstance(observed, dict), "observedAttempt must be an object")
    _require(
        set(observed) == {
            "runId",
            "runUrl",
            "runAttempt",
            "status",
            "conclusion",
            "imageDigest",
            "signatureVerified",
        },
        "observedAttempt schema changed",
    )
    _require(observed == {
        "runId": CURRENT_RUN_ID,
        "runUrl": CURRENT_RUN_URL,
        "runAttempt": 1,
        "status": "completed",
        "conclusion": "success",
        "imageDigest": CURRENT_IMAGE_DIGEST,
        "signatureVerified": True,
    }, "verified candidate attempt evidence changed")
    return lifecycle


def _env_inventory(text: str) -> dict[str, str]:
    return {
        line.split("=", 1)[0].strip(): line.split("=", 1)[1].strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }


def _first_from(text: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^\s*FROM\s+([^\s]+)(?:\s+AS\s+\S+)?\s*$", line, re.IGNORECASE)
        if match:
            return match.group(1)
    raise CodexHandoffError("Dockerfile FROM image is missing")


def _verify_forbidden_handoff_paths(root: Path, forbidden_paths: tuple[Path, ...]) -> str:
    """Allow ignored local files, but never tracked files or secret-bearing handoff fixtures."""
    if (root / ".git").exists():
        relative_paths = [path.relative_to(root).as_posix() for path in forbidden_paths]
        completed = subprocess.run(
            (
                "git",
                "-c",
                f"safe.directory={root.resolve().as_posix()}",
                "-C",
                str(root),
                "ls-files",
                "--",
                *relative_paths,
            ),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        _require(completed.returncode == 0, "cannot verify forbidden paths against the Git index")
        tracked = tuple(line.strip() for line in completed.stdout.splitlines() if line.strip())
        _require(not tracked, f"local or secret path is tracked by Git: {', '.join(tracked)}")
        return "git-index"

    for path in forbidden_paths:
        _require(not path.exists(), f"local or secret path must not be present in handoff fixture: {path.relative_to(root)}")
    return "filesystem-absence"


def _inspect_actions_workflow(root: Path) -> dict[str, Any]:
    tool = root / "tools/check_github_actions_ghcr_static_plan.py"
    spec = importlib.util.spec_from_file_location("v322_github_actions_plan_for_handoff", tool)
    _require(spec is not None and spec.loader is not None, "cannot load v322 GitHub Actions checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        result = module.inspect_static_workflow_plan(root)
    except module.StaticWorkflowPlanError as exc:
        raise CodexHandoffError(f"GitHub Actions workflow check failed: {exc}") from exc
    state = result.get("publishLifecycleState")
    expected_results = {
        "preparation-closed": PREPARATION_READY_RESULT,
        "authorization-open": AUTHORIZATION_OPEN_RESULT,
        "authorization-closed-awaiting-evidence": AUTHORIZATION_CLOSED_AWAITING_EVIDENCE_RESULT,
        "attempt-recorded": ATTEMPT_RECORDED_RESULT,
    }
    _require(state in expected_results, "GitHub Actions checker returned an unknown lifecycle state")
    _require(result.get("result") == expected_results[state], "GitHub Actions result/lifecycle state pair differs")
    _require(
        result.get("publishGateReady") is (state == "authorization-open"),
        "GitHub Actions result/lifecycle gate pair differs",
    )
    _full_sha_or_none(result.get("approvedPreparationSha"), "static checker approvedPreparationSha")
    if state == "preparation-closed":
        _require(result.get("approvedPreparationSha") is None, "closed preparation cannot contain approved SHA")
    else:
        _require(result.get("approvedPreparationSha") is not None, "authorization state requires approved SHA")
    return result


def _inspect_production_deployment_plan(root: Path) -> dict[str, Any]:
    tool = root / "tools/check_production_deployment_plan.py"
    spec = importlib.util.spec_from_file_location("v334_production_deployment_plan_for_handoff", tool)
    _require(spec is not None and spec.loader is not None, "cannot load v334 production deployment plan checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        result = module.inspect_plan(root)
    except module.DeploymentPlanError as exc:
        raise CodexHandoffError(f"production deployment plan check failed: {exc}") from exc
    _require(result.get("result") == READY_RESULT, "production deployment plan result differs")
    _require(result.get("nextSafeStage") == NEXT_SAFE_STAGE, "production deployment plan next stage differs")
    _require(result.get("approvalReady") is False, "production deployment approval must remain closed")
    _require(result.get("productionDeploymentExecuted") is False, "production deployment must remain unexecuted")
    return result


def inspect_codex_handoff(root: Path) -> dict[str, Any]:
    policy = _read_json(root / "deploy/backend-image-ghcr-policy.example.json")
    isolated_evidence = _read_json(root / ISOLATED_EVIDENCE_PATH)
    # The source-generic workflow checker validates the current v377 lifecycle.
    # The older deployment-plan fields below remain immutable v351 history.
    lifecycle = _read_json(root / LIFECYCLE_PATH)
    env_example = _read(root / "deploy/production.env.example")
    compose = _read(root / "deploy/docker-compose.production.yml")
    production_dockerfile = _read(root / "backend/Dockerfile.production")
    local_dockerfile = _read(root / "backend/Dockerfile")
    agents = _read(root / "AGENTS.md")
    prompt = _read(root / "NEXT_CHAT_PROMPT.md")
    handoff = _read(root / "NEXT_CHAT_HANDOFF.md")
    current = _read(root / "docs/current/CURRENT_STATUS.md")
    ghcr_doc = _read(root / "docs/current/BACKEND_IMAGE_GHCR_POLICY.md")
    security_doc = _read(root / "docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md")
    docs_index = _read(root / "docs/README.md")
    actions_result = _inspect_actions_workflow(root)
    deployment_plan_result = _inspect_production_deployment_plan(root)

    _require(policy.get("schemaVersion") == TOOL_VERSION, "unexpected v334 schemaVersion")
    _require(_bool(policy, "preparedOnly") is False, "verified image publication must be complete")
    _require(
        policy.get("publishApprovalModel") == "owner-only-source-controlled-two-step",
        "owner-only publish approval model changed",
    )
    _require(
        policy.get("ownerOnlyApprovalPhase")
        == "v355-v351-provider-release-deployed-verified-content-ready",
        "owner-only phase changed",
    )
    _require(policy.get("publishLifecyclePath") == LIFECYCLE_PATH, "publish lifecycle path changed")
    _require(policy.get("publishLifecycleState") == "attempt-recorded", "policy lifecycle must be attempt-recorded")
    _require(
        policy.get("publishLifecycleSupportedStates") == list(LIFECYCLE_SUPPORTED_STATES),
        "policy lifecycle supported-state list changed",
    )
    _require(
        policy.get("priorApprovedPreparationSha")
        == lifecycle.get("priorApprovedPreparationSha"),
        "policy/lifecycle prior exact-SHA approval differs",
    )
    lifecycle_prior_attempt = lifecycle.get("priorAttemptEvidence")
    _require(isinstance(lifecycle_prior_attempt, dict), "lifecycle prior attempt evidence is missing")
    summary_keys = (
        "recordCommitSha",
        "runId",
        "conclusion",
        "registryLoginExecuted",
        "imageBuildExecuted",
        "imagePushExecuted",
    )
    _require(
        policy.get("priorAttemptEvidence")
        == {key: lifecycle_prior_attempt[key] for key in summary_keys},
        "policy/lifecycle prior attempt evidence differs",
    )
    policy_history = policy.get("attemptHistory")
    lifecycle_history = lifecycle.get("attemptHistory")
    _require(isinstance(lifecycle_history, list), "lifecycle attempt history is missing")
    _require(
        policy_history
        == [{key: item[key] for key in summary_keys} for item in lifecycle_history],
        "policy/lifecycle attempt history differs",
    )
    _require(
        policy.get("approvedPreparationSha") == lifecycle.get("approvedPreparationSha"),
        "policy/lifecycle approved preparation differs",
    )
    _full_sha_or_none(policy.get("approvedPreparationSha"), "policy approvedPreparationSha")
    current_policy_attempt = policy.get("currentAttemptEvidence")
    _require(isinstance(current_policy_attempt, dict), "policy current attempt evidence is missing")
    _full_sha_or_none(current_policy_attempt.get("authorizationSha"), "policy authorizationSha")
    _full_sha_or_none(current_policy_attempt.get("closureSha"), "policy closureSha")
    _full_sha_or_none(current_policy_attempt.get("recordCommitSha"), "policy recordCommitSha")
    _require(current_policy_attempt.get("conclusion") in {"success", "failure"}, "policy current attempt conclusion differs")
    closure = lifecycle.get("closure")
    observed = lifecycle.get("observedAttempt")
    _require(isinstance(closure, dict), "lifecycle closure evidence is missing")
    _require(isinstance(observed, dict), "lifecycle observed attempt is missing")
    _require(
        current_policy_attempt.get("authorizationSha")
        == closure.get("authorizationSourceSha"),
        "policy/lifecycle authorization evidence differs",
    )
    _require(
        current_policy_attempt.get("closureSha") == closure.get("closureCommitSha"),
        "policy/lifecycle closure evidence differs",
    )
    for policy_key, lifecycle_key in (
        ("runId", "runId"),
        ("runUrl", "runUrl"),
        ("conclusion", "conclusion"),
        ("imageDigest", "imageDigest"),
        ("signatureVerified", "signatureVerified"),
    ):
        _require(
            current_policy_attempt.get(policy_key) == observed.get(lifecycle_key),
            f"policy/lifecycle {policy_key} evidence differs",
        )
    _require(_bool(policy, "priorExactPreparationShaApproved") is True, "prior exact-SHA approval record is missing")
    _require(lifecycle.get("state") == policy.get("publishLifecycleState"), "policy/lifecycle state differs")
    _require(policy.get("githubRemote") == EXPECTED_REMOTE, "GitHub remote changed")
    _require(policy.get("registryProvider") == "github-container-registry", "registry provider must be GHCR")
    _require(policy.get("registryHost") == "ghcr.io", "registry host must be ghcr.io")
    _require(policy.get("namespace") == EXPECTED_NAMESPACE, "GHCR namespace changed")
    _require(_bool(policy, "namespaceResolved") is True, "namespace must remain resolved")
    _require(policy.get("repositoryName") == "upgrade-rpg-backend", "repository name changed")
    _require(policy.get("repositoryIdentity") == EXPECTED_REPOSITORY, "repository identity changed")
    _require(policy.get("repositoryVisibility") == "private", "repository must remain private")
    _require(policy.get("productionReferenceMode") == "digest-only", "production reference must remain digest-only")
    _require(policy.get("productionReferenceTemplate") == EXPECTED_REFERENCE_TEMPLATE, "production reference template changed")
    _require(policy.get("productionReference") == EXPECTED_REFERENCE, "verified production reference changed")
    _require(
        policy.get("verifiedCandidateReference") == VERIFIED_CANDIDATE_REFERENCE,
        "verified candidate reference changed",
    )
    _require(
        _bool(policy, "verifiedCandidateAppliedToRender") is True,
        "verified candidate Render application is missing",
    )
    _require(policy.get("renderLiveReference") == VERIFIED_CANDIDATE_REFERENCE, "Render live reference changed")
    _require(
        policy.get("renderProviderReleaseApprovedPreparationSha") == PROVIDER_RELEASE_PREPARATION_SHA,
        "Render provider-release approval changed",
    )
    _require(
        policy.get("renderProviderReleaseDeployId") == PROVIDER_RELEASE_DEPLOY_ID,
        "Render provider-release deploy changed",
    )
    _require(
        policy.get("renderProviderReleaseEvidence") == PROVIDER_RELEASE_EVIDENCE_PATH,
        "Render provider-release evidence changed",
    )
    _require(_bool(policy, "productionReferenceStaticPrepared") is True, "production reference static preparation is missing")
    _require(_bool(policy, "productionReferenceAppliedToRuntime") is False, "production reference must not be applied to runtime yet")
    _require(policy.get("targetPlatform") == "linux/amd64", "target platform changed")
    _require(policy.get("productionDockerfile") == "backend/Dockerfile.production", "production Dockerfile path changed")
    _require(policy.get("baseImageReference") == EXPECTED_BASE, "base image reference changed")
    _require(_bool(policy, "baseImageDigestApproved") is True, "base image digest approval missing")
    _require(policy.get("ciCredentialStrategy") == "github-actions-github-token", "CI credential strategy changed")
    _require(
        policy.get("localCredentialStrategy") == "github-cli-oauth-read-packages",
        "local credential strategy must remain the approved GitHub CLI OAuth flow",
    )
    _require(policy.get("isolatedValidationEvidence") == ISOLATED_EVIDENCE_PATH, "isolated validation evidence path changed")
    _require(isolated_evidence == {
        "schemaVersion": "v353.v351-image-isolated-runtime-validation",
        "completedAtUtc": "2026-07-27T00:21:22Z",
        "approvedByUserMessage": True,
        "workflowRunId": CURRENT_RUN_ID,
        "workflowRunAttempt": 1,
        "workflowConclusion": "success",
        "sourceCommitSha": AUTHORIZATION_SHA,
        "preparationCommitSha": APPROVED_PREPARATION_SHA,
        "closureCommitSha": CLOSURE_SHA,
        "recordCommitSha": RECORD_COMMIT_SHA,
        "artifactIds": CURRENT_ARTIFACT_IDS,
        "artifactDigests": CURRENT_ARTIFACT_DIGESTS,
        "imageReference": VERIFIED_CANDIDATE_REFERENCE,
        "imageId": CURRENT_IMAGE_DIGEST,
        "platform": "linux/amd64",
        "supplyChainValidation": {
            "localSbomGenerated": True,
            "localTrivyHighCriticalFindings": 0,
            "registryProvenanceVerified": True,
            "registrySbomFormat": "SPDX-2.3",
            "registrySbomPackages": 87,
            "registryTrivyHighCriticalFindings": 0,
            "cosignSigned": True,
            "cosignVerified": True,
        },
        "registryAuthentication": "github-cli-oauth-read-packages-to-docker-credential-store",
        "pullExecuted": True,
        "containerExecution": {
            "executed": True,
            "user": "65532:65532",
            "effectiveUid": 65532,
            "internalNetwork": True,
            "publishedHostPorts": [],
            "volumes": [],
            "readOnlyRootFilesystem": True,
            "tmpfs": ["/tmp:rw,noexec,nosuid,size=64m"],
            "capabilitiesDropped": ["ALL"],
            "noNewPrivileges": True,
            "pidsLimit": 128,
            "memoryBytes": 268435456,
            "nanoCpus": 1000000000,
        },
        "runtimeValidation": {
            "pythonVersion": "3.11.15",
            "machine": "x86_64",
            "systemCaX509Count": 119,
            "healthPath": "/api/v1/health",
            "healthStatus": 200,
            "healthOk": True,
            "healthType": "system.health",
            "pipPresent": False,
            "rootFilesystemWriteBlocked": True,
            "tmpfsWriteRemovePassed": True,
            "alembicCommandExecuted": False,
            "databaseHealthPathCalled": False,
            "actualDatabaseConnectionAttempted": False,
        },
        "cleanup": {
            "containerRemoved": True,
            "internalNetworkRemoved": True,
            "localImageRemoved": True,
            "volumeCreated": False,
            "existingPostgresContainerHealthyAfterCleanup": True,
        },
        "productionRuntimeApplied": False,
        "renderBackendDeployApproved": False,
        "renderBackendDeployExecuted": False,
        "renderStaticDeployApproved": False,
        "renderStaticDeployExecuted": False,
        "databaseWriteExecuted": False,
        "alembicMutationExecuted": False,
        "adminWriteExecuted": False,
        "contentOrBalanceChanged": False,
        "result": "v351-image-publish-and-isolated-validation-complete",
        "nextSafeStage": "prepare-v351-provider-release-exact-sha-approval",
    }, "isolated image pull/runtime evidence changed")

    for key in (
        "githubActionsWorkflowPresent",
        "githubActionsWorkflowCreationApproved",
        "githubActionsWorkflowExecutionApproved",
        "githubActionsWorkflowExecutionExecuted",
        "githubActionsStaticPlanPresent",
        "githubActionsStaticPlanVerified",
        "actionShasResolved",
        "actionShasApproved",
        "githubConnectorRepositoryAccess",
        "githubConnectorSelectedRepositoryOnly",
        "repositoryActionsSettingsReviewed",
        "repositoryActionsSettingsMutationApproved",
        "repositoryActionsSettingsMutationExecuted",
        "publishEnvironmentReviewed",
        "publishEnvironmentCreationApproved",
        "publishEnvironmentCreated",
        "publishEnvironmentMainOnly",
        "ciDockerLoginApproved",
        "ciImageBuildApproved",
        "ciImagePushApproved",
        "dependencyAndFrontendInputsLocked",
        "actualDockerCommandExecuted",
        "localImageBuildApproved",
        "actualRegistryMutationExecuted",
        "localDockerLoginApproved",
        "localImagePullApproved",
        "containerStartApproved",
        "exactPreparationShaApproved",
        "isolatedImagePullExecuted",
        "isolatedContainerExecutionExecuted",
        "isolatedCleanupExecuted",
        "productionDeploymentPlanReviewed",
        "actualDatabaseRestoreExecuted",
        "actualDatabaseAlembicMutationExecuted",
    ):
        _require(_bool(policy, key) is True, f"completed/approved v334 state must remain true: {key}")
    for key in (
        "longLivedCredentialInRepository",
        "registryCredentialFileInRepository",
        "githubPatCreated",
        "publishEnvironmentRequiredReviewerConfigured",
        "publishEnvironmentPreventSelfReviewConfigured",
        "publishEnvironmentReviewerAvailableForCurrentPlan",
        "sourceControlledPublishGateReady",
        "publishEnvironmentConfigured",
        "localImagePushApproved",
        "productionDeploymentApproved",
        "productionDeploymentExecuted",
        "productionDeploymentApprovalReady",
    ):
        _require(_bool(policy, key) is False, f"blocked/unexecuted v334 state must remain false: {key}")
    for key in (
        "renderPublicPreviewDeploymentApprovalReady",
        "renderPublicPreviewDeploymentApproved",
        "renderPublicPreviewDeploymentExecuted",
    ):
        _require(_bool(policy, key) is True, f"Render public preview deployment must be complete: {key}")
    _require(
        policy.get("renderPublicPreviewDeploymentEvidence")
        == "deploy/review/render-service-initial-deploy-v347.json",
        "Render public preview evidence path changed",
    )
    _require(policy.get("productionDeploymentPlan") == PRODUCTION_DEPLOY_PLAN_PATH, "production deployment plan path changed")
    _require(
        policy.get("nextSafeStage") == PROVIDER_RELEASE_NEXT_STAGE,
        "unexpected image-policy next safe stage",
    )
    _require(
        actions_result.get("publishLifecycleState") == "attempt-recorded",
        "root handoff must use the recorded attempt state",
    )
    _require(
        actions_result.get("result") == ATTEMPT_RECORDED_RESULT,
        "root workflow lifecycle must preserve the verified recorded attempt",
    )

    env = _env_inventory(env_example)
    _require(env.get("BACKEND_IMAGE") == EXPECTED_REFERENCE, "production env repository/reference differs")
    _require("<github-account-or-organization>" not in env_example, "old namespace placeholder remains")
    _require("image: ${BACKEND_IMAGE:?" in compose, "production Compose must require BACKEND_IMAGE")
    _require(re.search(r"(?m)^\s+build:\s*$", compose) is None, "production Compose must not build")
    _require(re.search(r"(?m)^\s+ports:\s*$", compose) is None, "production backend host ports must remain absent")
    _require(re.search(r"(?m)^\s+replicas:\s*1\s*$", compose) is not None, "backend replicas must remain 1")

    _require(_first_from(production_dockerfile) == EXPECTED_BASE, "production Dockerfile base digest differs")
    _require(_first_from(local_dockerfile) == "python:3.11-slim", "local Dockerfile must remain preserved")
    _require("USER 65532:65532" in production_dockerfile, "production Dockerfile must remain non-root")
    _require("runtime-musllinux-amd64-py311.lock" in production_dockerfile, "production musllinux lock is missing")
    _require("/usr/local/lib/python3.11/site-packages/setuptools*" in production_dockerfile, "runtime build tools are not removed")
    production_cmd = next((line.lower() for line in production_dockerfile.splitlines() if line.strip().startswith("CMD ")), "")
    _require("--workers" not in production_cmd, "production Uvicorn worker count must remain 1")
    _require("alembic" not in production_cmd, "container startup must not run Alembic")

    current_markers = (
        "v384.vue-game-domain-foundation",
        "vue-game-domain-foundation",
        "migrate-vue-game-shell-town-hud",
    )
    for path, text in (
        ("AGENTS.md", agents),
        ("NEXT_CHAT_HANDOFF.md", handoff),
        ("docs/current/CURRENT_STATUS.md", current),
    ):
        for marker in current_markers:
            _require(marker in text, f"{path} is missing current marker: {marker}")
    for marker in ("AGENTS.md", "NEXT_CHAT_HANDOFF.md", "docs/current/CURRENT_STATUS.md"):
        _require(marker in prompt, f"prompt is missing reading-order marker: {marker}")
    _require("실행 중인" in agents and "서버를 재사용" in agents, "AGENTS.md is missing persistent server permission")
    _require("필요한 extension" in agents, "AGENTS.md is missing recurring install/permission request rule")
    _require(EXPECTED_REPOSITORY in ghcr_doc, "GHCR policy doc is missing repository")
    _require("GITHUB_TOKEN" in ghcr_doc, "GHCR policy doc is missing credential strategy")
    _require("required reviewer" in security_doc, "security checklist is missing reviewer gate")
    _require("실제 secret 값은 적지 않습니다" in security_doc, "security checklist could expose secrets")
    _require(
        "Upgrade RPG Docs Hub" in docs_index
        and "Reference Index" in docs_index
        and "Generated Index" in docs_index
        and "Archive Index" in docs_index,
        "docs index is not current",
    )
    workflow_files = {
        path.relative_to(root).as_posix()
        for path in (root / ".github/workflows").rglob("*")
        if path.is_file()
    }
    _require(workflow_files == {WORKFLOW_PATH}, "unexpected workflow file set")
    secrets_dir = root / "deploy/secrets"
    allowed_secret_files = {"README.md"}
    if secrets_dir.exists():
        actual = {path.name for path in secrets_dir.iterdir() if path.is_file()}
        _require(actual <= allowed_secret_files, "actual secret file exists under deploy/secrets")

    forbidden_paths = (
        root / "backend/.env",
        root / "deploy/production.env",
        root / "local-backups",
        root / "local-review-artifacts",
    )
    package_safety_mode = _verify_forbidden_handoff_paths(root, forbidden_paths)

    for path in (
        root / "docs/current/BACKEND_IMAGE_SOURCE_DIGEST_POLICY.md",
        root / "docs/current/BACKEND_IMAGE_REGISTRY_BASE_SELECTION.md",
        root / "deploy/backend-image-source-digest-policy.example.json",
        root / "deploy/backend-image-registry-base-selection.example.json",
        root / "tools/check_backend_image_source_digest_policy.py",
        root / "tools/check_backend_image_registry_base_selection.py",
    ):
        _require(not path.exists(), f"superseded active file remains: {path.relative_to(root)}")

    revision = root / "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py"
    _require(revision.is_file(), "reviewed Alembic revision is missing")
    actual_sha = hashlib.sha256(revision.read_bytes()).hexdigest()
    _require(actual_sha == REVISION_SHA256, f"reviewed revision SHA-256 differs: {actual_sha}")

    return {
        "toolVersion": TOOL_VERSION,
        "githubRemote": EXPECTED_REMOTE,
        "namespace": EXPECTED_NAMESPACE,
        "repository": EXPECTED_REPOSITORY,
        "repositoryVisibility": "private",
        "targetPlatform": "linux/amd64",
        "baseImageDigestApproved": True,
        "ciCredentialStrategy": "github-actions-github-token",
        "localCredentialStrategy": "github-cli-oauth-read-packages",
        "workflowCreationApproved": True,
        "workflowExecutionApproved": True,
        "workflowExecutionExecuted": True,
        "ciRegistryMutationApproved": True,
        "runtimeMutationExecuted": False,
        "githubActionsStaticPlanVerified": True,
        "workflowFilePresent": actions_result["workflowFilePresent"],
        "workflowSourceSha256": actions_result["workflowSourceSha256"],
        "workflowSemanticSha256": actions_result["workflowSemanticSha256"],
        "actionShasApproved": actions_result["actionShasApproved"],
        "actionsSettingsConfigured": actions_result["actionsSettingsConfigured"],
        "publishEnvironmentExists": actions_result["publishEnvironmentExists"],
        "publishEnvironmentConfigured": actions_result["publishEnvironmentConfigured"],
        "publishGateReady": actions_result["publishGateReady"],
        "publishLifecycleState": actions_result["publishLifecycleState"],
        "publishLifecycleSupportedStates": list(LIFECYCLE_SUPPORTED_STATES),
        "workflowExecutionHistoryCount": len(lifecycle["attemptHistory"]) + 1,
        "priorApprovedPreparationSha": lifecycle["priorApprovedPreparationSha"],
        "approvedPreparationSha": lifecycle["approvedPreparationSha"],
        "authorizationSha": closure["authorizationSourceSha"],
        "closureSha": closure["closureCommitSha"],
        "recordCommitSha": current_policy_attempt["recordCommitSha"],
        "currentRunId": current_policy_attempt["runId"],
        "currentArtifactIds": current_policy_attempt["artifactIds"],
        "currentImageDigest": current_policy_attempt["imageDigest"],
        "productionReference": EXPECTED_REFERENCE,
        "verifiedCandidateReference": VERIFIED_CANDIDATE_REFERENCE,
        "verifiedCandidateAppliedToRender": True,
        "productionReferenceStaticPrepared": True,
        "productionReferenceAppliedToRuntime": False,
        "isolatedImagePullExecuted": True,
        "isolatedContainerExecutionExecuted": True,
        "isolatedCleanupExecuted": True,
        "productionDeploymentPlanReviewed": deployment_plan_result["planReviewCompleted"],
        "productionDeploymentApprovalReady": deployment_plan_result["approvalReady"],
        "productionDeploymentApproved": False,
        "productionDeploymentExecuted": False,
        "ownerApprovalRecorded": lifecycle["ownerApproval"]["recorded"],
        "workflowRunAttemptMustEqual": lifecycle["authorizationPolicy"]["workflowRunAttemptMustEqual"],
        "singleDispatchApiCheckRequired": lifecycle["authorizationPolicy"]["singleDispatchApiCheckRequired"],
        "rerunForbidden": lifecycle["authorizationPolicy"]["rerunForbidden"],
        "immediateClosureAfterRunAccepted": lifecycle["authorizationPolicy"]["immediateClosureAfterRunAccepted"],
        "dockerBuildContextEnvExcluded": actions_result["dockerBuildContextEnvExcluded"],
        "reproducibleBuildReady": actions_result["reproducibleBuildReady"],
        "packageSafetyMode": package_safety_mode,
        "result": READY_RESULT,
        "nextSafeStage": NEXT_SAFE_STAGE,
    }


def render(result: dict[str, Any]) -> str:
    return "\n".join((
        "Codex/GHCR v334 production deployment plan verification (read-only)",
        "The deploy plan is reviewed, required production inputs are unresolved, and execution remains blocked.",
        "",
        f"- GitHub remote: {result['githubRemote']}",
        f"- namespace/repository: {result['namespace']} / {result['repository']}",
        f"- visibility/target: {result['repositoryVisibility']} / {result['targetPlatform']}",
        f"- base image digest approved: {result['baseImageDigestApproved']}",
        f"- credential strategy: {result['ciCredentialStrategy']} / local={result['localCredentialStrategy']}",
        f"- forbidden path verification: {result['packageSafetyMode']}",
        "- workflow file/creation approved: yes/yes",
        f"- reviewed workflow source SHA-256: {result['workflowSourceSha256']}",
        f"- reviewed workflow semantic SHA-256: {result['workflowSemanticSha256']}",
        f"- workflow execution history: {result['workflowExecutionHistoryCount']} source-controlled attempts",
        "- action allowlist/full SHA enforcement: configured/configured (live rechecked 2026-07-27)",
        "- CI login/build/push approved/executed: yes/yes/yes / yes/yes/yes",
        "- publish environment/main-only: present/configured (live rechecked 2026-07-27)",
        "- native required reviewer/current private plan: missing/unavailable",
        "- publish approval model: owner-only-source-controlled-two-step (attempt recorded; gate closed)",
        f"- publish lifecycle: {result['publishLifecycleState']} / gate={result['publishGateReady']}",
        f"- lifecycle states: {', '.join(result['publishLifecycleSupportedStates'])}",
        f"- prior approved preparation SHA: {result['priorApprovedPreparationSha']}",
        f"- approved preparation SHA: {result['approvedPreparationSha']}",
        f"- authorization/closure/record SHA: {result['authorizationSha']} / {result['closureSha']} / {result['recordCommitSha']}",
        f"- current run/artifact IDs: {result['currentRunId']} / {result['currentArtifactIds']}",
        f"- latest verified image digest: {result['currentImageDigest']}",
        f"- current production reference: {EXPECTED_REFERENCE}",
        f"- verified candidate reference: {result['verifiedCandidateReference']}",
        "- generic production reference static/runtime applied: yes/no",
        "- Render public preview verified candidate applied: yes",
        "- isolated pull/container/cleanup executed: yes/yes/yes",
        "- production deploy plan reviewed / approval ready: yes/no",
        "- latest result: provenance/SBOM, exact-digest Trivy 0 findings, Cosign sign/verify passed",
        "- single-run policy: run_attempt=1 / single dispatch / rerun forbidden / immediate closure",
        "- PUBLISH_REVIEWER_GATE_READY: lifecycle-controlled false (fail-closed before GHCR login)",
        "- root Docker context env files/re-includes: excluded/forbidden",
        "- dependency/frontend inputs: exact versions + SHA-256 locks ready",
        "- isolated container cleaned / registry push / DB restore / Alembic: yes/yes/yes/yes",
        f"- result: {result['result']}",
        f"- next safe stage: {result['nextSafeStage']}",
    ))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = inspect_codex_handoff(root)
    except CodexHandoffError as exc:
        payload = {"toolVersion": TOOL_VERSION, "result": BLOCKED_RESULT, "reason": str(exc)}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("Codex/GHCR handoff verification")
            print(f"- result: {BLOCKED_RESULT}")
            print(f"- reason: {exc}")
        return 1 if args.strict else 0
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

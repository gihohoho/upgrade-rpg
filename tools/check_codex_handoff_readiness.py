#!/usr/bin/env python3
"""Validate the v330 SLSA v1 provenance-path preparation handoff."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
from typing import Any

TOOL_VERSION = "v330.slsa-v1-provenance-path-preparation"
READY_RESULT = "github-actions-ghcr-owner-only-provenance-path-preparation-ready-publish-gated"
PREPARATION_READY_RESULT = READY_RESULT
AUTHORIZATION_OPEN_RESULT = "github-actions-ghcr-owner-only-authorization-open"
AUTHORIZATION_CLOSED_AWAITING_EVIDENCE_RESULT = (
    "github-actions-ghcr-owner-only-authorization-closed-awaiting-evidence"
)
ATTEMPT_RECORDED_RESULT = "github-actions-ghcr-owner-only-attempt-recorded-publish-gated"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "review-and-approve-exact-provenance-path-preparation-sha"
EXPECTED_REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
EXPECTED_NAMESPACE = "gihohoho"
EXPECTED_REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
EXPECTED_REFERENCE = EXPECTED_REPOSITORY + "@sha256:<approved-64-hex-digest>"
EXPECTED_BASE = "python:3.11.15-alpine3.23@sha256:ac0151f0eec4b7ba78bc47d337f328c6db706e7255b35b2327c2749f058c82fe"
WORKFLOW_PATH = ".github/workflows/publish-backend-ghcr.yml"
LIFECYCLE_PATH = "deploy/github-actions-ghcr-publish-lifecycle.json"
LIFECYCLE_SCHEMA_VERSION = "v326.owner-only-publish-lifecycle-with-attempt-history"
PRIOR_APPROVED_PREPARATION_SHA = "350bbd085f1cf636810d75ddcbb5321e0791256c"
SECOND_APPROVED_PREPARATION_SHA = "2f77ebf0f60a39c936509df26f903995f0c62967"
PRIOR_ATTEMPT_EVIDENCE = {
    "preparationSha": PRIOR_APPROVED_PREPARATION_SHA,
    "authorizationSha": "32e5102877851ace06e1c0ed3bcb48310b8d65b6",
    "closureSha": "362f5f1901d234b5b86f2a7cefdabd28ac61f896",
    "recordCommitSha": "1f12ea59eb54385337557e9754f86731ec53d253",
    "runId": 29716038891,
    "runUrl": "https://github.com/gihohoho/upgrade-rpg/actions/runs/29716038891",
    "conclusion": "failure",
    "registryLoginExecuted": False,
    "imageBuildExecuted": False,
    "imagePushExecuted": False,
}
ATTEMPT_HISTORY = [
    {
        **PRIOR_ATTEMPT_EVIDENCE,
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
]
APPROVED_PREPARATION_SHA = "13b15409929d77b4e6209481596e4f4550a22ba5"
AUTHORIZATION_SHA = "4fb31f51ca0de15d77a73390b5a07e394ffce12a"
CLOSURE_SHA = "ddf475c1a2449feb50ef2af1a536e4150cf0ad59"
RECORD_COMMIT_SHA = "f945214f2387b6aa191655d3740e18ef862bd6fb"
CURRENT_RUN_ID = 29886540317
CURRENT_RUN_URL = f"https://github.com/gihohoho/upgrade-rpg/actions/runs/{CURRENT_RUN_ID}"
CURRENT_ARTIFACT_IDS = [8516735247, 8516749365]
CURRENT_IMAGE_DIGEST = "sha256:6e4aefad0cdf1767670b7f736477dd9e00f17bf49a03fa471828df6667c41149"
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
    _require(lifecycle.get("state") == "preparation-closed", "root handoff lifecycle must be preparation-closed")
    _require(_bool(lifecycle, "publishReviewerGateReady") is False, "root handoff publish lifecycle gate must be false")
    _require(
        lifecycle.get("priorApprovedPreparationSha") == PRIOR_APPROVED_PREPARATION_SHA,
        "prior exact-SHA approval record changed",
    )
    _require(lifecycle.get("priorAttemptEvidence") == PRIOR_ATTEMPT_EVIDENCE, "prior attempt evidence changed")
    _require(lifecycle.get("attemptHistory") == ATTEMPT_HISTORY, "prior four-attempt history changed")
    _require(lifecycle.get("approvedPreparationSha") is None, "preparation must await exact-SHA approval")

    owner_approval = lifecycle.get("ownerApproval")
    _require(isinstance(owner_approval, dict), "ownerApproval must be an object")
    _require(
        set(owner_approval) == {"recorded", "recordedAtUtc", "evidence"},
        "ownerApproval schema changed",
    )
    _require(_bool(owner_approval, "recorded") is False, "preparation must not self-record owner approval")
    _require(owner_approval.get("recordedAtUtc") is None, "preparation approval timestamp must be empty")
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
        "authorizationSourceSha": None,
        "closureCommitSha": None,
        "preparedAtUtc": None,
    }, "preparation closure evidence must be empty")

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
        "runId": None,
        "runUrl": None,
        "runAttempt": None,
        "status": "not-dispatched",
        "conclusion": None,
        "imageDigest": None,
        "signatureVerified": False,
    }, "preparation attempt evidence must be empty")
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


def inspect_codex_handoff(root: Path) -> dict[str, Any]:
    policy = _read_json(root / "deploy/backend-image-ghcr-policy.example.json")
    lifecycle = _inspect_publish_lifecycle(root)
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
    handoff_prompt = _read(root / "docs/handoff/NEXT_CHAT_PROMPT.md")
    handoff_state = _read(root / "docs/handoff/NEXT_CHAT_HANDOFF.md")
    actions_result = _inspect_actions_workflow(root)

    _require(policy.get("schemaVersion") == TOOL_VERSION, "unexpected v330 schemaVersion")
    _require(_bool(policy, "preparedOnly") is True, "focused fix must remain preparation-only")
    _require(
        policy.get("publishApprovalModel") == "owner-only-source-controlled-two-step",
        "owner-only publish approval model changed",
    )
    _require(policy.get("ownerOnlyApprovalPhase") == "preparation-awaiting-exact-sha-approval", "owner-only phase changed")
    _require(policy.get("publishLifecyclePath") == LIFECYCLE_PATH, "publish lifecycle path changed")
    _require(policy.get("publishLifecycleState") == "preparation-closed", "policy lifecycle must be preparation-closed")
    _require(
        policy.get("publishLifecycleSupportedStates") == list(LIFECYCLE_SUPPORTED_STATES),
        "policy lifecycle supported-state list changed",
    )
    _require(
        policy.get("priorApprovedPreparationSha") == PRIOR_APPROVED_PREPARATION_SHA,
        "policy prior exact-SHA approval record changed",
    )
    _require(policy.get("priorAttemptEvidence") == {
        "recordCommitSha": PRIOR_ATTEMPT_EVIDENCE["recordCommitSha"],
        "runId": PRIOR_ATTEMPT_EVIDENCE["runId"],
        "conclusion": "failure",
        "registryLoginExecuted": False,
        "imageBuildExecuted": False,
        "imagePushExecuted": False,
    }, "policy prior attempt evidence changed")
    _require(policy.get("attemptHistory") == [
        {key: item[key] for key in ("recordCommitSha", "runId", "conclusion", "registryLoginExecuted", "imageBuildExecuted", "imagePushExecuted")}
        for item in ATTEMPT_HISTORY
    ], "policy prior four-attempt history changed")
    _require(policy.get("approvedPreparationSha") is None, "policy must await exact preparation SHA")
    _require(policy.get("currentAttemptEvidence") == {
        "authorizationSha": AUTHORIZATION_SHA,
        "closureSha": CLOSURE_SHA,
        "recordCommitSha": RECORD_COMMIT_SHA,
        "runId": CURRENT_RUN_ID,
        "runUrl": CURRENT_RUN_URL,
        "conclusion": "failure",
        "registryLoginExecuted": True,
        "imageBuildExecuted": True,
        "imagePushExecuted": True,
        "artifactCount": 2,
        "artifactIds": CURRENT_ARTIFACT_IDS,
        "imageDigest": CURRENT_IMAGE_DIGEST,
        "signatureVerified": False,
    }, "current vulnerability-gated attempt evidence changed")
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
    _require(policy.get("productionReferenceTemplate") == EXPECTED_REFERENCE, "production reference changed")
    _require(policy.get("targetPlatform") == "linux/amd64", "target platform changed")
    _require(policy.get("productionDockerfile") == "backend/Dockerfile.production", "production Dockerfile path changed")
    _require(policy.get("baseImageReference") == EXPECTED_BASE, "base image reference changed")
    _require(_bool(policy, "baseImageDigestApproved") is True, "base image digest approval missing")
    _require(policy.get("ciCredentialStrategy") == "github-actions-github-token", "CI credential strategy changed")
    _require(policy.get("localCredentialStrategy") == "deferred", "local credential strategy must remain deferred")

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
    ):
        _require(_bool(policy, key) is True, f"completed/approved v330 state must remain true: {key}")
    for key in (
        "longLivedCredentialInRepository",
        "registryCredentialFileInRepository",
        "githubPatCreated",
        "publishEnvironmentRequiredReviewerConfigured",
        "publishEnvironmentPreventSelfReviewConfigured",
        "publishEnvironmentReviewerAvailableForCurrentPlan",
        "sourceControlledPublishGateReady",
        "publishEnvironmentConfigured",
        "localDockerLoginApproved",
        "localImagePullApproved",
        "exactPreparationShaApproved",
        "localImagePushApproved",
        "containerStartApproved",
        "actualDatabaseAlembicMutationExecuted",
    ):
        _require(_bool(policy, key) is False, f"blocked/unexecuted v330 state must remain false: {key}")
    _require(policy.get("nextSafeStage") == NEXT_SAFE_STAGE, "unexpected next safe stage")
    _require(
        actions_result.get("publishLifecycleState") == "preparation-closed",
        "root handoff must use the closed preparation state",
    )
    _require(actions_result.get("result") == READY_RESULT, "root handoff must use the preparation-ready result")

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

    common_markers = (TOOL_VERSION, EXPECTED_REMOTE, EXPECTED_REPOSITORY)
    for path, text in (
        ("AGENTS.md", agents),
        ("NEXT_CHAT_PROMPT.md", prompt),
        ("NEXT_CHAT_HANDOFF.md", handoff),
        ("docs/current/CURRENT_STATUS.md", current),
    ):
        for marker in common_markers:
            _require(marker in text, f"{path} is missing marker: {marker}")
        _require("GITHUB_TOKEN" in text or "github-actions-github-token" in text, f"{path} is missing CI credential strategy")
        _require(LIFECYCLE_PATH in text, f"{path} is missing source-controlled publish lifecycle path")
        _require("source-controlled lifecycle gate" in text, f"{path} is missing lifecycle gate marker")
    _require("check_github_actions_ghcr_static_plan.py --strict" in agents, "AGENTS.md is missing first checker")
    _require("실행 중인 개발 서버를 재사용" in agents, "AGENTS.md is missing persistent server permission")
    _require(READY_RESULT in prompt, "prompt is missing expected result")
    _require(NEXT_SAFE_STAGE in prompt, "prompt is missing next safe stage")
    _require("필요한 extension" in prompt, "prompt is missing recurring install/permission request rule")
    _require(EXPECTED_REPOSITORY in ghcr_doc, "GHCR policy doc is missing repository")
    _require("GITHUB_TOKEN" in ghcr_doc, "GHCR policy doc is missing credential strategy")
    _require("required reviewer" in security_doc, "security checklist is missing reviewer gate")
    _require("실제 secret 값은 적지 않습니다" in security_doc, "security checklist could expose secrets")
    _require("Docs Index" in docs_index and "archive/production-deployment/" in docs_index, "docs index is not current")
    _require(prompt == handoff_prompt, "root and docs/handoff prompts differ")
    _require(handoff == handoff_state, "root and docs/handoff state differ")
    lifecycle_markers = (
        "source-controlled lifecycle gate",
        "run_attempt=1",
        "single dispatch",
        "immediate closure",
        "closureCommitSha",
        "attempt-recorded",
        "review-recorded-workflow-attempt-evidence",
    )
    for path, text in (
        ("NEXT_CHAT_PROMPT.md", prompt),
        ("NEXT_CHAT_HANDOFF.md", handoff),
        ("docs/handoff/NEXT_CHAT_PROMPT.md", handoff_prompt),
        ("docs/handoff/NEXT_CHAT_HANDOFF.md", handoff_state),
    ):
        for marker in lifecycle_markers:
            _require(marker in text, f"{path} is missing lifecycle marker: {marker}")

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
        "localCredentialStrategy": "deferred",
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
        "priorApprovedPreparationSha": lifecycle["priorApprovedPreparationSha"],
        "approvedPreparationSha": lifecycle["approvedPreparationSha"],
        "authorizationSha": AUTHORIZATION_SHA,
        "closureSha": CLOSURE_SHA,
        "recordCommitSha": RECORD_COMMIT_SHA,
        "currentRunId": CURRENT_RUN_ID,
        "currentArtifactIds": CURRENT_ARTIFACT_IDS,
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
        "Codex/GHCR v330 SLSA v1 provenance-path preparation handoff verification (read-only)",
        "The focused fix is prepared with the source-controlled publish gate closed.",
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
        "- workflow execution approved/executed: yes/yes (four runs recorded; latest failed post-push)",
        "- action allowlist/full SHA enforcement: configured/configured (live rechecked 2026-07-22)",
        "- CI login/build/push approved/executed: yes/yes/yes / yes/yes/yes",
        "- publish environment/main-only: present/configured (live rechecked 2026-07-22)",
        "- native required reviewer/current private plan: missing/unavailable",
        "- publish approval model: owner-only-source-controlled-two-step (preparation closed; gate closed)",
        f"- publish lifecycle: {result['publishLifecycleState']} / gate={result['publishGateReady']}",
        f"- lifecycle states: {', '.join(result['publishLifecycleSupportedStates'])}",
        f"- prior approved preparation SHA: {result['priorApprovedPreparationSha']}",
        f"- approved focused-fix preparation SHA: {result['approvedPreparationSha']}",
        f"- authorization/closure/record SHA: {result['authorizationSha']} / {result['closureSha']} / {result['recordCommitSha']}",
        f"- latest run/artifact IDs: {result['currentRunId']} / {result['currentArtifactIds']}",
        f"- pushed image digest: {CURRENT_IMAGE_DIGEST} (unsigned; not a verified candidate)",
        "- focused fix: validate SLSA v1 buildDefinition.buildType fail-closed",
        "- single-run policy: run_attempt=1 / single dispatch / rerun forbidden / immediate closure",
        "- PUBLISH_REVIEWER_GATE_READY: lifecycle-controlled false (fail-closed before GHCR login)",
        "- root Docker context env files/re-includes: excluded/forbidden",
        "- dependency/frontend inputs: exact versions + SHA-256 locks ready",
        "- container/registry/DB/Alembic mutation executed: no/yes/no/no",
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

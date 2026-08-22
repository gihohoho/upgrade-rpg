#!/usr/bin/env python3
"""Fail-closed, provider-free preparation for the v377 email release.

The default command is read-only. Lifecycle write modes edit only the tracked
publish lifecycle after a clean pushed-main exact-SHA check. Render modes read
strict key-only local inventories and write only Git-ignored, sanitized JSON.
No mode calls GitHub, GHCR, Render, Brevo, or a public endpoint.
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "deploy/v377-email-release-guard.example.json"
WORKFLOW_PATH = ROOT / ".github/workflows/publish-backend-ghcr.yml"
LIFECYCLE_PATH = ROOT / "deploy/github-actions-ghcr-publish-lifecycle.json"
IMAGE_POLICY_PATH = ROOT / "deploy/backend-image-ghcr-policy.example.json"
V351_EVIDENCE_PATH = ROOT / "deploy/review/render-v351-provider-release-v355.json"
RENDER_ENV_EXAMPLE_PATH = ROOT / "deploy/render.production.env.example"
LOCAL_REPORT_DIR = ROOT / "local-review-artifacts/release"
RENDER_PREPARATION_PATH = LOCAL_REPORT_DIR / "v377-render-preparation.json"
RENDER_ATTEMPT_PATH = LOCAL_REPORT_DIR / "v377-render-attempt.json"

TOOL_VERSION = "v377.email-release-deployment-guard.v1"
RESULT = "v377-email-release-source-guard-prepared"
IMAGE_REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
SERVICE_NAME = "upgrade-rpg-api"
OLD_IMAGE_DIGEST = "sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac"
OLD_IMAGE_REFERENCE = f"{IMAGE_REPOSITORY}@{OLD_IMAGE_DIGEST}"
OLD_SERVICE_ID_SHA256 = "bb2c7aeab76e28e363ce85be0964245110c51f212879a55bbb19cc8b46bb5d46"
OLD_DEPLOY_ID_SHA256 = "7e80fbc0efe0b13dd8b8daefee0bda83ab55141722c50bd8ae9b5cf513a3e9bc"
OLD_EVIDENCE_PATH_SHA256 = "0bf97470d9b51a21c2f958f0b51235326f1e4338c9da96cd09de96d3b953737f"
LIFECYCLE_RELATIVE = "deploy/github-actions-ghcr-publish-lifecycle.json"
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
SERVICE_ID_PATTERN = re.compile(r"^srv-[a-z0-9]+$")
DEPLOY_ID_PATTERN = re.compile(r"^dep-[a-z0-9]+$")

REQUIRED_ENV_KEYS = (
    "ENVIRONMENT",
    "DEBUG",
    "JWT_SECRET_KEY",
    "CORS_ORIGINS",
    "EMAIL_PROVIDER",
    "BREVO_API_KEY",
    "BREVO_FROM_EMAIL",
    "BREVO_FROM_NAME",
    "EMAIL_TOKEN_SECRET",
    "AUTH_ABUSE_SECRET",
    "PUBLIC_FRONTEND_ORIGIN",
    "EMAIL_DELIVERY_TIMEOUT_SECONDS",
    "EMAIL_OUTBOX_WORKER_ENABLED",
    "EMAIL_OUTBOX_POLL_SECONDS",
    "EMAIL_OUTBOX_MAINTENANCE_INTERVAL_SECONDS",
    "EMAIL_OUTBOX_PREPARING_TIMEOUT_SECONDS",
    "EMAIL_OUTBOX_SENDING_TIMEOUT_SECONDS",
    "EMAIL_OUTBOX_RETENTION_DAYS",
    "REQUEST_BODY_LIMIT_BYTES",
    "AUTH_REQUEST_BODY_LIMIT_BYTES",
    "AUTH_TRUSTED_PROXY_MODE",
    "AUTH_DISCOVERY_RESPONSE_FLOOR_MS",
    "AUTH_DISCOVERY_RESPONSE_JITTER_MS",
    "AUTH_RATE_LIMIT_RETENTION_DAYS",
    "UNVERIFIED_ACCOUNT_TTL_HOURS",
)

PREPARE_PUBLISH_ACTION = "create-fresh-v377-publish-preparation"
AUTHORIZE_PUBLISH_ACTION = "open-owner-approved-v377-publish-once"
CLOSE_PUBLISH_ACTION = "close-accepted-v377-publish-immediately"
RECORD_PUBLISH_ACTION = "record-v377-publish-attempt-once-no-rerun"
PREPARE_RENDER_ACTION = "prepare-existing-render-service-exact-v377-image"
RECORD_RENDER_ACTION = "record-existing-render-service-deploy-once"
AUTHORIZATION_POLICY = {
    "authorizationCommitMustBeDirectChild": True,
    "authorizationChangedPaths": [LIFECYCLE_RELATIVE],
    "workflowRunAttemptMustEqual": 1,
    "singleDispatchApiCheckRequired": True,
    "rerunForbidden": True,
    "immediateClosureAfterRunAccepted": True,
}


class V377ReleaseGuardError(RuntimeError):
    """A failure safe to display without credential or endpoint values."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise V377ReleaseGuardError(message)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def full_sha(value: Any, label: str) -> str:
    require(isinstance(value, str) and SHA_PATTERN.fullmatch(value) is not None, f"{label} must be an exact SHA")
    return value


def exact_digest(value: Any, label: str) -> str:
    require(isinstance(value, str) and DIGEST_PATTERN.fullmatch(value) is not None, f"{label} must be an exact digest")
    return value


def utc_timestamp(value: Any, label: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} must be UTC")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise V377ReleaseGuardError(f"{label} must be UTC") from None
    require(parsed.utcoffset() == timedelta(0), f"{label} must be UTC")
    return parsed


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), "required JSON file is missing")
    try:
        size = path.stat().st_size
        require(0 < size <= 1_000_000, "JSON file size is outside the guard boundary")
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise V377ReleaseGuardError("required JSON file is invalid") from None
    require(isinstance(payload, dict), "JSON root must be an object")
    return payload


def _json_clone(payload: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(payload)


def _git(*args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        raise V377ReleaseGuardError("Git preflight could not run") from None
    require(completed.returncode == 0, "Git preflight failed")
    return completed.stdout.strip()


def require_clean_pushed_main(expected_head: str) -> None:
    full_sha(expected_head, "confirmed source")
    require(_git("branch", "--show-current") == "main", "release preparation requires main")
    require(_git("status", "--porcelain") == "", "release preparation requires a clean worktree")
    require(_git("rev-parse", "HEAD") == expected_head, "confirmed source differs from HEAD")
    require(_git("rev-parse", "--verify", "origin/main") == expected_head, "confirmed source differs from origin/main")


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    temporary = path.with_name(f".{path.name}.v377.{os.getpid()}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temporary, path)
    except OSError:
        raise V377ReleaseGuardError("guard output could not be written atomically") from None
    finally:
        temporary.unlink(missing_ok=True)


def _tracked_env_keys(path: Path) -> set[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        raise V377ReleaseGuardError("Render environment example could not be read") from None
    keys: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        require(re.fullmatch(r"[A-Z][A-Z0-9_]*", key) is not None, "Render environment example contains an invalid key")
        require(key not in keys, "Render environment example contains a duplicate key")
        keys.add(key)
    return keys


def _require_authorization_policy(lifecycle: dict[str, Any]) -> None:
    require(
        lifecycle.get("authorizationPolicy") == AUTHORIZATION_POLICY,
        "publish authorization policy differs",
    )


def _require_key_names_only(keys: Any, label: str) -> list[str]:
    require(
        isinstance(keys, list) and all(isinstance(item, str) for item in keys),
        f"{label} must contain key names only",
    )
    require(len(keys) == len(set(keys)), f"{label} contains duplicate keys")
    require(
        all(re.fullmatch(r"[A-Z][A-Z0-9_]*", item) is not None for item in keys),
        f"{label} contains a non-key value",
    )
    return keys


def validate_static_guard(plan: dict[str, Any], *, root: Path = ROOT) -> dict[str, Any]:
    require(plan.get("schemaVersion") == TOOL_VERSION, "v377 release guard version differs")
    require(plan.get("result") == RESULT, "v377 release guard result differs")
    require(plan.get("productionResourcesMutated") is False, "source guard must not claim provider mutation")
    require(plan.get("networkAccessExecuted") is False, "source guard must not claim network access")

    source = plan.get("source") or {}
    require(source == {
        "branch": "main",
        "cleanPushedExactShaRequired": True,
        "sourceCommitSha": None,
    }, "source preparation boundary differs")

    actions = plan.get("githubActions") or {}
    require(actions.get("workflow") == ".github/workflows/publish-backend-ghcr.yml", "publish workflow path differs")
    require(actions.get("imageRepository") == IMAGE_REPOSITORY, "image repository differs")
    require(actions.get("targetPlatform") == "linux/amd64", "image platform differs")
    require(actions.get("lifecyclePath") == LIFECYCLE_RELATIVE, "publish lifecycle path differs")
    require(actions.get("states") == [
        "preparation-closed",
        "authorization-open",
        "authorization-closed-awaiting-evidence",
        "attempt-recorded",
    ], "publish lifecycle states differ")
    require(actions.get("authorizationChangedPaths") == [LIFECYCLE_RELATIVE], "authorization path boundary differs")
    for key in (
        "freshPreparationRequired",
        "singleDispatchRequired",
        "rerunForbidden",
        "immediateClosureRequired",
        "historicalAttemptsImmutable",
    ):
        require(actions.get(key) is True, f"GitHub release safety rule differs: {key}")
    require(actions.get("workflowRunAttemptMustEqual") == 1, "workflow attempt boundary differs")
    require(actions.get("completedV351EvidenceReusable") is False, "v351 workflow evidence reuse must be forbidden")

    render = plan.get("render") or {}
    require(render.get("serviceMode") == "existing-image-web-service", "Render service mode differs")
    require(render.get("serviceName") == SERVICE_NAME, "Render service name differs")
    require(render.get("serviceIdentitySha256") == OLD_SERVICE_ID_SHA256, "Render service identity hash differs")
    require(render.get("imageRepository") == IMAGE_REPOSITORY, "Render image repository differs")
    require(render.get("previousV351ImageDigest") == OLD_IMAGE_DIGEST, "v351 image digest boundary differs")
    require(render.get("previousV351DeployIdSha256") == OLD_DEPLOY_ID_SHA256, "v351 deploy hash boundary differs")
    require(render.get("completedV351EvidencePathSha256") == OLD_EVIDENCE_PATH_SHA256, "v351 evidence path hash differs")
    require(render.get("environmentExample") == "deploy/render.production.env.example", "Render environment source differs")
    require(render.get("requiredEmailSecurityEnvKeys") == list(REQUIRED_ENV_KEYS), "Render email/security key inventory differs")
    require(render.get("environmentEvidenceMode") == "key-names-only", "Render environment evidence mode differs")
    for key in ("secretValuesRecorded", "endpointsRecorded", "automaticRetry", "providerMutationDuringGuard"):
        require(render.get(key) is False, f"Render release boundary differs: {key}")
    for key in ("exactDigestRequired", "singleManualDeployOnly"):
        require(render.get(key) is True, f"Render release boundary differs: {key}")

    required_keys = _tracked_env_keys(root / render["environmentExample"])
    require(set(REQUIRED_ENV_KEYS).issubset(required_keys), "tracked Render example is missing v377 email/security keys")

    workflow = (root / actions["workflow"]).read_text(encoding="utf-8")
    for marker in (
        "workflow_dispatch:",
        "approved_preparation_commit",
        "publishReviewerGateReady",
        "authorization-open",
        "workflow re-runs are forbidden",
        "changed == [LIFECYCLE_PATH]",
    ):
        require(marker in workflow, "publish workflow lost an owner-only lifecycle marker")
    require(re.search(r"(?m)^  (?:push|pull_request|pull_request_target|schedule):", workflow) is None, "publish workflow gained an automatic trigger")

    lifecycle = load_json(root / actions["lifecyclePath"])
    _require_authorization_policy(lifecycle)
    observed = lifecycle.get("observedAttempt") or {}
    require(lifecycle.get("state") == "attempt-recorded", "current historical lifecycle must remain completed before fresh preparation")
    require(lifecycle.get("publishReviewerGateReady") is False, "current historical publish gate must remain closed")
    require(observed.get("runAttempt") == 1 and observed.get("status") == "completed", "current publish attempt evidence differs")
    _current_attempt_history_entry(lifecycle, load_json(IMAGE_POLICY_PATH))

    v351 = load_json(root / "deploy/review/render-v351-provider-release-v355.json")
    backend = v351.get("backend") or {}
    require(sha256_text(str(backend.get("deployId") or "")) == OLD_DEPLOY_ID_SHA256, "v351 deploy identity hash differs")
    require(str(backend.get("liveImageReference") or "") == OLD_IMAGE_REFERENCE, "v351 live image evidence differs")
    require(sha256_text(V351_EVIDENCE_PATH.relative_to(root).as_posix()) == OLD_EVIDENCE_PATH_SHA256, "v351 evidence path boundary differs")
    return {
        "result": RESULT,
        "requiredEnvKeyCount": len(REQUIRED_ENV_KEYS),
        "providerMutationExecuted": False,
        "networkAccessExecuted": False,
    }


def _current_attempt_history_entry(previous: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    _require_authorization_policy(previous)
    require(previous.get("state") == "attempt-recorded", "fresh preparation requires a completed prior lifecycle")
    require(previous.get("publishReviewerGateReady") is False, "prior publish gate must be closed")
    approved = full_sha(previous.get("approvedPreparationSha"), "prior approved preparation")
    closure = previous.get("closure") or {}
    authorization = full_sha(closure.get("authorizationSourceSha"), "prior authorization")
    closure_sha = full_sha(closure.get("closureCommitSha"), "prior closure")
    observed = previous.get("observedAttempt") or {}
    require(observed.get("runAttempt") == 1, "prior workflow rerun evidence is forbidden")
    require(observed.get("status") == "completed", "prior workflow attempt is incomplete")
    current = policy.get("currentAttemptEvidence") or {}
    require(current.get("authorizationSha") == authorization, "policy authorization evidence differs")
    require(current.get("closureSha") == closure_sha, "policy closure evidence differs")
    require(current.get("runId") == observed.get("runId"), "policy workflow run evidence differs")
    require(current.get("runUrl") == observed.get("runUrl"), "policy workflow URL evidence differs")
    require(current.get("conclusion") == observed.get("conclusion"), "policy workflow conclusion differs")
    digest = observed.get("imageDigest")
    if digest is not None:
        exact_digest(digest, "prior image")
    require(current.get("imageDigest") == digest, "policy image digest evidence differs")
    signature_verified = observed.get("signatureVerified")
    require(isinstance(signature_verified, bool), "prior signature evidence differs")
    require(current.get("signatureVerified") is signature_verified, "policy signature evidence differs")
    conclusion = observed.get("conclusion")
    require(conclusion in {
        "success",
        "failure",
        "neutral",
        "cancelled",
        "skipped",
        "timed_out",
        "action_required",
        "stale",
        "startup_failure",
    }, "prior workflow conclusion differs")
    if conclusion == "success":
        require(digest is not None, "successful prior attempt requires an image digest")
        require(signature_verified is True, "successful prior attempt requires verified signature evidence")
    artifact_count = current.get("artifactCount")
    require(isinstance(artifact_count, int) and not isinstance(artifact_count, bool) and artifact_count >= 0, "policy artifact count differs")
    for key in ("registryLoginExecuted", "imageBuildExecuted", "imagePushExecuted"):
        require(isinstance(current.get(key), bool), f"policy {key} evidence differs")
    return {
        "preparationSha": approved,
        "authorizationSha": authorization,
        "closureSha": closure_sha,
        "recordCommitSha": full_sha(current.get("recordCommitSha"), "prior record commit"),
        "runId": observed.get("runId"),
        "runUrl": observed.get("runUrl"),
        "conclusion": observed.get("conclusion"),
        "registryLoginExecuted": current.get("registryLoginExecuted") is True,
        "imageBuildExecuted": current.get("imageBuildExecuted") is True,
        "imagePushExecuted": current.get("imagePushExecuted") is True,
        "artifactCount": artifact_count,
        "imageDigest": digest,
        "signatureVerified": signature_verified,
    }


def create_fresh_publish_preparation(
    previous: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Reset a completed lifecycle while appending immutable attempt evidence."""
    prior_history = previous.get("attemptHistory")
    require(isinstance(prior_history, list) and prior_history, "prior attempt history is missing")
    entry = _current_attempt_history_entry(previous, policy)
    require(entry not in prior_history, "completed v351 attempt was already appended")
    prepared = _json_clone(previous)
    prepared["schemaVersion"] = f"v377.owner-only-publish-lifecycle-with-{len(prior_history) + 1}-attempt-history"
    prepared["state"] = "preparation-closed"
    prepared["publishReviewerGateReady"] = False
    prepared["priorApprovedPreparationSha"] = entry["preparationSha"]
    prepared["priorAttemptEvidence"] = _json_clone(entry)
    prepared["attemptHistory"] = [*_json_clone({"history": prior_history})["history"], entry]
    prepared["approvedPreparationSha"] = None
    prepared["ownerApproval"] = {
        "recorded": False,
        "recordedAtUtc": None,
        "evidence": "exact-40-character-sha-user-message",
    }
    prepared["closure"] = {
        "authorizationSourceSha": None,
        "closureCommitSha": None,
        "preparedAtUtc": None,
    }
    prepared["observedAttempt"] = {
        "runId": None,
        "runUrl": None,
        "runAttempt": None,
        "status": "not-dispatched",
        "conclusion": None,
        "imageDigest": None,
        "signatureVerified": False,
    }
    validate_fresh_publish_preparation(previous, prepared, entry)
    return prepared


def validate_fresh_publish_preparation(
    previous: dict[str, Any],
    prepared: dict[str, Any],
    expected_entry: dict[str, Any],
) -> None:
    prior_history = previous.get("attemptHistory")
    history = prepared.get("attemptHistory")
    require(isinstance(prior_history, list) and isinstance(history, list), "publish history differs")
    require(history[:-1] == prior_history, "historical publish attempts changed")
    require(history[-1] == expected_entry, "completed v351 attempt was not preserved exactly once")
    require(len(history) == len(prior_history) + 1, "fresh preparation appended more than one attempt")
    require(prepared.get("state") == "preparation-closed", "fresh preparation state differs")
    require(prepared.get("publishReviewerGateReady") is False, "fresh preparation gate must remain closed")
    require(prepared.get("approvedPreparationSha") is None, "fresh preparation must not self-authorize")
    require(prepared.get("ownerApproval") == {
        "recorded": False,
        "recordedAtUtc": None,
        "evidence": "exact-40-character-sha-user-message",
    }, "fresh preparation owner approval must be empty")
    require(prepared.get("closure") == {
        "authorizationSourceSha": None,
        "closureCommitSha": None,
        "preparedAtUtc": None,
    }, "fresh preparation closure evidence must be empty")
    require(prepared.get("observedAttempt") == {
        "runId": None,
        "runUrl": None,
        "runAttempt": None,
        "status": "not-dispatched",
        "conclusion": None,
        "imageDigest": None,
        "signatureVerified": False,
    }, "fresh preparation must not reuse v351 attempt evidence")
    _require_authorization_policy(prepared)


def open_publish_authorization(
    prepared: dict[str, Any],
    *,
    preparation_sha: str,
    approved_at_utc: str,
    live_settings_rechecked_at_utc: str,
) -> dict[str, Any]:
    full_sha(preparation_sha, "approved preparation")
    _require_authorization_policy(prepared)
    require(prepared.get("state") == "preparation-closed", "authorization parent must be preparation-closed")
    require(prepared.get("publishReviewerGateReady") is False, "authorization parent gate must be closed")
    require(prepared.get("approvedPreparationSha") is None, "authorization parent is already approved")
    approved_at = utc_timestamp(approved_at_utc, "owner approval timestamp")
    checked_at = utc_timestamp(live_settings_rechecked_at_utc, "live-settings timestamp")
    now = datetime.now(timezone.utc)
    require(approved_at <= checked_at <= now + timedelta(seconds=5), "authorization timestamps differ")
    require((now - checked_at).total_seconds() <= 4 * 60 * 60, "live-settings check is stale")
    current = _json_clone(prepared)
    current["state"] = "authorization-open"
    current["publishReviewerGateReady"] = True
    current["approvedPreparationSha"] = preparation_sha
    current["ownerApproval"] = {
        "recorded": True,
        "recordedAtUtc": approved_at_utc,
        "evidence": "exact-40-character-sha-user-message",
    }
    settings = current.get("githubLiveSettings")
    require(isinstance(settings, dict), "GitHub live-settings evidence is missing")
    settings["recheckedAtUtc"] = live_settings_rechecked_at_utc
    require(current.get("attemptHistory") == prepared.get("attemptHistory"), "authorization changed attempt history")
    return current


def close_publish_authorization(
    opened: dict[str, Any],
    *,
    authorization_sha: str,
    run_id: int,
    run_status: str,
    closed_at_utc: str,
) -> dict[str, Any]:
    full_sha(authorization_sha, "authorization source")
    _require_authorization_policy(opened)
    require(opened.get("state") == "authorization-open", "closure parent must be authorization-open")
    require(opened.get("publishReviewerGateReady") is True, "authorization gate is not open")
    preparation_sha = full_sha(opened.get("approvedPreparationSha"), "approved preparation")
    require(authorization_sha != preparation_sha, "authorization must be a direct-child commit, not the preparation")
    owner = opened.get("ownerApproval") or {}
    require(owner.get("recorded") is True, "closure requires recorded owner approval")
    utc_timestamp(owner.get("recordedAtUtc"), "owner approval timestamp")
    require(isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0, "workflow run ID differs")
    require(run_status in {"queued", "in_progress", "completed"}, "accepted workflow status differs")
    closed_at = utc_timestamp(closed_at_utc, "closure timestamp")
    now = datetime.now(timezone.utc)
    require(closed_at <= now + timedelta(seconds=5), "closure timestamp is in the future")
    require((now - closed_at).total_seconds() <= 10 * 60, "authorization was not closed immediately")
    current = _json_clone(opened)
    current["state"] = "authorization-closed-awaiting-evidence"
    current["publishReviewerGateReady"] = False
    current["closure"] = {
        "authorizationSourceSha": authorization_sha,
        "closureCommitSha": None,
        "preparedAtUtc": closed_at_utc,
    }
    current["observedAttempt"] = {
        "runId": run_id,
        "runUrl": f"https://github.com/gihohoho/upgrade-rpg/actions/runs/{run_id}",
        "runAttempt": 1,
        "status": run_status,
        "conclusion": None,
        "imageDigest": None,
        "signatureVerified": False,
    }
    return current


def record_publish_attempt(
    closed: dict[str, Any],
    *,
    closure_sha: str,
    conclusion: str,
    image_digest: str | None,
    signature_verified: bool,
) -> dict[str, Any]:
    full_sha(closure_sha, "closure commit")
    _require_authorization_policy(closed)
    require(closed.get("state") == "authorization-closed-awaiting-evidence", "attempt parent must be closed")
    require(closed.get("publishReviewerGateReady") is False, "attempt parent gate must remain closed")
    closure = closed.get("closure") or {}
    authorization_sha = full_sha(closure.get("authorizationSourceSha"), "closed authorization source")
    require(closure.get("closureCommitSha") is None, "attempt parent must not self-record its closure commit")
    utc_timestamp(closure.get("preparedAtUtc"), "closure timestamp")
    require(closure_sha != authorization_sha, "closure evidence must come from a direct-child commit")
    observed = closed.get("observedAttempt") or {}
    run_id = observed.get("runId")
    require(isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0, "accepted workflow run ID differs")
    require(
        observed.get("runUrl") == f"https://github.com/gihohoho/upgrade-rpg/actions/runs/{run_id}",
        "accepted workflow run URL differs",
    )
    require(observed.get("runAttempt") == 1, "workflow reruns are forbidden")
    require(observed.get("status") in {"queued", "in_progress", "completed"}, "accepted workflow status differs")
    require(observed.get("conclusion") is None, "attempt parent already contains conclusion evidence")
    require(observed.get("imageDigest") is None, "attempt parent already contains digest evidence")
    require(observed.get("signatureVerified") is False, "attempt parent already contains signature evidence")
    require(conclusion in {
        "success",
        "failure",
        "neutral",
        "cancelled",
        "skipped",
        "timed_out",
        "action_required",
        "stale",
        "startup_failure",
    }, "workflow conclusion differs")
    if image_digest is not None:
        exact_digest(image_digest, "published image")
        require(image_digest != OLD_IMAGE_DIGEST, "v351 image digest cannot be reused for v377")
        prior_digests = {
            item.get("imageDigest")
            for item in closed.get("attemptHistory", [])
            if isinstance(item, dict)
        }
        require(image_digest not in prior_digests, "a historical image digest cannot be reused")
    if conclusion == "success":
        require(image_digest is not None, "successful publish requires a new exact digest")
        require(signature_verified is True, "successful publish requires verified signature evidence")
    current = _json_clone(closed)
    current["state"] = "attempt-recorded"
    current["closure"]["closureCommitSha"] = closure_sha
    current["observedAttempt"].update({
        "status": "completed",
        "conclusion": conclusion,
        "imageDigest": image_digest,
        "signatureVerified": signature_verified,
    })
    return current


def _strict_render_inventory(payload: dict[str, Any], plan: dict[str, Any]) -> None:
    require(set(payload) == {"serviceId", "currentImageReference", "latestDeployId", "environmentKeys"}, "Render inventory must contain identifiers and key names only")
    service_id = payload.get("serviceId")
    deploy_id = payload.get("latestDeployId")
    require(isinstance(service_id, str) and SERVICE_ID_PATTERN.fullmatch(service_id) is not None, "Render service identity shape differs")
    require(isinstance(deploy_id, str) and DEPLOY_ID_PATTERN.fullmatch(deploy_id) is not None, "Render deploy identity shape differs")
    render = plan["render"]
    require(sha256_text(service_id) == render["serviceIdentitySha256"], "Render existing service identity differs")
    require(payload.get("currentImageReference") == OLD_IMAGE_REFERENCE, "Render current image is not the v351 baseline")
    require(sha256_text(deploy_id) == render["previousV351DeployIdSha256"], "Render latest deploy is not the v351 baseline")
    keys = _require_key_names_only(payload.get("environmentKeys"), "Render environment inventory")
    require(set(REQUIRED_ENV_KEYS).issubset(set(keys)), "Render environment inventory is missing v377 email/security keys")


def _successful_publish(lifecycle: dict[str, Any]) -> tuple[str, str]:
    require(lifecycle.get("state") == "attempt-recorded", "Render preparation requires recorded publish evidence")
    require(lifecycle.get("publishReviewerGateReady") is False, "publish gate must be closed before Render preparation")
    observed = lifecycle.get("observedAttempt") or {}
    require(observed.get("runAttempt") == 1, "Render preparation refuses workflow rerun evidence")
    require(observed.get("status") == "completed" and observed.get("conclusion") == "success", "Render preparation requires a successful publish")
    digest = exact_digest(observed.get("imageDigest"), "published image")
    require(digest != OLD_IMAGE_DIGEST, "Render preparation refuses the v351 image digest")
    require(observed.get("signatureVerified") is True, "Render preparation requires signature evidence")
    authorization_sha = full_sha((lifecycle.get("closure") or {}).get("authorizationSourceSha"), "published source")
    return authorization_sha, digest


def create_render_preparation(
    plan: dict[str, Any],
    lifecycle: dict[str, Any],
    inventory: dict[str, Any],
    *,
    source_sha: str,
) -> dict[str, Any]:
    validate_static_guard_without_current_lifecycle(plan)
    _strict_render_inventory(inventory, plan)
    published_source, digest = _successful_publish(lifecycle)
    require(full_sha(source_sha, "confirmed published source") == published_source, "confirmed source differs from publish evidence")
    observed = lifecycle["observedAttempt"]
    closure = lifecycle["closure"]
    preparation = {
        "schemaVersion": TOOL_VERSION,
        "state": "render-prepared",
        "sourceCommitSha": source_sha,
        "imageReference": f"{IMAGE_REPOSITORY}@{digest}",
        "imageDigest": digest,
        "serviceName": SERVICE_NAME,
        "serviceIdentitySha256": sha256_text(inventory["serviceId"]),
        "previousDeployIdSha256": sha256_text(inventory["latestDeployId"]),
        "requiredEnvironmentKeys": list(REQUIRED_ENV_KEYS),
        "environmentEvidenceMode": "key-names-only",
        "secretValuesRecorded": False,
        "endpointsRecorded": False,
        "publishEvidence": {
            "preparationCommitSha": lifecycle.get("approvedPreparationSha"),
            "authorizationCommitSha": published_source,
            "closureCommitSha": closure.get("closureCommitSha"),
            "runId": observed.get("runId"),
            "runAttempt": 1,
            "conclusion": "success",
            "signatureVerified": True,
        },
        "completedV351EvidenceReused": False,
        "deployAttemptCount": 0,
        "deploymentExecuted": False,
        "automaticRetry": False,
        "providerMutationDuringGuard": False,
    }
    validate_render_preparation(preparation, plan)
    return preparation


def validate_static_guard_without_current_lifecycle(plan: dict[str, Any]) -> None:
    """Validate the immutable contract subset after the lifecycle has advanced."""
    require(plan.get("schemaVersion") == TOOL_VERSION, "v377 release guard version differs")
    require(plan.get("result") == RESULT, "v377 release guard result differs")
    require(plan.get("productionResourcesMutated") is False, "source guard must not claim provider mutation")
    require(plan.get("networkAccessExecuted") is False, "source guard must not claim network access")
    actions = plan.get("githubActions") or {}
    require(actions.get("workflow") == ".github/workflows/publish-backend-ghcr.yml", "publish workflow path differs")
    require(actions.get("lifecyclePath") == LIFECYCLE_RELATIVE, "publish lifecycle path differs")
    require(actions.get("authorizationChangedPaths") == [LIFECYCLE_RELATIVE], "authorization path boundary differs")
    for key in (
        "freshPreparationRequired",
        "singleDispatchRequired",
        "rerunForbidden",
        "immediateClosureRequired",
        "historicalAttemptsImmutable",
    ):
        require(actions.get(key) is True, f"GitHub release safety rule differs: {key}")
    require(actions.get("workflowRunAttemptMustEqual") == 1, "workflow attempt boundary differs")
    require(actions.get("completedV351EvidenceReusable") is False, "v351 workflow evidence reuse must be forbidden")
    render = plan.get("render") or {}
    require(render.get("requiredEmailSecurityEnvKeys") == list(REQUIRED_ENV_KEYS), "Render email/security key inventory differs")
    require(render.get("previousV351ImageDigest") == OLD_IMAGE_DIGEST, "v351 image digest boundary differs")
    require(render.get("previousV351DeployIdSha256") == OLD_DEPLOY_ID_SHA256, "v351 deploy hash boundary differs")
    require(render.get("serviceIdentitySha256") == OLD_SERVICE_ID_SHA256, "Render service identity hash differs")
    require(render.get("environmentEvidenceMode") == "key-names-only", "Render environment evidence mode differs")
    for key in ("secretValuesRecorded", "endpointsRecorded", "automaticRetry", "providerMutationDuringGuard"):
        require(render.get(key) is False, f"Render release boundary differs: {key}")
    for key in ("exactDigestRequired", "singleManualDeployOnly"):
        require(render.get(key) is True, f"Render release boundary differs: {key}")


def validate_render_preparation(payload: dict[str, Any], plan: dict[str, Any]) -> None:
    require(set(payload) == {
        "schemaVersion",
        "state",
        "sourceCommitSha",
        "imageReference",
        "imageDigest",
        "serviceName",
        "serviceIdentitySha256",
        "previousDeployIdSha256",
        "requiredEnvironmentKeys",
        "environmentEvidenceMode",
        "secretValuesRecorded",
        "endpointsRecorded",
        "publishEvidence",
        "completedV351EvidenceReused",
        "deployAttemptCount",
        "deploymentExecuted",
        "automaticRetry",
        "providerMutationDuringGuard",
    }, "Render preparation field boundary differs")
    require(payload.get("schemaVersion") == TOOL_VERSION and payload.get("state") == "render-prepared", "Render preparation version/state differs")
    full_sha(payload.get("sourceCommitSha"), "Render source")
    digest = exact_digest(payload.get("imageDigest"), "Render candidate")
    require(digest != OLD_IMAGE_DIGEST, "Render preparation reused the v351 digest")
    require(payload.get("imageReference") == f"{IMAGE_REPOSITORY}@{digest}", "Render exact image reference differs")
    require(payload.get("serviceName") == SERVICE_NAME, "Render service differs")
    require(payload.get("serviceIdentitySha256") == OLD_SERVICE_ID_SHA256, "Render service identity differs")
    require(payload.get("previousDeployIdSha256") == OLD_DEPLOY_ID_SHA256, "Render previous deploy identity differs")
    require(payload.get("requiredEnvironmentKeys") == list(REQUIRED_ENV_KEYS), "Render required environment keys differ")
    require(payload.get("environmentEvidenceMode") == "key-names-only", "Render environment evidence must remain key-only")
    for key in ("secretValuesRecorded", "endpointsRecorded", "completedV351EvidenceReused", "deploymentExecuted", "automaticRetry", "providerMutationDuringGuard"):
        require(payload.get(key) is False, f"Render preparation boundary differs: {key}")
    require(payload.get("deployAttemptCount") == 0, "Render preparation must not claim a deploy")
    publish = payload.get("publishEvidence") or {}
    require(set(publish) == {
        "preparationCommitSha",
        "authorizationCommitSha",
        "closureCommitSha",
        "runId",
        "runAttempt",
        "conclusion",
        "signatureVerified",
    }, "Render publish evidence boundary differs")
    for key in ("preparationCommitSha", "authorizationCommitSha", "closureCommitSha"):
        full_sha(publish.get(key), f"publish {key}")
    require(publish.get("authorizationCommitSha") == payload.get("sourceCommitSha"), "Render source and publish authorization differ")
    require(publish.get("runAttempt") == 1 and publish.get("conclusion") == "success", "Render publish attempt evidence differs")
    require(publish.get("signatureVerified") is True, "Render publish signature evidence differs")
    require(plan["render"].get("completedV351EvidencePathSha256") == OLD_EVIDENCE_PATH_SHA256, "v351 evidence reuse boundary differs")


def record_render_attempt(
    preparation: dict[str, Any],
    observation: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any]:
    validate_render_preparation(preparation, plan)
    require(set(observation) == {
        "serviceId",
        "deployId",
        "imageReference",
        "status",
        "attemptCount",
        "automaticRetry",
        "environmentKeys",
    }, "Render observation must contain identifiers, state, and key names only")
    service_id = observation.get("serviceId")
    deploy_id = observation.get("deployId")
    require(isinstance(service_id, str) and SERVICE_ID_PATTERN.fullmatch(service_id) is not None, "Render service identity shape differs")
    require(isinstance(deploy_id, str) and DEPLOY_ID_PATTERN.fullmatch(deploy_id) is not None, "Render deploy identity shape differs")
    require(sha256_text(service_id) == preparation["serviceIdentitySha256"], "Render service changed")
    new_deploy_hash = sha256_text(deploy_id)
    require(new_deploy_hash != preparation["previousDeployIdSha256"], "v351 deploy ID cannot be reused")
    require(observation.get("imageReference") == preparation["imageReference"], "Render live image differs from the prepared digest")
    require(observation.get("status") == "live", "Render attempt is not live")
    require(observation.get("attemptCount") == 1, "Render deployment must have exactly one attempt")
    require(observation.get("automaticRetry") is False, "Render automatic retry is forbidden")
    keys = _require_key_names_only(observation.get("environmentKeys"), "Render environment observation")
    require(set(REQUIRED_ENV_KEYS).issubset(set(keys)), "Render live environment is missing v377 email/security keys")
    return {
        "schemaVersion": TOOL_VERSION,
        "state": "render-attempt-recorded",
        "sourceCommitSha": preparation["sourceCommitSha"],
        "imageReference": preparation["imageReference"],
        "imageDigest": preparation["imageDigest"],
        "serviceName": SERVICE_NAME,
        "serviceIdentitySha256": preparation["serviceIdentitySha256"],
        "previousDeployIdSha256": preparation["previousDeployIdSha256"],
        "newDeployIdSha256": new_deploy_hash,
        "requiredEnvironmentKeys": list(REQUIRED_ENV_KEYS),
        "environmentEvidenceMode": "key-names-only",
        "secretValuesRecorded": False,
        "endpointsRecorded": False,
        "publishEvidence": _json_clone(preparation["publishEvidence"]),
        "completedV351EvidenceReused": False,
        "deployAttemptCount": 1,
        "deploymentExecuted": True,
        "deployStatus": "live",
        "automaticRetry": False,
    }


def _require_local_input_path(path: Path) -> None:
    resolved_root = LOCAL_REPORT_DIR.resolve()
    try:
        resolved = path.resolve()
    except OSError:
        raise V377ReleaseGuardError("local Render inventory path is invalid") from None
    require(resolved_root in resolved.parents, "Render inventory must stay in the ignored release directory")
    relative = resolved.relative_to(ROOT.resolve()).as_posix()
    require(sha256_text(relative) != OLD_EVIDENCE_PATH_SHA256, "completed v351 evidence cannot be reused")


def _require_ignored_output(path: Path) -> None:
    relative = path.relative_to(ROOT).as_posix()
    completed = subprocess.run(["git", "check-ignore", "--quiet", "--", relative], cwd=ROOT, check=False)
    require(completed.returncode == 0, "Render guard output must be Git-ignored")


def _print_static(summary: dict[str, Any]) -> None:
    print("v377 email release deployment guard (source-only)")
    print("- GitHub lifecycle: fresh preparation / owner-only open / immediate close / one attempt")
    print(f"- Render email/security environment keys: {summary['requiredEnvKeyCount']} (names only)")
    print("- old digest/deploy/evidence reuse: forbidden")
    print("- secret values/endpoints displayed: no")
    print("- network/provider mutation: no/no")
    print(f"- result: {summary['result']}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--prepare-publish", action="store_true")
    modes.add_argument("--authorize-publish", action="store_true")
    modes.add_argument("--close-publish", action="store_true")
    modes.add_argument("--record-publish", action="store_true")
    modes.add_argument("--prepare-render", action="store_true")
    modes.add_argument("--record-render", action="store_true")
    parser.add_argument("--confirm-action")
    parser.add_argument("--confirm-source-sha")
    parser.add_argument("--confirm-preparation-sha")
    parser.add_argument("--approved-at-utc")
    parser.add_argument("--live-settings-rechecked-at-utc")
    parser.add_argument("--confirm-authorization-sha")
    parser.add_argument("--run-id", type=int)
    parser.add_argument("--run-status", choices=("queued", "in_progress", "completed"))
    parser.add_argument("--closed-at-utc")
    parser.add_argument("--confirm-closure-sha")
    parser.add_argument("--conclusion")
    parser.add_argument("--image-digest")
    parser.add_argument("--signature-verified", action="store_true")
    parser.add_argument("--inventory")
    parser.add_argument("--observation")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        plan = load_json(PLAN_PATH)
        if not any((args.prepare_publish, args.authorize_publish, args.close_publish, args.record_publish, args.prepare_render, args.record_render)):
            _print_static(validate_static_guard(plan))
            return 0

        lifecycle = load_json(LIFECYCLE_PATH)
        if args.prepare_publish:
            require(args.confirm_action == PREPARE_PUBLISH_ACTION, "fresh publish action confirmation differs")
            source_sha = full_sha(args.confirm_source_sha, "confirmed source")
            require_clean_pushed_main(source_sha)
            prepared = create_fresh_publish_preparation(lifecycle, load_json(IMAGE_POLICY_PATH))
            _atomic_write_json(LIFECYCLE_PATH, prepared)
            print("v377 fresh publish preparation written; gate remains closed; provider mutation: no")
        elif args.authorize_publish:
            require(args.confirm_action == AUTHORIZE_PUBLISH_ACTION, "publish authorization action confirmation differs")
            preparation_sha = full_sha(args.confirm_preparation_sha, "approved preparation")
            require_clean_pushed_main(preparation_sha)
            opened = open_publish_authorization(
                lifecycle,
                preparation_sha=preparation_sha,
                approved_at_utc=args.approved_at_utc or "",
                live_settings_rechecked_at_utc=args.live_settings_rechecked_at_utc or "",
            )
            _atomic_write_json(LIFECYCLE_PATH, opened)
            print("v377 owner-approved publish authorization written; dispatch count allowed: one")
        elif args.close_publish:
            require(args.confirm_action == CLOSE_PUBLISH_ACTION, "publish closure action confirmation differs")
            authorization_sha = full_sha(args.confirm_authorization_sha, "authorization source")
            require_clean_pushed_main(authorization_sha)
            closed = close_publish_authorization(
                lifecycle,
                authorization_sha=authorization_sha,
                run_id=args.run_id or 0,
                run_status=args.run_status or "",
                closed_at_utc=args.closed_at_utc or "",
            )
            _atomic_write_json(LIFECYCLE_PATH, closed)
            print("v377 publish authorization closed immediately; gate closed; automatic retry: forbidden")
        elif args.record_publish:
            require(args.confirm_action == RECORD_PUBLISH_ACTION, "publish record action confirmation differs")
            closure_sha = full_sha(args.confirm_closure_sha, "closure commit")
            require_clean_pushed_main(closure_sha)
            recorded = record_publish_attempt(
                lifecycle,
                closure_sha=closure_sha,
                conclusion=args.conclusion or "",
                image_digest=args.image_digest,
                signature_verified=args.signature_verified,
            )
            _atomic_write_json(LIFECYCLE_PATH, recorded)
            print("v377 publish attempt recorded; gate closed; rerun: forbidden")
        elif args.prepare_render:
            require(args.confirm_action == PREPARE_RENDER_ACTION, "Render preparation action confirmation differs")
            source_sha = full_sha(args.confirm_source_sha, "confirmed source")
            require(_git("branch", "--show-current") == "main", "Render preparation requires main")
            require(_git("status", "--porcelain") == "", "Render preparation requires a clean worktree")
            require(_git("rev-parse", "HEAD") == _git("rev-parse", "--verify", "origin/main"), "Render preparation requires pushed main")
            require(_git("merge-base", "--is-ancestor", source_sha, "HEAD") == "", "published source is not in main history")
            inventory_path = ROOT / (args.inventory or "")
            _require_local_input_path(inventory_path)
            preparation = create_render_preparation(plan, lifecycle, load_json(inventory_path), source_sha=source_sha)
            _require_ignored_output(RENDER_PREPARATION_PATH)
            _atomic_write_json(RENDER_PREPARATION_PATH, preparation)
            print("v377 Render exact-image preparation written (sanitized); provider mutation: no")
        else:
            require(args.confirm_action == RECORD_RENDER_ACTION, "Render record action confirmation differs")
            observation_path = ROOT / (args.observation or "")
            _require_local_input_path(observation_path)
            recorded = record_render_attempt(load_json(RENDER_PREPARATION_PATH), load_json(observation_path), plan)
            _require_ignored_output(RENDER_ATTEMPT_PATH)
            _atomic_write_json(RENDER_ATTEMPT_PATH, recorded)
            print("v377 Render deploy attempt recorded (sanitized); attempts: one; automatic retry: no")
    except V377ReleaseGuardError as exc:
        print(f"v377 email release guard failed: {exc}", file=sys.stderr)
        return 1
    except Exception:
        print("v377 email release guard failed: unexpected local guard error", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

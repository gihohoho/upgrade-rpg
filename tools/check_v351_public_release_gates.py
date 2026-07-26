#!/usr/bin/env python3
"""Fail-closed checker for the v351 backend/static public release gates."""

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
BACKEND_POLICY_PATH = ROOT / "deploy/backend-image-ghcr-policy.example.json"
STATIC_PLAN_PATH = ROOT / "deploy/render-static-site.example.json"

VERSION = "v352.v351-public-release-gates-prepared-backend-image-approval-required"
RESULT = "v351-backend-image-preparation-closed-owner-approval-required"
NEXT_STAGE = "owner-approve-v352-v351-backend-image-preparation-sha"
BASELINE = "81beaa0864c3422fb9fc2071b9c4965936ecafac"
LIFECYCLE_VERSION = "v352.owner-only-publish-lifecycle-with-six-attempt-history"
CURRENT_IMAGE = (
    "ghcr.io/gihohoho/upgrade-rpg-backend@"
    "sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1"
)
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
    require(plan.get("productionResourcesMutated") is False, "provider mutation flag must be false")

    source = plan.get("source") or {}
    require(source.get("baselineCommit") == BASELINE, "v351 source baseline differs")
    require(source.get("branch") == "main", "release branch must be main")
    require(source.get("cleanPushedPreparationRequired") is True, "clean pushed preparation is required")
    require(source.get("runtimeFiles") == EXPECTED_HASHES, "runtime file hash contract differs")

    actions = plan.get("githubActions") or {}
    require(actions.get("trigger") == "workflow_dispatch-only", "workflow trigger differs")
    require(actions.get("lifecycleSchemaVersion") == LIFECYCLE_VERSION, "lifecycle version differs")
    require(actions.get("lifecycleState") == "preparation-closed", "lifecycle must be preparation-closed")
    require(actions.get("publishReviewerGateReady") is False, "publish gate must be closed")
    require(actions.get("approvedPreparationSha") is None, "preparation must not self-approve")
    require(actions.get("ownerApprovalRecorded") is False, "owner approval must be absent")
    require(actions.get("priorAttemptCount") == 6, "six prior attempts must be preserved")
    require(actions.get("newWorkflowDispatchExecuted") is False, "new workflow must not be dispatched")
    require(actions.get("newRegistryMutationExecuted") is False, "new registry mutation must be false")

    backend = plan.get("backendRelease") or {}
    require(backend.get("currentLiveImage") == CURRENT_IMAGE, "current live image differs")
    require(backend.get("newImageReference") is None, "new image must not be invented")
    require(backend.get("supplyChainValidationRequired") is True, "supply-chain validation is required")
    require(backend.get("isolatedRuntimeValidationRequired") is True, "isolated validation is required")
    require(backend.get("renderExactImageDeployPreparationReady") is False, "Render image deploy must remain blocked")
    require(backend.get("renderDeployApproved") is False, "Render backend deploy must be unapproved")
    require(backend.get("renderDeployExecuted") is False, "Render backend deploy must be unexecuted")

    frontend = plan.get("frontendRelease") or {}
    require(frontend.get("serviceId") == "srv-d9iu337aqgkc73am4lh0", "static service differs")
    require(frontend.get("autoDeploy") is False, "static auto-deploy must remain off")
    require(frontend.get("releaseSourceBaseline") == BASELINE, "static release baseline differs")
    require(frontend.get("staticDeployPreparationReady") is False, "static deploy must remain blocked")
    require(frontend.get("staticDeployApproved") is False, "static deploy must be unapproved")
    require(frontend.get("staticDeployExecuted") is False, "static deploy must be unexecuted")

    forbidden = plan.get("forbiddenBeforeNextSeparateApproval") or []
    for marker in (
        "GitHub Actions dispatch",
        "GHCR login, build, push, or tag mutation",
        "Render backend deploy",
        "Render Static Site deploy",
        "database or Alembic mutation",
        "automatic deploy or retry",
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
    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        require(path.is_file(), f"missing pinned source: {relative}")
        require(sha256_file(path) == expected, f"pinned source hash differs: {relative}")

    lifecycle = load_json(LIFECYCLE_PATH)
    require(lifecycle.get("schemaVersion") == LIFECYCLE_VERSION, "live lifecycle schema differs")
    require(lifecycle.get("state") == "preparation-closed", "live lifecycle is not preparation-closed")
    require(lifecycle.get("publishReviewerGateReady") is False, "live publish gate is open")
    require(lifecycle.get("approvedPreparationSha") is None, "live lifecycle self-approved")
    require((lifecycle.get("ownerApproval") or {}).get("recorded") is False, "live owner approval must be absent")
    require(len(lifecycle.get("attemptHistory") or []) == 6, "live attempt history count differs")
    require((lifecycle.get("observedAttempt") or {}).get("status") == "not-dispatched", "new workflow was dispatched")

    policy = load_json(BACKEND_POLICY_PATH)
    require(policy.get("publishLifecycleState") == "preparation-closed", "backend policy lifecycle differs")
    require(policy.get("approvedPreparationSha") is None, "backend policy self-approved")
    require(policy.get("exactPreparationShaApproved") is False, "backend policy approval must be false")
    require(policy.get("sourceControlledPublishGateReady") is False, "backend policy gate is open")
    require(policy.get("nextSafeStage") == NEXT_STAGE, "backend policy next stage differs")

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

    print("v351 public release gate verification (static, no provider mutation)")
    print(f"- source baseline: {BASELINE}")
    print("- backend image lifecycle: preparation-closed / gate=false / approval=null")
    print("- prior workflow attempts preserved: 6")
    print("- new workflow/registry/Render mutations: no/no/no")
    print("- frontend static deploy: blocked until new image verification and separate approval")
    print(f"- result: {RESULT}")
    print(f"- next safe stage: {NEXT_STAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

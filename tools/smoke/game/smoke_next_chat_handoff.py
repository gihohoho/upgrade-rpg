#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERSION = "v328.alpine-musllinux-runtime-minimization-preparation"
STATIC_PLAN_VERSION = VERSION
READY_RESULT = "github-actions-ghcr-owner-only-runtime-minimization-preparation-ready-publish-gated"
NEXT_SAFE_STAGE = "review-and-approve-exact-runtime-minimization-preparation-sha"
REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
PREPARATION = "b35dfacf427162b348a6bd29eb030778edc7741c"
AUTHORIZATION = "04e002060e576f19f4d8687b33635a414486206d"
CLOSURE = "64e5ae0f5e5385ba00df16bb10ac33789ca3760a"
RECORD = "303a2ed01c69c29894efdcde4ead6c2291c3d8bc"
RUN_ID = 29883012957
ARTIFACT_ID = 8515504259
REVISION_SHA256 = "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa"


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"missing file: {relative}")
    return path.read_text(encoding="utf-8")


def contains(relative: str, *markers: str) -> None:
    text = read(relative)
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{relative} missing marker: {marker}")


def main() -> int:
    assert read("NEXT_CHAT_PROMPT.md") == read("docs/handoff/NEXT_CHAT_PROMPT.md")
    assert read("NEXT_CHAT_HANDOFF.md") == read("docs/handoff/NEXT_CHAT_HANDOFF.md")

    for relative in (
        "AGENTS.md",
        "NEXT_CHAT_PROMPT.md",
        "NEXT_CHAT_HANDOFF.md",
        "docs/current/CURRENT_STATUS.md",
    ):
        contains(relative, VERSION, REMOTE, REPOSITORY)

    contains(
        "NEXT_CHAT_PROMPT.md",
        READY_RESULT,
        NEXT_SAFE_STAGE,
        "source-controlled lifecycle gate",
        "run_attempt=1",
        "single dispatch",
        "immediate closure",
        "closureCommitSha",
        "attempt-recorded",
        "review-recorded-workflow-attempt-evidence",
        PREPARATION,
        str(RUN_ID),
        str(ARTIFACT_ID),
    )
    contains(
        "NEXT_CHAT_HANDOFF.md",
        READY_RESULT,
        NEXT_SAFE_STAGE,
        "GITHUB_TOKEN",
        "required reviewer",
        "Trivy",
        PREPARATION,
        AUTHORIZATION,
        CLOSURE,
        RECORD,
        str(RUN_ID),
        str(ARTIFACT_ID),
    )

    policy = json.loads(read("deploy/backend-image-ghcr-policy.example.json"))
    assert policy["schemaVersion"] == VERSION
    assert policy["preparedOnly"] is True
    assert policy["ownerOnlyApprovalPhase"] == "preparation-awaiting-exact-sha-approval"
    assert policy["publishLifecycleState"] == "preparation-closed"
    assert policy["approvedPreparationSha"] is None
    assert policy["exactPreparationShaApproved"] is False
    assert policy["sourceControlledPublishGateReady"] is False
    assert policy["actualRegistryMutationExecuted"] is False
    assert policy["currentAttemptEvidence"] == {
        "authorizationSha": AUTHORIZATION,
        "closureSha": CLOSURE,
        "recordCommitSha": RECORD,
        "runId": RUN_ID,
        "runUrl": f"https://github.com/gihohoho/upgrade-rpg/actions/runs/{RUN_ID}",
        "conclusion": "failure",
        "registryLoginExecuted": False,
        "imageBuildExecuted": True,
        "imagePushExecuted": False,
        "artifactCount": 1,
        "artifactId": ARTIFACT_ID,
        "imageDigest": None,
        "signatureVerified": False,
    }

    lifecycle = json.loads(read("deploy/github-actions-ghcr-publish-lifecycle.json"))
    assert lifecycle["schemaVersion"] == "v326.owner-only-publish-lifecycle-with-attempt-history"
    assert lifecycle["state"] == "preparation-closed"
    assert lifecycle["publishReviewerGateReady"] is False
    assert lifecycle["approvedPreparationSha"] is None
    assert lifecycle["ownerApproval"]["recorded"] is False
    assert lifecycle["closure"]["authorizationSourceSha"] is None
    assert lifecycle["closure"]["closureCommitSha"] is None
    assert lifecycle["observedAttempt"]["runId"] is None
    assert lifecycle["observedAttempt"]["status"] == "not-dispatched"
    assert lifecycle["observedAttempt"]["conclusion"] is None
    assert lifecycle["observedAttempt"]["imageDigest"] is None
    assert lifecycle["observedAttempt"]["signatureVerified"] is False

    static_plan = json.loads(read("deploy/github-actions-ghcr-static-plan.example.json"))
    assert static_plan["schemaVersion"] == STATIC_PLAN_VERSION
    assert static_plan["supplyChainGates"]["vulnerabilityGate"]["ignoreUnfixed"] is False
    assert static_plan["ownerOnlyApprovalPolicy"]["runAttemptMustEqual"] == 1
    assert static_plan["ownerOnlyApprovalPolicy"]["singleDispatchApiCheckRequired"] is True

    workflow = read(".github/workflows/publish-backend-ghcr.yml")
    for marker in (
        "workflow_dispatch:",
        "--severity HIGH,CRITICAL",
        "--ignore-unfixed=false",
        "cosign sign --yes",
        "cosign verify",
        'DOCKER_BUILD_RECORD_UPLOAD: "false"',
    ):
        if marker not in workflow:
            raise AssertionError(f"workflow missing fail-closed marker: {marker}")

    security = read("docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md")
    if "실제 secret 값은 적지 않습니다" not in security or "required reviewer" not in security:
        raise AssertionError("security handoff rules are incomplete")

    revision = ROOT / "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py"
    if hashlib.sha256(revision.read_bytes()).hexdigest() != REVISION_SHA256:
        raise AssertionError("reviewed Alembic revision SHA-256 differs")

    print("OK: v328 Codex handoff and Alpine runtime preparation documents are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

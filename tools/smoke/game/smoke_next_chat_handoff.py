#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERSION = "v330.slsa-v1-provenance-path-preparation"
STATIC_PLAN_VERSION = VERSION
READY_RESULT = "github-actions-ghcr-owner-only-provenance-path-preparation-ready-publish-gated"
NEXT_SAFE_STAGE = "review-and-approve-exact-provenance-path-preparation-sha"
REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
PREPARATION = "13b15409929d77b4e6209481596e4f4550a22ba5"
AUTHORIZATION = "4fb31f51ca0de15d77a73390b5a07e394ffce12a"
CLOSURE = "ddf475c1a2449feb50ef2af1a536e4150cf0ad59"
RECORD = "f945214f2387b6aa191655d3740e18ef862bd6fb"
RUN_ID = 29886540317
ARTIFACT_IDS = [8516735247, 8516749365]
IMAGE_DIGEST = "sha256:6e4aefad0cdf1767670b7f736477dd9e00f17bf49a03fa471828df6667c41149"
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
        *(str(value) for value in ARTIFACT_IDS),
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
        *(str(value) for value in ARTIFACT_IDS),
    )

    policy = json.loads(read("deploy/backend-image-ghcr-policy.example.json"))
    assert policy["schemaVersion"] == VERSION
    assert policy["preparedOnly"] is True
    assert policy["ownerOnlyApprovalPhase"] == "preparation-awaiting-exact-sha-approval"
    assert policy["publishLifecycleState"] == "preparation-closed"
    assert policy["approvedPreparationSha"] is None
    assert policy["exactPreparationShaApproved"] is False
    assert policy["sourceControlledPublishGateReady"] is False
    assert policy["actualRegistryMutationExecuted"] is True
    assert policy["currentAttemptEvidence"] == {
        "authorizationSha": AUTHORIZATION,
        "closureSha": CLOSURE,
        "recordCommitSha": RECORD,
        "runId": RUN_ID,
        "runUrl": f"https://github.com/gihohoho/upgrade-rpg/actions/runs/{RUN_ID}",
        "conclusion": "failure",
        "registryLoginExecuted": True,
        "imageBuildExecuted": True,
        "imagePushExecuted": True,
        "artifactCount": 2,
        "artifactIds": ARTIFACT_IDS,
        "imageDigest": IMAGE_DIGEST,
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
        'build_definition = slsa.get("buildDefinition")',
        'if not build_definition.get("buildType"):',
    ):
        if marker not in workflow:
            raise AssertionError(f"workflow missing fail-closed marker: {marker}")

    security = read("docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md")
    if "실제 secret 값은 적지 않습니다" not in security or "required reviewer" not in security:
        raise AssertionError("security handoff rules are incomplete")

    revision = ROOT / "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py"
    if hashlib.sha256(revision.read_bytes()).hexdigest() != REVISION_SHA256:
        raise AssertionError("reviewed Alembic revision SHA-256 differs")

    print("OK: v330 Codex handoff and SLSA v1 provenance-path preparation documents are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

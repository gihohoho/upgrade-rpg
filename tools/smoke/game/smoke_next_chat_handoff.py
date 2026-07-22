#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERSION = "v332.verified-digest-production-reference-static-prepared"
STATIC_PLAN_VERSION = "v330.slsa-v1-provenance-path-preparation"
READY_RESULT = "verified-digest-production-reference-static-prepared-runtime-blocked"
NEXT_SAFE_STAGE = "review-production-reference-and-approve-isolated-pull-validation"
REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
PREPARATION = "36e8720a53ef7ff6a8334de6bc99646998d63fc9"
AUTHORIZATION = "26a11356e33c978afa8cd8a4881500fa62cdbc5c"
CLOSURE = "1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5"
RECORD = "1f0340ddfcf3c8a74cf14110d5957627d4c5d38a"
RUN_ID = 29909291344
ARTIFACT_IDS = [8525220616, 8525254543]
IMAGE_DIGEST = "sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2"
PRODUCTION_REFERENCE = f"{REPOSITORY}@{IMAGE_DIGEST}"
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
    assert policy["preparedOnly"] is False
    assert policy["ownerOnlyApprovalPhase"] == "verified-production-reference-static-prepared"
    assert policy["publishLifecycleState"] == "attempt-recorded"
    assert policy["approvedPreparationSha"] == PREPARATION
    assert policy["exactPreparationShaApproved"] is True
    assert policy["sourceControlledPublishGateReady"] is False
    assert policy["actualRegistryMutationExecuted"] is True
    assert policy["productionReference"] == PRODUCTION_REFERENCE
    assert policy["productionReferenceStaticPrepared"] is True
    assert policy["productionReferenceAppliedToRuntime"] is False
    assert policy["currentAttemptEvidence"] == {
        "authorizationSha": AUTHORIZATION,
        "closureSha": CLOSURE,
        "recordCommitSha": RECORD,
        "runId": RUN_ID,
        "runUrl": f"https://github.com/gihohoho/upgrade-rpg/actions/runs/{RUN_ID}",
        "conclusion": "success",
        "registryLoginExecuted": True,
        "imageBuildExecuted": True,
        "imagePushExecuted": True,
        "artifactCount": 2,
        "artifactIds": ARTIFACT_IDS,
        "imageDigest": IMAGE_DIGEST,
        "signatureVerified": True,
    }

    lifecycle = json.loads(read("deploy/github-actions-ghcr-publish-lifecycle.json"))
    assert lifecycle["schemaVersion"] == "v326.owner-only-publish-lifecycle-with-attempt-history"
    assert lifecycle["state"] == "attempt-recorded"
    assert lifecycle["publishReviewerGateReady"] is False
    assert lifecycle["approvedPreparationSha"] == PREPARATION
    assert lifecycle["ownerApproval"]["recorded"] is True
    assert lifecycle["closure"]["authorizationSourceSha"] == AUTHORIZATION
    assert lifecycle["closure"]["closureCommitSha"] == CLOSURE
    assert lifecycle["observedAttempt"]["runId"] == RUN_ID
    assert lifecycle["observedAttempt"]["status"] == "completed"
    assert lifecycle["observedAttempt"]["conclusion"] == "success"
    assert lifecycle["observedAttempt"]["imageDigest"] == IMAGE_DIGEST
    assert lifecycle["observedAttempt"]["signatureVerified"] is True

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

    print("OK: v332 production reference and handoff documents are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

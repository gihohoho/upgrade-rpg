#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERSION = "v334.production-deploy-plan-reviewed-inputs-blocked"
STATIC_PLAN_VERSION = "v330.slsa-v1-provenance-path-preparation"
READY_RESULT = "production-deploy-plan-reviewed-inputs-blocked"
NEXT_SAFE_STAGE = "select-production-targets-and-complete-executable-deploy-plan"
REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
PREPARATION = "fb231afa5081f5bfd7b459081a58bc5acd6699df"
APPROVED_PREPARATION = "b48dfd0751b12b1b3afb6474f9d35359ba2f8177"
AUTHORIZATION = "7578eb665c03ee0fcb9399929328ce684cdd1b31"
CLOSURE = "5d547126322dbe3c235e855cc9c2f7337342ae36"
RECORD = "5c842deec6d1f496679a144897f485b07428810b"
RUN_ID = 30226905547
ARTIFACT_IDS = [8638838292, 8638825538]
IMAGE_DIGEST = "sha256:143be5eb21ec8c9318c7d0c4f3fbd5ac2de32439977a1d660c7247b6d3a507ac"
VERIFIED_CANDIDATE_REFERENCE = f"{REPOSITORY}@{IMAGE_DIGEST}"
PRODUCTION_REFERENCE = f"{REPOSITORY}@sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1"
CURRENT_VERSION = "v369.starter-skill-book-and-weapon-master-skill-icons-applied"
CURRENT_RESULT = "starter-skill-book-and-weapon-master-skill-icons-applied"
CURRENT_NEXT_STAGE = "owner-review-v369-local-icons-and-select-next-character-step"
PRIOR_PROVIDER_VERSION = "v355.v351-provider-release-deployed-verified-content-ready"
PRIOR_PROVIDER_RESULT = "v351-provider-release-deployed-verified-content-ready"
PRIOR_PROVIDER_NEXT_STAGE = "select-first-content-and-balance-change-scope"
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
        contains(
            relative,
            VERSION,
            CURRENT_VERSION,
            CURRENT_RESULT,
            CURRENT_NEXT_STAGE,
            PRIOR_PROVIDER_VERSION,
            PRIOR_PROVIDER_RESULT,
            PRIOR_PROVIDER_NEXT_STAGE,
            REMOTE,
            REPOSITORY,
        )

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
        "Neon restore",
        "deploy/review/isolated-image-pull-validation-v353.json",
        "deploy/production-deploy-plan.example.json",
        APPROVED_PREPARATION,
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
        APPROVED_PREPARATION,
        AUTHORIZATION,
        CLOSURE,
        RECORD,
        str(RUN_ID),
        *(str(value) for value in ARTIFACT_IDS),
    )
    contains(
        "AGENTS.md",
        "시각 위계",
        "반응형 동작",
        "브라우저 기본 `alert`/`confirm`",
        "결과와 반환 수량",
        "고정 설명",
        "source/generated seed",
        "src/assets/**/*.png",
        "던전앤파이터풍",
        "일부가 잘리는 close-up 구도",
        "실제 브라우저 슬롯 크기",
        "기본 등급은 효과 없는 흰색 테두리",
        "등급별 CSS 테두리",
        "승급 표식",
        "복잡한 세공",
        "`위로 정렬` 버튼",
        "단계마다 별도 PNG",
        "더 긴 상위 이름 안에 기본 장비 이름 전체",
    )
    for relative in ("NEXT_CHAT_PROMPT.md", "NEXT_CHAT_HANDOFF.md", "docs/current/CURRENT_STATUS.md"):
        contains(
            relative,
            "[무기 아바타]",
            "[오라 아바타]",
            "[클론 레어 아바타]",
            "2^강화단계",
            "33개",
            "표시 상승량 100%",
            "성공 확률 50%",
            "23개",
            "SPECIAL_EQUIPMENT_AI_ICON_ASSETS.md",
            "src/assets/**/*.png",
            "테두리 없음",
            "여백 없이",
            "?v=361",
            "흰색 테두리",
            "↑ 위로 정렬",
            "첫 빈 칸",
            "?v=368",
            "NORMAL_EQUIPMENT_AI_ICON_ASSETS.md",
            "195개",
            "tier + equipGroup",
        )

    frontend_plan = json.loads(read("deploy/render-static-site.example.json"))
    assert frontend_plan["source"]["publishedSourceAllowlist"] == [
        "index.html",
        "admin.html",
        "src/**/*.js",
        "src/**/*.css",
        "src/assets/**/*.png",
    ]

    policy = json.loads(read("deploy/backend-image-ghcr-policy.example.json"))
    assert policy["schemaVersion"] == VERSION
    assert policy["preparedOnly"] is False
    assert (
        policy["ownerOnlyApprovalPhase"]
        == "v355-v351-provider-release-deployed-verified-content-ready"
    )
    assert policy["publishLifecycleState"] == "attempt-recorded"
    assert policy["approvedPreparationSha"] == APPROVED_PREPARATION
    assert policy["exactPreparationShaApproved"] is True
    assert policy["sourceControlledPublishGateReady"] is False
    assert policy["actualRegistryMutationExecuted"] is True
    assert policy["productionReference"] == PRODUCTION_REFERENCE
    assert policy["verifiedCandidateReference"] == VERIFIED_CANDIDATE_REFERENCE
    assert policy["verifiedCandidateAppliedToRender"] is True
    assert policy["productionReferenceStaticPrepared"] is True
    assert policy["productionReferenceAppliedToRuntime"] is False
    assert policy["localCredentialStrategy"] == "github-cli-oauth-read-packages"
    assert policy["isolatedImagePullExecuted"] is True
    assert policy["isolatedContainerExecutionExecuted"] is True
    assert policy["isolatedCleanupExecuted"] is True
    assert policy["productionDeploymentPlanReviewed"] is True
    assert policy["productionDeploymentApprovalReady"] is False
    assert policy["productionDeploymentApproved"] is False
    assert policy["productionDeploymentExecuted"] is False
    assert policy["renderPublicPreviewDeploymentApprovalReady"] is True
    assert policy["renderPublicPreviewDeploymentApproved"] is True
    assert policy["renderPublicPreviewDeploymentExecuted"] is True
    assert (
        policy["renderPublicPreviewDeploymentEvidence"]
        == "deploy/review/render-service-initial-deploy-v347.json"
    )
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
    assert lifecycle["schemaVersion"] == "v352.owner-only-publish-lifecycle-with-six-attempt-history"
    assert lifecycle["state"] == "attempt-recorded"
    assert lifecycle["publishReviewerGateReady"] is False
    assert lifecycle["approvedPreparationSha"] == APPROVED_PREPARATION
    assert lifecycle["ownerApproval"]["recorded"] is True
    assert lifecycle["closure"]["authorizationSourceSha"] == AUTHORIZATION
    assert lifecycle["closure"]["closureCommitSha"] == CLOSURE
    assert lifecycle["observedAttempt"]["runId"] == RUN_ID
    assert lifecycle["observedAttempt"]["status"] == "completed"
    assert lifecycle["observedAttempt"]["conclusion"] == "success"
    assert lifecycle["observedAttempt"]["imageDigest"] == IMAGE_DIGEST
    assert lifecycle["observedAttempt"]["signatureVerified"] is True
    assert lifecycle["attemptHistory"][-1]["preparationSha"] == PREPARATION
    assert lifecycle["attemptHistory"][-1]["runId"] == 30180738530
    assert lifecycle["attemptHistory"][-1]["imageDigest"] == "sha256:f3bf6eed45e46e9d2022df4ab62eb6ca55b1ec0997b8ed342ae250c4a60052c1"
    assert lifecycle["attemptHistory"][-1]["signatureVerified"] is True

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

    evidence = json.loads(read("deploy/review/isolated-image-pull-validation-v353.json"))
    assert evidence["imageReference"] == VERIFIED_CANDIDATE_REFERENCE
    assert evidence["runtimeValidation"]["healthOk"] is True
    assert evidence["cleanup"]["containerRemoved"] is True
    assert evidence["cleanup"]["internalNetworkRemoved"] is True
    assert evidence["cleanup"]["localImageRemoved"] is True
    assert evidence["renderBackendDeployExecuted"] is False
    assert evidence["renderStaticDeployExecuted"] is False

    plan = json.loads(read("deploy/production-deploy-plan.example.json"))
    assert plan["schemaVersion"] == VERSION
    assert plan["planReview"]["completed"] is True
    assert plan["approvalContract"]["approvalReady"] is False
    assert plan["approvalContract"]["productionDeploymentExecuted"] is False
    assert plan["nextSafeStage"] == NEXT_SAFE_STAGE

    print("OK: current deployment checkpoints and handoff documents are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

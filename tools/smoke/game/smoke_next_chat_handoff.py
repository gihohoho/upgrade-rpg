#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERSION = "v320.github-actions-ghcr-workflow-prepared-gated"
READY_RESULT = "github-actions-ghcr-workflow-prepared-publish-gated"
NEXT_SAFE_STAGE = "choose-private-repository-publish-approval-model"
REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
REVISION_SHA256 = "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa"
TRIVY_SHA256 = "8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9"


def read(relative: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        raise AssertionError(f"missing file: {relative}")
    return path.read_text(encoding="utf-8")


def assert_contains(relative: str, *markers: str) -> None:
    text = read(relative)
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{relative} missing marker: {marker}")


def assert_not_contains(relative: str, *markers: str) -> None:
    text = read(relative)
    for marker in markers:
        if marker in text:
            raise AssertionError(f"{relative} contains forbidden marker: {marker}")


def assert_same(left: str, right: str) -> None:
    if read(left) != read(right):
        raise AssertionError(f"handoff mirror differs: {left} != {right}")


def main() -> int:
    required = (
        ".github/workflows/publish-backend-ghcr.yml",
        "AGENTS.md",
        "README.md",
        "README_BACKEND_READY.md",
        "NEXT_CHAT_PROMPT.md",
        "NEXT_CHAT_HANDOFF.md",
        "docs/README.md",
        "docs/NEXT_CHAT_START_GUIDE.md",
        "docs/NEXT_STEPS.md",
        "docs/current/README.md",
        "docs/current/CURRENT_STATUS.md",
        "docs/current/PROJECT_STRUCTURE.md",
        "docs/current/ROADMAP.md",
        "docs/current/BACKEND_IMAGE_GHCR_POLICY.md",
        "docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md",
        "docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md",
        "docs/handoff/NEXT_CHAT_PROMPT.md",
        "docs/handoff/NEXT_CHAT_HANDOFF.md",
        "deploy/backend-image-ghcr-policy.example.json",
        "deploy/github-actions-ghcr-static-plan.example.json",
        "tools/check_codex_handoff_readiness.py",
        "tools/check_github_actions_ghcr_static_plan.py",
        "tools/smoke/backend/smoke_codex_handoff_readiness.py",
        "tools/smoke/backend/smoke_github_actions_ghcr_static_plan.py",
    )
    for relative in required:
        read(relative)

    assert_same("NEXT_CHAT_PROMPT.md", "docs/handoff/NEXT_CHAT_PROMPT.md")
    assert_same("NEXT_CHAT_HANDOFF.md", "docs/handoff/NEXT_CHAT_HANDOFF.md")

    assert_contains(
        "AGENTS.md",
        VERSION,
        REMOTE,
        REPOSITORY,
        "github-actions-github-token",
        "실행 중인 개발 서버를 재사용",
        "숨김 파일과 `.env`",
        "PUBLISH_REVIEWER_GATE_READY",
        "check_github_actions_ghcr_static_plan.py --strict",
        "git commit",
        "Git 한 줄 명령을 다시 제공하지 않습니다",
    )
    assert_contains(
        "NEXT_CHAT_PROMPT.md",
        VERSION,
        REMOTE,
        REPOSITORY,
        "`gihohoho`는 기호가 직접 확인한 고정 namespace",
        READY_RESULT,
        NEXT_SAFE_STAGE,
        "ZIP을 기준으로 작업하지 않습니다",
        "Codex가 프로젝트 루트에서 직접",
        "필요한 extension, 권한, 설치",
        "source-controlled `PUBLISH_REVIEWER_GATE_READY`",
    )
    assert_contains(
        "NEXT_CHAT_HANDOFF.md",
        VERSION,
        "source rpg_game: public 23/749, application 22/748",
        "revision SHA-256: " + REVISION_SHA256,
        REPOSITORY,
        "workflow file/creation approved: yes/yes",
        "workflow execution approved/executed: yes/no",
        "CI login/build/push executed: no/no/no",
        "handoff mode: current repository + Git `main` (ZIP 없음)",
        "GitHub App 연결과 repository 읽기 권한은 해결됨",
        "source-controlled false",
    )
    assert_contains(
        "deploy/backend-image-ghcr-policy.example.json",
        '"schemaVersion": "' + VERSION + '"',
        '"githubRemote": "' + REMOTE + '"',
        '"namespace": "gihohoho"',
        '"repositoryIdentity": "' + REPOSITORY + '"',
        '"ciCredentialStrategy": "github-actions-github-token"',
        '"githubActionsWorkflowPresent": true',
        '"githubActionsWorkflowCreationApproved": true',
        '"githubActionsWorkflowExecutionApproved": true',
        '"githubActionsWorkflowExecutionExecuted": false',
        '"actionShasApproved": true',
        '"repositoryActionsSettingsMutationExecuted": true',
        '"publishEnvironmentCreated": true',
        '"publishEnvironmentMainOnly": true',
        '"publishEnvironmentRequiredReviewerConfigured": false',
        '"sourceControlledPublishGateReady": false',
        '"ciImagePushApproved": true',
        '"actualRegistryMutationExecuted": false',
    )
    assert_contains(
        "deploy/github-actions-ghcr-static-plan.example.json",
        '"schemaVersion": "' + VERSION + '"',
        '"workflowFilePresent": true',
        '"workflowCreationApproved": true',
        '"workflowExecutionApproved": true',
        '"workflowExecutionExecuted": false',
        '"publishExecutionAllowedNow": false',
        '"allowedEvents"',
        '"workflow_dispatch"',
        '"contents": "read"',
        '"packages": "write"',
        '"id-token": "write"',
        '"githubArtifactAttestationsPermission": "not-requested"',
        '"resolvedActionShasApproved": true',
        '"repositoryAllowlistConfigured": true',
        '"sourceControlledGateValue": false',
        '"sourceControlledPublishGateReady": false',
        TRIVY_SHA256,
        '"registryMutationExecuted": false',
        '"nextSafeStage": "' + NEXT_SAFE_STAGE + '"',
    )
    assert_not_contains(
        "deploy/github-actions-ghcr-static-plan.example.json",
        '"repository": "aquasecurity/trivy-action"',
        '"attestations": "write"',
    )
    assert_contains(
        ".github/workflows/publish-backend-ghcr.yml",
        "workflow_dispatch:",
        "permissions:\n  contents: read",
        "context: .",
        "file: backend/Dockerfile.production",
        "PUBLISH_REVIEWER_GATE_READY: \"false\"",
        "--severity HIGH,CRITICAL",
        "--ignore-unfixed=false",
        TRIVY_SHA256,
        "unverified-sha-${{ github.sha }}",
        "published-trivy-results.json",
        "provenance: mode=max",
        "sbom: true",
        "cosign sign --yes",
        "cosign verify",
    )
    assert_not_contains(
        ".github/workflows/publish-backend-ghcr.yml",
        "pull_request_target:",
        "aquasecurity/trivy-action",
        "actions/attest",
        "attestations: write",
        "vars.PUBLISH_REVIEWER_GATE_READY",
        ":latest",
    )
    assert_contains(
        "docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md",
        "실제 secret 값은 이 문서에 적지 않습니다",
        "required reviewer",
        "source-controlled gate",
        "Trivy `0.70.0`",
        "로컬 `gh` CLI",
    )
    assert_contains(
        "deploy/production.env.example",
        REPOSITORY + "@sha256:<approved-64-hex-digest>",
        "sslmode=verify-full",
        "sslrootcert=/run/secrets/postgres_ca.pem",
    )
    assert_contains(
        "tools/run_smoke_core.sh",
        "smoke_codex_handoff_readiness.py",
        "smoke_github_actions_ghcr_static_plan.py",
        "smoke_next_chat_handoff.py",
        "smoke_docs_index_archive.js",
    )
    assert_contains(
        ".gitignore",
        "/local-backups/",
        "/local-review-artifacts/",
        "/deploy/production.env",
        "/deploy/secrets/*",
    )

    for removed in (
        "docs/CURRENT_STATUS.md",
        "docs/PROJECT_STRUCTURE.md",
        "docs/current/BACKEND_IMAGE_SOURCE_DIGEST_POLICY.md",
        "docs/current/BACKEND_IMAGE_REGISTRY_BASE_SELECTION.md",
        "deploy/backend-image-source-digest-policy.example.json",
        "deploy/backend-image-registry-base-selection.example.json",
        "tools/check_backend_image_source_digest_policy.py",
        "tools/check_backend_image_registry_base_selection.py",
    ):
        if (ROOT / removed).exists():
            raise AssertionError(f"superseded duplicate remains: {removed}")

    revision = ROOT / "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py"
    actual_sha = hashlib.sha256(revision.read_bytes()).hexdigest()
    if actual_sha != REVISION_SHA256:
        raise AssertionError(f"reviewed revision SHA-256 differs: {actual_sha}")

    print("OK: v320 Codex handoff and document structure are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

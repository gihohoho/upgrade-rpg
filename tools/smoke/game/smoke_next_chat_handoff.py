#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERSION = "v319.github-connector-actions-settings-reviewed"
READY_RESULT = "github-connector-actions-settings-verified-workflow-not-created"
NEXT_SAFE_STAGE = "request-repository-actions-supply-chain-settings-change-approval"
REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
REVISION_SHA256 = "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa"


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


def assert_same(left: str, right: str) -> None:
    if read(left) != read(right):
        raise AssertionError(f"handoff mirror differs: {left} != {right}")


def main() -> int:
    required = (
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
        "check_github_actions_ghcr_static_plan.py --strict",
        "git commit",
        "Git 한 줄 명령을 다시 제공하지 않습니다",
    )
    assert_contains(
        "NEXT_CHAT_PROMPT.md",
        VERSION,
        REMOTE,
        REPOSITORY,
        "gihohoho`는 기호가 직접 확인한 고정 namespace",
        READY_RESULT,
        NEXT_SAFE_STAGE,
        "ZIP을 기준으로 작업하지 않습니다",
        "Codex가 프로젝트 루트에서 직접",
        "`upgrade-rpg` 저장소 하나만 허용",
    )
    assert_contains(
        "NEXT_CHAT_HANDOFF.md",
        VERSION,
        "source rpg_game: public 23/749, application 22/748",
        "revision SHA-256: " + REVISION_SHA256,
        REPOSITORY,
        "workflow/login/pull/build/push approved: no/no/no/no/no",
        "handoff mode: current repository + Git `main` (ZIP 없음)",
        "GitHub App 연결과 repository 읽기 권한은 해결됨",
    )
    assert_contains(
        "deploy/backend-image-ghcr-policy.example.json",
        '"schemaVersion": "' + VERSION + '"',
        '"githubRemote": "' + REMOTE + '"',
        '"namespace": "gihohoho"',
        '"namespaceResolved": true',
        '"repositoryIdentity": "' + REPOSITORY + '"',
        '"ciCredentialStrategy": "github-actions-github-token"',
        '"githubActionsWorkflowCreationApproved": false',
        '"githubActionsStaticPlanPresent": true',
        '"githubActionsStaticPlanVerified": true',
        '"actionShasResolved": true',
        '"actionShasApproved": false',
        '"githubConnectorRepositoryAccess": true',
        '"githubConnectorSelectedRepositoryOnly": true',
        '"repositoryActionsSettingsReviewed": true',
        '"repositoryActionsSettingsMutationApproved": false',
        '"publishEnvironmentReviewed": true',
        '"publishEnvironmentCreationApproved": false',
        '"imageBuildApproved": false',
    )
    assert_contains(
        "deploy/github-actions-ghcr-static-plan.example.json",
        '"schemaVersion": "' + VERSION + '"',
        '"allowedEvents"',
        '"workflow_dispatch"',
        '"contents": "read"',
        '"packages": "write"',
        '"attestations": "write"',
        '"id-token": "write"',
        '"resolvedActionShaCandidatesReviewed": true',
        '"resolvedActionShasApproved": false',
        '"githubConnectorRepositoryAccess": true',
        '"actionsSettingsReviewed": true',
        '"publishEnvironmentReviewed": true',
        '"publishEnvironmentConfigured": false',
        '"workflowCreationApproved": false',
        '"nextSafeStage": "' + NEXT_SAFE_STAGE + '"',
    )
    assert_contains(
        "deploy/production.env.example",
        REPOSITORY + "@sha256:<approved-64-hex-digest>",
        "sslmode=verify-full",
        "sslrootcert=/run/secrets/postgres_ca.pem",
    )
    assert_contains(
        "docs/current/BACKEND_IMAGE_GHCR_POLICY.md",
        REMOTE,
        REPOSITORY,
        "GITHUB_TOKEN",
        "workflow creation approved: no",
        "static workflow plan present/verified: yes/yes",
        "action SHAs approved: no",
    )
    assert_contains(
        "docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md",
        VERSION,
        "workflow_dispatch",
        "pull_request_target",
        "contents: read",
        "packages: write",
        "attestations: write",
        "id-token: write",
        "HIGH,CRITICAL",
        "Sigstore keyless OIDC",
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

    print("OK: v319 Codex handoff and document structure are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

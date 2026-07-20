#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VERSION = "v322.owner-only-single-run-lifecycle-hardened-publish-gated"
READY_RESULT = "github-actions-ghcr-owner-only-single-run-lifecycle-ready-publish-gated"
NEXT_SAFE_STAGE = "review-and-approve-exact-preparation-fix-sha"
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


def assert_exact_transient_handoff_smoke_skip_scope() -> None:
    script = read("tools/run_smoke_core.sh")
    opener = 'if [[ "${SKIP_GHCR_HANDOFF_SMOKES:-0}" != "1" ]]; then'
    if script.count("SKIP_GHCR_HANDOFF_SMOKES") != 1:
        raise AssertionError("SKIP_GHCR_HANDOFF_SMOKES must have exactly one guarded scope")
    lines = [line.strip() for line in script.splitlines()]
    try:
        start = lines.index(opener)
        end = lines.index("fi", start + 1)
    except ValueError as exc:
        raise AssertionError("closed-root handoff smoke skip guard is incomplete") from exc
    guarded = lines[start + 1:end]
    expected = [
        "python tools/smoke/backend/smoke_github_actions_ghcr_static_plan.py",
        "python tools/smoke/backend/smoke_codex_handoff_readiness.py",
        "python tools/smoke/game/smoke_next_chat_handoff.py",
    ]
    if guarded != expected:
        raise AssertionError(f"transient lifecycle skip scope must contain exactly three closed-root smokes: {guarded!r}")


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
        "deploy/github-actions-ghcr-publish-lifecycle.json",
        "tools/check_codex_handoff_readiness.py",
        "tools/check_github_actions_ghcr_static_plan.py",
        "tools/generate_backend_linux_dependency_locks.py",
        "backend/requirements/pip-bootstrap.lock",
        "backend/requirements/runtime-linux-amd64-py311.lock",
        "backend/requirements/dev-linux-amd64-py311.lock",
        "tools/smoke/backend/smoke_codex_handoff_readiness.py",
        "tools/smoke/backend/smoke_github_actions_ghcr_static_plan.py",
    )
    for relative in required:
        read(relative)

    assert_same("NEXT_CHAT_PROMPT.md", "docs/handoff/NEXT_CHAT_PROMPT.md")
    assert_same("NEXT_CHAT_HANDOFF.md", "docs/handoff/NEXT_CHAT_HANDOFF.md")
    assert_exact_transient_handoff_smoke_skip_scope()

    assert_contains(
        "AGENTS.md",
        VERSION,
        REMOTE,
        REPOSITORY,
        "github-actions-github-token",
        "실행 중인 개발 서버를 재사용",
        "숨김 파일과 `.env`",
        "deploy/github-actions-ghcr-publish-lifecycle.json",
        "source-controlled lifecycle gate",
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
        "ZIP은 기준으로 작업하지 않습니다",
        "Codex가 프로젝트 루트에서 직접",
        "필요한 extension, 권한, 설치",
        "deploy/github-actions-ghcr-publish-lifecycle.json",
        "source-controlled lifecycle gate",
        "run_attempt=1",
        "single dispatch",
        "immediate closure",
        "closureCommitSha",
        "attempt-recorded",
        "review-recorded-workflow-attempt-evidence",
    )
    assert_contains(
        "NEXT_CHAT_HANDOFF.md",
        VERSION,
        "source DB: rpg_game",
        "source public tables/rows: 23/749",
        "source application tables/rows: 22/748",
        "revision SHA-256: " + REVISION_SHA256,
        REPOSITORY,
        "workflow file/creation approved: yes/yes",
        "workflow execution approved/executed: yes/no",
        "CI login/build/push executed: no/no/no",
        "기준: 현재 repository + Git `main`; ZIP은 기본 생성하지 않음",
        "2026-07-20 GitHub live 재확인",
        "preparation-closed",
        "source-controlled lifecycle gate",
        "run_attempt=1",
        "single dispatch",
        "immediate closure",
        "closureCommitSha",
        "attempt-recorded",
        "review-recorded-workflow-attempt-evidence",
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
        '"ownerOnlyApprovalPhase": "preparation-closed"',
        '"publishLifecyclePath": "deploy/github-actions-ghcr-publish-lifecycle.json"',
        '"publishLifecycleState": "preparation-closed"',
        '"publishLifecycleSupportedStates"',
        '"attempt-recorded"',
        '"priorApprovedPreparationSha": "f4788acf5455b07169320bd29f43ddf92ff1d5ad"',
        '"priorExactPreparationShaApproved": true',
        '"dependencyAndFrontendInputsLocked": true',
        '"ciImagePushApproved": true',
        '"actualRegistryMutationExecuted": false',
    )
    assert_contains(
        "deploy/github-actions-ghcr-static-plan.example.json",
        '"schemaVersion": "' + VERSION + '"',
        '"staticPolicyOnly": true',
        '"workflowFilePresent": true',
        '"workflowCreationApproved": true',
        '"workflowExecutionApproved": true',
        '"workflowExecutionEvidenceTrackedInLifecycle": true',
        '"publishExecutionAuthorizationTrackedInLifecycle": true',
        '"publishLifecyclePath": "deploy/github-actions-ghcr-publish-lifecycle.json"',
        '"publishLifecycleSchemaVersion": "v322.owner-only-publish-lifecycle"',
        '"allowedLifecycleStates"',
        '"attempt-recorded"',
        '"allowedEvents"',
        '"workflow_dispatch"',
        '"contents": "read"',
        '"packages": "write"',
        '"id-token": "write"',
        '"githubArtifactAttestationsPermission": "not-requested"',
        '"resolvedActionShasApproved": true',
        '"repositoryAllowlistConfigured": true',
        '"runAttemptMustEqual": 1',
        '"repositoryOwnerActorRequired": true',
        '"singleDispatchApiCheckRequired": true',
        '"closureCommitImmediatelyAfterRunAccepted": true',
        '"sourceControlledGate": "deploy/github-actions-ghcr-publish-lifecycle.json#publishReviewerGateReady"',
        '"gateValueDerivedFromLifecycleState": true',
        '"gateChangeRequiresSinglePathCommit": true',
        '"publishApprovalModel": "owner-only-source-controlled-two-step"',
        '"status": "dependency-and-frontend-inputs-locked"',
        TRIVY_SHA256,
        '"registryMutationEvidenceTrackedInLifecycle": true',
        '"sourceControlledLifecyclePolicyReady": true',
        '"nextSafeStagePolicy": "follow-source-controlled-publish-lifecycle-state"',
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
        "approved_preparation_commit:",
        "PUBLISH_LIFECYCLE_PATH: deploy/github-actions-ghcr-publish-lifecycle.json",
        'require(os.environ["EXPECTED_RUN_ATTEMPT"] == "1", "workflow re-runs are forbidden")',
        "Require exactly one first-attempt dispatch for this authorization",
        'require(len(runs) <= 1, "more than one dispatch exists for this authorization commit")',
        'require(current.get("state") == "authorization-open", "publish lifecycle is not authorization-open")',
        "Enforce owner-only two-step authorization gate before registry access",
        "backend/requirements/dev-linux-amd64-py311.lock",
        "--require-hashes",
        "--severity HIGH,CRITICAL",
        "--ignore-unfixed=false",
        TRIVY_SHA256,
        "unverified-sha-${{ github.sha }}",
        "published-trivy-results.json",
        "provenance: mode=max",
        "sbom: true",
        "cosign sign --yes",
        "cosign verify",
        "python tools/check_github_actions_ghcr_static_plan.py --strict\n"
        "          python -m compileall -q backend/app backend/scripts backend/alembic tools\n"
        "          SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh",
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
        "deploy/github-actions-ghcr-publish-lifecycle.json",
        '"schemaVersion": "v322.owner-only-publish-lifecycle"',
        '"state": "preparation-closed"',
        '"publishReviewerGateReady": false',
        '"priorApprovedPreparationSha": "f4788acf5455b07169320bd29f43ddf92ff1d5ad"',
        '"approvedPreparationSha": null',
        '"closureCommitSha": null',
        '"recorded": false',
        '"workflowRunAttemptMustEqual": 1',
        '"singleDispatchApiCheckRequired": true',
        '"rerunForbidden": true',
        '"immediateClosureAfterRunAccepted": true',
        '"status": "not-dispatched"',
    )
    assert_contains(
        "docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md",
        "실제 secret 값은 적지 않습니다",
        "required reviewer",
        "source-controlled gate",
        "deploy/github-actions-ghcr-publish-lifecycle.json",
        "`run_attempt=1`; rerun 금지",
        "single dispatch",
        "immediate closure commit",
        "partial evidence는 성공 또는 배포 승인 증거가 아닙니다",
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

    print("OK: v322 Codex handoff and owner-only lifecycle documents are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

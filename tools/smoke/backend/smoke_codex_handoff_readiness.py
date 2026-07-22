#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_codex_handoff_readiness.py"
REQUIRED = (
    ".dockerignore",
    ".gitattributes",
    ".github/workflows/publish-backend-ghcr.yml",
    "AGENTS.md",
    "NEXT_CHAT_PROMPT.md",
    "NEXT_CHAT_HANDOFF.md",
    "README.md",
    "backend/Dockerfile",
    "backend/Dockerfile.production",
    "backend/pyproject.toml",
    "backend/requirements/pip-bootstrap.in",
    "backend/requirements/pip-bootstrap.lock",
    "backend/requirements/runtime.in",
    "backend/requirements/runtime-linux-amd64-py311.lock",
    "backend/requirements/dev.in",
    "backend/requirements/dev-linux-amd64-py311.lock",
    "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py",
    "deploy/backend-image-ghcr-policy.example.json",
    "deploy/github-actions-ghcr-publish-lifecycle.json",
    "deploy/docker-compose.production.yml",
    "deploy/production.env.example",
    "deploy/secrets/README.md",
    "docs/README.md",
    "docs/current/CURRENT_STATUS.md",
    "docs/current/BACKEND_IMAGE_GHCR_POLICY.md",
    "docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md",
    "docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md",
    "deploy/github-actions-ghcr-static-plan.example.json",
    "docs/handoff/NEXT_CHAT_PROMPT.md",
    "docs/handoff/NEXT_CHAT_HANDOFF.md",
    "tools/check_github_actions_ghcr_static_plan.py",
    "tools/generate_backend_linux_dependency_locks.py",
)


def load_tool():
    spec = importlib.util.spec_from_file_location("v326_codex_handoff", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v326 Codex handoff checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_fixture(temp: Path) -> None:
    for relative in REQUIRED:
        source = ROOT / relative
        target = temp / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def expect_blocked(module, temp: Path) -> None:
    try:
        module.inspect_codex_handoff(temp)
    except module.CodexHandoffError:
        return
    raise AssertionError("unsafe v326 Codex handoff fixture was not blocked")


def main() -> int:
    module = load_tool()
    result = module.inspect_codex_handoff(ROOT)
    assert result["result"] == module.READY_RESULT
    assert result["namespace"] == "gihohoho"
    assert result["repository"] == "ghcr.io/gihohoho/upgrade-rpg-backend"
    assert result["ciCredentialStrategy"] == "github-actions-github-token"
    assert result["localCredentialStrategy"] == "deferred"
    assert result["workflowCreationApproved"] is True
    assert result["workflowExecutionApproved"] is True
    assert result["workflowExecutionExecuted"] is True
    assert result["ciRegistryMutationApproved"] is True
    assert result["runtimeMutationExecuted"] is False
    assert result["packageSafetyMode"] in {"git-index", "filesystem-absence"}
    assert result["githubActionsStaticPlanVerified"] is True
    assert result["workflowFilePresent"] is True
    assert re.fullmatch(r"[0-9a-f]{64}", result["workflowSourceSha256"])
    assert re.fullmatch(r"[0-9a-f]{64}", result["workflowSemanticSha256"])
    assert result["actionShasApproved"] is True
    assert result["actionsSettingsConfigured"] is True
    assert result["publishEnvironmentExists"] is True
    assert result["publishEnvironmentConfigured"] is False
    assert result["publishGateReady"] is False
    assert result["publishLifecycleState"] == "preparation-closed"
    assert result["publishLifecycleSupportedStates"] == [
        "preparation-closed",
        "authorization-open",
        "authorization-closed-awaiting-evidence",
        "attempt-recorded",
    ]
    assert result["priorApprovedPreparationSha"] == "350bbd085f1cf636810d75ddcbb5321e0791256c"
    assert result["approvedPreparationSha"] is None
    assert result["ownerApprovalRecorded"] is False
    assert result["workflowRunAttemptMustEqual"] == 1
    assert result["singleDispatchApiCheckRequired"] is True
    assert result["rerunForbidden"] is True
    assert result["immediateClosureAfterRunAccepted"] is True
    assert result["dockerBuildContextEnvExcluded"] is True
    assert result["reproducibleBuildReady"] is True

    root_actions_result = module._inspect_actions_workflow(ROOT)
    module._inspect_actions_workflow = lambda _root: root_actions_result

    mutations = (
        ("namespace", "invented-account"),
        ("namespaceResolved", False),
        ("repositoryIdentity", "ghcr.io/other/upgrade-rpg-backend"),
        ("repositoryVisibility", "public"),
        ("targetPlatform", "linux/arm64"),
        ("ciCredentialStrategy", "committed-pat"),
        ("localCredentialStrategy", "plaintext-file"),
        ("githubPatCreated", True),
        ("githubActionsWorkflowPresent", False),
        ("githubActionsWorkflowCreationApproved", False),
        ("githubActionsWorkflowExecutionExecuted", False),
        ("actionShasApproved", False),
        ("githubConnectorRepositoryAccess", False),
        ("repositoryActionsSettingsMutationExecuted", False),
        ("publishEnvironmentCreated", False),
        ("publishEnvironmentRequiredReviewerConfigured", True),
        ("sourceControlledPublishGateReady", True),
        ("actualRegistryMutationExecuted", True),
        ("priorExactPreparationShaApproved", False),
        ("priorApprovedPreparationSha", "0" * 40),
        ("exactPreparationShaApproved", True),
        ("actualDockerCommandExecuted", False),
        ("ownerOnlyApprovalPhase", "authorization-open"),
        ("publishLifecycleState", "authorization-open"),
        ("publishLifecycleSupportedStates", ["preparation-closed"]),
    )
    for key, value in mutations:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            path = temp / "deploy/backend-image-ghcr-policy.example.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload[key] = value
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            expect_blocked(module, temp)

    lifecycle_mutations = (
        lambda p: p.update({"schemaVersion": "v321.unsafe"}),
        lambda p: p.update({"state": "authorization-open"}),
        lambda p: p.update({"publishReviewerGateReady": True}),
        lambda p: p.update({"priorApprovedPreparationSha": "0" * 40}),
        lambda p: p.update({"approvedPreparationSha": "f4788acf5455b07169320bd29f43ddf92ff1d5ad"}),
        lambda p: p["ownerApproval"].update({"recorded": True}),
        lambda p: p["ownerApproval"].update({"recordedAtUtc": "not-utc"}),
        lambda p: p["ownerApproval"].update({"evidence": "codex-self-approval"}),
        lambda p: p["authorizationPolicy"].update({"workflowRunAttemptMustEqual": 2}),
        lambda p: p["authorizationPolicy"].update({"authorizationCommitMustBeDirectChild": False}),
        lambda p: p["authorizationPolicy"].update({"singleDispatchApiCheckRequired": False}),
        lambda p: p["authorizationPolicy"].update({"rerunForbidden": False}),
        lambda p: p["authorizationPolicy"].update({"immediateClosureAfterRunAccepted": False}),
        lambda p: p["authorizationPolicy"]["authorizationChangedPaths"].append(".github/workflows/publish-backend-ghcr.yml"),
        lambda p: p["closure"].update({"closureCommitSha": "0" * 40}),
        lambda p: p["observedAttempt"].update({"runAttempt": 2}),
    )
    for mutation in lifecycle_mutations:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            path = temp / "deploy/github-actions-ghcr-publish-lifecycle.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            mutation(payload)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            expect_blocked(module, temp)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        copy_fixture(temp)
        workflow = temp / ".github/workflows/extra.yml"
        workflow.write_text("name: unexpected\n", encoding="utf-8")
        expect_blocked(module, temp)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        copy_fixture(temp)
        secret = temp / "deploy/secrets/token.txt"
        secret.write_text("not-a-real-token", encoding="utf-8")
        expect_blocked(module, temp)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        copy_fixture(temp)
        local_env = temp / "backend/.env"
        local_env.write_text("NOT_A_REAL_SECRET=fixture-only\n", encoding="utf-8")
        expect_blocked(module, temp)

    print("OK: v326 Codex/GHCR retry-preparation lifecycle handoff smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

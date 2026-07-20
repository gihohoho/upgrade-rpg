#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
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
    spec = importlib.util.spec_from_file_location("v321_codex_handoff", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v321 Codex handoff checker")
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
    raise AssertionError("unsafe v321 Codex handoff fixture was not blocked")


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
    assert result["workflowExecutionExecuted"] is False
    assert result["ciRegistryMutationApproved"] is True
    assert result["runtimeMutationExecuted"] is False
    assert result["packageSafetyMode"] in {"git-index", "filesystem-absence"}
    assert result["githubActionsStaticPlanVerified"] is True
    assert result["workflowFilePresent"] is True
    assert result["workflowSourceSha256"] == "9c3384f5f8d879320d41b04833a63842744e55c14cd12743c9aea0a3a74e8c5a"
    assert result["workflowSemanticSha256"] == "9a7af533b42854977897b26fe0aae364667f9be65a7d9dfab4c51a2bf1c31652"
    assert result["actionShasApproved"] is True
    assert result["actionsSettingsConfigured"] is True
    assert result["publishEnvironmentExists"] is True
    assert result["publishEnvironmentConfigured"] is False
    assert result["publishGateReady"] is False
    assert result["dockerBuildContextEnvExcluded"] is True
    assert result["reproducibleBuildReady"] is True

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
        ("githubActionsWorkflowExecutionExecuted", True),
        ("actionShasApproved", False),
        ("githubConnectorRepositoryAccess", False),
        ("repositoryActionsSettingsMutationExecuted", False),
        ("publishEnvironmentCreated", False),
        ("publishEnvironmentRequiredReviewerConfigured", True),
        ("sourceControlledPublishGateReady", True),
        ("actualRegistryMutationExecuted", True),
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

    print("OK: v321 Codex/GHCR owner-only reproducibility-locked handoff smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

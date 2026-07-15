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
    ".github/workflows/publish-backend-ghcr.yml",
    "AGENTS.md",
    "NEXT_CHAT_PROMPT.md",
    "NEXT_CHAT_HANDOFF.md",
    "README.md",
    "backend/Dockerfile",
    "backend/Dockerfile.production",
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
)


def load_tool():
    spec = importlib.util.spec_from_file_location("v320_codex_handoff", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v320 Codex handoff checker")
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
    raise AssertionError("unsafe v320 Codex handoff fixture was not blocked")


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
    assert result["workflowSourceSha256"] == "83393cb875cf43ce1bc30d245c100482818af96cd7b5417d81b9cb45ce62a993"
    assert result["workflowSemanticSha256"] == "2f1b1baf3f7db363f2f175b98623ec97e59a785592ae32d023f4b5123f2bd4c0"
    assert result["actionShasApproved"] is True
    assert result["actionsSettingsConfigured"] is True
    assert result["publishEnvironmentExists"] is True
    assert result["publishEnvironmentConfigured"] is False
    assert result["publishGateReady"] is False
    assert result["dockerBuildContextEnvExcluded"] is True
    assert result["reproducibleBuildReady"] is False

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

    print("OK: v320 Codex/GHCR prepared-and-gated handoff smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

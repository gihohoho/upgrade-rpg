#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_github_actions_ghcr_static_plan.py"
REQUIRED = (
    "deploy/github-actions-ghcr-static-plan.example.json",
    "docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md",
)


def load_tool():
    spec = importlib.util.spec_from_file_location("v319_github_actions_plan", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v319 GitHub Actions static plan checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_fixture(temp: Path) -> None:
    for relative in REQUIRED:
        source = ROOT / relative
        target = temp / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def mutate_plan(temp: Path, callback) -> None:
    path = temp / "deploy/github-actions-ghcr-static-plan.example.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    callback(payload)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def expect_blocked(module, temp: Path) -> None:
    try:
        module.inspect_static_workflow_plan(temp)
    except module.StaticWorkflowPlanError:
        return
    raise AssertionError("unsafe v319 GitHub Actions plan fixture was not blocked")


def main() -> int:
    module = load_tool()
    result = module.inspect_static_workflow_plan(ROOT)
    assert result["result"] == module.READY_RESULT
    assert result["trigger"] == "workflow_dispatch-only"
    assert result["workflowFilePresent"] is False
    assert result["actionShaCandidatesReviewed"] is True
    assert result["actionShasApproved"] is False
    assert result["githubConnectorRepositoryAccess"] is True
    assert result["actionsSettingsReviewed"] is True
    assert result["publishEnvironmentConfigured"] is False
    assert result["supplyChainGate"] == "fail-closed"

    mutations = (
        lambda p: p["triggerPolicy"]["allowedEvents"].append("push"),
        lambda p: p["permissionsPolicy"]["buildScanJob"].update({"packages": "write"}),
        lambda p: p["permissionsPolicy"]["publishAttestSignJob"].update({"contents": "write"}),
        lambda p: p["actionPolicy"].update({"resolvedActionShasApproved": True}),
        lambda p: p["actionPolicy"]["allowlist"][0].update({"reviewedSha": "0" * 40}),
        lambda p: p["actionPolicy"]["allowlist"][0].update({"upstreamTagCommitVerified": False}),
        lambda p: p["actionPolicy"]["allowlist"][0].update({"approvedSha": "v6"}),
        lambda p: p["supplyChainGates"]["vulnerabilityGate"].update({"severity": ["CRITICAL"]}),
        lambda p: p["supplyChainGates"]["vulnerabilityGate"].update({"ignoreUnfixed": True}),
        lambda p: p["supplyChainGates"].update({"automaticDeployment": True}),
        lambda p: p["repositoryReview"]["githubConnector"].update({"selectedRepositories": ["gihohoho/other"]}),
        lambda p: p["repositoryReview"]["actionsSettings"].update({"allowedActions": "selected"}),
        lambda p: p["repositoryReview"]["actionsSettings"].update({"requireFullLengthCommitSha": True}),
        lambda p: p["repositoryReview"]["publishEnvironment"].update({"exists": True}),
        lambda p: p["requiredRepositorySetup"].update({"githubConnectorRepositoryAccess": False}),
        lambda p: p["requiredRepositorySetup"].update({"actionsSettingsReviewed": False}),
        lambda p: p["requiredRepositorySetup"].update({"publishEnvironmentConfigured": True}),
        lambda p: p.update({"repositoryActionsSettingsMutationApproved": True}),
        lambda p: p.update({"publishEnvironmentCreationApproved": True}),
        lambda p: p.update({"workflowCreationApproved": True}),
    )
    for mutation in mutations:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            mutate_plan(temp, mutation)
            expect_blocked(module, temp)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        copy_fixture(temp)
        workflow = temp / ".github/workflows/publish-backend-ghcr.yml"
        workflow.parent.mkdir(parents=True, exist_ok=True)
        workflow.write_text("name: unsafe-before-approval\n", encoding="utf-8")
        expect_blocked(module, temp)

    print("OK: v319 GitHub connector/Actions settings review smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

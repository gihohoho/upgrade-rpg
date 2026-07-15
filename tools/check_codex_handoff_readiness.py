#!/usr/bin/env python3
"""Validate the v320 Codex/GHCR handoff using repository files only."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
from typing import Any

TOOL_VERSION = "v320.github-actions-ghcr-workflow-prepared-gated"
READY_RESULT = "github-actions-ghcr-workflow-prepared-publish-gated"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "choose-private-repository-publish-approval-model"
EXPECTED_REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
EXPECTED_NAMESPACE = "gihohoho"
EXPECTED_REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
EXPECTED_REFERENCE = EXPECTED_REPOSITORY + "@sha256:<approved-64-hex-digest>"
EXPECTED_BASE = "python:3.11.15-slim-bookworm@sha256:28255a3ace7eb4c48bc1b57b90af29e1bc82b4fd6c60614a8e3dce61b87ff941"
WORKFLOW_PATH = ".github/workflows/publish-backend-ghcr.yml"
REVISION_SHA256 = "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa"


class CodexHandoffError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CodexHandoffError(message)


def _read(path: Path) -> str:
    if not path.is_file():
        raise CodexHandoffError(f"required file is missing: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise CodexHandoffError(f"invalid JSON: {path.as_posix()}: {exc}") from exc
    _require(isinstance(value, dict), f"JSON root must be an object: {path.as_posix()}")
    return value


def _bool(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    _require(isinstance(value, bool), f"{key} must be a boolean")
    return value


def _env_inventory(text: str) -> dict[str, str]:
    return {
        line.split("=", 1)[0].strip(): line.split("=", 1)[1].strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }


def _first_from(text: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^\s*FROM\s+([^\s]+)(?:\s+AS\s+\S+)?\s*$", line, re.IGNORECASE)
        if match:
            return match.group(1)
    raise CodexHandoffError("Dockerfile FROM image is missing")


def _verify_forbidden_handoff_paths(root: Path, forbidden_paths: tuple[Path, ...]) -> str:
    """Allow ignored local files, but never tracked files or secret-bearing handoff fixtures."""
    if (root / ".git").exists():
        relative_paths = [path.relative_to(root).as_posix() for path in forbidden_paths]
        completed = subprocess.run(
            (
                "git",
                "-c",
                f"safe.directory={root.resolve().as_posix()}",
                "-C",
                str(root),
                "ls-files",
                "--",
                *relative_paths,
            ),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        _require(completed.returncode == 0, "cannot verify forbidden paths against the Git index")
        tracked = tuple(line.strip() for line in completed.stdout.splitlines() if line.strip())
        _require(not tracked, f"local or secret path is tracked by Git: {', '.join(tracked)}")
        return "git-index"

    for path in forbidden_paths:
        _require(not path.exists(), f"local or secret path must not be present in handoff fixture: {path.relative_to(root)}")
    return "filesystem-absence"


def _inspect_actions_workflow(root: Path) -> dict[str, Any]:
    tool = root / "tools/check_github_actions_ghcr_static_plan.py"
    spec = importlib.util.spec_from_file_location("v320_github_actions_plan_for_handoff", tool)
    _require(spec is not None and spec.loader is not None, "cannot load v320 GitHub Actions checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        result = module.inspect_static_workflow_plan(root)
    except module.StaticWorkflowPlanError as exc:
        raise CodexHandoffError(f"GitHub Actions workflow check failed: {exc}") from exc
    _require(result.get("result") == READY_RESULT, "GitHub Actions workflow result differs")
    return result


def inspect_codex_handoff(root: Path) -> dict[str, Any]:
    policy = _read_json(root / "deploy/backend-image-ghcr-policy.example.json")
    env_example = _read(root / "deploy/production.env.example")
    compose = _read(root / "deploy/docker-compose.production.yml")
    production_dockerfile = _read(root / "backend/Dockerfile.production")
    local_dockerfile = _read(root / "backend/Dockerfile")
    agents = _read(root / "AGENTS.md")
    prompt = _read(root / "NEXT_CHAT_PROMPT.md")
    handoff = _read(root / "NEXT_CHAT_HANDOFF.md")
    current = _read(root / "docs/current/CURRENT_STATUS.md")
    ghcr_doc = _read(root / "docs/current/BACKEND_IMAGE_GHCR_POLICY.md")
    security_doc = _read(root / "docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md")
    docs_index = _read(root / "docs/README.md")
    handoff_prompt = _read(root / "docs/handoff/NEXT_CHAT_PROMPT.md")
    handoff_state = _read(root / "docs/handoff/NEXT_CHAT_HANDOFF.md")
    actions_result = _inspect_actions_workflow(root)

    _require(policy.get("schemaVersion") == TOOL_VERSION, "unexpected v320 schemaVersion")
    _require(_bool(policy, "preparedOnly") is True, "policy must remain prepared-only")
    _require(policy.get("publishApprovalModel") == "undecided", "publish approval model must remain undecided")
    _require(policy.get("githubRemote") == EXPECTED_REMOTE, "GitHub remote changed")
    _require(policy.get("registryProvider") == "github-container-registry", "registry provider must be GHCR")
    _require(policy.get("registryHost") == "ghcr.io", "registry host must be ghcr.io")
    _require(policy.get("namespace") == EXPECTED_NAMESPACE, "GHCR namespace changed")
    _require(_bool(policy, "namespaceResolved") is True, "namespace must remain resolved")
    _require(policy.get("repositoryName") == "upgrade-rpg-backend", "repository name changed")
    _require(policy.get("repositoryIdentity") == EXPECTED_REPOSITORY, "repository identity changed")
    _require(policy.get("repositoryVisibility") == "private", "repository must remain private")
    _require(policy.get("productionReferenceMode") == "digest-only", "production reference must remain digest-only")
    _require(policy.get("productionReferenceTemplate") == EXPECTED_REFERENCE, "production reference changed")
    _require(policy.get("targetPlatform") == "linux/amd64", "target platform changed")
    _require(policy.get("productionDockerfile") == "backend/Dockerfile.production", "production Dockerfile path changed")
    _require(policy.get("baseImageReference") == EXPECTED_BASE, "base image reference changed")
    _require(_bool(policy, "baseImageDigestApproved") is True, "base image digest approval missing")
    _require(policy.get("ciCredentialStrategy") == "github-actions-github-token", "CI credential strategy changed")
    _require(policy.get("localCredentialStrategy") == "deferred", "local credential strategy must remain deferred")

    for key in (
        "githubActionsWorkflowPresent",
        "githubActionsWorkflowCreationApproved",
        "githubActionsWorkflowExecutionApproved",
        "githubActionsStaticPlanPresent",
        "githubActionsStaticPlanVerified",
        "actionShasResolved",
        "actionShasApproved",
        "githubConnectorRepositoryAccess",
        "githubConnectorSelectedRepositoryOnly",
        "repositoryActionsSettingsReviewed",
        "repositoryActionsSettingsMutationApproved",
        "repositoryActionsSettingsMutationExecuted",
        "publishEnvironmentReviewed",
        "publishEnvironmentCreationApproved",
        "publishEnvironmentCreated",
        "publishEnvironmentMainOnly",
        "ciDockerLoginApproved",
        "ciImageBuildApproved",
        "ciImagePushApproved",
    ):
        _require(_bool(policy, key) is True, f"completed/approved v320 state must remain true: {key}")
    for key in (
        "longLivedCredentialInRepository",
        "registryCredentialFileInRepository",
        "githubPatCreated",
        "githubActionsWorkflowExecutionExecuted",
        "publishEnvironmentRequiredReviewerConfigured",
        "publishEnvironmentPreventSelfReviewConfigured",
        "publishEnvironmentReviewerAvailableForCurrentPlan",
        "sourceControlledPublishGateReady",
        "publishEnvironmentConfigured",
        "localDockerLoginApproved",
        "localImagePullApproved",
        "localImageBuildApproved",
        "localImagePushApproved",
        "containerStartApproved",
        "actualRegistryMutationExecuted",
        "actualDockerCommandExecuted",
        "actualDatabaseAlembicMutationExecuted",
    ):
        _require(_bool(policy, key) is False, f"blocked/unexecuted v320 state must remain false: {key}")
    _require(policy.get("nextSafeStage") == NEXT_SAFE_STAGE, "unexpected next safe stage")

    env = _env_inventory(env_example)
    _require(env.get("BACKEND_IMAGE") == EXPECTED_REFERENCE, "production env repository/reference differs")
    _require("<github-account-or-organization>" not in env_example, "old namespace placeholder remains")
    _require("image: ${BACKEND_IMAGE:?" in compose, "production Compose must require BACKEND_IMAGE")
    _require(re.search(r"(?m)^\s+build:\s*$", compose) is None, "production Compose must not build")
    _require(re.search(r"(?m)^\s+ports:\s*$", compose) is None, "production backend host ports must remain absent")
    _require(re.search(r"(?m)^\s+replicas:\s*1\s*$", compose) is not None, "backend replicas must remain 1")

    _require(_first_from(production_dockerfile) == EXPECTED_BASE, "production Dockerfile base digest differs")
    _require(_first_from(local_dockerfile) == "python:3.11-slim", "local Dockerfile must remain preserved")
    _require("USER app" in production_dockerfile, "production Dockerfile must remain non-root")
    production_cmd = next((line.lower() for line in production_dockerfile.splitlines() if line.strip().startswith("CMD ")), "")
    _require("--workers" not in production_cmd, "production Uvicorn worker count must remain 1")
    _require("alembic" not in production_cmd, "container startup must not run Alembic")

    common_markers = (TOOL_VERSION, EXPECTED_REMOTE, EXPECTED_REPOSITORY)
    for path, text in (
        ("AGENTS.md", agents),
        ("NEXT_CHAT_PROMPT.md", prompt),
        ("NEXT_CHAT_HANDOFF.md", handoff),
        ("docs/current/CURRENT_STATUS.md", current),
    ):
        for marker in common_markers:
            _require(marker in text, f"{path} is missing marker: {marker}")
        _require("GITHUB_TOKEN" in text or "github-actions-github-token" in text, f"{path} is missing CI credential strategy")
        _require("PUBLISH_REVIEWER_GATE_READY" in text, f"{path} is missing fail-closed publish gate")
    _require("check_github_actions_ghcr_static_plan.py --strict" in agents, "AGENTS.md is missing first checker")
    _require("실행 중인 개발 서버를 재사용" in agents, "AGENTS.md is missing persistent server permission")
    _require(READY_RESULT in prompt, "prompt is missing expected result")
    _require(NEXT_SAFE_STAGE in prompt, "prompt is missing next safe stage")
    _require("필요한 extension" in prompt, "prompt is missing recurring install/permission request rule")
    _require(EXPECTED_REPOSITORY in ghcr_doc, "GHCR policy doc is missing repository")
    _require("GITHUB_TOKEN" in ghcr_doc, "GHCR policy doc is missing credential strategy")
    _require("required reviewer" in security_doc, "security checklist is missing reviewer gate")
    _require("실제 secret 값은 이 문서에 적지 않습니다" in security_doc, "security checklist could expose secrets")
    _require("Docs Index" in docs_index and "archive/production-deployment/" in docs_index, "docs index is not current")
    _require(prompt == handoff_prompt, "root and docs/handoff prompts differ")
    _require(handoff == handoff_state, "root and docs/handoff state differ")

    workflow_files = {
        path.relative_to(root).as_posix()
        for path in (root / ".github/workflows").rglob("*")
        if path.is_file()
    }
    _require(workflow_files == {WORKFLOW_PATH}, "unexpected workflow file set")
    secrets_dir = root / "deploy/secrets"
    allowed_secret_files = {"README.md"}
    if secrets_dir.exists():
        actual = {path.name for path in secrets_dir.iterdir() if path.is_file()}
        _require(actual <= allowed_secret_files, "actual secret file exists under deploy/secrets")

    forbidden_paths = (
        root / "backend/.env",
        root / "deploy/production.env",
        root / "local-backups",
        root / "local-review-artifacts",
    )
    package_safety_mode = _verify_forbidden_handoff_paths(root, forbidden_paths)

    for path in (
        root / "docs/current/BACKEND_IMAGE_SOURCE_DIGEST_POLICY.md",
        root / "docs/current/BACKEND_IMAGE_REGISTRY_BASE_SELECTION.md",
        root / "deploy/backend-image-source-digest-policy.example.json",
        root / "deploy/backend-image-registry-base-selection.example.json",
        root / "tools/check_backend_image_source_digest_policy.py",
        root / "tools/check_backend_image_registry_base_selection.py",
    ):
        _require(not path.exists(), f"superseded active file remains: {path.relative_to(root)}")

    revision = root / "backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py"
    _require(revision.is_file(), "reviewed Alembic revision is missing")
    actual_sha = hashlib.sha256(revision.read_bytes()).hexdigest()
    _require(actual_sha == REVISION_SHA256, f"reviewed revision SHA-256 differs: {actual_sha}")

    return {
        "toolVersion": TOOL_VERSION,
        "githubRemote": EXPECTED_REMOTE,
        "namespace": EXPECTED_NAMESPACE,
        "repository": EXPECTED_REPOSITORY,
        "repositoryVisibility": "private",
        "targetPlatform": "linux/amd64",
        "baseImageDigestApproved": True,
        "ciCredentialStrategy": "github-actions-github-token",
        "localCredentialStrategy": "deferred",
        "workflowCreationApproved": True,
        "workflowExecutionApproved": True,
        "workflowExecutionExecuted": False,
        "ciRegistryMutationApproved": True,
        "runtimeMutationExecuted": False,
        "githubActionsStaticPlanVerified": True,
        "workflowFilePresent": actions_result["workflowFilePresent"],
        "workflowSourceSha256": actions_result["workflowSourceSha256"],
        "workflowSemanticSha256": actions_result["workflowSemanticSha256"],
        "actionShasApproved": actions_result["actionShasApproved"],
        "actionsSettingsConfigured": actions_result["actionsSettingsConfigured"],
        "publishEnvironmentExists": actions_result["publishEnvironmentExists"],
        "publishEnvironmentConfigured": actions_result["publishEnvironmentConfigured"],
        "publishGateReady": actions_result["publishGateReady"],
        "dockerBuildContextEnvExcluded": actions_result["dockerBuildContextEnvExcluded"],
        "reproducibleBuildReady": actions_result["reproducibleBuildReady"],
        "packageSafetyMode": package_safety_mode,
        "result": READY_RESULT,
        "nextSafeStage": NEXT_SAFE_STAGE,
    }


def render(result: dict[str, Any]) -> str:
    return "\n".join((
        "Codex/GHCR handoff verification (read-only)",
        "The workflow is prepared, but it has not run and no Docker, registry, DB, or Alembic mutation was executed.",
        "",
        f"- GitHub remote: {result['githubRemote']}",
        f"- namespace/repository: {result['namespace']} / {result['repository']}",
        f"- visibility/target: {result['repositoryVisibility']} / {result['targetPlatform']}",
        f"- base image digest approved: {result['baseImageDigestApproved']}",
        f"- credential strategy: {result['ciCredentialStrategy']} / local={result['localCredentialStrategy']}",
        f"- forbidden path verification: {result['packageSafetyMode']}",
        "- workflow file/creation approved: yes/yes",
        f"- reviewed workflow source SHA-256: {result['workflowSourceSha256']}",
        f"- reviewed workflow semantic SHA-256: {result['workflowSemanticSha256']}",
        "- workflow execution approved/executed: yes/no",
        "- recorded action allowlist/full SHA enforcement: configured/configured (2026-07-15 browser snapshot)",
        "- CI login/build/push approved/executed: yes/yes/yes / no/no/no",
        "- recorded publish environment/main-only: present/configured (2026-07-15 browser snapshot)",
        "- native required reviewer/current private plan: missing/unavailable",
        "- publish approval model: undecided",
        "- PUBLISH_REVIEWER_GATE_READY: source-controlled false (fail-closed before GHCR login)",
        "- root Docker context env files/re-includes: excluded/forbidden",
        "- deterministic dependency/toolchain lock: incomplete (required before first publish)",
        "- container/registry/DB/Alembic mutation executed: no/no/no/no",
        f"- result: {result['result']}",
        f"- next safe stage: {result['nextSafeStage']}",
    ))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = inspect_codex_handoff(root)
    except CodexHandoffError as exc:
        payload = {"toolVersion": TOOL_VERSION, "result": BLOCKED_RESULT, "reason": str(exc)}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("Codex/GHCR handoff verification")
            print(f"- result: {BLOCKED_RESULT}")
            print(f"- reason: {exc}")
        return 1 if args.strict else 0
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate the v319 Codex/GHCR handoff using repository files only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

TOOL_VERSION = "v319.github-connector-actions-settings-reviewed"
READY_RESULT = "github-connector-actions-settings-verified-workflow-not-created"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "request-repository-actions-supply-chain-settings-change-approval"
EXPECTED_REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
EXPECTED_NAMESPACE = "gihohoho"
EXPECTED_REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
EXPECTED_REFERENCE = EXPECTED_REPOSITORY + "@sha256:<approved-64-hex-digest>"
EXPECTED_BASE = "python:3.11.15-slim-bookworm@sha256:28255a3ace7eb4c48bc1b57b90af29e1bc82b4fd6c60614a8e3dce61b87ff941"
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
    if not isinstance(value, dict):
        raise CodexHandoffError(f"JSON root must be an object: {path.as_posix()}")
    return value


def _bool(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise CodexHandoffError(f"{key} must be a boolean")
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
    """Keep local ignored files usable while remaining fail-closed for extracted ZIPs."""
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
        _require(not path.exists(), f"local or secret path must not be present in handoff ZIP: {path.relative_to(root)}")
    return "filesystem-absence"


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
    actions_plan = _read_json(root / "deploy/github-actions-ghcr-static-plan.example.json")
    actions_plan_doc = _read(root / "docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md")
    docs_index = _read(root / "docs/README.md")
    handoff_prompt = _read(root / "docs/handoff/NEXT_CHAT_PROMPT.md")
    handoff_state = _read(root / "docs/handoff/NEXT_CHAT_HANDOFF.md")

    _require(policy.get("schemaVersion") == TOOL_VERSION, "unexpected v319 schemaVersion")
    _require(_bool(policy, "reviewOnly") is True, "policy must remain review-only")
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
        "longLivedCredentialInRepository",
        "registryCredentialFileInRepository",
        "githubPatCreated",
        "githubActionsWorkflowPresent",
        "githubActionsWorkflowCreationApproved",
        "dockerLoginApproved",
        "imagePullApproved",
        "imageBuildApproved",
        "imagePushApproved",
        "containerStartApproved",
        "actualRegistryMutationExecuted",
        "actualDockerCommandExecuted",
        "actualDatabaseAlembicMutationExecuted",
        "actionShasApproved",
        "repositoryActionsSettingsMutationApproved",
        "publishEnvironmentCreationApproved",
        "publishEnvironmentConfigured",
    ):
        _require(_bool(policy, key) is False, f"{key} must remain false")
    for key in (
        "githubConnectorRepositoryAccess",
        "githubConnectorSelectedRepositoryOnly",
        "repositoryActionsSettingsReviewed",
        "publishEnvironmentReviewed",
    ):
        _require(_bool(policy, key) is True, f"verified repository review must remain true: {key}")
    _require(_bool(policy, "actionShasResolved") is True, "action SHA candidates must remain resolved")
    _require(_bool(policy, "githubActionsStaticPlanPresent") is True, "GitHub Actions static plan must be present")
    _require(_bool(policy, "githubActionsStaticPlanVerified") is True, "GitHub Actions static plan must be verified")
    _require(policy.get("nextSafeStage") == NEXT_SAFE_STAGE, "unexpected next safe stage")

    _require(actions_plan.get("schemaVersion") == TOOL_VERSION, "static workflow plan version differs")
    _require(actions_plan.get("reviewOnly") is True, "static workflow plan must remain review-only")
    _require(actions_plan.get("workflowFilePresent") is False, "workflow file must remain absent")
    _require(actions_plan.get("workflowCreationApproved") is False, "workflow creation must remain unapproved")
    action_policy = actions_plan.get("actionPolicy")
    _require(isinstance(action_policy, dict), "static workflow action policy is missing")
    _require(action_policy.get("resolvedActionShaCandidatesReviewed") is True, "action SHA candidates are not reviewed")
    _require(action_policy.get("resolvedActionShasApproved") is False, "action SHA candidates must remain unapproved")
    repository_review = actions_plan.get("repositoryReview")
    _require(isinstance(repository_review, dict), "static workflow repository review is missing")
    connector_review = repository_review.get("githubConnector")
    _require(isinstance(connector_review, dict), "GitHub connector review is missing")
    _require(connector_review.get("selectedRepositories") == ["gihohoho/upgrade-rpg"], "connector scope changed")
    _require(connector_review.get("repositoryAccessVerified") is True, "connector access is not verified")
    settings_review = repository_review.get("actionsSettings")
    _require(isinstance(settings_review, dict), "Actions settings review is missing")
    _require(settings_review.get("reviewed") is True, "Actions settings are not reviewed")
    _require(settings_review.get("allowedActions") == "all", "reviewed Actions policy changed")
    _require(settings_review.get("requireFullLengthCommitSha") is False, "unapproved SHA policy change detected")
    environment_review = repository_review.get("publishEnvironment")
    _require(isinstance(environment_review, dict), "publish environment review is missing")
    _require(environment_review.get("reviewed") is True, "publish environment was not reviewed")
    _require(environment_review.get("exists") is False, "publish environment exists before approval")
    _require(actions_plan.get("nextSafeStage") == NEXT_SAFE_STAGE, "static workflow plan next stage differs")
    _require("workflow_dispatch" in actions_plan_doc, "static workflow plan document is missing trigger policy")
    _require("packages: write" in actions_plan_doc, "static workflow plan document is missing package permission")
    _require("Sigstore keyless OIDC" in actions_plan_doc, "static workflow plan document is missing signature policy")

    env = _env_inventory(env_example)
    _require(env.get("BACKEND_IMAGE") == EXPECTED_REFERENCE, "production env repository/reference differs")
    _require("<github-account-or-organization>" not in env_example, "old namespace placeholder remains in active env example")
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

    common_markers = (
        TOOL_VERSION,
        EXPECTED_REMOTE,
        EXPECTED_REPOSITORY,
    )
    for path, text in (
        ("AGENTS.md", agents),
        ("NEXT_CHAT_PROMPT.md", prompt),
        ("NEXT_CHAT_HANDOFF.md", handoff),
        ("docs/current/CURRENT_STATUS.md", current),
    ):
        for marker in common_markers:
            _require(marker in text, f"{path} is missing marker: {marker}")
        _require("GITHUB_TOKEN" in text or "github-actions-github-token" in text, f"{path} is missing CI credential strategy")
        _require("workflow/login/pull/build/push approved: no" in text, f"{path} is missing workflow/build approval boundary")
    _require("check_github_actions_ghcr_static_plan.py --strict" in agents, "AGENTS.md is missing first checker")
    _require(READY_RESULT in prompt, "prompt is missing expected result")
    _require(NEXT_SAFE_STAGE in prompt, "prompt is missing next safe stage")
    _require(EXPECTED_REPOSITORY in ghcr_doc, "GHCR policy doc is missing repository")
    _require("GITHUB_TOKEN" in ghcr_doc, "GHCR policy doc is missing credential strategy")
    _require("Docs Index" in docs_index and "archive/production-deployment/" in docs_index, "docs index is not current")
    _require(prompt == handoff_prompt, "root and docs/handoff prompts differ")
    _require(handoff == handoff_state, "root and docs/handoff state differ")

    workflow_dir = root / ".github/workflows"
    _require(not workflow_dir.exists() or not any(workflow_dir.rglob("*")), "workflow files exist before approval")
    secrets_dir = root / "deploy/secrets"
    allowed_secret_files = {"README.md"}
    if secrets_dir.exists():
        actual = {p.name for p in secrets_dir.iterdir() if p.is_file()}
        _require(actual <= allowed_secret_files, "actual secret file exists under deploy/secrets")

    forbidden_paths = (
        root / "backend/.env",
        root / "deploy/production.env",
        root / "local-backups",
        root / "local-review-artifacts",
    )
    package_safety_mode = _verify_forbidden_handoff_paths(root, forbidden_paths)

    # Superseded current files should be archived, not duplicated.
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
        "workflowCreationApproved": False,
        "dockerLoginApproved": False,
        "imagePullApproved": False,
        "imageBuildApproved": False,
        "imagePushApproved": False,
        "runtimeMutationExecuted": False,
        "githubActionsStaticPlanVerified": True,
        "workflowFilePresent": False,
        "actionShaCandidatesReviewed": True,
        "actionShasApproved": False,
        "githubConnectorRepositoryAccess": True,
        "repositoryActionsSettingsReviewed": True,
        "publishEnvironmentConfigured": False,
        "packageSafetyMode": package_safety_mode,
        "result": READY_RESULT,
        "nextSafeStage": NEXT_SAFE_STAGE,
    }


def render(result: dict[str, Any]) -> str:
    return "\n".join((
        "Codex/GHCR namespace handoff verification (read-only)",
        "No token/PAT was read, no workflow was created, and no Docker, registry, DB, or Alembic mutation was executed.",
        "",
        f"- GitHub remote: {result['githubRemote']}",
        f"- namespace/repository: {result['namespace']} / {result['repository']}",
        f"- visibility/target: {result['repositoryVisibility']} / {result['targetPlatform']}",
        f"- base image digest approved: {result['baseImageDigestApproved']}",
        f"- credential strategy: {result['ciCredentialStrategy']} / local={result['localCredentialStrategy']}",
        f"- forbidden path verification: {result['packageSafetyMode']}",
        "- GitHub Actions static plan/workflow present: verified/no",
        "- action SHA candidates reviewed/approved: yes/no",
        "- GitHub connector repository access: verified (upgrade-rpg only)",
        "- repository Actions settings reviewed/changed: yes/no",
        "- publish environment reviewed/configured: yes/no",
        "- workflow/login/pull/build/push approved: no/no/no/no/no",
        "- workflow/login/pull/build/push executed: no/no/no/no/no",
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
            print("Codex/GHCR namespace handoff verification")
            print(f"- result: {BLOCKED_RESULT}")
            print(f"- reason: {exc}")
        return 1 if args.strict else 0
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

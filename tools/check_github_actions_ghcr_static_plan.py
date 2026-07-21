#!/usr/bin/env python3
"""Validate the v324 owner-only, repeatable single-run GHCR publish lifecycle policy."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

import yaml

TOOL_VERSION = "v324.bootstrap-fixed-retry-preparation-publish-gated"
READY_RESULT = "github-actions-ghcr-owner-only-retry-preparation-ready-publish-gated"
AUTHORIZATION_OPEN_RESULT = "github-actions-ghcr-owner-only-authorization-open"
AUTHORIZATION_CLOSED_RESULT = (
    "github-actions-ghcr-owner-only-authorization-closed-awaiting-evidence"
)
ATTEMPT_RECORDED_RESULT = "github-actions-ghcr-owner-only-attempt-recorded-publish-gated"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "review-and-approve-exact-bootstrap-fix-preparation-sha"
AUTHORIZATION_OPEN_NEXT_SAFE_STAGE = "dispatch-one-owner-approved-workflow-run"
AUTHORIZATION_CLOSED_NEXT_SAFE_STAGE = "record-workflow-run-evidence"
ATTEMPT_RECORDED_NEXT_SAFE_STAGE = "review-recorded-workflow-attempt-evidence"
REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
REPOSITORY = "gihohoho/upgrade-rpg"
IMAGE_REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
WORKFLOW_PATH = ".github/workflows/publish-backend-ghcr.yml"
LIFECYCLE_PATH = "deploy/github-actions-ghcr-publish-lifecycle.json"
LIFECYCLE_SCHEMA_VERSION = "v324.owner-only-publish-lifecycle"
PRIOR_APPROVED_PREPARATION_SHA = "350bbd085f1cf636810d75ddcbb5321e0791256c"
PRIOR_ATTEMPT_EVIDENCE = {
    "preparationSha": PRIOR_APPROVED_PREPARATION_SHA,
    "authorizationSha": "32e5102877851ace06e1c0ed3bcb48310b8d65b6",
    "closureSha": "362f5f1901d234b5b86f2a7cefdabd28ac61f896",
    "recordCommitSha": "1f12ea59eb54385337557e9754f86731ec53d253",
    "runId": 29716038891,
    "runUrl": "https://github.com/gihohoho/upgrade-rpg/actions/runs/29716038891",
    "conclusion": "failure",
    "registryLoginExecuted": False,
    "imageBuildExecuted": False,
    "imagePushExecuted": False,
}
EXPECTED_WORKFLOW_SHA256 = "245630348d384cc1c862014454cb73b6149a8c3a20d7b114763bc6fe655ef4bd"
EXPECTED_WORKFLOW_SEMANTIC_SHA256 = "e08c3788e88da351112bc381d225e418938f7bd74ccec7eb83f9f59eff6f724c"
SMOKE_CORE_PATH = "tools/run_smoke_core.sh"
TRANSIENT_SMOKE_SKIP_VARIABLE = "SKIP_GHCR_HANDOFF_SMOKES"
TRANSIENT_SMOKE_SKIP_COMMAND = "SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh"
DIRECT_STATIC_STRICT_COMMAND = "python tools/check_github_actions_ghcr_static_plan.py --strict"
SKIPPABLE_CLOSED_ROOT_SMOKES = (
    "python tools/smoke/backend/smoke_github_actions_ghcr_static_plan.py",
    "python tools/smoke/backend/smoke_codex_handoff_readiness.py",
    "python tools/smoke/game/smoke_next_chat_handoff.py",
)
ATTEMPT_EVIDENCE_CHANGED_PATH_ALLOWLIST = frozenset({
    LIFECYCLE_PATH,
    "AGENTS.md",
    "NEXT_CHAT_HANDOFF.md",
    "NEXT_CHAT_PROMPT.md",
    "docs/handoff/NEXT_CHAT_HANDOFF.md",
    "docs/handoff/NEXT_CHAT_PROMPT.md",
    "docs/current/CURRENT_STATUS.md",
    "docs/current/BACKEND_IMAGE_GHCR_POLICY.md",
    "docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md",
    "docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md",
    "docs/current/ROADMAP.md",
    "docs/CHANGELOG.md",
    "docs/NEXT_STEPS.md",
})
DOCKERFILE_FRONTEND = "docker/dockerfile:1.21.0@sha256:27f9262d43452075f3c410287a2c43f5ef1bf7ec2bb06e8c9eeb1b8d453087bc"
LOCK_SHA256 = {
    "backend/requirements/pip-bootstrap.lock": "bcc097cb08562a39c235ad52c7183a7e2ae9b80010463cc404ff772881ced4f7",
    "backend/requirements/runtime-linux-amd64-py311.lock": "863fc3dca235aaf692f4a065e4449e198bba9b5317ab29af57bc7e301b57a42c",
    "backend/requirements/dev-linux-amd64-py311.lock": "5c5b025a96621f02b3667899db43f1e1f02e3fa55b50b615d95304e7f242844b",
}
REPRODUCIBILITY_INPUT_SHA256 = {
    "backend/requirements/pip-bootstrap.in": "9df44a3db13ef551bf575949d553b8d14044635b91c09e85dc6d3ea97f50d225",
    "backend/requirements/runtime.in": "9eeff8d010a3f18711d82e68effa3874c15f63b99a1f65988106cc46719727ce",
    "backend/requirements/dev.in": "6404277a75ce651735fcea3f89b5eee548cfd58ee197faed27b03333d587e2fe",
    "backend/pyproject.toml": "1c10a732138522f00b87c5fdc8fc866affc9dbbe87f3bca81af94354d35f864b",
    "backend/Dockerfile.production": "2ccd445b3b73f52825d8696d241d34a180c513dde2bebabbae3e0a833624af5e",
}
CERTIFICATE_IDENTITY = (
    "https://github.com/gihohoho/upgrade-rpg/"
    ".github/workflows/publish-backend-ghcr.yml@refs/heads/main"
)
EXPECTED_ACTIONS = {
    "actions/checkout": ("v7.0.0", "9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0"),
    "actions/setup-python": ("v6.2.0", "a309ff8b426b58ec0e2a45f0f869d46889d02405"),
    "docker/setup-buildx-action": ("v4.2.0", "bb05f3f5519dd87d3ba754cc423b652a5edd6d2c"),
    "docker/login-action": ("v4.4.0", "af1e73f918a031802d376d3c8bbc3fe56130a9b0"),
    "docker/build-push-action": ("v7.3.0", "53b7df96c91f9c12dcc8a07bcb9ccacbed38856a"),
    "anchore/sbom-action": ("v0.24.0", "e22c389904149dbc22b58101806040fa8d37a610"),
    "sigstore/cosign-installer": ("v4.1.2", "6f9f17788090df1f26f669e9d70d6ae9567deba6"),
    "actions/upload-artifact": ("v7.0.1", "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"),
}
DOCKERIGNORE_ENV_PATTERNS = (
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "backend/.env",
    "*.env",
    "*.env.*",
    ".envrc",
    "**/.envrc",
)
EXPECTED_ACTION_STEP_SHA256 = {
    "validate:Check out exact source commit": "6a4854f55ba0b6116c44566bc17db3d475f1715371932312953e2bdfe6469475",
    "validate:Set up Python 3.11.15": "a609038eeba3cc4d4e2544a17e2a5dd608afc8164eb0a206d805c03cce4f69ab",
    "build_scan:Check out exact source commit": "9350d08554e0602d5c761ee37f7ee71fd5de268beda39865527d91747903bef4",
    "build_scan:Set up Python 3.11.15": "a609038eeba3cc4d4e2544a17e2a5dd608afc8164eb0a206d805c03cce4f69ab",
    "build_scan:Set up Docker Buildx": "9e98d11cbaa23d6e221aa919e69bb31ec2e0b2d883023c8abc55c998b2b383f4",
    "build_scan:Build local linux/amd64 image without registry mutation": "96dc0dadb21da51d7ff7856c0f9fbd9da21fc43d32f7038edc82518ad748d201",
    "build_scan:Generate local SPDX JSON SBOM": "0f52e862c1309ab829151d6f126da1e7a67c54f7f222ec4b8ee0dda857e12c27",
    "build_scan:Retain non-secret review artifacts": "e4b6f148dcfbdc4823351bb99a476f25e0e990654ca3eafc15a4d62a22512b6e",
    "publish_sign_verify:Check out exact source commit": "6a4854f55ba0b6116c44566bc17db3d475f1715371932312953e2bdfe6469475",
    "publish_sign_verify:Set up Python 3.11.15": "a609038eeba3cc4d4e2544a17e2a5dd608afc8164eb0a206d805c03cce4f69ab",
    "publish_sign_verify:Set up Docker Buildx": "9e98d11cbaa23d6e221aa919e69bb31ec2e0b2d883023c8abc55c998b2b383f4",
    "publish_sign_verify:Log in to GHCR with ephemeral GITHUB_TOKEN": "510ff6f9df0abbd302bf4eb383301d9d8da6d7e9988902ed09131635931104cd",
    "publish_sign_verify:Build and push digest candidate with BuildKit attestations": "ade6afcfa55ab989a485f67d5dbd0d710d39751d93fe248e4671c9b26ded55d7",
    "publish_sign_verify:Set up Cosign": "d6dfc3975100db9978b85ccf2ee1d3233f5d4dff603d0796984c39c19095a115",
    "publish_sign_verify:Retain exact-digest evidence": "ebc4e0374a405d9096052e77ebfb5025fc7a7e3e3e3c3abb11602da31946f2ee",
}
EXPECTED_RUN_STEP_SHA256 = {
    "validate:Check manual approval inputs": "baecf21094a45363d43ec715dcd49e5ef85792dd32531ae08c9821c5a0ddfadc",
    "validate:Require exactly one first-attempt dispatch for this authorization": "859d94c81dc38f0a8b9f95ac5381775adb37e9d8bd08052c5daed72f1d6b2242",
    "validate:Verify source-controlled authorization transition": "fb300d83e2ad2836f5c906006ffd5e5a8d445af4284cd10491d1ce480e918424",
    "validate:Install backend validation dependencies": "a1f8712efd41e02e0005138d9f6a3a7f1a0f9273445ee541769f204a2ee8d3c3",
    "validate:Run fail-closed repository checks": "97a9a7e2755fb6d8917f104d08c4a5c4971288b5dfd906c1bf63b995a77ce8d6",
    "build_scan:Validate local SBOM structure": "f0209099c473f80e08077f73bfdc6d7d9d8c40d238611d52cb36ccc4e2febac9",
    "build_scan:Install checksum-pinned Trivy 0.70.0": "22c99c3087798ff0a62797f773e206e248ab473954b770ba8b2acffbd8b74d64",
    "build_scan:Block HIGH and CRITICAL vulnerabilities in local image": "d1272d7f19a1a8d3d54449ec9be5914ba44dbfc99ccfe995f58460cdbaeac5e5",
    "build_scan:Validate local Trivy JSON evidence": "219c442ec7a7d2017acc6606bb28d4a291275ff11de145ab139e9d2c14ce3986",
    "publish_sign_verify:Enforce owner-only two-step authorization gate before registry access": "01ef0fd96cbec1ec23d26dedb437b04aa9994adbc0233f4373fbce80a36c589e",
    "publish_sign_verify:Install checksum-pinned Trivy 0.70.0": "22c99c3087798ff0a62797f773e206e248ab473954b770ba8b2acffbd8b74d64",
    "publish_sign_verify:Record exact pushed digest": "037fdfa573f401e059dc2e38da86b90d088f0319e8767c6076f5f97ead29b7de",
    "publish_sign_verify:Inspect BuildKit provenance and SBOM on exact digest": "8395f1bd48b56880b4aca84f78c0d5a213db86b8cf90be10e353f8b59dfeb1a2",
    "publish_sign_verify:Block vulnerabilities in exact pushed digest before signing": "cb62951efdd38437c05e4f4c76c5cfe60bee7686f3915711e12e81d2d2f0adf6",
    "publish_sign_verify:Validate exact-digest Trivy JSON evidence": "8c3dac75fb13d9fe6183867fe61ec8ca6ee7c14eb8da59b7970df04eef133182",
    "publish_sign_verify:Sign exact digest with GitHub OIDC after all image gates": "bf287d3d80e1bd95acd54ad9294a8804a813ed10c076d557419ebdb53072453f",
    "publish_sign_verify:Verify Cosign certificate identity and issuer": "e8023f861ed97c7c8fab60c77ca6cba4b187e0f96766fca83e1c88c387cd8aad",
    "publish_sign_verify:Emit verified candidate digest": "c1c32852e363f84a84e4598f0e0a4a3f7bad576b2496dd7cf1da59a02551f261",
}
EXPECTED_RUN_STEP_ENV = {
    "validate:Check manual approval inputs": {
        "SOURCE_COMMIT": "${{ inputs.source_commit }}",
        "APPROVED_PREPARATION_COMMIT": "${{ inputs.approved_preparation_commit }}",
        "APPROVAL_REASON": "${{ inputs.approval_reason }}",
        "CONFIRM_PUBLISH": "${{ inputs.confirm_publish }}",
        "EXPECTED_GITHUB_SHA": "${{ github.sha }}",
        "EXPECTED_GITHUB_REF": "${{ github.ref }}",
        "EXPECTED_EVENT_NAME": "${{ github.event_name }}",
        "EXPECTED_RUN_ATTEMPT": "${{ github.run_attempt }}",
        "EXPECTED_ACTOR": "${{ github.actor }}",
        "EXPECTED_REPOSITORY_OWNER": "${{ github.repository_owner }}",
    },
    "validate:Require exactly one first-attempt dispatch for this authorization": {
        "ACTIONS_TOKEN": "${{ secrets.GITHUB_TOKEN }}",
        "EXPECTED_RUN_ID": "${{ github.run_id }}",
        "EXPECTED_RUN_ATTEMPT": "${{ github.run_attempt }}",
        "EXPECTED_ACTOR": "${{ github.actor }}",
        "REPOSITORY": "${{ github.repository }}",
        "SOURCE_COMMIT": "${{ inputs.source_commit }}",
    },
    "validate:Verify source-controlled authorization transition": {
        "APPROVED_PREPARATION_COMMIT": "${{ inputs.approved_preparation_commit }}",
        "SOURCE_COMMIT": "${{ inputs.source_commit }}",
        "EXPECTED_RUN_ATTEMPT": "${{ github.run_attempt }}",
    },
    "validate:Install backend validation dependencies": None,
    "validate:Run fail-closed repository checks": None,
    "build_scan:Validate local SBOM structure": None,
    "build_scan:Install checksum-pinned Trivy 0.70.0": {
        "TRIVY_VERSION": "0.70.0",
        "TRIVY_SHA256": "8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9",
    },
    "build_scan:Block HIGH and CRITICAL vulnerabilities in local image": None,
    "build_scan:Validate local Trivy JSON evidence": None,
    "publish_sign_verify:Enforce owner-only two-step authorization gate before registry access": {
        "APPROVED_PREPARATION_COMMIT": "${{ inputs.approved_preparation_commit }}",
        "SOURCE_COMMIT": "${{ inputs.source_commit }}",
        "EXPECTED_RUN_ATTEMPT": "${{ github.run_attempt }}",
    },
    "publish_sign_verify:Install checksum-pinned Trivy 0.70.0": {
        "TRIVY_VERSION": "0.70.0",
        "TRIVY_SHA256": "8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9",
    },
    "publish_sign_verify:Record exact pushed digest": {
        "DIGEST": "${{ steps.publish.outputs.digest }}",
    },
    "publish_sign_verify:Inspect BuildKit provenance and SBOM on exact digest": {
        "DIGEST": "${{ steps.publish.outputs.digest }}",
    },
    "publish_sign_verify:Block vulnerabilities in exact pushed digest before signing": {
        "DIGEST": "${{ steps.publish.outputs.digest }}",
    },
    "publish_sign_verify:Validate exact-digest Trivy JSON evidence": None,
    "publish_sign_verify:Sign exact digest with GitHub OIDC after all image gates": {
        "DIGEST": "${{ steps.publish.outputs.digest }}",
    },
    "publish_sign_verify:Verify Cosign certificate identity and issuer": {
        "DIGEST": "${{ steps.publish.outputs.digest }}",
    },
    "publish_sign_verify:Emit verified candidate digest": {
        "DIGEST": "${{ steps.publish.outputs.digest }}",
    },
}


class GitHubActionsLoader(yaml.SafeLoader):
    """YAML 1.2-like loader that keeps `on` as text and rejects duplicate keys."""


GitHubActionsLoader.yaml_implicit_resolvers = {
    key: list(value) for key, value in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
for resolver_key, resolvers in GitHubActionsLoader.yaml_implicit_resolvers.items():
    GitHubActionsLoader.yaml_implicit_resolvers[resolver_key] = [
        resolver for resolver in resolvers if resolver[0] != "tag:yaml.org,2002:bool"
    ]
GitHubActionsLoader.add_implicit_resolver(
    "tag:yaml.org,2002:bool",
    re.compile(r"^(?:true|false)$", re.IGNORECASE),
    list("tTfF"),
)


def _construct_unique_mapping(loader: GitHubActionsLoader, node: yaml.MappingNode, deep: bool = False):
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key: {key}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


GitHubActionsLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


class StaticWorkflowPlanError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise StaticWorkflowPlanError(message)


def _read(path: Path) -> str:
    if not path.is_file():
        raise StaticWorkflowPlanError(f"required file is missing: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise StaticWorkflowPlanError(f"invalid JSON: {path.as_posix()}: {exc}") from exc
    _require(isinstance(payload, dict), "plan JSON root must be an object")
    return payload


def _bool(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    _require(isinstance(value, bool), f"{key} must be a boolean")
    return value


def _full_sha(value: Any, label: str) -> str:
    _require(
        isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None,
        f"{label} must be a lowercase full 40-character commit SHA",
    )
    return value


def _utc_timestamp(value: Any, label: str) -> str:
    _require(isinstance(value, str), f"{label} is missing")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise StaticWorkflowPlanError(
            f"{label} must be UTC YYYY-MM-DDTHH:MM:SSZ"
        ) from exc
    return value


def _git(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ("git", "-C", str(root), *args),
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise StaticWorkflowPlanError(
            "an open/closing authorization lifecycle requires an actual readable Git repository"
        ) from exc
    return completed.stdout.strip()


def _require_actual_git_root(root: Path) -> None:
    top_level = Path(_git(root, "rev-parse", "--show-toplevel")).resolve()
    _require(top_level == root.resolve(), "lifecycle Git verification must run at the repository root")


def _git_json(root: Path, revision: str, relative: str) -> dict[str, Any]:
    try:
        payload = json.loads(_git(root, "show", f"{revision}:{relative}"))
    except json.JSONDecodeError as exc:
        raise StaticWorkflowPlanError(
            f"invalid lifecycle JSON at {revision}:{relative}: {exc}"
        ) from exc
    _require(isinstance(payload, dict), "historical lifecycle JSON root must be an object")
    return payload


def _require_single_parent_transition(root: Path, expected_parent: str) -> str:
    _require_actual_git_root(root)
    head = _full_sha(_git(root, "rev-parse", "HEAD"), "current HEAD")
    ancestry = _git(root, "rev-list", "--parents", "-n", "1", head).split()
    _require(len(ancestry) == 2, "publish lifecycle transition commit must have exactly one parent")
    _require(ancestry[1] == expected_parent, "publish lifecycle transition parent differs")
    changed = _git(
        root,
        "diff",
        "--name-only",
        "--diff-filter=ACDMRTUXB",
        expected_parent,
        head,
    ).splitlines()
    _require(changed == [LIFECYCLE_PATH], "publish lifecycle transition may change only its JSON file")
    committed = _git(root, "show", f"HEAD:{LIFECYCLE_PATH}")
    working = _read(root / LIFECYCLE_PATH)
    _require(
        json.loads(committed) == json.loads(working),
        "working lifecycle file differs from the checked HEAD commit",
    )
    return head


def _require_attempt_record_transition(
    root: Path,
    lifecycle: dict[str, Any],
    closure_commit: str,
) -> str:
    _require_actual_git_root(root)
    committed = _git_json(root, "HEAD", LIFECYCLE_PATH)
    _require(committed == lifecycle, "working lifecycle file differs from the checked HEAD commit")
    record_commit = _full_sha(
        _git(root, "log", "-1", "--format=%H", "--", LIFECYCLE_PATH),
        "attempt evidence record commit",
    )
    ancestry = _git(root, "rev-list", "--parents", "-n", "1", record_commit).split()
    _require(len(ancestry) == 2, "attempt evidence commit must have exactly one parent")
    _require(ancestry[1] == closure_commit, "attempt evidence commit parent differs from closure commit")
    changed = set(_git(
        root,
        "diff",
        "--name-only",
        "--diff-filter=ACDMRTUXB",
        closure_commit,
        record_commit,
    ).splitlines())
    _require(LIFECYCLE_PATH in changed, "attempt evidence commit must update the lifecycle file")
    _require(
        changed <= ATTEMPT_EVIDENCE_CHANGED_PATH_ALLOWLIST,
        f"attempt evidence commit changed an unapproved path: {sorted(changed - ATTEMPT_EVIDENCE_CHANGED_PATH_ALLOWLIST)}",
    )
    recorded = _git_json(root, record_commit, LIFECYCLE_PATH)
    _require(recorded == lifecycle, "stable attempt evidence differs from its record commit")
    return record_commit


def _require_live_settings(lifecycle: dict[str, Any]) -> None:
    settings = lifecycle.get("githubLiveSettings")
    _require(isinstance(settings, dict), "GitHub live settings evidence is missing")
    rechecked_at = settings.get("recheckedAtUtc")
    required = {
        "actionsAllowlistMatchesPlan": True,
        "fullLengthActionShaRequired": True,
        "githubOwnedActionsBlanketAllowed": False,
        "verifiedCreatorsBlanketAllowed": False,
        "forkWriteTokensEnabled": False,
        "forkSecretsEnabled": False,
        "defaultWorkflowPermissions": "read-contents-and-packages",
        "actionsCanApprovePullRequests": False,
        "environmentExists": True,
        "environmentMainOnly": True,
        "environmentSecretsCount": 0,
        "environmentVariablesCount": 0,
        "nativeRequiredReviewerConfigured": False,
        "preventSelfReviewConfigured": False,
    }
    _require(set(settings) == set(required) | {"recheckedAtUtc"}, "GitHub live settings keys changed")
    _require(isinstance(rechecked_at, str), "GitHub live settings recheck timestamp is missing")
    try:
        datetime.strptime(rechecked_at, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise StaticWorkflowPlanError(
            "GitHub live settings recheck timestamp must be UTC YYYY-MM-DDTHH:MM:SSZ"
        ) from exc
    for key, expected in required.items():
        _require(settings.get(key) == expected, f"GitHub live setting differs: {key}")


def _require_refreshed_live_settings(parent: dict[str, Any], current: dict[str, Any]) -> None:
    parent_settings = parent.get("githubLiveSettings")
    current_settings = current.get("githubLiveSettings")
    _require(isinstance(parent_settings, dict), "preparation live-settings evidence is missing")
    _require(isinstance(current_settings, dict), "authorization live-settings evidence is missing")
    parent_without_time = {key: value for key, value in parent_settings.items() if key != "recheckedAtUtc"}
    current_without_time = {key: value for key, value in current_settings.items() if key != "recheckedAtUtc"}
    _require(
        parent_without_time == current_without_time,
        "authorization may refresh only the live-settings recheck timestamp",
    )
    parent_time = _utc_timestamp(parent_settings.get("recheckedAtUtc"), "preparation live-settings timestamp")
    current_time = _utc_timestamp(current_settings.get("recheckedAtUtc"), "authorization live-settings timestamp")
    _require(current_time > parent_time, "authorization must contain a newer live-settings recheck timestamp")


def _require_lifecycle_shape(lifecycle: dict[str, Any]) -> None:
    _require(set(lifecycle) == {
        "schemaVersion",
        "state",
        "publishReviewerGateReady",
        "priorApprovedPreparationSha",
        "priorAttemptEvidence",
        "approvedPreparationSha",
        "ownerApproval",
        "githubLiveSettings",
        "authorizationPolicy",
        "closure",
        "observedAttempt",
    }, "publish lifecycle top-level keys changed")
    _require(lifecycle.get("schemaVersion") == LIFECYCLE_SCHEMA_VERSION, "lifecycle schema changed")
    _require(
        lifecycle.get("priorApprovedPreparationSha") == PRIOR_APPROVED_PREPARATION_SHA,
        "prior owner-approved preparation SHA changed",
    )
    _require(
        lifecycle.get("priorAttemptEvidence") == PRIOR_ATTEMPT_EVIDENCE,
        "prior workflow attempt evidence changed",
    )
    owner = lifecycle.get("ownerApproval")
    _require(isinstance(owner, dict), "owner approval record is missing")
    _require(
        set(owner) == {"recorded", "recordedAtUtc", "evidence"},
        "owner approval record keys changed",
    )
    _require(
        owner.get("evidence") == "exact-40-character-sha-user-message",
        "owner approval evidence type changed",
    )
    policy = lifecycle.get("authorizationPolicy")
    _require(isinstance(policy, dict), "lifecycle authorization policy is missing")
    _require(policy == {
        "authorizationCommitMustBeDirectChild": True,
        "authorizationChangedPaths": [LIFECYCLE_PATH],
        "workflowRunAttemptMustEqual": 1,
        "singleDispatchApiCheckRequired": True,
        "rerunForbidden": True,
        "immediateClosureAfterRunAccepted": True,
    }, "lifecycle authorization policy changed")
    closure = lifecycle.get("closure")
    observed = lifecycle.get("observedAttempt")
    _require(isinstance(closure, dict), "lifecycle closure record is missing")
    _require(isinstance(observed, dict), "lifecycle attempt record is missing")
    _require(
        set(closure) == {"authorizationSourceSha", "preparedAtUtc", "closureCommitSha"},
        "lifecycle closure record keys changed",
    )
    _require(set(observed) == {
        "runId",
        "runUrl",
        "runAttempt",
        "status",
        "conclusion",
        "imageDigest",
        "signatureVerified",
    }, "lifecycle attempt record keys changed")
    _require_live_settings(lifecycle)


def _verify_lifecycle(root: Path, lifecycle: dict[str, Any]) -> dict[str, Any]:
    _require_lifecycle_shape(lifecycle)
    state = lifecycle.get("state")
    gate = lifecycle.get("publishReviewerGateReady")
    owner = lifecycle["ownerApproval"]
    closure = lifecycle["closure"]
    observed = lifecycle["observedAttempt"]

    if state == "preparation-closed":
        _require(gate is False, "preparation lifecycle gate must be false")
        _require(lifecycle.get("approvedPreparationSha") is None, "preparation must not self-authorize")
        _require(owner.get("recorded") is False, "preparation must await a fresh exact-SHA approval")
        _require(owner.get("recordedAtUtc") is None, "preparation approval timestamp must be empty")
        _require(
            closure == {
                "authorizationSourceSha": None,
                "preparedAtUtc": None,
                "closureCommitSha": None,
            },
            "preparation closure record must be empty",
        )
        _require(observed == {
            "runId": None,
            "runUrl": None,
            "runAttempt": None,
            "status": "not-dispatched",
            "conclusion": None,
            "imageDigest": None,
            "signatureVerified": False,
        }, "preparation attempt record must be empty")
        return {
            "state": state,
            "gate": False,
            "approvedPreparationSha": None,
            "result": READY_RESULT,
            "nextSafeStage": NEXT_SAFE_STAGE,
        }

    if state == "authorization-open":
        preparation = _full_sha(
            lifecycle.get("approvedPreparationSha"), "approved preparation SHA"
        )
        _require(gate is True, "authorization-open lifecycle gate must be true")
        _require(owner.get("recorded") is True, "authorization-open owner approval must be recorded")
        _utc_timestamp(owner.get("recordedAtUtc"), "owner approval timestamp")
        head = _require_single_parent_transition(root, preparation)
        parent = _git_json(root, preparation, LIFECYCLE_PATH)
        _require(parent.get("state") == "preparation-closed", "authorization parent must be preparation-closed")
        _require(parent.get("publishReviewerGateReady") is False, "authorization parent gate must be false")
        _require(parent.get("approvedPreparationSha") is None, "authorization parent must not self-authorize")
        _require(
            parent.get("priorAttemptEvidence") == lifecycle.get("priorAttemptEvidence"),
            "authorization changed prior attempt evidence",
        )
        _require_refreshed_live_settings(parent, lifecycle)
        _require(
            closure == {
                "authorizationSourceSha": None,
                "preparedAtUtc": None,
                "closureCommitSha": None,
            },
            "open authorization must not claim closure",
        )
        _require(observed.get("status") == "not-dispatched", "open authorization must not claim dispatch evidence")
        _require(observed.get("runId") is None and observed.get("runAttempt") is None, "open authorization run evidence must be empty")
        return {
            "state": state,
            "gate": True,
            "approvedPreparationSha": preparation,
            "authorizationSourceSha": head,
            "result": AUTHORIZATION_OPEN_RESULT,
            "nextSafeStage": AUTHORIZATION_OPEN_NEXT_SAFE_STAGE,
        }

    if state == "authorization-closed-awaiting-evidence":
        preparation = _full_sha(
            lifecycle.get("approvedPreparationSha"), "approved preparation SHA"
        )
        authorization = _full_sha(
            closure.get("authorizationSourceSha"), "closed authorization source SHA"
        )
        _require(gate is False, "closed authorization lifecycle gate must be false")
        _require(owner.get("recorded") is True, "closed authorization must retain owner approval")
        _utc_timestamp(owner.get("recordedAtUtc"), "owner approval timestamp")
        _utc_timestamp(closure.get("preparedAtUtc"), "closure timestamp")
        _require(closure.get("closureCommitSha") is None, "closure must not self-record its commit SHA")
        _require_single_parent_transition(root, authorization)
        parent = _git_json(root, authorization, LIFECYCLE_PATH)
        _require(parent.get("state") == "authorization-open", "closure parent must be authorization-open")
        _require(parent.get("publishReviewerGateReady") is True, "closure parent gate must be true")
        _require(parent.get("approvedPreparationSha") == preparation, "closure changed approved preparation SHA")
        _require(parent.get("ownerApproval") == owner, "closure changed owner approval evidence")
        _require(
            parent.get("priorAttemptEvidence") == lifecycle.get("priorAttemptEvidence"),
            "closure changed prior attempt evidence",
        )
        _require(
            parent.get("githubLiveSettings") == lifecycle.get("githubLiveSettings"),
            "closure changed GitHub live-settings evidence",
        )
        run_id = observed.get("runId")
        _require(
            isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0,
            "closure must record the accepted positive workflow run ID",
        )
        _require(
            observed.get("runUrl")
            == f"https://github.com/{REPOSITORY}/actions/runs/{run_id}",
            "closure workflow run URL differs from its run ID",
        )
        _require(observed.get("runAttempt") == 1, "only workflow run_attempt 1 may be closed")
        _require(
            observed.get("status") in {"queued", "in_progress", "completed"},
            "closure must follow an accepted workflow dispatch",
        )
        _require(observed.get("conclusion") is None, "full conclusion evidence belongs in attempt-recorded")
        _require(observed.get("imageDigest") is None, "full digest evidence belongs in attempt-recorded")
        _require(observed.get("signatureVerified") is False, "full signature evidence belongs in attempt-recorded")
        return {
            "state": state,
            "gate": False,
            "approvedPreparationSha": preparation,
            "authorizationSourceSha": authorization,
            "result": AUTHORIZATION_CLOSED_RESULT,
            "nextSafeStage": AUTHORIZATION_CLOSED_NEXT_SAFE_STAGE,
        }

    if state == "attempt-recorded":
        preparation = _full_sha(
            lifecycle.get("approvedPreparationSha"), "approved preparation SHA"
        )
        authorization = _full_sha(
            closure.get("authorizationSourceSha"), "recorded authorization source SHA"
        )
        closure_commit = _full_sha(
            closure.get("closureCommitSha"), "recorded closure commit SHA"
        )
        _require(gate is False, "attempt-recorded lifecycle gate must be false")
        _require(owner.get("recorded") is True, "attempt evidence must retain owner approval")
        _utc_timestamp(owner.get("recordedAtUtc"), "owner approval timestamp")
        _utc_timestamp(closure.get("preparedAtUtc"), "closure timestamp")
        record_commit = _require_attempt_record_transition(root, lifecycle, closure_commit)
        closed = _git_json(root, closure_commit, LIFECYCLE_PATH)
        _require(
            closed.get("state") == "authorization-closed-awaiting-evidence",
            "attempt evidence parent must be authorization-closed-awaiting-evidence",
        )
        _require(closed.get("publishReviewerGateReady") is False, "attempt evidence parent gate must be false")
        _require(closed.get("approvedPreparationSha") == preparation, "attempt evidence changed preparation SHA")
        _require(closed.get("ownerApproval") == owner, "attempt evidence changed owner approval")
        _require(
            closed.get("priorAttemptEvidence") == lifecycle.get("priorAttemptEvidence"),
            "attempt evidence changed prior attempt evidence",
        )
        _require(
            closed.get("githubLiveSettings") == lifecycle.get("githubLiveSettings"),
            "attempt evidence changed GitHub live-settings evidence",
        )
        _require(
            closed.get("closure", {}).get("authorizationSourceSha") == authorization,
            "attempt evidence changed authorization source SHA",
        )
        _require(
            closed.get("closure", {}).get("closureCommitSha") is None,
            "attempt evidence parent must not self-record its commit SHA",
        )
        _require(
            closed.get("closure", {}).get("preparedAtUtc") == closure.get("preparedAtUtc"),
            "attempt evidence changed the closure timestamp",
        )
        closure_ancestry = _git(root, "rev-list", "--parents", "-n", "1", closure_commit).split()
        _require(
            len(closure_ancestry) == 2 and closure_ancestry[1] == authorization,
            "recorded closure commit is not a direct child of its authorization",
        )
        closure_changed = _git(
            root,
            "diff",
            "--name-only",
            "--diff-filter=ACDMRTUXB",
            authorization,
            closure_commit,
        ).splitlines()
        _require(closure_changed == [LIFECYCLE_PATH], "recorded closure changed an unapproved path")
        opened = _git_json(root, authorization, LIFECYCLE_PATH)
        _require(opened.get("state") == "authorization-open", "recorded authorization must be open")
        _require(opened.get("publishReviewerGateReady") is True, "recorded authorization gate was not open")
        _require(opened.get("approvedPreparationSha") == preparation, "recorded authorization preparation differs")
        authorization_ancestry = _git(root, "rev-list", "--parents", "-n", "1", authorization).split()
        _require(
            len(authorization_ancestry) == 2 and authorization_ancestry[1] == preparation,
            "recorded authorization is not a direct child of its preparation",
        )
        authorization_changed = _git(
            root,
            "diff",
            "--name-only",
            "--diff-filter=ACDMRTUXB",
            preparation,
            authorization,
        ).splitlines()
        _require(authorization_changed == [LIFECYCLE_PATH], "recorded authorization changed an unapproved path")
        prepared = _git_json(root, preparation, LIFECYCLE_PATH)
        _require(prepared.get("state") == "preparation-closed", "recorded preparation must be closed")
        _require(prepared.get("publishReviewerGateReady") is False, "recorded preparation gate must be false")
        _require(prepared.get("approvedPreparationSha") is None, "recorded preparation must not self-authorize")
        run_id = observed.get("runId")
        _require(
            isinstance(run_id, int) and not isinstance(run_id, bool) and run_id > 0,
            "recorded workflow run ID must be a positive integer",
        )
        _require(
            observed.get("runUrl")
            == f"https://github.com/{REPOSITORY}/actions/runs/{run_id}",
            "recorded workflow run URL differs from its run ID",
        )
        closed_observed = closed.get("observedAttempt", {})
        _require(closed_observed.get("runId") == run_id, "attempt evidence changed the accepted run ID")
        _require(closed_observed.get("runUrl") == observed.get("runUrl"), "attempt evidence changed the accepted run URL")
        _require(closed_observed.get("runAttempt") == 1, "closure did not record first workflow attempt")
        _require(observed.get("runAttempt") == 1, "only workflow run_attempt 1 may be recorded")
        _require(observed.get("status") == "completed", "attempt evidence must be completed")
        conclusion = observed.get("conclusion")
        _require(conclusion in {
            "success",
            "failure",
            "neutral",
            "cancelled",
            "skipped",
            "timed_out",
            "action_required",
            "stale",
            "startup_failure",
        }, "recorded workflow conclusion is invalid")
        digest = observed.get("imageDigest")
        _require(
            digest is None
            or (isinstance(digest, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", digest)),
            "recorded image digest must be null or an exact sha256 digest",
        )
        signature_verified = observed.get("signatureVerified")
        _require(isinstance(signature_verified, bool), "signature verification evidence must be boolean")
        if conclusion == "success":
            _require(digest is not None, "successful workflow must record the exact image digest")
            _require(signature_verified is True, "successful workflow must record verified signature evidence")
        return {
            "state": state,
            "gate": False,
            "approvedPreparationSha": preparation,
            "authorizationSourceSha": authorization,
            "closureCommitSha": closure_commit,
            "attemptRecordCommitSha": record_commit,
            "result": ATTEMPT_RECORDED_RESULT,
            "nextSafeStage": ATTEMPT_RECORDED_NEXT_SAFE_STAGE,
        }

    raise StaticWorkflowPlanError(f"unsupported publish lifecycle state: {state!r}")


def _canonical_sha256(payload: Any) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _string_scalars(payload: Any, path: tuple[Any, ...] = ()):
    if isinstance(payload, dict):
        for key, value in payload.items():
            yield from _string_scalars(value, path + (key,))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            yield from _string_scalars(value, path + (index,))
    elif isinstance(payload, str):
        yield path, payload


def _verify_dockerignore(dockerignore: str) -> None:
    lines = {
        line.strip()
        for line in dockerignore.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    missing = set(DOCKERIGNORE_ENV_PATTERNS) - lines
    _require(not missing, f"Docker build context environment excludes are missing: {sorted(missing)}")
    allowed_negations = {"!deploy/secrets/README.md"}
    unsafe_reincludes = sorted(
        line for line in lines if line.startswith("!") and line not in allowed_negations
    )
    _require(
        not unsafe_reincludes,
        f"Docker build context has an unreviewed negation that could re-include secrets: {unsafe_reincludes}",
    )


def _verify_reproducibility_files(root: Path) -> None:
    for relative, expected in {**LOCK_SHA256, **REPRODUCIBILITY_INPUT_SHA256}.items():
        path = root / relative
        _require(path.is_file(), f"reproducibility input is missing: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        _require(actual == expected, f"reproducibility input SHA-256 changed: {relative}")

    dockerfile = _read(root / "backend/Dockerfile.production")
    _require(
        dockerfile.splitlines()[0] == f"# syntax={DOCKERFILE_FRONTEND}",
        "Dockerfile frontend must remain version-and-digest pinned",
    )
    for marker in (
        "backend/requirements/pip-bootstrap.lock",
        "backend/requirements/runtime-linux-amd64-py311.lock",
        "--require-hashes",
        "--only-binary=:all:",
        "--no-index",
        "--platform manylinux_2_17_x86_64",
        "--python-version 3.11",
    ):
        _require(marker in dockerfile, f"production Dockerfile lock marker is missing: {marker}")
    _require("pip install --upgrade pip" not in dockerfile, "mutable pip upgrade is forbidden")
    _require("python -m pip install ." not in dockerfile, "production install must use the runtime hash lock")

    pyproject = _read(root / "backend/pyproject.toml")
    _require(
        'requires = ["setuptools==80.10.2", "wheel==0.46.3"]' in pyproject,
        "Python build-system requirements must remain exact-pinned",
    )


def _verify_transient_core_smoke_skip(smoke_core: str) -> None:
    expected_block = "\n".join((
        'if [[ "${SKIP_GHCR_HANDOFF_SMOKES:-0}" != "1" ]]; then',
        f"  {SKIPPABLE_CLOSED_ROOT_SMOKES[0]}",
        f"  {SKIPPABLE_CLOSED_ROOT_SMOKES[1]}",
        f"  {SKIPPABLE_CLOSED_ROOT_SMOKES[2]}",
        "fi",
    ))
    _require(expected_block in smoke_core, "closed-root smoke skip block changed")
    skip_lines = [
        line for line in smoke_core.splitlines() if TRANSIENT_SMOKE_SKIP_VARIABLE in line
    ]
    _require(
        skip_lines == ['if [[ "${SKIP_GHCR_HANDOFF_SMOKES:-0}" != "1" ]]; then'],
        "transient smoke skip flag may control only the reviewed three-smoke block",
    )
    for command in SKIPPABLE_CLOSED_ROOT_SMOKES:
        _require(
            smoke_core.count(command) == 1,
            f"closed-root smoke command must appear exactly once: {command}",
        )


def _load_workflow(workflow: str) -> dict[str, Any]:
    try:
        payload = yaml.load(workflow, Loader=GitHubActionsLoader)
    except yaml.YAMLError as exc:
        raise StaticWorkflowPlanError(f"invalid workflow YAML: {exc}") from exc
    _require(isinstance(payload, dict), "workflow YAML root must be an object")
    return payload


def _workflow_steps(job: dict[str, Any], name: str) -> list[dict[str, Any]]:
    steps = job.get("steps")
    _require(isinstance(steps, list) and steps, f"workflow job has no steps: {name}")
    _require(all(isinstance(step, dict) for step in steps), f"workflow job has an invalid step: {name}")
    allowed_keys = {"name", "uses", "with", "run", "env", "id", "if"}
    names: list[str] = []
    for step in steps:
        _require(set(step) <= allowed_keys, f"workflow step has unsafe keys in {name}: {set(step) - allowed_keys}")
        _require("continue-on-error" not in step, f"continue-on-error is forbidden: {name}")
        step_name = step.get("name")
        _require(isinstance(step_name, str) and step_name, f"workflow step name is missing: {name}")
        names.append(step_name)
    _require(len(names) == len(set(names)), f"duplicate workflow step name: {name}")
    return steps


def _step_by_name(steps: list[dict[str, Any]], name: str) -> dict[str, Any]:
    matches = [step for step in steps if step.get("name") == name]
    _require(len(matches) == 1, f"workflow step is missing or duplicated: {name}")
    return matches[0]


def _verify_workflow(workflow: str) -> None:
    actual_workflow_sha256 = hashlib.sha256(workflow.encode("utf-8")).hexdigest()
    _require(
        actual_workflow_sha256 == EXPECTED_WORKFLOW_SHA256,
        "workflow source differs from the reviewed SHA-256 lock",
    )
    payload = _load_workflow(workflow)
    actual_semantic_sha256 = _canonical_sha256(payload)
    _require(
        actual_semantic_sha256 == EXPECTED_WORKFLOW_SEMANTIC_SHA256,
        "workflow execution semantics differ from the reviewed SHA-256 lock",
    )
    _require(
        set(payload) == {"name", "on", "permissions", "concurrency", "env", "jobs"},
        "workflow top-level keys changed",
    )
    _require(payload.get("name") == "Publish backend image candidate to GHCR", "workflow name changed")

    triggers = payload.get("on")
    _require(isinstance(triggers, dict), "workflow on block must be an object")
    _require(set(triggers) == {"workflow_dispatch"}, "only workflow_dispatch is allowed")
    dispatch = triggers.get("workflow_dispatch")
    _require(isinstance(dispatch, dict) and set(dispatch) == {"inputs"}, "workflow_dispatch shape changed")
    inputs = dispatch.get("inputs")
    _require(isinstance(inputs, dict), "workflow_dispatch inputs are missing")
    _require(
        set(inputs) == {
            "source_commit",
            "approved_preparation_commit",
            "approval_reason",
            "confirm_publish",
        },
        "workflow inputs changed",
    )
    _require(inputs["source_commit"].get("required") is True, "source_commit must be required")
    _require(inputs["source_commit"].get("type") == "string", "source_commit must be a string")
    _require(
        inputs["approved_preparation_commit"].get("required") is True,
        "approved_preparation_commit must be required",
    )
    _require(
        inputs["approved_preparation_commit"].get("type") == "string",
        "approved_preparation_commit must be a string",
    )
    _require(inputs["approval_reason"].get("required") is True, "approval_reason must be required")
    _require(inputs["approval_reason"].get("type") == "string", "approval_reason must be a string")
    _require(inputs["confirm_publish"].get("required") is True, "confirm_publish must be required")
    _require(inputs["confirm_publish"].get("type") == "boolean", "confirm_publish must be boolean")
    _require(inputs["confirm_publish"].get("default") is False, "confirm_publish must default to false")

    _require(payload.get("permissions") == {"contents": "read"}, "workflow default permissions changed")
    _require(
        payload.get("concurrency") == {"group": "ghcr-backend-publish", "cancel-in-progress": False},
        "workflow concurrency policy changed",
    )
    _require(
        payload.get("env") == {
            "IMAGE_REPOSITORY": IMAGE_REPOSITORY,
            "CERTIFICATE_IDENTITY": CERTIFICATE_IDENTITY,
            "OIDC_ISSUER": "https://token.actions.githubusercontent.com",
            "PUBLISH_LIFECYCLE_PATH": LIFECYCLE_PATH,
            "DOCKER_BUILD_RECORD_UPLOAD": "false",
        },
        "workflow global environment changed",
    )

    jobs = payload.get("jobs")
    _require(isinstance(jobs, dict), "workflow jobs block must be an object")
    _require(set(jobs) == {"validate", "build_scan", "publish_sign_verify"}, "workflow job set changed")
    validate = jobs["validate"]
    build_scan = jobs["build_scan"]
    publish = jobs["publish_sign_verify"]
    _require(isinstance(validate, dict) and isinstance(build_scan, dict) and isinstance(publish, dict), "workflow job is invalid")
    _require(set(validate) == {"name", "runs-on", "permissions", "steps"}, "validate job keys changed")
    _require(set(build_scan) == {"name", "needs", "runs-on", "steps"}, "build_scan job keys changed")
    _require(
        set(publish) == {"name", "needs", "runs-on", "environment", "permissions", "steps"},
        "publish job keys changed",
    )
    _require(validate.get("runs-on") == "ubuntu-latest", "validate runner changed")
    _require(
        validate.get("permissions") == {"actions": "read", "contents": "read"},
        "validate job must have actions=read and contents=read only",
    )
    _require(build_scan.get("runs-on") == "ubuntu-latest" and build_scan.get("needs") == "validate", "build_scan dependency changed")
    _require(publish.get("runs-on") == "ubuntu-latest" and publish.get("needs") == "build_scan", "publish dependency changed")
    _require(publish.get("environment") == "ghcr-production-publish", "publish environment changed")
    _require(
        publish.get("permissions") == {"contents": "read", "packages": "write", "id-token": "write"},
        "publish permissions changed",
    )

    validate_steps = _workflow_steps(validate, "validate")
    build_steps = _workflow_steps(build_scan, "build_scan")
    publish_steps = _workflow_steps(publish, "publish_sign_verify")
    expected_step_names = {
        "validate": [
            "Check manual approval inputs",
            "Require exactly one first-attempt dispatch for this authorization",
            "Check out exact source commit",
            "Verify source-controlled authorization transition",
            "Set up Python 3.11.15",
            "Install backend validation dependencies",
            "Run fail-closed repository checks",
        ],
        "build_scan": [
            "Check out exact source commit",
            "Set up Python 3.11.15",
            "Set up Docker Buildx",
            "Build local linux/amd64 image without registry mutation",
            "Generate local SPDX JSON SBOM",
            "Validate local SBOM structure",
            "Install checksum-pinned Trivy 0.70.0",
            "Block HIGH and CRITICAL vulnerabilities in local image",
            "Validate local Trivy JSON evidence",
            "Retain non-secret review artifacts",
        ],
        "publish_sign_verify": [
            "Check out exact source commit",
            "Enforce owner-only two-step authorization gate before registry access",
            "Set up Python 3.11.15",
            "Set up Docker Buildx",
            "Install checksum-pinned Trivy 0.70.0",
            "Log in to GHCR with ephemeral GITHUB_TOKEN",
            "Build and push digest candidate with BuildKit attestations",
            "Record exact pushed digest",
            "Inspect BuildKit provenance and SBOM on exact digest",
            "Block vulnerabilities in exact pushed digest before signing",
            "Validate exact-digest Trivy JSON evidence",
            "Set up Cosign",
            "Sign exact digest with GitHub OIDC after all image gates",
            "Verify Cosign certificate identity and issuer",
            "Retain exact-digest evidence",
            "Emit verified candidate digest",
        ],
    }
    for job_name, steps in (
        ("validate", validate_steps),
        ("build_scan", build_steps),
        ("publish_sign_verify", publish_steps),
    ):
        _require(
            [step["name"] for step in steps] == expected_step_names[job_name],
            f"workflow step set or order changed: {job_name}",
        )

    actual_action_step_sha256: dict[str, str] = {}
    actual_run_step_sha256: dict[str, str] = {}
    for job_name, steps in (
        ("validate", validate_steps),
        ("build_scan", build_steps),
        ("publish_sign_verify", publish_steps),
    ):
        for step in steps:
            step_key = f"{job_name}:{step['name']}"
            if "uses" in step:
                actual_action_step_sha256[step_key] = _canonical_sha256(step)
            if "run" in step:
                run = step.get("run")
                _require(isinstance(run, str), f"workflow run body is not text: {step_key}")
                actual_run_step_sha256[step_key] = hashlib.sha256(run.encode("utf-8")).hexdigest()

    _require(
        actual_action_step_sha256 == EXPECTED_ACTION_STEP_SHA256,
        "an action step definition differs from the reviewed per-step lock",
    )
    _require(
        actual_run_step_sha256 == EXPECTED_RUN_STEP_SHA256,
        "a run step body differs from the reviewed per-step lock",
    )
    _require(
        set(actual_run_step_sha256) == set(EXPECTED_RUN_STEP_ENV),
        "run step environment lock set changed",
    )
    for job_name, steps in (
        ("validate", validate_steps),
        ("build_scan", build_steps),
        ("publish_sign_verify", publish_steps),
    ):
        for step in steps:
            if "run" not in step:
                continue
            step_key = f"{job_name}:{step['name']}"
            expected_env = EXPECTED_RUN_STEP_ENV[step_key]
            expected_keys = {"name", "run"} if expected_env is None else {"name", "run", "env"}
            _require(set(step) == expected_keys, f"run step keys changed: {step_key}")
            if expected_env is not None:
                _require(step.get("env") == expected_env, f"run step environment changed: {step_key}")

    repository_checks = _step_by_name(validate_steps, "Run fail-closed repository checks")
    repository_checks_run = repository_checks.get("run")
    _require(isinstance(repository_checks_run, str), "repository checks command is missing")
    repository_check_lines = repository_checks_run.splitlines()
    _require(
        repository_check_lines.count(DIRECT_STATIC_STRICT_COMMAND) == 1,
        "workflow must run the lifecycle-aware static checker directly exactly once",
    )
    _require(
        repository_check_lines.count(TRANSIENT_SMOKE_SKIP_COMMAND) == 1,
        "workflow transient smoke skip command changed",
    )
    _require(
        repository_check_lines.index(DIRECT_STATIC_STRICT_COMMAND)
        < repository_check_lines.index(TRANSIENT_SMOKE_SKIP_COMMAND),
        "direct static strict check must run before transient core-smoke skip",
    )
    _require(
        "bash tools/run_smoke_core.sh" not in repository_check_lines,
        "workflow must not run the closed-root smoke baseline without its transient scope flag",
    )

    secret_expression = re.compile(
        r"(?:\bsecrets\s*(?:\.|\[)|\bgithub\.token\b|"
        r"\bgithub\s*\[\s*['\"]token['\"]\s*\]|"
        r"tojson\s*\(\s*(?:secrets|github)\s*\))",
        re.IGNORECASE,
    )
    sensitive_scalars = [
        (path, value)
        for path, value in _string_scalars(payload)
        if secret_expression.search(value)
    ]
    _require(
        sensitive_scalars == [
            (
                ("jobs", "validate", "steps", 1, "env", "ACTIONS_TOKEN"),
                "${{ secrets.GITHUB_TOKEN }}",
            ),
            (
                ("jobs", "publish_sign_verify", "steps", 5, "with", "password"),
                "${{ secrets.GITHUB_TOKEN }}",
            ),
        ],
        "workflow secret/token expression is outside the two approved GITHUB_TOKEN paths",
    )
    for step in (*validate_steps, *build_steps, *publish_steps):
        if "if" in step:
            allowed_conditions = {
                "Retain non-secret review artifacts": "always()",
                "Retain exact-digest evidence": "${{ always() && steps.publish.outputs.digest != '' }}",
            }
            _require(
                allowed_conditions.get(step.get("name")) == step.get("if"),
                f"unexpected conditional step: {step.get('name')}",
            )

    uses_values = [
        step["uses"]
        for step in (*validate_steps, *build_steps, *publish_steps)
        if "uses" in step
    ]
    used_repositories: set[str] = set()
    for value in uses_values:
        _require(isinstance(value, str), "workflow action reference must be text")
        match = re.fullmatch(r"([^@\s]+)@([0-9a-f]{40})", value)
        _require(match is not None, f"action is not pinned to a full SHA: {value}")
        repository, sha = match.groups()
        _require(repository in EXPECTED_ACTIONS, f"action is outside the allowlist: {repository}")
        _require(sha == EXPECTED_ACTIONS[repository][1], f"action SHA changed: {repository}")
        used_repositories.add(repository)
    _require(used_repositories == set(EXPECTED_ACTIONS), "workflow action set differs from the allowlist")

    local_build = _step_by_name(build_steps, "Build local linux/amd64 image without registry mutation")
    _require(
        local_build.get("with") == {
            "context": ".",
            "file": "backend/Dockerfile.production",
            "platforms": "linux/amd64",
            "load": True,
            "push": False,
            "tags": "upgrade-rpg-backend:scan-${{ github.sha }}",
        },
        "local build inputs changed",
    )
    local_upload = _step_by_name(build_steps, "Retain non-secret review artifacts")
    _require(local_upload.get("with", {}).get("if-no-files-found") == "error", "local evidence files must be required")

    trivy_install_env = {
        "TRIVY_VERSION": "0.70.0",
        "TRIVY_SHA256": "8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9",
    }
    for steps, job_name in ((build_steps, "build_scan"), (publish_steps, "publish_sign_verify")):
        install_step = _step_by_name(steps, "Install checksum-pinned Trivy 0.70.0")
        _require(install_step.get("env") == trivy_install_env, f"Trivy install lock changed: {job_name}")
        install_run = install_step.get("run")
        _require(isinstance(install_run, str), f"Trivy install command is missing: {job_name}")
        for marker in (
            "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/",
            "sha256sum --check --strict",
            "tar -xzf",
        ):
            _require(marker in install_run, f"Trivy install marker is missing in {job_name}: {marker}")

    for steps, step_name, expected_output in (
        (build_steps, "Block HIGH and CRITICAL vulnerabilities in local image", "trivy-results.json"),
        (publish_steps, "Block vulnerabilities in exact pushed digest before signing", "published-trivy-results.json"),
    ):
        scan_step = _step_by_name(steps, step_name)
        scan_run = scan_step.get("run")
        _require(isinstance(scan_run, str), f"Trivy scan command is missing: {step_name}")
        for marker in (
            "--scanners vuln",
            "--pkg-types os,library",
            "--severity HIGH,CRITICAL",
            "--ignore-unfixed=false",
            f"--output {expected_output}",
            "--exit-code 1",
        ):
            _require(marker in scan_run, f"Trivy scan marker is missing in {step_name}: {marker}")

    validate_checkout = _step_by_name(validate_steps, "Check out exact source commit")
    publish_checkout = _step_by_name(publish_steps, "Check out exact source commit")
    for checkout, job_name in ((validate_checkout, "validate"), (publish_checkout, "publish_sign_verify")):
        _require(
            checkout.get("with") == {
                "ref": "${{ inputs.source_commit }}",
                "fetch-depth": 2,
                "persist-credentials": False,
            },
            f"{job_name} lifecycle checkout must fetch exactly the source and its parent",
        )

    gate = _step_by_name(
        publish_steps,
        "Enforce owner-only two-step authorization gate before registry access",
    )
    _require(
        gate.get("env") == {
            "APPROVED_PREPARATION_COMMIT": "${{ inputs.approved_preparation_commit }}",
            "SOURCE_COMMIT": "${{ inputs.source_commit }}",
            "EXPECTED_RUN_ATTEMPT": "${{ github.run_attempt }}",
        },
        "publish lifecycle gate environment changed",
    )
    _require("vars." not in workflow, "repository/environment vars must not control the reviewer gate")

    publish_names = [step["name"] for step in publish_steps]
    ordered_names = (
        "Enforce owner-only two-step authorization gate before registry access",
        "Log in to GHCR with ephemeral GITHUB_TOKEN",
        "Build and push digest candidate with BuildKit attestations",
        "Inspect BuildKit provenance and SBOM on exact digest",
        "Block vulnerabilities in exact pushed digest before signing",
        "Set up Cosign",
        "Sign exact digest with GitHub OIDC after all image gates",
        "Verify Cosign certificate identity and issuer",
        "Emit verified candidate digest",
    )
    indices = [publish_names.index(name) if name in publish_names else -1 for name in ordered_names]
    _require(all(index >= 0 for index in indices), "publish/sign/verify step is missing")
    _require(indices == sorted(indices), "publish/sign/verify order changed")
    _require(
        publish_names.index("Enforce owner-only two-step authorization gate before registry access")
        < publish_names.index("Log in to GHCR with ephemeral GITHUB_TOKEN"),
        "publish lifecycle gate must run before GHCR login",
    )
    publish_build = _step_by_name(publish_steps, "Build and push digest candidate with BuildKit attestations")
    _require(
        publish_build.get("with") == {
            "context": ".",
            "file": "backend/Dockerfile.production",
            "platforms": "linux/amd64",
            "push": True,
            "tags": "${{ env.IMAGE_REPOSITORY }}:unverified-sha-${{ github.sha }}",
            "provenance": "mode=max",
            "sbom": True,
        },
        "publish build inputs changed",
    )

    for marker in (
        "SOURCE_COMMIT: ${{ inputs.source_commit }}",
        "APPROVED_PREPARATION_COMMIT: ${{ inputs.approved_preparation_commit }}",
        "EXPECTED_GITHUB_REF: ${{ github.ref }}",
        "EXPECTED_RUN_ATTEMPT: ${{ github.run_attempt }}",
        "EXPECTED_ACTOR: ${{ github.actor }}",
        "EXPECTED_REPOSITORY_OWNER: ${{ github.repository_owner }}",
        'require(os.environ["EXPECTED_RUN_ATTEMPT"] == "1", "workflow re-runs are forbidden")',
        'require(os.environ["EXPECTED_ACTOR"] == os.environ["EXPECTED_REPOSITORY_OWNER"], "only the repository owner may publish")',
        "actions/workflows/",
        "more than one dispatch exists for this authorization commit",
        "authorization commit may change only the publish lifecycle file",
        "refs/heads/main",
        "fetch-depth: 2",
        "persist-credentials: false",
        'DOCKER_BUILD_RECORD_UPLOAD: "false"',
        "python-version: \"3.11.15\"",
        "backend/requirements/pip-bootstrap.lock",
        "backend/requirements/dev-linux-amd64-py311.lock",
        "--require-hashes",
        "--only-binary=:all:",
        "python tools/generate_backend_linux_dependency_locks.py --check",
        "python tools/check_github_actions_ghcr_static_plan.py --strict",
        "bash tools/run_smoke_core.sh",
        "TRIVY_VERSION: \"0.70.0\"",
        "TRIVY_SHA256: 8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9",
        "sha256sum --check --strict",
        "--severity HIGH,CRITICAL",
        "--ignore-unfixed=false",
        "--exit-code 1",
        "published-trivy-results.json",
        'require(lifecycle.get("state") == "authorization-open", "publish authorization is not open")',
        'require(lifecycle.get("publishReviewerGateReady") is True, "publish gate is not source-controlled true")',
        "password: ${{ secrets.GITHUB_TOKEN }}",
        "[[ \"$DIGEST\" =~ ^sha256:[0-9a-f]{64}$ ]]",
        "cosign sign --yes \"$IMAGE_REPOSITORY@$DIGEST\"",
        "docker buildx imagetools inspect",
        "--format '{{ json .Provenance }}'",
        "--format '{{ json .SBOM }}'",
        "cosign verify",
        '--certificate-identity "$CERTIFICATE_IDENTITY"',
        '--certificate-oidc-issuer "$OIDC_ISSUER"',
        "Verified candidate: $IMAGE_REPOSITORY@$DIGEST",
        "${{ always() && steps.publish.outputs.digest != '' }}",
    ):
        _require(marker in workflow, f"workflow security marker is missing: {marker}")
    _require(
        workflow.count(
            'require(os.environ["EXPECTED_RUN_ATTEMPT"] == "1", '
            '"workflow re-runs are forbidden")'
        ) == 4,
        "every input, dispatch, validation, and publish gate must reject workflow re-runs",
    )
    _require(
        workflow.count('require(run.get("run_attempt") == 1, "workflow re-runs are forbidden")') == 1,
        "the unique-dispatch API response must prove run_attempt 1",
    )
    _require(
        workflow.count("actions/workflows/") == 1,
        "exactly one Actions workflow-runs API lookup is required",
    )
    for forbidden in ("actions/attest", "aquasecurity/trivy-action", "attestations: write", ".trivyignore", ":latest"):
        _require(forbidden not in workflow, f"forbidden workflow marker found: {forbidden}")

    secret_references = set(re.findall(r"secrets\.([A-Za-z0-9_]+)", workflow))
    _require(secret_references == {"GITHUB_TOKEN"}, "workflow may reference only ephemeral GITHUB_TOKEN")


def inspect_static_workflow_plan(root: Path) -> dict[str, Any]:
    plan = _read_json(root / "deploy/github-actions-ghcr-static-plan.example.json")
    lifecycle = _read_json(root / LIFECYCLE_PATH)
    document = _read(root / "docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md")
    workflow = _read(root / WORKFLOW_PATH)
    smoke_core = _read(root / SMOKE_CORE_PATH)
    dockerignore = _read(root / ".dockerignore")
    gitattributes = _read(root / ".gitattributes")

    _require(plan.get("schemaVersion") == TOOL_VERSION, "unexpected v324 schemaVersion")
    _require(_bool(plan, "staticPolicyOnly") is True, "plan must remain state-independent policy")
    _require(
        plan.get("publishApprovalModel") == "owner-only-source-controlled-two-step",
        "owner-only publish approval model changed",
    )
    _require(plan.get("publishApprovalModelOptions") == [
        "github-enterprise-cloud-required-reviewer",
        "owner-only-source-controlled-two-step",
        "keep-publishing-disabled",
    ], "publish approval model options changed")
    _require(plan.get("githubRemote") == REMOTE, "GitHub remote changed")
    _require(plan.get("repository") == REPOSITORY, "GitHub repository changed")
    _require(plan.get("defaultBranch") == "main", "default branch must remain main")
    _require(plan.get("registry") == "ghcr.io", "registry must remain GHCR")
    _require(plan.get("imageRepository") == IMAGE_REPOSITORY, "image repository changed")
    _require(plan.get("targetPlatform") == "linux/amd64", "target platform changed")
    _require(plan.get("repositoryTextLineEnding") == "lf", "repository text line-ending policy changed")
    _require("* text=auto eol=lf" in gitattributes.splitlines(), "repository text files must remain LF-normalized")
    _require(plan.get("workflowPath") == WORKFLOW_PATH, "workflow path changed")
    _require(plan.get("publishLifecyclePath") == LIFECYCLE_PATH, "publish lifecycle path changed")
    _require(
        plan.get("publishLifecycleSchemaVersion") == LIFECYCLE_SCHEMA_VERSION,
        "publish lifecycle schema policy changed",
    )
    _require(
        plan.get("workflowSourceSha256") == EXPECTED_WORKFLOW_SHA256,
        "reviewed workflow source SHA-256 changed",
    )
    _require(
        plan.get("workflowSemanticSha256") == EXPECTED_WORKFLOW_SEMANTIC_SHA256,
        "reviewed workflow semantic SHA-256 changed",
    )
    build_context = plan.get("dockerBuildContextPolicy")
    _require(isinstance(build_context, dict), "Docker build context policy is missing")
    _require(build_context.get("context") == ".", "Docker build context policy changed")
    _require(build_context.get("dockerignore") == ".dockerignore", "Docker ignore policy changed")
    _require(
        build_context.get("requiredEnvironmentExcludes") == list(DOCKERIGNORE_ENV_PATTERNS),
        "Docker environment exclude policy changed",
    )
    _require(build_context.get("environmentReincludeAllowed") is False, "environment re-includes are forbidden")
    _require(
        build_context.get("environmentExamplesSentToBuildContext") is False,
        "environment examples must stay outside the Docker build context",
    )
    _require(
        build_context.get("dockerfileSpecificIgnoreAllowed") is False,
        "Dockerfile-specific ignore override must remain forbidden",
    )
    _require(
        not (root / "backend/Dockerfile.production.dockerignore").exists(),
        "backend/Dockerfile.production.dockerignore would override the reviewed root .dockerignore",
    )
    _verify_dockerignore(dockerignore)
    _verify_reproducibility_files(root)
    for key in (
        "workflowFilePresent",
        "workflowCreationApproved",
        "workflowExecutionApproved",
        "workflowExecutionEvidenceTrackedInLifecycle",
        "publishExecutionAuthorizationTrackedInLifecycle",
        "registryLoginApproved",
        "imageBuildApproved",
        "imagePushApproved",
        "registryMutationApproved",
        "registryMutationEvidenceTrackedInLifecycle",
    ):
        _require(_bool(plan, key) is True, f"approved v324 policy must remain true: {key}")

    owner_policy = plan.get("ownerOnlyApprovalPolicy")
    _require(isinstance(owner_policy, dict), "owner-only approval policy is missing")
    _require(owner_policy.get("selectedOn") == "2026-07-20", "owner-only selection date changed")
    _require(
        owner_policy.get("phase") == "bootstrap-fixed-retry-preparation",
        "owner-only lifecycle policy phase changed",
    )
    for key in (
        "riskAcceptedByOwner",
        "exactPreparationShaApprovalRequired",
        "separateAuthorizationCommitRequired",
        "oneWorkflowRunPerAuthorization",
        "repositoryOwnerActorRequired",
        "singleDispatchApiCheckRequired",
        "gateRecloseRequiredAfterEveryAttempt",
        "closureCommitImmediatelyAfterRunAccepted",
        "liveGitHubSettingsRecheckRequiredBeforeAuthorization",
    ):
        _require(owner_policy.get(key) is True, f"owner-only safety rule must remain true: {key}")
    _require(owner_policy.get("runAttemptMustEqual") == 1, "only workflow run_attempt 1 is allowed")
    _require(
        owner_policy.get("authorizationChangedPaths") == [LIFECYCLE_PATH],
        "authorization commit path policy changed",
    )
    _require(owner_policy.get("allowedLifecycleStates") == [
        "preparation-closed",
        "authorization-open",
        "authorization-closed-awaiting-evidence",
        "attempt-recorded",
    ], "allowed publish lifecycle states changed")

    transient_smoke = plan.get("transientAuthorizationSmokePolicy")
    _require(isinstance(transient_smoke, dict), "transient authorization smoke policy is missing")
    _require(transient_smoke == {
        "environmentVariable": TRANSIENT_SMOKE_SKIP_VARIABLE,
        "enabledValue": "1",
        "workflowCommand": TRANSIENT_SMOKE_SKIP_COMMAND,
        "directStaticStrictCommand": DIRECT_STATIC_STRICT_COMMAND,
        "directStaticStrictMustPrecedeCoreSmoke": True,
        "skippedClosedRootSmokes": list(SKIPPABLE_CLOSED_ROOT_SMOKES),
        "allOtherCoreSmokesRemainRequired": True,
    }, "transient authorization smoke policy changed")

    attempt_evidence = plan.get("attemptEvidencePolicy")
    _require(isinstance(attempt_evidence, dict), "attempt evidence policy is missing")
    _require(attempt_evidence == {
        "state": "attempt-recorded",
        "gateMustRemainClosed": True,
        "closureCommitShaMustReferenceDirectParentClosure": True,
        "lifecyclePathRequiredInFirstRecordCommit": True,
        "firstRecordChangedPathAllowlist": sorted(ATTEMPT_EVIDENCE_CHANGED_PATH_ALLOWLIST),
        "codeWorkflowCheckerChangesAllowed": False,
        "stableRecordedStateAllowedAfterFirstRecordCommit": True,
        "nextPreparationPreservesPriorAttemptEvidence": True,
        "successRequiresDigestAndVerifiedSignature": True,
    }, "attempt evidence policy changed")

    trigger = plan.get("triggerPolicy")
    _require(isinstance(trigger, dict), "triggerPolicy must be an object")
    _require(trigger.get("allowedEvents") == ["workflow_dispatch"], "only workflow_dispatch is allowed")
    forbidden_events = trigger.get("forbiddenEvents")
    _require(isinstance(forbidden_events, list), "forbiddenEvents must be a list")
    for event in ("push", "pull_request", "pull_request_target", "schedule", "release", "repository_dispatch", "workflow_run"):
        _require(event in forbidden_events, f"unsafe trigger is not forbidden: {event}")
    _require(trigger.get("requiredRef") == "refs/heads/main", "required ref must remain main")
    source_commit = trigger.get("sourceCommitInput")
    _require(isinstance(source_commit, dict), "sourceCommitInput must be an object")
    _require(source_commit.get("required") is True, "source_commit must be required")
    _require(source_commit.get("pattern") == "^[0-9a-f]{40}$", "source_commit pattern changed")
    _require(source_commit.get("mustEqualGithubSha") is True, "source_commit must equal github.sha")
    preparation_commit = trigger.get("approvedPreparationCommitInput")
    _require(isinstance(preparation_commit, dict), "approvedPreparationCommitInput must be an object")
    _require(preparation_commit == {
        "required": True,
        "pattern": "^[0-9a-f]{40}$",
        "mustBeDirectParentOfSourceCommit": True,
    }, "approved preparation commit guard changed")
    reason = trigger.get("approvalReasonInput")
    _require(isinstance(reason, dict), "approvalReasonInput must be an object")
    _require(reason.get("required") is True and reason.get("minimumLength") == 10, "approval reason guard changed")
    _require(reason.get("mustNotBeLogged") is True, "approval reason must not be logged")
    confirmation = trigger.get("confirmPublishInput")
    _require(isinstance(confirmation, dict), "confirmPublishInput must be an object")
    _require(confirmation == {"required": True, "default": False, "mustEqual": True}, "confirmation guard changed")

    environment = trigger.get("environment")
    _require(isinstance(environment, dict), "environment policy must be an object")
    _require(environment.get("name") == "ghcr-production-publish", "publish environment name changed")
    _require(environment.get("exists") is True, "publish environment must exist")
    _require(environment.get("deploymentBranch") == "main", "publish environment must allow main only")
    _require(environment.get("deploymentBranchConfigured") is True, "main-only environment rule is missing")
    _require(environment.get("requiredReviewerConfigured") is False, "unverified reviewer must remain false")
    _require(environment.get("preventSelfReviewConfigured") is False, "unverified self-review guard must remain false")
    _require(environment.get("requiredReviewerAvailableForCurrentPlan") is False, "reviewer plan availability changed")
    _require(environment.get("privateRepositoryReviewerGateRequiresEnterpriseCloud") is True, "Enterprise requirement changed")
    _require(environment.get("configured") is False, "incomplete environment must remain unconfigured")
    _require(
        environment.get("sourceControlledGate")
        == f"{LIFECYCLE_PATH}#publishReviewerGateReady",
        "source-controlled lifecycle gate changed",
    )
    _require(environment.get("gateValueDerivedFromLifecycleState") is True, "gate must derive from lifecycle state")
    _require(environment.get("gateChangeRequiresSinglePathCommit") is True, "gate change must be a single-path commit")
    _require(environment.get("gateRunsBeforeRegistryLogin") is True, "gate must run before registry login")
    concurrency = trigger.get("concurrency")
    _require(concurrency == {"group": "ghcr-backend-publish", "cancelInProgress": False}, "concurrency policy changed")

    permissions = plan.get("permissionsPolicy")
    _require(isinstance(permissions, dict), "permissionsPolicy must be an object")
    read_only = {"contents": "read"}
    _require(permissions.get("workflowDefault") == read_only, "workflow default permissions changed")
    _require(
        permissions.get("validateJob") == {"actions": "read", "contents": "read"},
        "validate permissions must allow only Actions run lookup and contents read",
    )
    _require(permissions.get("buildScanJob") == read_only, "build/scan permissions changed")
    _require(
        permissions.get("publishSignVerifyJob") == {
            "contents": "read",
            "packages": "write",
            "id-token": "write",
        },
        "publish permissions changed",
    )
    _require(
        permissions.get("githubArtifactAttestationsPermission") == "not-requested",
        "unsupported attestations permission must not be requested",
    )

    action_policy = plan.get("actionPolicy")
    _require(isinstance(action_policy, dict), "actionPolicy must be an object")
    _require(action_policy.get("requireFullLengthCommitSha") is True, "full action SHA pinning must be required")
    _require(action_policy.get("resolvedActionShaCandidatesReviewed") is True, "action SHAs were not reviewed")
    _require(action_policy.get("resolvedActionShasApproved") is True, "action SHAs are not approved")
    _require(action_policy.get("repositoryAllowlistConfigured") is True, "repository action allowlist is missing")
    _require(action_policy.get("allowGithubOwnedActionsBlanket") is False, "GitHub action blanket allow is forbidden")
    _require(action_policy.get("allowVerifiedCreatorsBlanket") is False, "verified creator blanket allow is forbidden")
    allowlist = action_policy.get("allowlist")
    _require(isinstance(allowlist, list), "action allowlist must be a list")
    _require(len(allowlist) == len(EXPECTED_ACTIONS), "action allowlist length changed")
    for item in allowlist:
        _require(isinstance(item, dict), "action allowlist item must be an object")
        repository = item.get("repository")
        _require(repository in EXPECTED_ACTIONS, f"unexpected action repository: {repository}")
        expected_release, expected_sha = EXPECTED_ACTIONS[repository]
        _require(item.get("approvedRelease") == expected_release, f"action release changed: {repository}")
        _require(item.get("approvedSha") == expected_sha, f"action SHA changed: {repository}")
        _require(item.get("upstreamTagCommitVerified") is True, f"action tag commit unverified: {repository}")
        _require(
            item.get("releaseUrl") == f"https://github.com/{repository}/releases/tag/{expected_release}",
            f"official release URL changed: {repository}",
        )

    gates = plan.get("supplyChainGates")
    _require(isinstance(gates, dict), "supplyChainGates must be an object")
    _require(gates.get("failurePolicy") == "fail-closed", "supply-chain gates must fail closed")
    reproducibility = gates.get("reproducibilityGate")
    _require(isinstance(reproducibility, dict), "reproducibilityGate must be an object")
    _require(reproducibility.get("status") == "dependency-and-frontend-inputs-locked", "reproducibility lock status changed")
    _require(reproducibility.get("pythonRuntimeImageDigestPinned") is True, "Python runtime image digest is not pinned")
    for key in (
        "pythonBuildSystemRequirementsHashLocked",
        "pythonApplicationDependenciesHashLocked",
        "pipUpgradePinned",
        "dockerfileFrontendDigestPinned",
    ):
        _require(reproducibility.get(key) is True, f"reproducibility input is not locked: {key}")
    _require(
        reproducibility.get("sameSourceDeterministicBuildGuaranteed") is False,
        "byte-for-byte deterministic build must not be overclaimed",
    )
    _require(reproducibility.get("pinnedPipVersion") == "26.1.2", "pinned pip version changed")
    _require(reproducibility.get("dockerfileFrontend") == DOCKERFILE_FRONTEND, "Dockerfile frontend lock changed")
    _require(reproducibility.get("lockSha256") == LOCK_SHA256, "dependency lock SHA-256 map changed")
    _require(
        reproducibility.get("inputSha256") == REPRODUCIBILITY_INPUT_SHA256,
        "reproducibility input SHA-256 map changed",
    )
    _require(reproducibility.get("binaryWheelOnly") is True, "source distributions must remain forbidden")
    _require(reproducibility.get("hashCheckingRequired") is True, "pip hash checking must remain required")
    _require(reproducibility.get("requiredBeforeFirstPublish") is True, "reproducibility must block first publish")
    vulnerability = gates.get("vulnerabilityGate")
    _require(isinstance(vulnerability, dict), "vulnerabilityGate must be an object")
    _require(vulnerability.get("scanner") == "trivy", "vulnerability scanner changed")
    _require(vulnerability.get("version") == "0.70.0", "Trivy version changed")
    _require(vulnerability.get("asset") == "trivy_0.70.0_Linux-64bit.tar.gz", "Trivy asset changed")
    _require(
        vulnerability.get("assetSha256") == "8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9",
        "Trivy asset checksum changed",
    )
    _require(
        vulnerability.get("installMode") == "official-release-asset-with-hardcoded-sha256",
        "Trivy install mode changed",
    )
    _require(vulnerability.get("severity") == ["HIGH", "CRITICAL"], "HIGH/CRITICAL gate changed")
    _require(vulnerability.get("exitCodeOnFinding") == 1, "vulnerability findings must fail")
    _require(vulnerability.get("ignoreUnfixed") is False, "unfixed findings must not be ignored")
    _require(vulnerability.get("allowIgnoreFile") is False, "ignore files require separate review")
    attestations = gates.get("registryAttestations")
    _require(isinstance(attestations, dict), "registryAttestations must be an object")
    _require(attestations.get("provider") == "docker-buildkit", "registry attestation provider changed")
    _require(attestations.get("provenance") == "mode=max", "max provenance is required")
    _require(attestations.get("sbom") is True, "registry SBOM is required")
    github_attestations = gates.get("githubArtifactAttestations")
    _require(isinstance(github_attestations, dict), "githubArtifactAttestations state is missing")
    _require(github_attestations.get("used") is False, "unsupported GitHub attestations must not be used")
    _require(github_attestations.get("supportedForCurrentRepository") is False, "repository support state changed")
    _require(gates.get("postPushOrder") == [
        "capture-exact-registry-digest",
        "inspect-buildkit-slsa-provenance",
        "inspect-buildkit-spdx-sbom",
        "scan-exact-pushed-digest-high-critical",
        "cosign-keyless-sign-digest",
        "verify-cosign-identity-and-issuer",
        "emit-reviewed-candidate-digest",
    ], "post-push gate order changed")
    signature = gates.get("signatureVerification")
    _require(isinstance(signature, dict), "signatureVerification must be an object")
    _require(signature.get("mode") == "sigstore-keyless-oidc", "signature mode changed")
    _require(signature.get("oidcIssuer") == "https://token.actions.githubusercontent.com", "OIDC issuer changed")
    _require(signature.get("certificateIdentity") == CERTIFICATE_IDENTITY, "certificate identity changed")
    _require(gates.get("automaticDeployment") is False, "automatic deployment is forbidden")
    _require(gates.get("productionReferenceUpdate") is False, "production reference update is forbidden")

    review = plan.get("repositoryReview")
    _require(isinstance(review, dict), "repositoryReview must be an object")
    _require(review.get("reviewedOn") == "2026-07-20", "repository live recheck date changed")
    _require(
        isinstance(review.get("recheckedAtUtc"), str)
        and review["recheckedAtUtc"].startswith("2026-07-20T")
        and review["recheckedAtUtc"].endswith("Z"),
        "repository live recheck timestamp changed",
    )
    _require(
        review.get("verificationMode") == "interactive-browser-live-recheck",
        "repository live review mode changed",
    )
    _require(review.get("liveRecheckRequiredBeforeGateChange") is True, "live repository recheck must remain required")
    settings = review.get("actionsSettings")
    _require(isinstance(settings, dict), "Actions settings review is missing")
    _require(settings.get("changed") is True, "Actions settings change is not recorded")
    _require(settings.get("allowedActions") == "selected-full-sha-only", "Actions allow policy changed")
    _require(settings.get("requireFullLengthCommitSha") is True, "full SHA repository setting is off")
    _require(settings.get("defaultWorkflowPermissions") == "read-contents-and-packages", "default token policy changed")
    _require(settings.get("allowActionsCreateApprovePullRequests") is False, "Actions PR approval must remain off")
    fork = settings.get("forkPullRequestWorkflows")
    _require(isinstance(fork, dict), "fork workflow policy is missing")
    _require(fork.get("sendWriteTokens") is False, "fork workflows must not receive write tokens")
    _require(fork.get("sendSecretsAndVariables") is False, "fork workflows must not receive secrets")
    collaborators = review.get("collaborators")
    _require(collaborators == {"countExcludingOwner": 0, "independentReviewerAvailable": False}, "collaborator state changed")
    publish_environment = review.get("publishEnvironment")
    _require(isinstance(publish_environment, dict), "publishEnvironment review is missing")
    _require(publish_environment.get("exists") is True, "publish environment is missing")
    _require(publish_environment.get("deploymentBranchConfigured") is True, "main-only branch rule is missing")
    _require(publish_environment.get("requiredReviewerConfigured") is False, "reviewer state changed")
    _require(publish_environment.get("requiredReviewerAvailableForCurrentPlan") is False, "environment reviewer availability changed")
    _require(publish_environment.get("variablesCount") == 0, "publish environment variables must remain empty")
    _require(publish_environment.get("configured") is False, "environment must remain incomplete")

    setup = plan.get("requiredRepositorySetup")
    _require(isinstance(setup, dict), "requiredRepositorySetup must be an object")
    for key in (
        "githubConnectorRepositoryAccess",
        "githubConnectorSelectedRepositoryOnly",
        "actionsSettingsReviewed",
        "actionsSettingsChanged",
        "fullLengthActionShaPolicyEnabled",
        "restrictedActionAllowlistEnabled",
        "publishEnvironmentReviewed",
        "publishEnvironmentExists",
        "publishEnvironmentMainOnly",
        "sourceControlledLifecyclePolicyReady",
    ):
        _require(_bool(setup, key) is True, f"completed repository setup must remain true: {key}")
    for key in (
        "independentReviewerAvailable",
        "publishEnvironmentRequiredReviewerConfigured",
        "publishEnvironmentPreventSelfReviewConfigured",
        "publishEnvironmentReviewerAvailableForCurrentPlan",
        "publishEnvironmentConfigured",
    ):
        _require(_bool(setup, key) is False, f"unresolved reviewer setup must remain false: {key}")
    _require(
        plan.get("nextSafeStagePolicy") == "follow-source-controlled-publish-lifecycle-state",
        "static plan must defer the next stage to lifecycle state",
    )

    _verify_workflow(workflow)
    _verify_transient_core_smoke_skip(smoke_core)
    lifecycle_result = _verify_lifecycle(root, lifecycle)
    for marker in (
        TOOL_VERSION,
        EXPECTED_WORKFLOW_SHA256,
        EXPECTED_WORKFLOW_SEMANTIC_SHA256,
        "workflow_dispatch",
        "pull_request_target",
        "contents: read",
        "actions: read",
        "packages: write",
        "id-token: write",
        LIFECYCLE_PATH,
        "approved_preparation_commit",
        "DOCKER_BUILD_RECORD_UPLOAD",
        "authorization-open",
        "authorization-closed-awaiting-evidence",
        "attempt-recorded",
        "closureCommitSha",
        TRANSIENT_SMOKE_SKIP_COMMAND,
        DIRECT_STATIC_STRICT_COMMAND,
        "required reviewer",
        "workflow 파일 생성: 완료",
    ):
        _require(marker in document, f"workflow plan document is missing marker: {marker}")

    return {
        "toolVersion": TOOL_VERSION,
        "repository": REPOSITORY,
        "imageRepository": IMAGE_REPOSITORY,
        "trigger": "workflow_dispatch-only",
        "workflowSourceSha256": EXPECTED_WORKFLOW_SHA256,
        "workflowSemanticSha256": EXPECTED_WORKFLOW_SEMANTIC_SHA256,
        "workflowFilePresent": True,
        "workflowCreationApproved": True,
        "workflowExecutionApproved": True,
        "workflowExecutionExecuted": bool(lifecycle.get("priorAttemptEvidence")) or lifecycle_result["state"] in {
            "authorization-closed-awaiting-evidence",
            "attempt-recorded",
        },
        "registryMutationExecuted": bool(lifecycle.get("priorAttemptEvidence", {}).get("imagePushExecuted"))
        or (lifecycle_result["state"] == "attempt-recorded" and lifecycle["observedAttempt"].get("imageDigest") is not None),
        "actionShasApproved": True,
        "actionsSettingsConfigured": True,
        "publishEnvironmentExists": True,
        "publishEnvironmentConfigured": False,
        "publishLifecycleState": lifecycle_result["state"],
        "publishGateReady": lifecycle_result["gate"],
        "approvedPreparationSha": lifecycle_result["approvedPreparationSha"],
        "authorizationSourceSha": lifecycle_result.get("authorizationSourceSha"),
        "closureCommitSha": lifecycle_result.get("closureCommitSha"),
        "attemptRecordCommitSha": lifecycle_result.get("attemptRecordCommitSha"),
        "dockerBuildContextEnvExcluded": True,
        "reproducibleBuildReady": True,
        "supplyChainGate": "fail-closed",
        "result": lifecycle_result["result"],
        "nextSafeStage": lifecycle_result["nextSafeStage"],
    }


def render(result: dict[str, Any]) -> str:
    return "\n".join((
        "GitHub Actions/GHCR workflow verification (read-only)",
        "The source-controlled publish lifecycle was validated fail-closed.",
        "",
        f"- repository/image: {result['repository']} / {result['imageRepository']}",
        f"- trigger: {result['trigger']}",
        f"- reviewed workflow source SHA-256: {result['workflowSourceSha256']}",
        f"- reviewed workflow semantic SHA-256: {result['workflowSemanticSha256']}",
        "- recorded action allowlist/full SHA enforcement: configured/configured (2026-07-20 live recheck)",
        "- workflow file/creation approved: yes/yes",
        f"- workflow execution approved/executed: yes/{'yes' if result['workflowExecutionExecuted'] else 'no'}",
        "- publish permissions: contents=read, packages=write, id-token=write",
        "- pre-push gates: static checks, local OCI build, SPDX SBOM, HIGH/CRITICAL scan",
        "- post-push gates: exact digest, BuildKit provenance/SBOM, exact-digest Trivy, Cosign sign/verify",
        "- recorded environment/main-only: present/configured (2026-07-20 live recheck)",
        "- native required reviewer/current private plan: missing/unavailable",
        f"- publish lifecycle state: {result['publishLifecycleState']}",
        f"- source-controlled publish gate ready: {str(result['publishGateReady']).lower()}",
        "- root Docker context env files/re-includes: excluded/forbidden",
        "- dependency/frontend inputs: exact versions + SHA-256 locks ready",
        "- byte-for-byte deterministic image claim: no (not overclaimed)",
        f"- workflow/registry mutation executed: {'yes' if result['workflowExecutionExecuted'] else 'no'}/{'yes' if result['registryMutationExecuted'] else 'no'}",
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
        result = inspect_static_workflow_plan(root)
    except StaticWorkflowPlanError as exc:
        payload = {"toolVersion": TOOL_VERSION, "result": BLOCKED_RESULT, "reason": str(exc)}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("GitHub Actions/GHCR workflow verification")
            print(f"- result: {BLOCKED_RESULT}")
            print(f"- reason: {exc}")
        return 1 if args.strict else 0
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

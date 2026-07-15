#!/usr/bin/env python3
"""Validate the v320 fail-closed GitHub Actions/GHCR workflow and repository state."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from typing import Any

import yaml

TOOL_VERSION = "v320.github-actions-ghcr-workflow-prepared-gated"
READY_RESULT = "github-actions-ghcr-workflow-prepared-publish-gated"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "choose-private-repository-publish-approval-model"
REMOTE = "https://github.com/gihohoho/upgrade-rpg.git"
REPOSITORY = "gihohoho/upgrade-rpg"
IMAGE_REPOSITORY = "ghcr.io/gihohoho/upgrade-rpg-backend"
WORKFLOW_PATH = ".github/workflows/publish-backend-ghcr.yml"
EXPECTED_WORKFLOW_SHA256 = "83393cb875cf43ce1bc30d245c100482818af96cd7b5417d81b9cb45ce62a993"
EXPECTED_WORKFLOW_SEMANTIC_SHA256 = "2f1b1baf3f7db363f2f175b98623ec97e59a785592ae32d023f4b5123f2bd4c0"
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
    "validate:Check out exact source commit": "9350d08554e0602d5c761ee37f7ee71fd5de268beda39865527d91747903bef4",
    "validate:Set up Python 3.11.15": "a609038eeba3cc4d4e2544a17e2a5dd608afc8164eb0a206d805c03cce4f69ab",
    "build_scan:Check out exact source commit": "9350d08554e0602d5c761ee37f7ee71fd5de268beda39865527d91747903bef4",
    "build_scan:Set up Python 3.11.15": "a609038eeba3cc4d4e2544a17e2a5dd608afc8164eb0a206d805c03cce4f69ab",
    "build_scan:Set up Docker Buildx": "9e98d11cbaa23d6e221aa919e69bb31ec2e0b2d883023c8abc55c998b2b383f4",
    "build_scan:Build local linux/amd64 image without registry mutation": "96dc0dadb21da51d7ff7856c0f9fbd9da21fc43d32f7038edc82518ad748d201",
    "build_scan:Generate local SPDX JSON SBOM": "0f52e862c1309ab829151d6f126da1e7a67c54f7f222ec4b8ee0dda857e12c27",
    "build_scan:Retain non-secret review artifacts": "e4b6f148dcfbdc4823351bb99a476f25e0e990654ca3eafc15a4d62a22512b6e",
    "publish_sign_verify:Check out exact source commit": "9350d08554e0602d5c761ee37f7ee71fd5de268beda39865527d91747903bef4",
    "publish_sign_verify:Set up Python 3.11.15": "a609038eeba3cc4d4e2544a17e2a5dd608afc8164eb0a206d805c03cce4f69ab",
    "publish_sign_verify:Set up Docker Buildx": "9e98d11cbaa23d6e221aa919e69bb31ec2e0b2d883023c8abc55c998b2b383f4",
    "publish_sign_verify:Log in to GHCR with ephemeral GITHUB_TOKEN": "510ff6f9df0abbd302bf4eb383301d9d8da6d7e9988902ed09131635931104cd",
    "publish_sign_verify:Build and push digest candidate with BuildKit attestations": "ade6afcfa55ab989a485f67d5dbd0d710d39751d93fe248e4671c9b26ded55d7",
    "publish_sign_verify:Set up Cosign": "d6dfc3975100db9978b85ccf2ee1d3233f5d4dff603d0796984c39c19095a115",
    "publish_sign_verify:Retain exact-digest verification artifacts": "363a6d2c5bc8517273de3d891f97ccc3c466b3bb336f07a98d0cdfa92e5348b8",
}
EXPECTED_RUN_STEP_SHA256 = {
    "validate:Check manual approval inputs": "f6d30e12218c4d7cbfbc97d02d9bf548bba332d3e678e424c7b48be585531925",
    "validate:Verify checked out HEAD": "e131362a607c6353e49b1d526ce1b93c183006631417271fcfbaf480f9206a50",
    "validate:Install backend validation dependencies": "ad041a150de40f8672a3cce585cd896a2681ba93931e5622fcb306fc5bb5b0b8",
    "validate:Run fail-closed repository checks": "6a780c2ee0926e8cd2b9f51f74a4e781b8d97f61ce74b8f2cb81dc723c50d832",
    "build_scan:Validate local SBOM structure": "f0209099c473f80e08077f73bfdc6d7d9d8c40d238611d52cb36ccc4e2febac9",
    "build_scan:Install checksum-pinned Trivy 0.70.0": "22c99c3087798ff0a62797f773e206e248ab473954b770ba8b2acffbd8b74d64",
    "build_scan:Block HIGH and CRITICAL vulnerabilities in local image": "d1272d7f19a1a8d3d54449ec9be5914ba44dbfc99ccfe995f58460cdbaeac5e5",
    "build_scan:Validate local Trivy JSON evidence": "219c442ec7a7d2017acc6606bb28d4a291275ff11de145ab139e9d2c14ce3986",
    "publish_sign_verify:Enforce independent reviewer gate before registry access": "0f042027e9b0f32c7599d341828ae94c751a0b3554bc96500a3c5cdf28a4c8da",
    "publish_sign_verify:Install checksum-pinned Trivy 0.70.0": "22c99c3087798ff0a62797f773e206e248ab473954b770ba8b2acffbd8b74d64",
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
        "APPROVAL_REASON": "${{ inputs.approval_reason }}",
        "CONFIRM_PUBLISH": "${{ inputs.confirm_publish }}",
        "EXPECTED_GITHUB_SHA": "${{ github.sha }}",
        "EXPECTED_GITHUB_REF": "${{ github.ref }}",
    },
    "validate:Verify checked out HEAD": {"SOURCE_COMMIT": "${{ inputs.source_commit }}"},
    "validate:Install backend validation dependencies": None,
    "validate:Run fail-closed repository checks": None,
    "build_scan:Validate local SBOM structure": None,
    "build_scan:Install checksum-pinned Trivy 0.70.0": {
        "TRIVY_VERSION": "0.70.0",
        "TRIVY_SHA256": "8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9",
    },
    "build_scan:Block HIGH and CRITICAL vulnerabilities in local image": None,
    "build_scan:Validate local Trivy JSON evidence": None,
    "publish_sign_verify:Enforce independent reviewer gate before registry access": {
        "PUBLISH_REVIEWER_GATE_READY": "false",
    },
    "publish_sign_verify:Install checksum-pinned Trivy 0.70.0": {
        "TRIVY_VERSION": "0.70.0",
        "TRIVY_SHA256": "8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9",
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
    _require(set(inputs) == {"source_commit", "approval_reason", "confirm_publish"}, "workflow inputs changed")
    _require(inputs["source_commit"].get("required") is True, "source_commit must be required")
    _require(inputs["source_commit"].get("type") == "string", "source_commit must be a string")
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
    _require(set(validate) == {"name", "runs-on", "steps"}, "validate job keys changed")
    _require(set(build_scan) == {"name", "needs", "runs-on", "steps"}, "build_scan job keys changed")
    _require(
        set(publish) == {"name", "needs", "runs-on", "environment", "permissions", "steps"},
        "publish job keys changed",
    )
    _require(validate.get("runs-on") == "ubuntu-latest", "validate runner changed")
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
            "Check out exact source commit",
            "Verify checked out HEAD",
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
            "Enforce independent reviewer gate before registry access",
            "Check out exact source commit",
            "Set up Python 3.11.15",
            "Set up Docker Buildx",
            "Install checksum-pinned Trivy 0.70.0",
            "Log in to GHCR with ephemeral GITHUB_TOKEN",
            "Build and push digest candidate with BuildKit attestations",
            "Inspect BuildKit provenance and SBOM on exact digest",
            "Block vulnerabilities in exact pushed digest before signing",
            "Validate exact-digest Trivy JSON evidence",
            "Set up Cosign",
            "Sign exact digest with GitHub OIDC after all image gates",
            "Verify Cosign certificate identity and issuer",
            "Retain exact-digest verification artifacts",
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
        sensitive_scalars == [(
            ("jobs", "publish_sign_verify", "steps", 5, "with", "password"),
            "${{ secrets.GITHUB_TOKEN }}",
        )],
        "workflow secret/token expression is outside the single approved login password path",
    )
    for step in (*validate_steps, *build_steps, *publish_steps):
        if "if" in step:
            _require(
                step.get("name") == "Retain non-secret review artifacts" and step.get("if") == "always()",
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

    _require(publish_steps[0].get("name") == "Enforce independent reviewer gate before registry access", "publish gate must be first")
    gate = publish_steps[0]
    _require(gate.get("env") == {"PUBLISH_REVIEWER_GATE_READY": "false"}, "publish gate must remain source-controlled false")
    _require("vars." not in workflow, "repository/environment vars must not control the reviewer gate")

    publish_names = [step["name"] for step in publish_steps]
    ordered_names = (
        "Enforce independent reviewer gate before registry access",
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
        "EXPECTED_GITHUB_REF: ${{ github.ref }}",
        "refs/heads/main",
        "persist-credentials: false",
        "python-version: \"3.11.15\"",
        "python tools/check_github_actions_ghcr_static_plan.py --strict",
        "python tools/check_codex_handoff_readiness.py --strict",
        "bash tools/run_smoke_core.sh",
        "TRIVY_VERSION: \"0.70.0\"",
        "TRIVY_SHA256: 8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9",
        "sha256sum --check --strict",
        "--severity HIGH,CRITICAL",
        "--ignore-unfixed=false",
        "--exit-code 1",
        "published-trivy-results.json",
        'if [ "$PUBLISH_REVIEWER_GATE_READY" != "true" ]',
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
    ):
        _require(marker in workflow, f"workflow security marker is missing: {marker}")
    for forbidden in ("actions/attest", "aquasecurity/trivy-action", "attestations: write", ".trivyignore", ":latest"):
        _require(forbidden not in workflow, f"forbidden workflow marker found: {forbidden}")

    secret_references = set(re.findall(r"secrets\.([A-Za-z0-9_]+)", workflow))
    _require(secret_references == {"GITHUB_TOKEN"}, "workflow may reference only ephemeral GITHUB_TOKEN")


def inspect_static_workflow_plan(root: Path) -> dict[str, Any]:
    plan = _read_json(root / "deploy/github-actions-ghcr-static-plan.example.json")
    document = _read(root / "docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md")
    workflow = _read(root / WORKFLOW_PATH)
    dockerignore = _read(root / ".dockerignore")

    _require(plan.get("schemaVersion") == TOOL_VERSION, "unexpected v320 schemaVersion")
    _require(_bool(plan, "preparedOnly") is True, "stage must remain prepared-only")
    _require(plan.get("publishApprovalModel") == "undecided", "publish approval model must remain undecided")
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
    _require(plan.get("workflowPath") == WORKFLOW_PATH, "workflow path changed")
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
    for key in (
        "workflowFilePresent",
        "workflowCreationApproved",
        "workflowExecutionApproved",
        "registryLoginApproved",
        "imageBuildApproved",
        "imagePushApproved",
        "registryMutationApproved",
    ):
        _require(_bool(plan, key) is True, f"approved v320 state must remain true: {key}")
    for key in (
        "workflowExecutionExecuted",
        "publishExecutionAllowedNow",
        "registryMutationExecuted",
    ):
        _require(_bool(plan, key) is False, f"blocked/unexecuted v320 state must remain false: {key}")

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
    _require(environment.get("sourceControlledGate") == "PUBLISH_REVIEWER_GATE_READY", "source-controlled gate changed")
    _require(environment.get("sourceControlledGateValue") is False, "publish gate must remain false")
    _require(environment.get("gateChangeRequiresReviewedCommit") is True, "gate change must require a commit")
    _require(environment.get("gateRunsBeforeRegistryLogin") is True, "gate must run before registry login")
    concurrency = trigger.get("concurrency")
    _require(concurrency == {"group": "ghcr-backend-publish", "cancelInProgress": False}, "concurrency policy changed")

    permissions = plan.get("permissionsPolicy")
    _require(isinstance(permissions, dict), "permissionsPolicy must be an object")
    read_only = {"contents": "read"}
    _require(permissions.get("workflowDefault") == read_only, "workflow default permissions changed")
    _require(permissions.get("validateJob") == read_only, "validate permissions changed")
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
    _require(reproducibility.get("status") == "incomplete", "reproducibility status must remain incomplete")
    _require(reproducibility.get("pythonRuntimeImageDigestPinned") is True, "Python runtime image digest is not pinned")
    for key in (
        "pythonBuildSystemRequirementsHashLocked",
        "pythonApplicationDependenciesHashLocked",
        "pipUpgradePinned",
        "dockerfileFrontendDigestPinned",
        "sameSourceDeterministicBuildGuaranteed",
    ):
        _require(reproducibility.get(key) is False, f"unverified reproducibility claim changed: {key}")
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
    _require(review.get("reviewedOn") == "2026-07-15", "repository review observation date changed")
    _require(review.get("verificationMode") == "interactive-browser-snapshot", "repository review mode changed")
    _require(review.get("liveRecheckRequiredBeforeGateChange") is True, "live repository recheck must remain required")
    settings = review.get("actionsSettings")
    _require(isinstance(settings, dict), "Actions settings review is missing")
    _require(settings.get("changed") is True, "Actions settings change is not recorded")
    _require(settings.get("allowedActions") == "selected-full-sha-only", "Actions allow policy changed")
    _require(settings.get("requireFullLengthCommitSha") is True, "full SHA repository setting is off")
    _require(settings.get("defaultWorkflowPermissions") == "read-contents-and-packages", "default token policy changed")
    _require(settings.get("allowActionsCreateApprovePullRequests") is False, "Actions PR approval must remain off")
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
    ):
        _require(_bool(setup, key) is True, f"completed repository setup must remain true: {key}")
    for key in (
        "independentReviewerAvailable",
        "publishEnvironmentRequiredReviewerConfigured",
        "publishEnvironmentPreventSelfReviewConfigured",
        "publishEnvironmentReviewerAvailableForCurrentPlan",
        "sourceControlledPublishGateReady",
        "publishEnvironmentConfigured",
    ):
        _require(_bool(setup, key) is False, f"unresolved reviewer setup must remain false: {key}")
    _require(plan.get("nextSafeStage") == NEXT_SAFE_STAGE, "unexpected next safe stage")

    _verify_workflow(workflow)
    for marker in (
        TOOL_VERSION,
        EXPECTED_WORKFLOW_SHA256,
        EXPECTED_WORKFLOW_SEMANTIC_SHA256,
        "workflow_dispatch",
        "pull_request_target",
        "contents: read",
        "packages: write",
        "id-token: write",
        "HIGH,CRITICAL",
        "Docker BuildKit",
        "Sigstore Cosign keyless",
        "PUBLISH_REVIEWER_GATE_READY",
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
        "workflowExecutionExecuted": False,
        "actionShasApproved": True,
        "actionsSettingsConfigured": True,
        "publishEnvironmentExists": True,
        "publishEnvironmentConfigured": False,
        "publishGateReady": False,
        "dockerBuildContextEnvExcluded": True,
        "reproducibleBuildReady": False,
        "supplyChainGate": "fail-closed",
        "result": READY_RESULT,
        "nextSafeStage": NEXT_SAFE_STAGE,
    }


def render(result: dict[str, Any]) -> str:
    return "\n".join((
        "GitHub Actions/GHCR workflow verification (read-only)",
        "The workflow is prepared, but it has not run and registry mutation remains blocked.",
        "",
        f"- repository/image: {result['repository']} / {result['imageRepository']}",
        f"- trigger: {result['trigger']}",
        f"- reviewed workflow source SHA-256: {result['workflowSourceSha256']}",
        f"- reviewed workflow semantic SHA-256: {result['workflowSemanticSha256']}",
        "- recorded action allowlist/full SHA enforcement: configured/configured (2026-07-15 browser snapshot)",
        "- workflow file/creation approved: yes/yes",
        "- workflow execution approved/executed: yes/no",
        "- publish permissions: contents=read, packages=write, id-token=write",
        "- pre-push gates: static checks, local OCI build, SPDX SBOM, HIGH/CRITICAL scan",
        "- post-push gates: exact digest, BuildKit provenance/SBOM, exact-digest Trivy, Cosign sign/verify",
        "- recorded environment/main-only: present/configured (2026-07-15 browser snapshot)",
        "- native required reviewer/current private plan: missing/unavailable",
        "- publish approval model: undecided",
        "- PUBLISH_REVIEWER_GATE_READY: source-controlled false (fail-closed before GHCR login)",
        "- root Docker context env files/re-includes: excluded/forbidden",
        "- deterministic dependency/toolchain lock: incomplete (required before first publish)",
        "- workflow/registry mutation executed: no/no",
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

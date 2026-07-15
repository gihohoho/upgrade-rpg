#!/usr/bin/env python3
"""Validate the v313 backend image source/digest policy without Docker mutation.

The checker reads repository files only. It does not read registry credentials,
invoke Docker, pull/build/push an image, connect to PostgreSQL, or run Alembic.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

TOOL_VERSION = "v313.backend-image-source-digest-policy"
READY_RESULT = "backend-image-source-digest-policy-verified-provider-and-build-blocked"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "select-registry-repository-platform-and-base-image-digest"


class BackendImagePolicyError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise BackendImagePolicyError(message)


def _read(path: Path) -> str:
    if not path.is_file():
        raise BackendImagePolicyError(f"required file is missing: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise BackendImagePolicyError(f"invalid JSON: {path.as_posix()}: {exc}") from exc
    if not isinstance(value, dict):
        raise BackendImagePolicyError(f"JSON root must be an object: {path.as_posix()}")
    return value


def _bool(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise BackendImagePolicyError(f"{key} must be a boolean")
    return value


def _env_inventory(text: str) -> dict[str, str]:
    return {
        line.split("=", 1)[0].strip(): line.split("=", 1)[1].strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }


def _dockerfile_base_image(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        match = re.match(r"FROM\s+([^\s]+)(?:\s+AS\s+\S+)?$", stripped, re.IGNORECASE)
        if match:
            return match.group(1)
    raise BackendImagePolicyError("Dockerfile FROM image is missing")


def inspect_backend_image_policy(root: Path) -> dict[str, Any]:
    policy = _read_json(root / "deploy/backend-image-source-digest-policy.example.json")
    selection = _read_json(root / "deploy/production-architecture-selection.example.json")
    capacity = _read_json(root / "deploy/production-capacity-plan.example.json")
    evidence_path = root / str(policy.get("composeConfigRenderEvidence", ""))
    evidence = _read_json(evidence_path)
    compose = _read(root / "deploy/docker-compose.production.yml")
    env_example = _read(root / "deploy/production.env.example")
    dockerfile_path = root / str(policy.get("sourceDockerfile", ""))
    dockerfile = _read(dockerfile_path)
    policy_doc = _read(root / "docs/current/BACKEND_IMAGE_SOURCE_DIGEST_POLICY.md")
    isolated_doc = _read(root / "deploy/isolated-validation/README.md")

    _require(
        policy.get("schemaVersion") == "v313.backend-image-source-digest-policy",
        "unexpected backend image policy schemaVersion",
    )
    _require(_bool(policy, "reviewOnly") is True, "policy must remain review-only")
    _require(_bool(policy, "composeConfigRenderVerified") is True, "config render must be verified")
    _require(policy.get("registryProvider") == "deferred", "registry provider must remain deferred")
    _require(policy.get("targetPlatform") == "deferred", "target platform must remain deferred")
    _require(
        policy.get("repositoryIdentity")
        == "<approved-registry>/<approved-namespace>/upgrade-rpg-backend",
        "repository identity placeholder changed",
    )
    _require(policy.get("productionReferenceMode") == "digest-only", "production image must be digest-only")
    _require(policy.get("digestAlgorithm") == "sha256", "image digest algorithm must be sha256")
    _require(policy.get("digestHexLength") == 64, "image digest length must be 64 hex characters")
    _require(policy.get("sourceDockerfile") == "backend/Dockerfile", "unexpected Dockerfile path")
    _require(policy.get("sourceBuildContext") == ".", "production build context review must remain repository root")
    _require(_bool(policy, "sourceCommitRequired") is True, "source commit identity must be required")
    _require(
        policy.get("sourceCommitPattern") == "<approved-40-hex-git-commit>",
        "source commit placeholder changed",
    )
    _require(_bool(policy, "baseImageDigestRequiredBeforeBuild") is True, "base image digest gate is missing")
    _require(_bool(policy, "baseImageDigestApproved") is False, "base image digest must remain unapproved")

    supply_chain_keys = (
        "sbomRequiredBeforeRelease",
        "provenanceRequiredBeforeRelease",
        "signatureVerificationRequiredBeforeDeploy",
        "vulnerabilityReviewRequiredBeforeRelease",
    )
    for key in supply_chain_keys:
        _require(_bool(policy, key) is True, f"supply-chain gate is missing: {key}")

    for key in (
        "imagePullApproved",
        "imageBuildApproved",
        "imagePushApproved",
        "containerStartApproved",
        "actualRegistryCredentialsApplied",
        "actualImageDigestApplied",
        "actualProductionValuesApplied",
    ):
        _require(_bool(policy, key) is False, f"{key} must remain false")

    expected_evidence = "deploy/review/production-compose-config-render-v312.json"
    _require(str(policy.get("composeConfigRenderEvidence")) == expected_evidence, "unexpected evidence path")
    _require(selection.get("composeConfigRenderEvidence") == expected_evidence, "selection evidence path differs")
    _require(capacity.get("composeConfigRenderEvidence") == expected_evidence, "capacity evidence path differs")
    _require(selection.get("composeConfigRenderExecuted") is True, "selection must record completed config render")
    _require(capacity.get("composeConfigRenderExecuted") is True, "capacity plan must record completed config render")
    _require(selection.get("imagePullBuildApproved") is False, "selection must keep pull/build blocked")
    _require(capacity.get("imagePullBuildApproved") is False, "capacity plan must keep pull/build blocked")

    _require(
        evidence.get("schemaVersion") == "v312.production-compose-config-render-evidence",
        "unexpected config render evidence schemaVersion",
    )
    _require(_bool(evidence, "recordedFromUserOutput") is True, "evidence must be recorded from user output")
    _require(_bool(evidence, "reviewOnlySentinelsUsed") is True, "render must use review-only sentinels")
    _require(_bool(evidence, "rawRenderPersisted") is False, "raw render must not be persisted")
    _require(evidence.get("dockerSubcommand") == "compose config", "only compose config evidence is accepted")
    _require(evidence.get("renderedServices") == ["backend"], "rendered services must be backend-only")
    for key in (
        "hostPortsAbsent",
        "buildAbsent",
        "namedVolumesAbsent",
        "managedDatabaseServiceAbsent",
        "digestReferenceRendered",
        "productionGuardRendered",
        "tlsVerifyFullProviderCaRendered",
        "externalEdgeNetworkRendered",
    ):
        _require(_bool(evidence, key) is True, f"unsafe config render evidence: {key}")
    _require(evidence.get("backendReplicas") == 1, "rendered backend replicas must be 1")
    for key in (
        "imagePullBuildExecuted",
        "containerNetworkVolumeMutationExecuted",
        "databaseAlembicMutationExecuted",
    ):
        _require(_bool(evidence, key) is False, f"unexpected mutation evidence: {key}")
    _require(
        evidence.get("result") == "production-compose-config-render-verified-no-runtime-mutation",
        "unexpected config render result",
    )

    env = _env_inventory(env_example)
    expected_reference = policy.get("productionReferencePattern")
    _require(
        expected_reference
        == "<approved-registry>/<approved-namespace>/upgrade-rpg-backend@sha256:<approved-64-hex-digest>",
        "production image reference pattern changed",
    )
    _require(env.get("BACKEND_IMAGE") == expected_reference, "env image reference differs from policy")
    _require("image: ${BACKEND_IMAGE:?" in compose, "Compose must require BACKEND_IMAGE")
    _require(re.search(r"(?m)^\s+build:\s*$", compose) is None, "production Compose must not build")
    _require(re.search(r"(?m)^\s+ports:\s*$", compose) is None, "backend host ports must remain absent")

    base_image = _dockerfile_base_image(dockerfile)
    _require(base_image == policy.get("currentBaseImageReference"), "Dockerfile base image differs from policy inventory")
    base_digest_pinned = "@sha256:" in base_image and bool(re.search(r"@sha256:[0-9a-fA-F]{64}$", base_image))
    _require(base_digest_pinned is False, "policy expects base image digest approval to remain pending")

    for marker in (
        "digest-only",
        "registry provider: deferred",
        "target platform: deferred",
        "base image digest approved: no",
        "image pull/build/push approved: no/no/no",
        NEXT_SAFE_STAGE,
    ):
        _require(marker in policy_doc, f"backend image policy document is missing: {marker}")
    for marker in (
        "Stage 1 — 완료: config render only",
        "Stage 2A — 완료: image source/digest policy",
        "pull/build/push approved: no/no/no",
    ):
        _require(marker in isolated_doc, f"isolated validation document is missing: {marker}")

    return {
        "toolVersion": TOOL_VERSION,
        "policySchemaVersion": policy["schemaVersion"],
        "configRenderEvidenceVerified": True,
        "registryProvider": policy["registryProvider"],
        "repositoryIdentity": policy["repositoryIdentity"],
        "targetPlatform": policy["targetPlatform"],
        "productionReferenceMode": policy["productionReferenceMode"],
        "digestAlgorithm": policy["digestAlgorithm"],
        "digestHexLength": policy["digestHexLength"],
        "sourceDockerfile": policy["sourceDockerfile"],
        "sourceBuildContext": policy["sourceBuildContext"],
        "currentBaseImageReference": base_image,
        "baseImageDigestPinned": base_digest_pinned,
        "baseImageDigestApproved": False,
        "supplyChainGateCount": len(supply_chain_keys),
        "imagePullApproved": False,
        "imageBuildApproved": False,
        "imagePushApproved": False,
        "containerStartApproved": False,
        "actualRegistryCredentialsApplied": False,
        "actualImageDigestApplied": False,
        "actualMutationExecuted": False,
        "result": READY_RESULT,
        "nextSafeStage": NEXT_SAFE_STAGE,
    }


def render(result: dict[str, Any]) -> str:
    return "\n".join(
        (
            "Backend image source/digest policy verification (read-only)",
            "No registry credential read, Docker pull/build/push, container mutation, DB connection, or Alembic command was executed.",
            "",
            f"- config render evidence verified: {result['configRenderEvidenceVerified']}",
            f"- registry/repository/platform: {result['registryProvider']} / {result['repositoryIdentity']} / {result['targetPlatform']}",
            f"- production reference mode: {result['productionReferenceMode']} ({result['digestAlgorithm']}:{result['digestHexLength']})",
            f"- Dockerfile/build context: {result['sourceDockerfile']} / {result['sourceBuildContext']}",
            f"- current base image: {result['currentBaseImageReference']}",
            f"- base image digest pinned/approved: {result['baseImageDigestPinned']}/{result['baseImageDigestApproved']}",
            f"- supply-chain gates required: {result['supplyChainGateCount']}/4",
            "- image pull/build/push approved: no/no/no",
            "- image pull/build/push executed: no/no/no",
            "- container/DB/Alembic mutation executed: no/no/no",
            f"- result: {result['result']}",
            f"- next safe stage: {result['nextSafeStage']}",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = inspect_backend_image_policy(root)
    except Exception as exc:
        blocked = {
            "toolVersion": TOOL_VERSION,
            "result": BLOCKED_RESULT,
            "reason": f"{type(exc).__name__}: {exc}",
            "actualMutationExecuted": False,
        }
        print(
            json.dumps(blocked, ensure_ascii=False, indent=2)
            if args.json
            else "Backend image source/digest policy validation\n"
            f"- result: {BLOCKED_RESULT}\n"
            f"- reason: {blocked['reason']}\n"
            "- no mutation was executed."
        )
        return 1 if args.strict else 0
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

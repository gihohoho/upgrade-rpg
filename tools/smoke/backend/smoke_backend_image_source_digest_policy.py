#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_backend_image_source_digest_policy.py"
REQUIRED_FILES = (
    "deploy/backend-image-source-digest-policy.example.json",
    "deploy/production-architecture-selection.example.json",
    "deploy/production-capacity-plan.example.json",
    "deploy/review/production-compose-config-render-v312.json",
    "deploy/docker-compose.production.yml",
    "deploy/production.env.example",
    "backend/Dockerfile",
    "docs/current/BACKEND_IMAGE_SOURCE_DIGEST_POLICY.md",
    "deploy/isolated-validation/README.md",
)


def load_tool():
    spec = importlib.util.spec_from_file_location("v313_backend_image_policy", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v313 backend image policy checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_fixture(temp: Path) -> None:
    for relative in REQUIRED_FILES:
        target = temp / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8")


def expect_blocked(module, temp: Path) -> None:
    try:
        module.inspect_backend_image_policy(temp)
    except module.BackendImagePolicyError:
        return
    raise AssertionError("unsafe v313 backend image policy was not blocked")


def main() -> int:
    module = load_tool()
    result = module.inspect_backend_image_policy(ROOT)
    assert result["result"] == module.READY_RESULT
    assert result["configRenderEvidenceVerified"] is True
    assert result["registryProvider"] == "deferred"
    assert result["targetPlatform"] == "deferred"
    assert result["productionReferenceMode"] == "digest-only"
    assert result["baseImageDigestPinned"] is False
    assert result["baseImageDigestApproved"] is False
    assert result["supplyChainGateCount"] == 4
    assert result["imagePullApproved"] is False
    assert result["imageBuildApproved"] is False
    assert result["imagePushApproved"] is False
    assert result["actualMutationExecuted"] is False

    policy_mutations = (
        ("registryProvider", "unapproved-registry"),
        ("productionReferenceMode", "tag"),
        ("baseImageDigestApproved", True),
        ("imagePullApproved", True),
        ("imageBuildApproved", True),
        ("imagePushApproved", True),
    )
    for key, value in policy_mutations:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            path = temp / "deploy/backend-image-source-digest-policy.example.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload[key] = value
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            expect_blocked(module, temp)

    evidence_mutations = (
        ("hostPortsAbsent", False),
        ("buildAbsent", False),
        ("imagePullBuildExecuted", True),
        ("databaseAlembicMutationExecuted", True),
    )
    for key, value in evidence_mutations:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            path = temp / "deploy/review/production-compose-config-render-v312.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload[key] = value
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            expect_blocked(module, temp)

    print("OK: v313 backend image source/digest policy smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

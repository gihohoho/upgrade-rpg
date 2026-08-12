#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_production_secrets_tls_container_static.py"
REQUIRED_FILES = (
    "deploy/docker-compose.production.yml",
    "deploy/production.env.example",
    "deploy/README.md",
    "deploy/secrets/README.md",
    "docs/reference/database/POSTGRES_PRODUCTION_STATIC_VALIDATION.md",
    "backend/Dockerfile",
    ".gitignore",
    ".dockerignore",
)


def load_tool():
    spec = importlib.util.spec_from_file_location("production_static_current", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load production static checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_fixture(temp: Path) -> None:
    for relative in REQUIRED_FILES:
        target = temp / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    module = load_tool()
    result = module.inspect_production_static_templates(ROOT)
    assert result["result"] == module.READY_RESULT
    assert result["requiredComposeValueCount"] == 7
    assert result["composeServices"] == ["backend"]
    assert result["managedPostgresServiceAbsent"] is True
    assert result["backendDigestPinned"] is True
    assert result["tlsVerifyFullExample"] is True
    assert result["tlsCaPathExample"] is True
    assert result["externalEdgeNetwork"] is True
    assert result["hostPortsAbsent"] is True
    assert result["buildAbsent"] is True
    assert result["namedVolumesAbsent"] is True
    assert result["automaticAlembicAbsent"] is True
    assert result["actualMutationExecuted"] is False
    assert result["actualProductionSecretsTlsContainerExecutionApproved"] is False

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        copy_fixture(temp)
        env_path = temp / "deploy/production.env.example"
        env_path.write_text(
            env_path.read_text(encoding="utf-8").replace(
                "<generate-a-random-secret-of-at-least-32-characters>",
                "change-me-before-production",
            ),
            encoding="utf-8",
        )
        try:
            module.inspect_production_static_templates(temp)
        except module.ProductionStaticValidationError:
            pass
        else:
            raise AssertionError("unsafe production default was not blocked")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        copy_fixture(temp)
        env_path = temp / "deploy/production.env.example"
        env_path.write_text(
            env_path.read_text(encoding="utf-8").replace(
                module.APPROVED_BACKEND_REFERENCE,
                "ghcr.io/gihohoho/upgrade-rpg-backend@sha256:" + "0" * 64,
            ),
            encoding="utf-8",
        )
        try:
            module.inspect_production_static_templates(temp)
        except module.ProductionStaticValidationError:
            pass
        else:
            raise AssertionError("unapproved production image digest was not blocked")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        copy_fixture(temp)
        compose = temp / "deploy/docker-compose.production.yml"
        compose.write_text(
            compose.read_text(encoding="utf-8").replace(
                "services:\n  backend:",
                "services:\n  postgres:\n    image: postgres:16\n  backend:",
            ),
            encoding="utf-8",
        )
        try:
            module.inspect_production_static_templates(temp)
        except module.ProductionStaticValidationError:
            pass
        else:
            raise AssertionError("bundled PostgreSQL service was not blocked")

    print("OK: current production secrets/TLS/container static validation smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

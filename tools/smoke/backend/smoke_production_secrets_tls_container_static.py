#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_production_secrets_tls_container_static.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("v310_production_static", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v310 production static checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_tool()
    result = module.inspect_production_static_templates(ROOT)
    assert result["result"] == module.READY_RESULT
    assert result["requiredComposeValueCount"] == 9
    assert result["tlsVerifyFullExample"] is True
    assert result["tlsCaPathExample"] is True
    assert result["realSecretValuesAbsent"] is True
    assert result["adminerAbsent"] is True
    assert result["hostPortsAbsent"] is True
    assert result["backendHealthcheck"] is True
    assert result["automaticAlembicAbsent"] is True
    assert result["actualMutationExecuted"] is False
    assert result["actualProductionSecretsTlsContainerExecutionApproved"] is False

    # A local default secret in a production template must fail closed.
    with tempfile.TemporaryDirectory() as temp_dir:
        temp = Path(temp_dir)
        for relative in (
            "deploy/docker-compose.production.yml",
            "deploy/production.env.example",
            "deploy/README.md",
            "deploy/secrets/README.md",
            "docs/current/POSTGRES_PRODUCTION_STATIC_VALIDATION.md",
            "backend/Dockerfile",
            ".gitignore",
            ".dockerignore",
        ):
            target = temp / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8")
        env_path = temp / "deploy/production.env.example"
        env_path.write_text(env_path.read_text(encoding="utf-8").replace(
            "<generate-a-random-secret-of-at-least-32-characters>",
            "change-me-before-production",
        ), encoding="utf-8")
        try:
            module.inspect_production_static_templates(temp)
        except module.ProductionStaticValidationError:
            pass
        else:
            raise AssertionError("unsafe production default was not blocked")

    print("OK: v310 production secrets/TLS/container static validation smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

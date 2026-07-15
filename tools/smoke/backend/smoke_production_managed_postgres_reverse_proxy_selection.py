#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_production_managed_postgres_reverse_proxy_selection.py"
REQUIRED_FILES = (
    "deploy/production-architecture-selection.example.json",
    "deploy/production-capacity-plan.example.json",
    "deploy/docker-compose.production.yml",
    "deploy/production.env.example",
    "backend/Dockerfile",
    "docs/current/POSTGRES_PRODUCTION_MANAGED_DB_PROXY_SELECTION.md",
    "deploy/reverse-proxy/README.md",
    "deploy/isolated-validation/README.md",
)


def load_tool():
    spec = importlib.util.spec_from_file_location("v312_production_selection", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v312 production selection checker")
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
        module.inspect_production_architecture_selection(temp)
    except module.ProductionArchitectureSelectionError:
        return
    raise AssertionError("unsafe v312 architecture selection was not blocked")


def main() -> int:
    module = load_tool()
    result = module.inspect_production_architecture_selection(ROOT)
    assert result["result"] == module.READY_RESULT
    assert result["databaseMode"] == "managed-postgresql-selected"
    assert result["databaseTlsMode"] == "verify-full-with-provider-ca"
    assert result["publicEntrypoint"] == "external-reverse-proxy-https-selected"
    assert result["reverseProxyProduct"] == "deferred"
    assert result["backendReplicas"] == 1
    assert result["uvicornWorkersPerReplica"] == 1
    assert result["composeServices"] == ["backend"]
    assert result["requiredComposeValueCount"] == 7
    assert result["composeConfigRenderApproved"] is True
    assert result["composeConfigRenderExecuted"] is False
    assert result["imagePullBuildApproved"] is False
    assert result["containerStartApproved"] is False
    assert result["actualMutationExecuted"] is False

    for key, value in (
        ("databaseMode", "bundled-postgresql"),
        ("backendReplicas", 2),
        ("composeConfigRenderApproved", False),
        ("imagePullBuildApproved", True),
        ("containerStartApproved", True),
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            path = temp / "deploy/production-architecture-selection.example.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload[key] = value
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            expect_blocked(module, temp)

    print("OK: v312 managed PostgreSQL/reverse proxy selection smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

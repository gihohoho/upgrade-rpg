#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_production_capacity_tls_network_plan.py"
REQUIRED_FILES = (
    "deploy/production-capacity-plan.example.json",
    "deploy/docker-compose.production.yml",
    "deploy/production.env.example",
    "deploy/README.md",
    "deploy/isolated-validation/README.md",
    "docs/reference/database/POSTGRES_PRODUCTION_CAPACITY_TLS_NETWORK_PLAN.md",
    "backend/Dockerfile",
)


def load_tool():
    spec = importlib.util.spec_from_file_location("v311_production_capacity", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load v311 production capacity checker")
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
        module.inspect_production_capacity_plan(temp)
    except module.ProductionCapacityPlanError:
        return
    raise AssertionError("unsafe production capacity plan was not blocked")


def main() -> int:
    module = load_tool()
    result = module.inspect_production_capacity_plan(ROOT)
    assert result["result"] == module.READY_RESULT
    assert result["engineCount"] == 1
    assert result["applicationSteadyConnections"] == 5
    assert result["applicationBurstConnections"] == 15
    assert result["nonApplicationReserve"] == 10
    assert result["recommendedMinimum"] == 30
    assert result["postgresMaxConnectionsCandidate"] == 40
    assert result["candidateSpareAfterPlannedPeak"] == 15
    assert result["twoReplicaRecommendedMinimum"] == 50
    assert result["twoReplicaTwoWorkerRecommendedMinimum"] == 90
    assert result["tlsDatabaseMode"] == "managed-postgresql-selected"
    assert result["reverseProxyOnly"] is True
    assert result["managedDatabaseBoundary"] is True
    assert result["composeConfigRenderApproved"] is True
    assert result["composeConfigRenderExecuted"] is True
    assert result["actualDockerCommandExecuted"] is False
    assert result["isolatedContainerExecutionApproved"] is False

    for key, value in (
        ("postgresMaxConnectionsCandidate", 20),
        ("composeConfigRenderExecuted", False),
        ("isolatedContainerExecutionApproved", True),
        ("imagePullBuildApproved", True),
        ("tlsDatabaseMode", "disable-tls"),
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            copy_fixture(temp)
            plan_path = temp / "deploy/production-capacity-plan.example.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan[key] = value
            plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
            expect_blocked(module, temp)

    print("OK: v311-v313 production capacity/TLS/network plan smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL_PATH = ROOT / "tools/check_production_deployment_plan.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("production_deployment_plan", TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture() -> Path:
    root = Path(tempfile.mkdtemp(prefix="upgrade-rpg-deploy-plan-"))
    for relative in (
        "deploy/production-deploy-plan.example.json",
        "deploy/production.env.example",
        "deploy/docker-compose.production.yml",
        "deploy/review/isolated-image-pull-validation-v333.json",
        "docs/current/PRODUCTION_DEPLOYMENT_PLAN.md",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    return root


def must_block(tool, mutate) -> None:
    root = fixture()
    try:
        path = root / "deploy/production-deploy-plan.example.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        mutate(payload)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        try:
            tool.inspect_plan(root)
        except tool.DeploymentPlanError:
            return
        raise AssertionError("mutated production deployment plan was accepted")
    finally:
        shutil.rmtree(root)


def main() -> int:
    tool = load_tool()
    result = tool.inspect_plan(ROOT)
    assert result["result"] == tool.RESULT
    assert result["approvalReady"] is False
    assert result["productionDeploymentExecuted"] is False

    must_block(tool, lambda value: value["approvalContract"].update({"productionDeploymentApproved": True}))
    must_block(tool, lambda value: value["image"].update({"reference": value["image"]["reference"][:-1] + "0"}))
    must_block(tool, lambda value: value["requiredInputs"][0].update({"status": "resolved"}))
    must_block(tool, lambda value: value["orderedExecution"].append("docker compose down -v"))

    print("OK: v334 production deployment plan remains reviewed and fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

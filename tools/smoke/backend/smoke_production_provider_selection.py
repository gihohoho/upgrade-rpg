#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[3]
TOOL_PATH = ROOT / "tools/check_production_provider_selection.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("production_provider_selection", TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture() -> Path:
    root = Path(tempfile.mkdtemp(prefix="upgrade-rpg-provider-selection-"))
    for relative in (
        "deploy/production-provider-selection.example.json",
        "deploy/production-deploy-plan.example.json",
        "docs/current/PRODUCTION_PROVIDER_SELECTION.md",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    return root


def must_block(tool, mutate) -> None:
    root = fixture()
    try:
        path = root / "deploy/production-provider-selection.example.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        mutate(payload)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        try:
            tool.inspect_selection(root)
        except tool.ProviderSelectionError:
            return
        raise AssertionError("mutated provider selection was accepted")
    finally:
        shutil.rmtree(root)


def main() -> int:
    tool = load_tool()
    result = tool.inspect_selection(ROOT)
    assert result["result"] == tool.RESULT
    assert result["monthlyFixedCostUsd"] == 0
    assert result["accountOnboardingComplete"] is False
    assert result["productionDeploymentExecuted"] is False

    must_block(tool, lambda value: value["selectionStatus"].update({"paymentMethodAdded": True}))
    must_block(tool, lambda value: value["runtime"].update({"automaticDeploy": True}))
    must_block(tool, lambda value: value["database"].update({"tlsMode": "require"}))
    must_block(tool, lambda value: value["retainedSafetyBoundary"].update({"productionDeploymentApprovalReady": True}))
    must_block(tool, lambda value: value["database"].update({"endpointHostname": "secret.example"}))
    must_block(tool, lambda value: value["officialEvidence"].append("https://example.com/untrusted"))

    print("OK: v335 cost-minimum provider selection remains evidence-backed and fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

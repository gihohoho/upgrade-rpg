#!/usr/bin/env python3
"""Focused fail-closed smoke for the v351 public release gate contract."""

from __future__ import annotations

import copy
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_v351_public_release_gates.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("v351_release_gate", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expect_blocked(module, plan: dict, mutate) -> None:
    candidate = copy.deepcopy(plan)
    mutate(candidate)
    try:
        module.validate_contract(candidate)
    except module.ReleaseGateError:
        return
    raise AssertionError("unsafe v351 public release contract was accepted")


def main() -> int:
    module = load_tool()
    plan = module.load_json(module.PLAN_PATH)
    module.validate_contract(plan)

    mutations = (
        lambda p: p.update({"productionResourcesMutated": True}),
        lambda p: p["githubActions"].update({"lifecycleState": "authorization-open"}),
        lambda p: p["githubActions"].update({"publishReviewerGateReady": True}),
        lambda p: p["githubActions"].update({"approvedPreparationSha": "a" * 40}),
        lambda p: p["githubActions"].update({"ownerApprovalRecorded": True}),
        lambda p: p["githubActions"].update({"newWorkflowDispatchExecuted": True}),
        lambda p: p["githubActions"].update({"newRegistryMutationExecuted": True}),
        lambda p: p["backendRelease"].update({"newImageReference": module.CURRENT_IMAGE}),
        lambda p: p["backendRelease"].update({"renderExactImageDeployPreparationReady": True}),
        lambda p: p["backendRelease"].update({"renderDeployApproved": True}),
        lambda p: p["frontendRelease"].update({"autoDeploy": True}),
        lambda p: p["frontendRelease"].update({"staticDeployPreparationReady": True}),
        lambda p: p["frontendRelease"].update({"staticDeployApproved": True}),
    )
    for mutate in mutations:
        expect_blocked(module, plan, mutate)

    print("v351 public release gate smoke")
    print("- preparation self-approval/open gate/dispatch/registry mutation: rejected")
    print("- premature backend Render deploy: rejected")
    print("- premature frontend static deploy or auto-deploy: rejected")
    print("- database/admin/content mutation scope: absent")
    print("- result: v351-public-release-gates-fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

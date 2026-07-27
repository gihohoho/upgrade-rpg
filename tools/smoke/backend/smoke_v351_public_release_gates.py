#!/usr/bin/env python3
"""Focused fail-closed smoke for the v351 provider release gate contract."""

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
    raise AssertionError("unsafe v351 provider release contract was accepted")


def main() -> int:
    module = load_tool()
    plan = module.load_json(module.PLAN_PATH)
    module.validate_contract(plan)

    mutations = (
        lambda p: p.update({"productionResourcesMutated": False}),
        lambda p: p["ownerApproval"].update({"scopeConsumed": False}),
        lambda p: p["githubActions"].update({"lifecycleState": "authorization-open"}),
        lambda p: p["githubActions"].update({"publishReviewerGateReady": True}),
        lambda p: p["githubActions"].update({"workflowRunAttempt": 2}),
        lambda p: p["githubActions"].update({"workflowConclusion": "failure"}),
        lambda p: p["githubActions"].update({"signatureVerified": False}),
        lambda p: p["backendRelease"].update({"newImageReference": module.OLD_IMAGE}),
        lambda p: p["backendRelease"].update({"isolatedRuntimeValidationComplete": False}),
        lambda p: p["backendRelease"].update({"renderDeployApproved": False}),
        lambda p: p["backendRelease"].update({"renderDeployExecuted": False}),
        lambda p: p["backendRelease"].update({"renderDeployCount": 2}),
        lambda p: p["backendRelease"].update({"automaticRetry": True}),
        lambda p: p["frontendRelease"].update({"autoDeploy": True}),
        lambda p: p["frontendRelease"].update({"staticDeployApproved": False}),
        lambda p: p["frontendRelease"].update({"staticDeployExecuted": False}),
        lambda p: p["frontendRelease"].update({"staticDeployCount": 2}),
        lambda p: p["validation"].update({"browserMasterDataAppliedWithoutFallback": False}),
        lambda p: p["validation"].update({"adminGuardedReadOnlyVerified": False}),
        lambda p: p["approvalScopeAfterExactSha"].update({"databaseWrite": True}),
        lambda p: p["approvalScopeAfterExactSha"].update({"adminWrite": True}),
    )
    for mutate in mutations:
        expect_blocked(module, plan, mutate)

    print("v351 provider release gate smoke")
    print("- workflow rerun/open gate/unverified image: rejected")
    print("- missing approval, non-live deploy, or duplicate deploy: rejected")
    print("- provider auto-deploy/retry: rejected")
    print("- fallback or unverified admin guard: rejected")
    print("- database/Alembic/admin/content mutation: rejected")
    print("- result: v351-provider-release-gates-fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

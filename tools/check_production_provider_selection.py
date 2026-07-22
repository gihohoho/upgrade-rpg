#!/usr/bin/env python3
"""Fail-closed validation for the v335 cost-minimum provider selection."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse

VERSION = "v335.cost-minimum-provider-selection-account-onboarding-required"
RESULT = "cost-minimum-production-provider-selected-account-onboarding-required"
NEXT_STAGE = "owner-connect-render-and-neon-accounts"
SELECTION_PATH = "deploy/production-provider-selection.example.json"
DEPLOYMENT_PLAN_PATH = "deploy/production-deploy-plan.example.json"
DOC_PATH = "docs/current/PRODUCTION_PROVIDER_SELECTION.md"
IMAGE = "ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2"


class ProviderSelectionError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProviderSelectionError(message)


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing JSON file: {path.as_posix()}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProviderSelectionError(f"invalid JSON: {path.as_posix()}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root must be an object: {path.as_posix()}")
    return value


def boolean(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    require(isinstance(value, bool), f"{key} must be boolean")
    return value


def inspect_selection(root: Path) -> dict[str, Any]:
    selection = read_json(root / SELECTION_PATH)
    deploy_plan = read_json(root / DEPLOYMENT_PLAN_PATH)
    doc = (root / DOC_PATH).read_text(encoding="utf-8")

    require(selection.get("schemaVersion") == VERSION, "provider selection schemaVersion changed")
    require(
        set(selection) == {
            "schemaVersion", "researchedAtUtc", "selectionStatus", "runtime", "database",
            "ingressAndSecrets", "retainedSafetyBoundary", "rejectedAlternatives",
            "officialEvidence", "unresolvedInputs", "nextSafeStage",
        },
        "provider selection top-level schema changed",
    )
    require(
        re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(selection.get("researchedAtUtc"))) is not None,
        "researchedAtUtc must be UTC second precision",
    )

    status = selection.get("selectionStatus")
    require(isinstance(status, dict), "selectionStatus must be an object")
    for key in ("requestedByOwner", "costMinimumRequested", "selected"):
        require(boolean(status, key) is True, f"selection status must remain true: {key}")
    for key in ("productionResourcesMutated", "paymentMethodAdded"):
        require(boolean(status, key) is False, f"selection must remain non-mutating: {key}")
    require(status.get("monthlyFixedCostUsd") == 0, "selected fixed monthly cost must remain zero")
    require(status.get("deploymentClass") == "personal-hobby-public-preview-not-sla-production", "free tier must not be labeled SLA production")

    runtime = selection.get("runtime")
    require(isinstance(runtime, dict), "runtime must be an object")
    require((runtime.get("provider"), runtime.get("product"), runtime.get("plan")) == ("render", "web-service", "free"), "runtime selection changed")
    require(runtime.get("region") == "singapore", "Render region must remain Singapore")
    require(runtime.get("instanceCount") == 1 and runtime.get("ramMb") == 512 and runtime.get("cpu") == 0.1, "Render Free capacity changed")
    require(runtime.get("deploymentMethod") == "manual-image-backed-service", "runtime deployment must remain manual and image-backed")
    require(runtime.get("imageReference") == IMAGE and runtime.get("imagePlatform") == "linux/amd64", "runtime image identity changed")
    require(boolean(runtime, "automaticDeploy") is False, "automatic deploy must remain disabled")
    require(boolean(runtime, "managedTls") is True, "managed TLS must remain enabled")
    require(runtime.get("idleSpinDownMinutes") == 15 and runtime.get("coldStartApproxSeconds") == 60, "free runtime limitation record changed")
    require("do-not-add" in str(runtime.get("paymentMethodPolicy")), "no-payment-method cost guard is missing")

    database = selection.get("database")
    require(isinstance(database, dict), "database must be an object")
    require((database.get("provider"), database.get("plan"), database.get("region")) == ("neon", "free", "aws-ap-southeast-1"), "database selection changed")
    require(database.get("postgresqlMajorVersion") == 16, "PostgreSQL major version changed")
    require(database.get("storageLimitGb") == 0.5 and database.get("computeUnitHoursPerProjectMonth") == 100, "Neon Free limit record changed")
    require(database.get("restoreWindowHours") == 6, "Neon Free restore window changed")
    require(database.get("tlsMode") == "verify-full", "database TLS must remain verify-full")
    require(boolean(database, "pooledRuntimeConnection") is True, "runtime must use pooled database connection")
    require(boolean(database, "directMigrationConnection") is False, "migration connection must remain unopened")
    for key in ("endpointHostname", "databaseName", "roleName"):
        require(database.get(key) is None, f"uncreated database field must remain null: {key}")

    ingress = selection.get("ingressAndSecrets")
    require(isinstance(ingress, dict), "ingressAndSecrets must be an object")
    require(ingress.get("publicAddress") is None if "publicAddress" in ingress else True, "actual public address must not be recorded")
    require(boolean(ingress, "httpsRedirect") is True, "HTTPS redirect must remain enabled")
    require(boolean(ingress, "customDomainRequiredForFirstDeploy") is False, "custom domain must remain optional")
    require(boolean(ingress, "dnsChangeRequiredForFirstDeploy") is False, "first deploy must not require DNS mutation")
    require(boolean(ingress, "repositorySecretsAllowed") is False, "repository secret values must remain forbidden")
    require(boolean(ingress, "actualSecretValuesRecorded") is False, "actual secret values must not be recorded")

    safety = selection.get("retainedSafetyBoundary")
    require(isinstance(safety, dict), "retainedSafetyBoundary must be an object")
    require(safety.get("backendReplicas") == 1 and safety.get("uvicornWorkers") == 1, "backend replicas/workers must remain 1/1")
    require(boolean(safety, "exactPreparationShaApprovalStillRequired") is True, "exact-SHA approval guard is missing")
    for key in (
        "automaticMigration", "automaticDeployment", "databaseMutationApproved",
        "alembicMutationApproved", "productionDeploymentApprovalReady",
        "productionDeploymentApproved", "productionDeploymentExecuted",
    ):
        require(boolean(safety, key) is False, f"unsafe boundary opened: {key}")

    rejected = selection.get("rejectedAlternatives")
    require(isinstance(rejected, list) and {item.get("option") for item in rejected if isinstance(item, dict)} == {
        "render-free-postgresql", "koyeb-free-web-plus-koyeb-free-postgresql", "fly-io-plus-neon-free",
    }, "alternative comparison record changed")

    evidence = selection.get("officialEvidence")
    require(isinstance(evidence, list) and len(evidence) >= 10, "official evidence inventory is incomplete")
    allowed_hosts = {"render.com", "neon.com", "www.koyeb.com", "fly.io"}
    require(all(urlparse(url).scheme == "https" and urlparse(url).hostname in allowed_hosts for url in evidence), "non-official evidence URL entered selection")

    unresolved = selection.get("unresolvedInputs")
    expected_keys = {
        "render-account", "neon-account", "render-service", "neon-project",
        "registry-read-credential", "runtime-secrets-and-cors", "database-initialization-and-backup",
    }
    require(isinstance(unresolved, list) and {item.get("key") for item in unresolved if isinstance(item, dict)} == expected_keys, "unresolved onboarding inventory changed")
    require(all(item.get("status") != "resolved" for item in unresolved), "provider onboarding cannot be marked resolved before account connection")

    require(deploy_plan.get("schemaVersion") == "v334.production-deploy-plan-reviewed-inputs-blocked", "v334 deployment safety baseline changed")
    approval = deploy_plan.get("approvalContract", {})
    require(approval.get("approvalReady") is False and approval.get("productionDeploymentExecuted") is False, "v334 deployment approval boundary opened")
    require(all(item.get("status") == "unresolved" for item in deploy_plan.get("requiredInputs", [])), "actual deployment inputs must remain unresolved")

    for marker in (
        "Render Free Web Service", "Neon Free", "AWS Singapore", "$0", "verify-full",
        IMAGE, "owner-connect-render-and-neon-accounts", "production resources created: no",
    ):
        require(marker in doc, f"provider selection document missing marker: {marker}")
    require(selection.get("nextSafeStage") == NEXT_STAGE, "next safe stage changed")

    return {
        "toolVersion": VERSION,
        "runtime": "render-free-web-service-singapore",
        "database": "neon-free-postgresql16-aws-ap-southeast-1",
        "monthlyFixedCostUsd": 0,
        "providerSelectionComplete": True,
        "accountOnboardingComplete": False,
        "productionResourcesMutated": False,
        "productionDeploymentApprovalReady": False,
        "productionDeploymentExecuted": False,
        "result": RESULT,
        "nextSafeStage": NEXT_STAGE,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = inspect_selection(root)
    except (ProviderSelectionError, OSError) as exc:
        payload = {"toolVersion": VERSION, "result": "blocked-or-failed", "reason": str(exc)}
        print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else f"Production provider selection verification\n- result: blocked-or-failed\n- reason: {exc}")
        return 1 if args.strict else 0
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Production provider selection verification")
        print("- selected: Render Free Web Service (Singapore) + Neon Free PostgreSQL 16 (Singapore)")
        print("- fixed monthly cost: USD 0")
        print("- account onboarding/resources/deploy: no/no/no")
        print(f"- result: {result['result']}")
        print(f"- next safe stage: {result['nextSafeStage']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

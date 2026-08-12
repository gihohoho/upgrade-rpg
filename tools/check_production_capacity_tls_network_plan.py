#!/usr/bin/env python3
"""Validate the v311 production capacity/TLS/network plan without side effects.

This tool reads repository files only. It does not read real environment or
secret files, invoke Docker, connect to PostgreSQL, or execute Alembic.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
from typing import Any

TOOL_VERSION = "v311.production-capacity-tls-network-plan"
READY_RESULT = "production-capacity-tls-network-plan-verified-execution-blocked"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "select-registry-repository-platform-and-base-image-digest"
ALLOWED_TLS_MODES = {
    "managed-postgresql-preferred",
    "managed-postgresql-selected",
    "bundled-postgresql-tls-deferred",
}


class ProductionCapacityPlanError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ProductionCapacityPlanError(message)


def _read(path: Path) -> str:
    if not path.is_file():
        raise ProductionCapacityPlanError(f"required file is missing: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise ProductionCapacityPlanError(f"invalid JSON: {path.as_posix()}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProductionCapacityPlanError(f"JSON root must be an object: {path.as_posix()}")
    return value


def _int_value(plan: dict[str, Any], key: str, *, minimum: int, maximum: int) -> int:
    value = plan.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ProductionCapacityPlanError(f"{key} must be an integer")
    if not minimum <= value <= maximum:
        raise ProductionCapacityPlanError(f"{key} must be between {minimum} and {maximum}")
    return value


def _bool_value(plan: dict[str, Any], key: str) -> bool:
    value = plan.get(key)
    if not isinstance(value, bool):
        raise ProductionCapacityPlanError(f"{key} must be a boolean")
    return value


def _round_up_to_ten(value: int) -> int:
    return int(math.ceil(value / 10) * 10)


def _capacity_for(
    *,
    replicas: int,
    workers: int,
    pool_size: int,
    max_overflow: int,
    background_processes: int,
    background_pool_size: int,
    reserve: int,
    safety_percent: int,
) -> dict[str, int]:
    engine_count = replicas * workers
    application_steady = engine_count * pool_size
    application_burst = engine_count * (pool_size + max_overflow)
    background_burst = background_processes * background_pool_size
    planned_peak_before_safety = application_burst + background_burst + reserve
    raw_recommendation = math.ceil(
        planned_peak_before_safety * (100 + safety_percent) / 100
    )
    recommended_minimum = _round_up_to_ten(raw_recommendation)
    return {
        "engineCount": engine_count,
        "applicationSteadyConnections": application_steady,
        "applicationBurstConnections": application_burst,
        "backgroundBurstConnections": background_burst,
        "plannedPeakBeforeSafety": planned_peak_before_safety,
        "rawRecommendation": raw_recommendation,
        "recommendedMinimum": recommended_minimum,
    }


def inspect_production_capacity_plan(root: Path) -> dict[str, Any]:
    plan_path = root / "deploy/production-capacity-plan.example.json"
    plan = _read_json(plan_path)
    compose = _read(root / "deploy/docker-compose.production.yml")
    env_example = _read(root / "deploy/production.env.example")
    dockerfile = _read(root / "backend/Dockerfile")
    plan_doc = _read(root / "docs/reference/database/POSTGRES_PRODUCTION_CAPACITY_TLS_NETWORK_PLAN.md")
    isolated_doc = _read(root / "deploy/isolated-validation/README.md")
    deploy_readme = _read(root / "deploy/README.md")

    _require(plan.get("schemaVersion") == "v311.production-capacity-plan", "unexpected capacity plan schemaVersion")
    _require(_bool_value(plan, "reviewOnly") is True, "capacity plan must remain review-only")

    replicas = _int_value(plan, "backendReplicas", minimum=1, maximum=20)
    workers = _int_value(plan, "uvicornWorkersPerReplica", minimum=1, maximum=32)
    pool_size = _int_value(plan, "dbPoolSizePerWorker", minimum=1, maximum=100)
    max_overflow = _int_value(plan, "dbMaxOverflowPerWorker", minimum=0, maximum=200)
    background_processes = _int_value(plan, "backgroundWorkerProcesses", minimum=0, maximum=50)
    background_pool_size = _int_value(plan, "backgroundWorkerPoolSize", minimum=0, maximum=100)
    migration_connections = _int_value(plan, "migrationConnections", minimum=0, maximum=20)
    monitoring_connections = _int_value(plan, "monitoringConnections", minimum=0, maximum=50)
    admin_emergency_connections = _int_value(plan, "adminEmergencyConnections", minimum=1, maximum=50)
    other_reserved_connections = _int_value(plan, "otherReservedConnections", minimum=0, maximum=100)
    safety_percent = _int_value(plan, "safetyMarginPercent", minimum=10, maximum=100)
    candidate = _int_value(plan, "postgresMaxConnectionsCandidate", minimum=10, maximum=10000)

    reserve = (
        migration_connections
        + monitoring_connections
        + admin_emergency_connections
        + other_reserved_connections
    )
    capacity = _capacity_for(
        replicas=replicas,
        workers=workers,
        pool_size=pool_size,
        max_overflow=max_overflow,
        background_processes=background_processes,
        background_pool_size=background_pool_size,
        reserve=reserve,
        safety_percent=safety_percent,
    )

    _require(candidate >= capacity["recommendedMinimum"], "PostgreSQL max_connections candidate is below the calculated minimum")
    candidate_spare = candidate - capacity["plannedPeakBeforeSafety"]
    _require(candidate_spare >= admin_emergency_connections, "candidate does not preserve the emergency admin reserve")

    tls_mode = plan.get("tlsDatabaseMode")
    _require(isinstance(tls_mode, str) and tls_mode in ALLOWED_TLS_MODES, "unsupported tlsDatabaseMode")
    _require(
        plan.get("publicEntrypoint") == "external-reverse-proxy-https-selected",
        "public entrypoint must match the selected external reverse proxy HTTPS mode",
    )
    _require(_bool_value(plan, "composeConfigRenderApproved") is True, "Compose config render must be approved")
    _require(_bool_value(plan, "composeConfigRenderExecuted") is True, "completed config render must be recorded")
    _require(plan.get("composeConfigRenderEvidence") == "deploy/review/production-compose-config-render-v312.json", "config render evidence path is missing")
    _require(_bool_value(plan, "imagePullBuildApproved") is False, "image pull/build must remain unapproved")
    _require(_bool_value(plan, "isolatedContainerExecutionApproved") is False, "isolated container execution must remain unapproved")
    _require(_bool_value(plan, "actualProductionValuesApplied") is False, "actual production values must remain unapplied")

    docker_cmd = next(
        (line.strip() for line in dockerfile.splitlines() if line.strip().startswith("CMD ")),
        "",
    )
    dockerfile_single_worker = "--workers" not in docker_cmd
    _require(dockerfile_single_worker and workers == 1, "capacity plan must match the current single-worker Dockerfile")
    _require(replicas == 1 and "replicas: 1" in compose, "capacity plan must match the selected single backend replica template")

    pool_size_marker = f"DB_POOL_SIZE: ${{DB_POOL_SIZE:-{pool_size}}}"
    overflow_marker = f"DB_MAX_OVERFLOW: ${{DB_MAX_OVERFLOW:-{max_overflow}}}"
    _require(pool_size_marker in compose, "capacity pool size differs from production Compose default")
    _require(overflow_marker in compose, "capacity max overflow differs from production Compose default")
    _require(f"DB_POOL_SIZE={pool_size}" in env_example, "capacity pool size differs from production env example")
    _require(f"DB_MAX_OVERFLOW={max_overflow}" in env_example, "capacity max overflow differs from production env example")

    reverse_proxy_only = all(
        marker in compose
        for marker in (
            'expose:\n      - "8000"',
            "- edge",
            "external: true",
            "EDGE_NETWORK_NAME",
        )
    ) and re.search(r"(?m)^\s+ports:\s*$", compose) is None
    managed_database_boundary = all(
        marker not in compose.lower()
        for marker in ("  postgres:", "adminer", "postgres_password")
    ) and re.search(r"(?m)^volumes:\s*$", compose) is None
    _require(reverse_proxy_only, "backend must remain external-proxy-only without host ports")
    _require(managed_database_boundary, "bundled PostgreSQL service/volume must remain absent")

    for marker in (
        "managed-postgresql-selected",
        "bundled PostgreSQL TLS",
        "reverse proxy",
        "HTTPS `443`",
        "recommended minimum: 30",
        "review candidate max_connections: 40",
        "config render approved: yes",
        "isolated container execution approved: no",
        NEXT_SAFE_STAGE,
    ):
        _require(marker in plan_doc, f"capacity/TLS/network document is missing: {marker}")

    for marker in (
        "Stage 0",
        "Stage 1 — 완료: config render only",
        "v312-config-render-only",
        "Stage 2",
        "Stage 3",
        "Stage 4",
        "actual Docker config command executed on user PC: yes (config only)",
        "isolated container execution approved: no",
    ):
        _require(marker in isolated_doc, f"isolated validation plan is missing: {marker}")

    _require(
        all(marker in deploy_readme for marker in ("max_connections", "reverse proxy", "pull/build")),
        "deploy README must retain the production execution boundary",
    )

    scenario_two_replicas = _capacity_for(
        replicas=2,
        workers=workers,
        pool_size=pool_size,
        max_overflow=max_overflow,
        background_processes=background_processes,
        background_pool_size=background_pool_size,
        reserve=reserve,
        safety_percent=safety_percent,
    )
    scenario_two_by_two = _capacity_for(
        replicas=2,
        workers=2,
        pool_size=pool_size,
        max_overflow=max_overflow,
        background_processes=background_processes,
        background_pool_size=background_pool_size,
        reserve=reserve,
        safety_percent=safety_percent,
    )

    return {
        "toolVersion": TOOL_VERSION,
        "planSchemaVersion": plan["schemaVersion"],
        "backendReplicas": replicas,
        "uvicornWorkersPerReplica": workers,
        "engineCount": capacity["engineCount"],
        "poolSizePerWorker": pool_size,
        "maxOverflowPerWorker": max_overflow,
        "applicationSteadyConnections": capacity["applicationSteadyConnections"],
        "applicationBurstConnections": capacity["applicationBurstConnections"],
        "nonApplicationReserve": reserve,
        "safetyMarginPercent": safety_percent,
        "plannedPeakBeforeSafety": capacity["plannedPeakBeforeSafety"],
        "rawRecommendation": capacity["rawRecommendation"],
        "recommendedMinimum": capacity["recommendedMinimum"],
        "postgresMaxConnectionsCandidate": candidate,
        "candidateSpareAfterPlannedPeak": candidate_spare,
        "twoReplicaRecommendedMinimum": scenario_two_replicas["recommendedMinimum"],
        "twoReplicaTwoWorkerRecommendedMinimum": scenario_two_by_two["recommendedMinimum"],
        "tlsDatabaseMode": tls_mode,
        "reverseProxyOnly": reverse_proxy_only,
        "managedDatabaseBoundary": managed_database_boundary,
        "composeConfigRenderApproved": True,
        "composeConfigRenderExecuted": True,
        "dockerfileSingleWorker": dockerfile_single_worker,
        "actualDockerCommandExecuted": False,
        "actualSecretOrCertificateCreated": False,
        "actualDatabaseOrAlembicMutationExecuted": False,
        "isolatedContainerExecutionApproved": False,
        "actualProductionValuesApplied": False,
        "result": READY_RESULT,
        "nextSafeStage": NEXT_SAFE_STAGE,
    }


def render(result: dict[str, Any]) -> str:
    return "\n".join(
        (
            "Production capacity / TLS / network / isolated-container plan validation (read-only)",
            "No real env/secret read, Docker command, DB connection/write, or Alembic command was executed.",
            "",
            f"- backend replicas/workers: {result['backendReplicas']}/{result['uvicornWorkersPerReplica']}",
            f"- SQLAlchemy engine count: {result['engineCount']}",
            f"- pool steady/burst connections: {result['applicationSteadyConnections']}/{result['applicationBurstConnections']}",
            f"- non-application reserve/safety margin: {result['nonApplicationReserve']}/{result['safetyMarginPercent']}%",
            f"- planned peak before safety: {result['plannedPeakBeforeSafety']}",
            f"- recommended/candidate max_connections: {result['recommendedMinimum']}/{result['postgresMaxConnectionsCandidate']}",
            f"- candidate spare after planned peak: {result['candidateSpareAfterPlannedPeak']}",
            f"- future 2-replica / 2x2-worker minimums: {result['twoReplicaRecommendedMinimum']}/{result['twoReplicaTwoWorkerRecommendedMinimum']}",
            f"- TLS database mode: {result['tlsDatabaseMode']}",
            f"- reverse proxy only / managed DB boundary: {result['reverseProxyOnly']}/{result['managedDatabaseBoundary']}",
            "- compose config render approved/executed: yes/yes",
            "- actual Docker command executed: no",
            "- actual secret/CA/cert/key created: no",
            "- actual DB/Alembic mutation executed: no",
            "- isolated container execution approved: no",
            f"- result: {result['result']}",
            f"- next safe stage: {result['nextSafeStage']}",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Return non-zero when the plan boundary fails")
    parser.add_argument("--json", action="store_true", help="Print sanitized JSON")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]

    try:
        result = inspect_production_capacity_plan(root)
    except Exception as exc:  # fail closed with a short sanitized reason
        blocked = {
            "toolVersion": TOOL_VERSION,
            "result": BLOCKED_RESULT,
            "reason": f"{type(exc).__name__}: {exc}",
            "actualMutationExecuted": False,
        }
        if args.json:
            print(json.dumps(blocked, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(
                "Production capacity/TLS/network plan validation\n"
                f"- result: {BLOCKED_RESULT}\n"
                f"- reason: {blocked['reason']}\n"
                "- no mutation was executed."
            )
        return 1 if args.strict else 0

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate the v312 managed PostgreSQL/reverse-proxy architecture selection.

This checker reads repository files only. It does not read a real .env or
secret, invoke Docker, connect to PostgreSQL, or execute Alembic.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

TOOL_VERSION = "v312.production-managed-postgres-reverse-proxy-selection"
READY_RESULT = "managed-postgresql-reverse-proxy-selection-verified-config-render-complete"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "review-render-report-and-approve-backend-image-source-digest"
APPROVED_BACKEND_REFERENCE = (
    "ghcr.io/gihohoho/upgrade-rpg-backend@"
    "sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2"
)


class ProductionArchitectureSelectionError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ProductionArchitectureSelectionError(message)


def _read(path: Path) -> str:
    if not path.is_file():
        raise ProductionArchitectureSelectionError(
            f"required file is missing: {path.as_posix()}"
        )
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise ProductionArchitectureSelectionError(
            f"invalid JSON: {path.as_posix()}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise ProductionArchitectureSelectionError(
            f"JSON root must be an object: {path.as_posix()}"
        )
    return value


def _bool_value(value: dict[str, Any], key: str) -> bool:
    item = value.get(key)
    if not isinstance(item, bool):
        raise ProductionArchitectureSelectionError(f"{key} must be a boolean")
    return item


def _required_placeholder(text: str, name: str) -> bool:
    return re.search(rf"\$\{{{re.escape(name)}:\?[^}}]+\}}", text) is not None


def _compose_service_names(text: str) -> list[str]:
    names: list[str] = []
    in_services = False
    for line in text.splitlines():
        if line == "services:":
            in_services = True
            continue
        if not in_services:
            continue
        if line and not line.startswith(" "):
            break
        match = re.match(r"^  ([A-Za-z0-9_.-]+):\s*$", line)
        if match:
            names.append(match.group(1))
    return names


def inspect_production_architecture_selection(root: Path) -> dict[str, Any]:
    selection = _read_json(
        root / "deploy/production-architecture-selection.example.json"
    )
    capacity = _read_json(root / "deploy/production-capacity-plan.example.json")
    compose = _read(root / "deploy/docker-compose.production.yml")
    env_example = _read(root / "deploy/production.env.example")
    dockerfile = _read(root / "backend/Dockerfile")
    selection_doc = _read(
        root / "docs/current/POSTGRES_PRODUCTION_MANAGED_DB_PROXY_SELECTION.md"
    )
    proxy_doc = _read(root / "deploy/reverse-proxy/README.md")
    isolated_doc = _read(root / "deploy/isolated-validation/README.md")
    evidence = _read_json(root / "deploy/review/production-compose-config-render-v312.json")

    _require(
        selection.get("schemaVersion") == "v312.production-architecture-selection",
        "unexpected architecture selection schemaVersion",
    )
    _require(_bool_value(selection, "reviewOnly") is True, "selection must remain review-only")
    _require(
        selection.get("databaseMode") == "managed-postgresql-selected",
        "managed PostgreSQL must be selected",
    )
    _require(
        selection.get("databaseTlsMode") == "verify-full-with-provider-ca",
        "managed PostgreSQL must use verify-full with provider CA",
    )
    _require(
        selection.get("publicEntrypoint")
        == "external-reverse-proxy-https-selected",
        "external reverse proxy HTTPS must be selected",
    )
    _require(selection.get("reverseProxyProduct") == "deferred", "proxy product must remain deferred")
    _require(selection.get("backendReplicas") == 1, "backend replica count must be 1")
    _require(selection.get("uvicornWorkersPerReplica") == 1, "Uvicorn worker count must be 1")
    _require(_bool_value(selection, "backendHostPortPublished") is False, "backend host port must remain unpublished")
    _require(_bool_value(selection, "databaseContainerIncluded") is False, "bundled PostgreSQL must be absent")
    _require(_bool_value(selection, "databaseHostPortPublished") is False, "database host port must remain unpublished")
    _require(_bool_value(selection, "composeConfigRenderApproved") is True, "config render must be approved")
    _require(_bool_value(selection, "composeConfigRenderExecuted") is True, "user-PC config render completion must be recorded")
    _require(selection.get("composeConfigRenderEvidence") == "deploy/review/production-compose-config-render-v312.json", "selection evidence path is missing")
    for key in (
        "imagePullBuildApproved",
        "containerStartApproved",
        "containerCleanupApproved",
        "actualProductionValuesApplied",
    ):
        _require(_bool_value(selection, key) is False, f"{key} must remain false")

    _require(
        capacity.get("tlsDatabaseMode") == "managed-postgresql-selected",
        "capacity plan does not match the selected database mode",
    )
    _require(
        capacity.get("publicEntrypoint")
        == "external-reverse-proxy-https-selected",
        "capacity plan does not match the selected public entrypoint",
    )
    _require(capacity.get("backendReplicas") == 1, "capacity replica count differs")
    _require(capacity.get("uvicornWorkersPerReplica") == 1, "capacity worker count differs")
    _require(capacity.get("composeConfigRenderApproved") is True, "capacity plan must approve config render")
    _require(capacity.get("composeConfigRenderExecuted") is True, "capacity plan must record completed config render")
    _require(capacity.get("composeConfigRenderEvidence") == "deploy/review/production-compose-config-render-v312.json", "capacity evidence path is missing")
    _require(capacity.get("imagePullBuildApproved") is False, "capacity plan must block image pull/build")
    _require(capacity.get("isolatedContainerExecutionApproved") is False, "capacity plan must block container execution")
    _require(capacity.get("actualProductionValuesApplied") is False, "capacity plan must keep production values unapplied")

    _require(evidence.get("schemaVersion") == "v312.production-compose-config-render-evidence", "unexpected config render evidence schemaVersion")
    _require(evidence.get("recordedFromUserOutput") is True, "config render evidence must come from user output")
    _require(evidence.get("reviewOnlySentinelsUsed") is True, "config render must use review-only sentinels")
    _require(evidence.get("rawRenderPersisted") is False, "raw render must not be persisted")
    _require(evidence.get("dockerSubcommand") == "compose config", "only compose config evidence is accepted")
    _require(evidence.get("renderedServices") == ["backend"], "config render services must be backend-only")
    for key in ("hostPortsAbsent", "buildAbsent", "namedVolumesAbsent", "managedDatabaseServiceAbsent", "digestReferenceRendered", "productionGuardRendered", "tlsVerifyFullProviderCaRendered", "externalEdgeNetworkRendered"):
        _require(evidence.get(key) is True, f"config render evidence failed: {key}")
    _require(evidence.get("backendReplicas") == 1, "rendered backend replicas must be 1")
    for key in ("imagePullBuildExecuted", "containerNetworkVolumeMutationExecuted", "databaseAlembicMutationExecuted"):
        _require(evidence.get(key) is False, f"unexpected config render mutation: {key}")
    _require(evidence.get("result") == "production-compose-config-render-verified-no-runtime-mutation", "unexpected config render result")

    services = _compose_service_names(compose)
    _require(services == ["backend"], f"production Compose services must be backend-only: {services}")
    _require(re.search(r"(?m)^\s+ports:\s*$", compose) is None, "host ports must be absent")
    _require(re.search(r"(?m)^\s+build:\s*$", compose) is None, "production Compose must use an immutable image, not build")
    _require(re.search(r"(?m)^volumes:\s*$", compose) is None, "named volumes must be absent")
    _require("postgres:" not in compose.lower(), "bundled PostgreSQL service must be absent")
    _require("adminer" not in compose.lower(), "Adminer must be absent")

    required_values = (
        "BACKEND_IMAGE",
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "ADMIN_WRITE_DEV_KEY",
        "CORS_ORIGINS",
        "POSTGRES_CA_FILE",
        "EDGE_NETWORK_NAME",
    )
    required_status = {name: _required_placeholder(compose, name) for name in required_values}
    _require(all(required_status.values()), "required Compose placeholders are incomplete")

    env_inventory = {
        line.split("=", 1)[0].strip(): line.split("=", 1)[1].strip()
        for line in env_example.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }
    _require(
        env_inventory.get("BACKEND_IMAGE", "") == APPROVED_BACKEND_REFERENCE,
        "backend image must match the approved verified digest",
    )
    database_url = env_inventory.get("DATABASE_URL", "")
    _require("sslmode=verify-full" in database_url, "DATABASE_URL example must use verify-full")
    _require("sslrootcert=/run/secrets/postgres_ca.pem" in database_url, "DATABASE_URL example must use mounted provider CA")
    _require(env_inventory.get("POSTGRES_CA_FILE", "").startswith("<"), "CA path must remain a placeholder")
    _require(env_inventory.get("JWT_SECRET_KEY", "").startswith("<"), "JWT secret must remain a placeholder")
    _require(env_inventory.get("ADMIN_WRITE_DEV_KEY", "").startswith("<"), "Admin key must remain a placeholder")

    _require("image: ${BACKEND_IMAGE:?" in compose, "backend image must be required")
    _require('ENVIRONMENT: production' in compose and 'DEBUG: "false"' in compose, "production environment/debug guard is missing")
    _require('expose:\n      - "8000"' in compose, "backend expose 8000 boundary is missing")
    _require(
        all(marker in compose for marker in ("postgres_ca:", "source: postgres_ca", "target: postgres_ca.pem")),
        "provider CA Compose secret target is missing",
    )
    _require("external: true" in compose and "EDGE_NETWORK_NAME" in compose, "external edge network boundary is missing")
    _require("replicas: 1" in compose, "Compose replica count must be 1")
    _require("read_only: true" in compose, "backend read-only filesystem is missing")
    _require("no-new-privileges:true" in compose, "no-new-privileges is missing")
    _require("/api/v1/health" in compose, "backend healthcheck is missing")

    docker_cmd = next(
        (line.strip() for line in dockerfile.splitlines() if line.strip().startswith("CMD ")),
        "",
    )
    _require("--workers" not in docker_cmd, "Dockerfile must remain one Uvicorn worker")
    _require("alembic" not in docker_cmd.lower(), "Dockerfile must not run Alembic automatically")

    for marker in (
        "managed-postgresql-selected",
        "external-reverse-proxy-https-selected",
        "backend 1 replica / 1 worker",
        "config render approved: yes",
        "config render executed on user PC: yes",
        "image pull/build approved: no",
        NEXT_SAFE_STAGE,
    ):
        _require(marker in selection_doc, f"selection document is missing: {marker}")
    for marker in ("HTTPS `443`", "http://backend:8000", "제품은 아직 고정하지 않습니다"):
        _require(marker in proxy_doc, f"reverse proxy document is missing: {marker}")
    for marker in (
        "Stage 1 — 완료: config render only",
        "v312-config-render-only",
        "container/image/network/volume mutation executed: no",
    ):
        _require(marker in isolated_doc, f"isolated validation document is missing: {marker}")

    forbidden_defaults = (
        "rpg_password",
        "change-me-before-production",
        "local-admin-dev-key",
        "sslmode=disable",
        "sslmode=allow",
        "sslmode=prefer",
    )
    _require(
        not any(value in compose + env_example for value in forbidden_defaults),
        "unsafe production default is present",
    )

    return {
        "toolVersion": TOOL_VERSION,
        "selectionSchemaVersion": selection["schemaVersion"],
        "databaseMode": selection["databaseMode"],
        "databaseTlsMode": selection["databaseTlsMode"],
        "publicEntrypoint": selection["publicEntrypoint"],
        "reverseProxyProduct": selection["reverseProxyProduct"],
        "backendReplicas": selection["backendReplicas"],
        "uvicornWorkersPerReplica": selection["uvicornWorkersPerReplica"],
        "composeServices": services,
        "requiredComposeValueCount": sum(required_status.values()),
        "managedDatabaseContainerAbsent": True,
        "hostPortsAbsent": True,
        "backendImageDigestRequired": True,
        "tlsVerifyFullProviderCa": True,
        "externalEdgeNetwork": True,
        "composeConfigRenderApproved": True,
        "composeConfigRenderExecuted": True,
        "imagePullBuildApproved": False,
        "containerStartApproved": False,
        "actualProductionValuesApplied": False,
        "actualMutationExecuted": False,
        "result": READY_RESULT,
        "nextSafeStage": NEXT_SAFE_STAGE,
    }


def render(result: dict[str, Any]) -> str:
    return "\n".join(
        (
            "Managed PostgreSQL / external reverse proxy architecture selection (read-only)",
            "No real env/secret read, Docker command, DB connection/write, or Alembic command was executed.",
            "",
            f"- database/TLS mode: {result['databaseMode']} / {result['databaseTlsMode']}",
            f"- public entrypoint: {result['publicEntrypoint']}",
            f"- reverse proxy product: {result['reverseProxyProduct']}",
            f"- backend replicas/workers: {result['backendReplicas']}/{result['uvicornWorkersPerReplica']}",
            f"- Compose services: {','.join(result['composeServices'])}",
            f"- required Compose placeholders: {result['requiredComposeValueCount']}/7",
            f"- managed DB container/host ports absent: {result['managedDatabaseContainerAbsent']}/{result['hostPortsAbsent']}",
            f"- backend digest/TLS provider CA/edge network: {result['backendImageDigestRequired']}/{result['tlsVerifyFullProviderCa']}/{result['externalEdgeNetwork']}",
            "- compose config render approved/executed: yes/yes",
            "- image pull/build/container start approved: no/no",
            "- actual production values applied: no",
            f"- result: {result['result']}",
            f"- next safe stage: {result['nextSafeStage']}",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = inspect_production_architecture_selection(root)
    except Exception as exc:
        blocked = {
            "toolVersion": TOOL_VERSION,
            "result": BLOCKED_RESULT,
            "reason": f"{type(exc).__name__}: {exc}",
            "actualMutationExecuted": False,
        }
        print(
            json.dumps(blocked, ensure_ascii=False, indent=2)
            if args.json
            else "Managed PostgreSQL/reverse proxy selection validation\n"
            f"- result: {BLOCKED_RESULT}\n"
            f"- reason: {blocked['reason']}\n"
            "- no mutation was executed."
        )
        return 1 if args.strict else 0
    print(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        if args.json
        else render(result)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

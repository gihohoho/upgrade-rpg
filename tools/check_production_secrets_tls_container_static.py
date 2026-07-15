#!/usr/bin/env python3
"""Statically verify current production secret, TLS, and container templates.

This tool reads project files only. It does not read real secret files, invoke
Docker, open a database connection, edit environment files, or execute Alembic.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

TOOL_VERSION = "v312.production-secrets-tls-container-static-managed-db"
READY_RESULT = "production-static-validation-managed-db-template-verified-runtime-application-blocked"
BLOCKED_RESULT = "blocked-or-failed"
NEXT_SAFE_STAGE = "run-config-render-only-on-docker-capable-host"


class ProductionStaticValidationError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ProductionStaticValidationError(message)


def _read(path: Path) -> str:
    if not path.is_file():
        raise ProductionStaticValidationError(f"required file is missing: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


def _required_placeholder(text: str, name: str) -> bool:
    return re.search(rf"\$\{{{re.escape(name)}:\?[^}}]+\}}", text) is not None


def _compose_services(text: str) -> list[str]:
    values: list[str] = []
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
            values.append(match.group(1))
    return values


def inspect_production_static_templates(root: Path) -> dict[str, Any]:
    compose = _read(root / "deploy/docker-compose.production.yml")
    env_example = _read(root / "deploy/production.env.example")
    deploy_readme = _read(root / "deploy/README.md")
    static_doc = _read(root / "docs/current/POSTGRES_PRODUCTION_STATIC_VALIDATION.md")
    dockerfile = _read(root / "backend/Dockerfile")
    gitignore = _read(root / ".gitignore")
    dockerignore = _read(root / ".dockerignore")
    secret_readme = _read(root / "deploy/secrets/README.md")

    required_compose_values = (
        "BACKEND_IMAGE",
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "ADMIN_WRITE_DEV_KEY",
        "CORS_ORIGINS",
        "POSTGRES_CA_FILE",
        "EDGE_NETWORK_NAME",
    )
    required_status = {
        name: _required_placeholder(compose, name) for name in required_compose_values
    }
    env_inventory = {
        line.split("=", 1)[0].strip(): line.split("=", 1)[1].strip()
        for line in env_example.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }
    forbidden_defaults = (
        "rpg_password",
        "change-me-before-production",
        "local-admin-dev-key",
        "sslmode=disable",
        "sslmode=allow",
        "sslmode=prefer",
    )
    services = _compose_services(compose)
    docker_cmd = next(
        (line.lower() for line in dockerfile.splitlines() if line.strip().startswith("CMD ")),
        "",
    )

    result = {
        "toolVersion": TOOL_VERSION,
        "requiredComposeValues": required_status,
        "requiredComposeValueCount": sum(required_status.values()),
        "composeServices": services,
        "backendOnlyService": services == ["backend"],
        "managedPostgresServiceAbsent": "postgres" not in services,
        "adminerAbsent": "adminer" not in compose.lower(),
        "hostPortsAbsent": re.search(r"(?m)^\s+ports:\s*$", compose) is None,
        "buildAbsent": re.search(r"(?m)^\s+build:\s*$", compose) is None,
        "namedVolumesAbsent": re.search(r"(?m)^volumes:\s*$", compose) is None,
        "productionEnvironmentFixed": "ENVIRONMENT: production" in compose,
        "productionDebugFalse": 'DEBUG: "false"' in compose,
        "postgresCaSecret": all(
            marker in compose
            for marker in ("source: postgres_ca", "target: postgres_ca.pem", "postgres_ca:", "POSTGRES_CA_FILE")
        ),
        "backendDigestPlaceholder": bool(
            re.fullmatch(
                r"<approved-registry>/upgrade-rpg-backend@sha256:<approved-64-hex-digest>",
                env_inventory.get("BACKEND_IMAGE", ""),
            )
        ),
        "tlsVerifyFullExample": "sslmode=verify-full" in env_inventory.get("DATABASE_URL", ""),
        "tlsCaPathExample": "sslrootcert=/run/secrets/postgres_ca.pem" in env_inventory.get("DATABASE_URL", ""),
        "placeholderSecretsOnly": all(
            env_inventory.get(name, "").startswith("<")
            for name in ("POSTGRES_CA_FILE", "JWT_SECRET_KEY", "ADMIN_WRITE_DEV_KEY")
        ),
        "realSecretValuesAbsent": not any(value in compose + env_example + dockerfile for value in forbidden_defaults),
        "externalEdgeNetwork": all(
            marker in compose for marker in ("external: true", "EDGE_NETWORK_NAME")
        ),
        "singleReplica": "replicas: 1" in compose,
        "backendHealthcheck": all(
            marker in compose for marker in ("healthcheck:", "/api/v1/health", "urllib.request.urlopen")
        ),
        "backendReadOnly": "read_only: true" in compose,
        "backendTmpfs": "tmpfs:" in compose and "- /tmp" in compose,
        "noNewPrivileges": "no-new-privileges:true" in compose,
        "dockerfileNonRoot": all(marker in dockerfile for marker in ("USER app", "adduser --system")),
        "singleUvicornWorker": "--workers" not in docker_cmd,
        "automaticAlembicAbsent": "alembic" not in docker_cmd,
        "realDeploymentFilesIgnored": all(
            marker in gitignore
            for marker in ("/deploy/production.env", "/deploy/.env.production", "/deploy/secrets/*")
        ),
        "secretFilesExcludedFromBuild": all(
            marker in dockerignore
            for marker in ("deploy/production.env", "deploy/.env.production", "deploy/secrets/*")
        ),
        "reviewOnlyDocumented": all(
            marker in deploy_readme + static_doc + secret_readme
            for marker in ("실제", "secret", "Docker")
        ),
        "actualMutationExecuted": False,
        "actualProductionSecretsTlsContainerExecutionApproved": False,
        "result": READY_RESULT,
        "nextSafeStage": NEXT_SAFE_STAGE,
    }

    _require(result["requiredComposeValueCount"] == len(required_compose_values), "required Compose placeholders are incomplete")
    for key in (
        "backendOnlyService",
        "managedPostgresServiceAbsent",
        "adminerAbsent",
        "hostPortsAbsent",
        "buildAbsent",
        "namedVolumesAbsent",
        "productionEnvironmentFixed",
        "productionDebugFalse",
        "postgresCaSecret",
        "backendDigestPlaceholder",
        "tlsVerifyFullExample",
        "tlsCaPathExample",
        "placeholderSecretsOnly",
        "realSecretValuesAbsent",
        "externalEdgeNetwork",
        "singleReplica",
        "backendHealthcheck",
        "backendReadOnly",
        "backendTmpfs",
        "noNewPrivileges",
        "dockerfileNonRoot",
        "singleUvicornWorker",
        "automaticAlembicAbsent",
        "realDeploymentFilesIgnored",
        "secretFilesExcludedFromBuild",
        "reviewOnlyDocumented",
    ):
        _require(bool(result[key]), f"production static boundary failed: {key}")
    return result


def render(result: dict[str, Any]) -> str:
    return "\n".join(
        (
            "Production secrets / TLS / container static validation (read-only)",
            "No secret read/write, .env edit, Docker command, DB connection/write, or Alembic command was executed.",
            "",
            f"- required Compose placeholders: {result['requiredComposeValueCount']}/7",
            f"- Compose services/backend-only: {','.join(result['composeServices'])}/{result['backendOnlyService']}",
            f"- managed PostgreSQL service absent: {result['managedPostgresServiceAbsent']}",
            f"- Adminer/host ports/build/volumes absent: {result['adminerAbsent']}/{result['hostPortsAbsent']}/{result['buildAbsent']}/{result['namedVolumesAbsent']}",
            f"- production environment/debug fixed: {result['productionEnvironmentFixed']}/{result['productionDebugFalse']}",
            f"- backend digest/CA/edge boundary: {result['backendDigestPlaceholder']}/{result['postgresCaSecret']}/{result['externalEdgeNetwork']}",
            f"- TLS example verify-full/CA path: {result['tlsVerifyFullExample']}/{result['tlsCaPathExample']}",
            f"- backend healthcheck/read-only/non-root: {result['backendHealthcheck']}/{result['backendReadOnly']}/{result['dockerfileNonRoot']}",
            f"- backend replicas/Uvicorn workers: {1 if result['singleReplica'] else 'invalid'}/{1 if result['singleUvicornWorker'] else 'invalid'}",
            "- actual production secrets/TLS/container execution approved: no",
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
        result = inspect_production_static_templates(root)
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
            else "Production static validation\n"
            f"- result: {BLOCKED_RESULT}\n"
            f"- reason: {blocked['reason']}\n"
            "- no mutation was executed."
        )
        return 1 if args.strict else 0
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

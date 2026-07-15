#!/usr/bin/env python3
"""Statically verify production secret, TLS, and container review templates.

This tool reads project files only. It does not read real secret files, invoke
Docker, open a database connection, edit environment files, or execute Alembic.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any

TOOL_VERSION = "v310.production-secrets-tls-container-static-validation"
READY_RESULT = "production-static-validation-template-verified-runtime-application-blocked"
BLOCKED_RESULT = "blocked-or-failed"


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
        "POSTGRES_IMAGE",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "ADMIN_WRITE_DEV_KEY",
        "CORS_ORIGINS",
        "POSTGRES_PASSWORD_FILE",
        "POSTGRES_CA_FILE",
    )
    required_status = {
        name: _required_placeholder(compose, name) for name in required_compose_values
    }

    forbidden_defaults = (
        "rpg_password",
        "change-me-before-production",
        "local-admin-dev-key",
        "sslmode=disable",
        "sslmode=allow",
        "sslmode=prefer",
    )
    sensitive_template_text = "\n".join((compose, env_example, dockerfile))

    env_inventory = {
        line.split("=", 1)[0].strip(): line.split("=", 1)[1].strip()
        for line in env_example.splitlines()
        if line.strip() and not line.lstrip().startswith("#") and "=" in line
    }

    result = {
        "toolVersion": TOOL_VERSION,
        "requiredComposeValues": required_status,
        "requiredComposeValueCount": sum(required_status.values()),
        "productionEnvironmentFixed": "ENVIRONMENT: production" in compose,
        "productionDebugFalse": 'DEBUG: "false"' in compose,
        "postgresPasswordSecret": all(
            marker in compose
            for marker in (
                "POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password",
                "- postgres_password",
                "postgres_password:",
            )
        ),
        "postgresCaSecret": all(
            marker in compose
            for marker in (
                "- postgres_ca",
                "postgres_ca:",
                "POSTGRES_CA_FILE",
            )
        ),
        "digestPinnedImagePlaceholder": bool(
            re.fullmatch(
                r"postgres:16-alpine@sha256:<approved-64-hex-digest>",
                env_inventory.get("POSTGRES_IMAGE", ""),
            )
        ),
        "tlsVerifyFullExample": "sslmode=verify-full" in env_inventory.get("DATABASE_URL", ""),
        "tlsCaPathExample": "sslrootcert=/run/secrets/postgres_ca.pem" in env_inventory.get("DATABASE_URL", ""),
        "realSecretValuesAbsent": not any(value in sensitive_template_text for value in forbidden_defaults),
        "placeholderSecretsOnly": all(
            env_inventory.get(name, "").startswith("<")
            for name in ("POSTGRES_PASSWORD_FILE", "POSTGRES_CA_FILE", "JWT_SECRET_KEY", "ADMIN_WRITE_DEV_KEY")
        ),
        "adminerAbsent": "adminer" not in compose.lower(),
        "hostPortsAbsent": re.search(r"(?m)^\s+ports:\s*$", compose) is None,
        "backendHealthcheck": all(
            marker in compose
            for marker in ("healthcheck:", "/api/v1/health", "urllib.request.urlopen")
        ),
        "backendReadOnly": "read_only: true" in compose,
        "backendTmpfs": "tmpfs:" in compose and "- /tmp" in compose,
        "noNewPrivileges": "no-new-privileges:true" in compose,
        "internalDbNetwork": "internal: true" in compose,
        "dockerfileNonRoot": all(marker in dockerfile for marker in ("USER app", "adduser --system")),
        "automaticAlembicAbsent": "alembic" not in next(
            (line.lower() for line in dockerfile.splitlines() if line.strip().startswith("CMD ")),
            "",
        ),
        "realDeploymentFilesIgnored": all(
            marker in gitignore
            for marker in (
                "/deploy/production.env",
                "/deploy/.env.production",
                "/deploy/secrets/*",
            )
        ),
        "secretFilesExcludedFromBuild": all(
            marker in dockerignore
            for marker in ("deploy/production.env", "deploy/.env.production", "deploy/secrets/*")
        ),
        "reviewOnlyDocumented": all(
            marker in (deploy_readme + static_doc + secret_readme)
            for marker in ("실제", "secret", "Docker")
        ),
        "bundledPostgresTlsServerConfigured": False,
        "actualMutationExecuted": False,
        "actualProductionSecretsTlsContainerExecutionApproved": False,
        "result": READY_RESULT,
        "nextSafeStage": "separate-production-values-capacity-and-isolated-container-plan",
    }

    _require(result["requiredComposeValueCount"] == len(required_compose_values), "required Compose placeholders are incomplete")
    for key in (
        "productionEnvironmentFixed",
        "productionDebugFalse",
        "postgresPasswordSecret",
        "postgresCaSecret",
        "digestPinnedImagePlaceholder",
        "tlsVerifyFullExample",
        "tlsCaPathExample",
        "realSecretValuesAbsent",
        "placeholderSecretsOnly",
        "adminerAbsent",
        "hostPortsAbsent",
        "backendHealthcheck",
        "backendReadOnly",
        "backendTmpfs",
        "noNewPrivileges",
        "internalDbNetwork",
        "dockerfileNonRoot",
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
            f"- required Compose placeholders: {result['requiredComposeValueCount']}/9",
            f"- production environment/debug fixed: {result['productionEnvironmentFixed']}/{result['productionDebugFalse']}",
            f"- password/CA Compose secrets: {result['postgresPasswordSecret']}/{result['postgresCaSecret']}",
            f"- digest-pinned image placeholder: {result['digestPinnedImagePlaceholder']}",
            f"- TLS example verify-full/CA path: {result['tlsVerifyFullExample']}/{result['tlsCaPathExample']}",
            f"- actual secret values absent: {result['realSecretValuesAbsent']}",
            f"- Adminer/host ports absent: {result['adminerAbsent']}/{result['hostPortsAbsent']}",
            f"- backend healthcheck/read-only/non-root: {result['backendHealthcheck']}/{result['backendReadOnly']}/{result['dockerfileNonRoot']}",
            f"- automatic Alembic in container start: {not result['automaticAlembicAbsent']}",
            "- bundled PostgreSQL TLS server runtime configured: no (separate approval required)",
            "- actual production secrets/TLS/container execution approved: no",
            f"- result: {result['result']}",
            f"- next safe stage: {result['nextSafeStage']}",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Return a non-zero exit code on any static boundary failure")
    parser.add_argument("--json", action="store_true", help="Print sanitized JSON")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = inspect_production_static_templates(root)
    except Exception as exc:  # fail closed with a short sanitized reason
        blocked = {
            "toolVersion": TOOL_VERSION,
            "result": BLOCKED_RESULT,
            "reason": f"{type(exc).__name__}: {exc}",
            "actualMutationExecuted": False,
        }
        print(json.dumps(blocked, ensure_ascii=False, indent=2) if args.json else f"Production static validation\n- result: {BLOCKED_RESULT}\n- reason: {blocked['reason']}\n- no mutation was executed.")
        return 1 if args.strict else 0

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

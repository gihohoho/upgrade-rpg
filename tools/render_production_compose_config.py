#!/usr/bin/env python3
"""Render the v312 production Compose config with review-only sentinels.

The execute path invokes exactly `docker compose ... config`. It does not pull,
build, create, start, stop, or remove images, containers, networks, or volumes.
It never reads the project's real .env or secret files.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any

from check_production_managed_postgres_reverse_proxy_selection import (
    READY_RESULT as SELECTION_READY_RESULT,
    inspect_production_architecture_selection,
)

TOOL_VERSION = "v312.production-compose-config-render-only"
READY_RESULT = "production-compose-config-render-ready"
EXECUTED_RESULT = "production-compose-config-render-verified-no-runtime-mutation"
BLOCKED_RESULT = "blocked-or-failed"
CONFIRM_STAGE = "v312-config-render-only"
PROJECT_NAME = "rpg-prod-config-review-v312"
NEXT_SAFE_STAGE = "review-render-report-and-approve-backend-image-source-digest"


class ProductionComposeRenderError(RuntimeError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ProductionComposeRenderError(message)


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


def inspect_config_render_readiness(
    root: Path, *, docker_executable: str | None = None
) -> dict[str, Any]:
    selection = inspect_production_architecture_selection(root)
    _require(selection.get("result") == SELECTION_READY_RESULT, "architecture selection is not ready")
    resolved_docker = docker_executable or shutil.which("docker")
    return {
        "toolVersion": TOOL_VERSION,
        "architectureSelectionResult": selection["result"],
        "dockerCliAvailable": resolved_docker is not None,
        "approvedCommand": "docker compose --project-name ... --env-file <temporary> -f deploy/docker-compose.production.yml config",
        "realEnvironmentRead": False,
        "realSecretRead": False,
        "rawRenderPersisted": False,
        "containerMutationApproved": False,
        "imagePullBuildApproved": False,
        "databaseMutationApproved": False,
        "alembicCommandApproved": False,
        "result": READY_RESULT,
        "nextSafeStage": "execute-config-render-only-with-exact-confirmation",
    }


def _review_env_lines(ca_path: Path) -> list[str]:
    digest = "0" * 64
    return [
        f"BACKEND_IMAGE=review.invalid/upgrade-rpg-backend@sha256:{digest}",
        "EDGE_NETWORK_NAME=rpg-prod-review-edge-v312",
        f"POSTGRES_CA_FILE={ca_path.resolve().as_posix()}",
        "DATABASE_URL=postgresql+asyncpg://review_user:review_password@managed-db.review.invalid:5432/rpg_game?sslmode=verify-full&sslrootcert=/run/secrets/postgres_ca.pem",
        "APP_NAME=Idle RPG Backend Review",
        "JWT_SECRET_KEY=review-only-jwt-sentinel-000000000000000000000000",
        "ADMIN_WRITE_DEV_KEY=review-only-admin-sentinel-000000000000000000000",
        "ACCESS_TOKEN_EXPIRE_MINUTES=1440",
        'CORS_ORIGINS=["https://game.review.invalid"]',
        "DB_POOL_PRE_PING=true",
        "DB_POOL_SIZE=5",
        "DB_MAX_OVERFLOW=10",
        "DB_POOL_TIMEOUT_SECONDS=30",
        "DB_POOL_RECYCLE_SECONDS=1800",
    ]


def _inspect_rendered_config(rendered: str) -> dict[str, Any]:
    services = _compose_service_names(rendered)
    _require(services == ["backend"], f"rendered services must be backend-only: {services}")
    _require(re.search(r"(?m)^\s+ports:\s*$", rendered) is None, "rendered config contains host ports")
    _require(re.search(r"(?m)^\s+build:\s*$", rendered) is None, "rendered config contains build")
    _require(re.search(r"(?m)^volumes:\s*$", rendered) is None, "rendered config contains named volumes")
    _require("postgres:" not in rendered.lower(), "rendered config contains PostgreSQL service")
    _require("adminer" not in rendered.lower(), "rendered config contains Adminer")
    _require("review.invalid/upgrade-rpg-backend@sha256:" + "0" * 64 in rendered, "rendered backend digest is missing")
    _require("ENVIRONMENT: production" in rendered or "ENVIRONMENT: \"production\"" in rendered, "production environment is missing")
    _require(re.search(r"DEBUG:\s*[\"']?false[\"']?", rendered, re.IGNORECASE) is not None, "DEBUG=false is missing")
    _require("sslmode=verify-full" in rendered, "verify-full is missing")
    _require("sslrootcert=/run/secrets/postgres_ca.pem" in rendered, "provider CA path is missing")
    _require(
        "target: /run/secrets/postgres_ca.pem" in rendered
        or "target: postgres_ca.pem" in rendered,
        "provider CA secret target does not match DATABASE_URL",
    )
    _require("external: true" in rendered, "external edge network is missing")
    _require("rpg-prod-review-edge-v312" in rendered, "review edge network name is missing")
    _require(re.search(r"replicas:\s*1", rendered) is not None, "replica count is not 1")
    _require("read_only: true" in rendered, "read-only filesystem is missing")
    _require("no-new-privileges:true" in rendered, "no-new-privileges is missing")
    return {
        "services": services,
        "hostPortsAbsent": True,
        "buildAbsent": True,
        "namedVolumesAbsent": True,
        "managedDatabaseServiceAbsent": True,
        "backendDigestRendered": True,
        "productionGuardRendered": True,
        "tlsVerifyFullProviderCaRendered": True,
        "externalEdgeNetworkRendered": True,
        "backendReplicas": 1,
    }


def execute_config_render(
    root: Path,
    *,
    docker_executable: str | None = None,
    docker_command_prefix: list[str] | None = None,
) -> dict[str, Any]:
    readiness = inspect_config_render_readiness(root, docker_executable=docker_executable)
    resolved_docker = docker_executable or shutil.which("docker")
    _require(resolved_docker is not None, "Docker CLI is unavailable; run this on the user's Docker-capable PC")
    command_prefix = docker_command_prefix or [str(resolved_docker)]
    _require(bool(command_prefix), "Docker command prefix is empty")
    compose_path = (root / "deploy/docker-compose.production.yml").resolve()

    with tempfile.TemporaryDirectory(prefix="rpg-v312-compose-render-") as temp_dir:
        temp = Path(temp_dir)
        ca_path = temp / "review-only-postgres-ca.pem"
        env_path = temp / "review-only.env"
        ca_path.write_text("review-only sentinel; not a certificate\n", encoding="utf-8")
        env_path.write_text("\n".join(_review_env_lines(ca_path)) + "\n", encoding="utf-8")
        command = [
            *command_prefix,
            "compose",
            "--project-name",
            PROJECT_NAME,
            "--env-file",
            str(env_path),
            "-f",
            str(compose_path),
            "config",
        ]
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            timeout=60,
        )
        _require(completed.returncode == 0, f"docker compose config failed: {completed.stderr.strip()[:500]}")
        rendered_state = _inspect_rendered_config(completed.stdout)

    return {
        "toolVersion": TOOL_VERSION,
        "architectureSelectionResult": readiness["architectureSelectionResult"],
        "dockerCliAvailable": True,
        "dockerSubcommand": "compose config",
        "projectName": PROJECT_NAME,
        "reviewSentinelsOnly": True,
        "realEnvironmentRead": False,
        "realSecretRead": False,
        "rawRenderPersisted": False,
        "temporaryReviewFilesRemoved": True,
        "renderedState": rendered_state,
        "imagePullBuildExecuted": False,
        "containerCreateStartStopRemoveExecuted": False,
        "networkVolumeMutationExecuted": False,
        "databaseConnectionMutationExecuted": False,
        "alembicCommandExecuted": False,
        "result": EXECUTED_RESULT,
        "nextSafeStage": NEXT_SAFE_STAGE,
    }


def render_text(result: dict[str, Any]) -> str:
    if result["result"] == READY_RESULT:
        return "\n".join(
            (
                "Production Compose config render readiness (read-only)",
                "No Docker command, real env/secret read, DB connection, or Alembic command was executed.",
                "",
                f"- architecture selection: {result['architectureSelectionResult']}",
                f"- Docker CLI available: {result['dockerCliAvailable']}",
                "- approved Docker scope: compose config only",
                "- actual container/image/network/volume mutation approved: no",
                f"- result: {result['result']}",
                f"- next safe stage: {result['nextSafeStage']}",
            )
        )
    state = result["renderedState"]
    return "\n".join(
        (
            "Production Compose config render verification",
            "Review-only sentinels were used. Raw render output was not persisted.",
            "",
            f"- Docker subcommand/project: {result['dockerSubcommand']} / {result['projectName']}",
            f"- rendered services: {','.join(state['services'])}",
            f"- host ports/build/named volumes absent: {state['hostPortsAbsent']}/{state['buildAbsent']}/{state['namedVolumesAbsent']}",
            f"- managed DB service absent / backend replicas: {state['managedDatabaseServiceAbsent']}/{state['backendReplicas']}",
            f"- digest/production guard/TLS/edge rendered: {state['backendDigestRendered']}/{state['productionGuardRendered']}/{state['tlsVerifyFullProviderCaRendered']}/{state['externalEdgeNetworkRendered']}",
            "- image pull/build executed: no",
            "- container/network/volume mutation executed: no",
            "- DB/Alembic mutation executed: no",
            f"- result: {result['result']}",
            f"- next safe stage: {result['nextSafeStage']}",
        )
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--confirm-stage")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if args.execute:
            _require(args.confirm_stage == CONFIRM_STAGE, f"--confirm-stage must be exactly {CONFIRM_STAGE}")
            result = execute_config_render(root)
        else:
            result = inspect_config_render_readiness(root)
    except Exception as exc:
        blocked = {
            "toolVersion": TOOL_VERSION,
            "result": BLOCKED_RESULT,
            "reason": f"{type(exc).__name__}: {exc}",
            "imagePullBuildExecuted": False,
            "containerMutationExecuted": False,
            "databaseMutationExecuted": False,
            "alembicCommandExecuted": False,
        }
        print(
            json.dumps(blocked, ensure_ascii=False, indent=2)
            if args.json
            else "Production Compose config render\n"
            f"- result: {BLOCKED_RESULT}\n"
            f"- reason: {blocked['reason']}\n"
            "- no image/container/network/volume/DB/Alembic mutation was executed."
        )
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

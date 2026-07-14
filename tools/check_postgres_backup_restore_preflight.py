#!/usr/bin/env python3
"""Read-only gate and tooling check for PostgreSQL backup/restore rehearsal.

This command never creates a backup, restores a dump, creates/drops a database,
changes Docker resources, edits .env, or runs Alembic mutation commands. It:

1. re-runs the v289 schema-equivalence checker as a safety gate;
2. checks host and existing-container PostgreSQL client command availability;
3. prints the approved backup path/name policy and isolated database boundaries;
4. reports whether the project is ready to ASK for the user's execution approval.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from _safe_subprocess import run_captured

SOURCE_DATABASE = "rpg_game"
RESTORE_REHEARSAL_DATABASE = "rpg_game_restore_rehearsal_v290"
MIGRATION_TEST_DATABASE = "rpg_game_migration_empty_v290"
POSTGRES_CONTAINER = "upgrade_rpg_postgres"
BACKUP_DIRECTORY = "local-backups/postgres"
BACKUP_FILENAME_PATTERN = "rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump"
REQUIRED_CLIENT_COMMANDS = ("pg_dump", "pg_restore", "createdb", "dropdb")


@dataclass(frozen=True)
class CommandAvailability:
    command: str
    available: bool
    version: str
    location: str


def first_line(value: str) -> str:
    lines = value.strip().splitlines()
    return lines[0] if lines else "no output"


def host_command_availability(command: str) -> CommandAvailability:
    executable = shutil.which(command)
    if not executable:
        return CommandAvailability(command, False, "not found", "host")
    try:
        completed, output = run_captured([command, "--version"], timeout=10, check=False)
    except Exception as exc:  # pragma: no cover - installation dependent
        return CommandAvailability(command, False, f"{type(exc).__name__}: {exc}", "host")
    return CommandAvailability(
        command,
        completed.returncode == 0,
        first_line(output) if output else f"exit={completed.returncode}",
        "host",
    )


def docker_container_running() -> tuple[bool, str]:
    if not shutil.which("docker"):
        return False, "docker not found"
    try:
        completed, output = run_captured(
            ["docker", "inspect", "--format", "{{.State.Running}}", POSTGRES_CONTAINER],
            timeout=10,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - installation dependent
        return False, f"{type(exc).__name__}: {exc}"
    running = completed.returncode == 0 and first_line(output).lower() == "true"
    return running, first_line(output) if output else f"exit={completed.returncode}"


def container_command_availability(command: str, running: bool) -> CommandAvailability:
    if not running:
        return CommandAvailability(command, False, "container not running", "docker-container")
    try:
        completed, output = run_captured(
            ["docker", "exec", POSTGRES_CONTAINER, command, "--version"],
            timeout=10,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - installation dependent
        return CommandAvailability(
            command,
            False,
            f"{type(exc).__name__}: {exc}",
            "docker-container",
        )
    return CommandAvailability(
        command,
        completed.returncode == 0,
        first_line(output) if output else f"exit={completed.returncode}",
        "docker-container",
    )


def collect_schema_gate(root: Path) -> dict[str, Any]:
    checker = root / "tools/check_postgres_schema_equivalence.py"
    try:
        completed, output = run_captured(
            [sys.executable, str(checker), "--json"],
            cwd=root,
            timeout=45,
            check=False,
        )
        payload = json.loads(output)
    except Exception as exc:
        payload = {
            "readOnly": True,
            "schemaChanged": False,
            "connected": False,
            "classification": "connection-failed",
            "differenceCount": None,
            "differences": [],
            "error": f"{type(exc).__name__}: {exc}",
        }
    passed = (
        completed.returncode == 0
        if "completed" in locals()
        else False
    ) and payload.get("connected") is True and payload.get("classification") == "structurally-equivalent" and payload.get("differenceCount") == 0
    return {
        "passed": passed,
        "requiredClassification": "structurally-equivalent",
        "requiredDifferenceCount": 0,
        "result": payload,
    }


def gitignore_has_backup_rule(root: Path) -> bool:
    path = root / ".gitignore"
    if not path.exists():
        return False
    rules = {line.strip() for line in path.read_text(encoding="utf-8").splitlines()}
    return "/local-backups/" in rules or "local-backups/" in rules


def collect(root: Path) -> dict[str, Any]:
    schema_gate = collect_schema_gate(root)
    host_checks = [host_command_availability(command) for command in REQUIRED_CLIENT_COMMANDS]
    container_running, container_state = docker_container_running()
    container_checks = [
        container_command_availability(command, container_running)
        for command in REQUIRED_CLIENT_COMMANDS
    ]

    host_ready = all(item.available for item in host_checks)
    container_ready = container_running and all(item.available for item in container_checks)
    if container_ready:
        execution_mode = "docker-container"
    elif host_ready:
        execution_mode = "host"
    else:
        execution_mode = "unavailable"

    backup_ignored = gitignore_has_backup_rule(root)
    blocking_reasons: list[str] = []
    if not schema_gate["passed"]:
        classification = schema_gate["result"].get("classification", "unknown")
        difference_count = schema_gate["result"].get("differenceCount")
        blocking_reasons.append(
            f"schema gate not passed: classification={classification}, differenceCount={difference_count}"
        )
    if execution_mode == "unavailable":
        blocking_reasons.append(
            "pg_dump/pg_restore/createdb/dropdb are not all available on the host or existing PostgreSQL container"
        )
    if not backup_ignored:
        blocking_reasons.append("/local-backups/ is not protected by .gitignore")

    ready = not blocking_reasons
    return {
        "readOnly": True,
        "databaseMutationAttempted": False,
        "backupCreated": False,
        "restoreAttempted": False,
        "databaseCreateDropAttempted": False,
        "dockerResourceChanged": False,
        "environmentFileChanged": False,
        "alembicMutationAttempted": False,
        "classification": "ready-for-user-approval" if ready else "blocked",
        "readyForUserApproval": ready,
        "blockingReasons": blocking_reasons,
        "schemaGate": schema_gate,
        "toolAvailability": {
            "host": [asdict(item) for item in host_checks],
            "dockerContainer": {
                "name": POSTGRES_CONTAINER,
                "running": container_running,
                "state": container_state,
                "commands": [asdict(item) for item in container_checks],
            },
            "selectedExecutionMode": execution_mode,
        },
        "backupPolicy": {
            "directory": BACKUP_DIRECTORY,
            "directoryCreated": False,
            "gitIgnored": backup_ignored,
            "format": "PostgreSQL custom format (-Fc)",
            "filenamePattern": BACKUP_FILENAME_PATTERN,
            "containsSensitiveGameAndUserData": True,
            "containsEnvironmentFile": False,
            "shareExternally": False,
            "includeInGit": False,
            "includeInHandoffZip": False,
            "checksumSidecarPattern": f"{BACKUP_FILENAME_PATTERN}.sha256",
        },
        "databaseBoundary": {
            "sourceDatabase": SOURCE_DATABASE,
            "sourceIsReadOnlyDuringRehearsal": True,
            "restoreRehearsalDatabase": RESTORE_REHEARSAL_DATABASE,
            "migrationTestDatabase": MIGRATION_TEST_DATABASE,
            "restoreIntoSourceDatabaseAllowed": False,
            "databaseNamesAreDistinct": len(
                {SOURCE_DATABASE, RESTORE_REHEARSAL_DATABASE, MIGRATION_TEST_DATABASE}
            )
            == 3,
        },
        "comparisonPlan": {
            "beforeBackup": [
                "record source database identity and PostgreSQL version",
                "record public table count",
                "record per-table row counts and total row count",
            ],
            "afterRestore": [
                "record rehearsal database identity",
                "compare public table count",
                "compare every table row count and total row count",
                "run schema equivalence against the rehearsal database without changing .env",
            ],
            "expectedKnownBaseline": {
                "modelTables": 22,
                "publicTables": 22,
                "totalRows": 748,
            },
        },
        "migrationValidationPlan": {
            "database": MIGRATION_TEST_DATABASE,
            "startsEmpty": True,
            "separateFromRestoreRehearsal": True,
            "revisionCreationAllowedNow": False,
            "upgradeDowngradeAllowedNow": False,
            "stampAllowedNow": False,
            "nextApprovalBoundary": "create backup only after reviewing this preflight result",
        },
    }


def render_text(payload: dict[str, Any]) -> str:
    gate = payload["schemaGate"]["result"]
    tools = payload["toolAvailability"]
    lines = [
        "PostgreSQL backup/restore preflight (read-only)",
        "No dump, restore, database create/drop, Docker change, .env edit, or Alembic mutation is executed.",
        "",
        f"- schema gate: {gate.get('classification')} / differences={gate.get('differenceCount')}",
        f"- selected client mode: {tools['selectedExecutionMode']}",
        f"- backup directory policy: {payload['backupPolicy']['directory']}",
        f"- filename pattern: {payload['backupPolicy']['filenamePattern']}",
        f"- restore rehearsal DB: {payload['databaseBoundary']['restoreRehearsalDatabase']}",
        f"- migration test DB: {payload['databaseBoundary']['migrationTestDatabase']}",
        f"- result: {payload['classification']}",
    ]
    for location in ("host",):
        for item in tools[location]:
            status = "OK" if item["available"] else "MISSING"
            lines.append(f"    [{status}] {location}/{item['command']}: {item['version']}")
    container = tools["dockerContainer"]
    lines.append(
        f"    [{'OK' if container['running'] else 'MISSING'}] container/{container['name']}: {container['state']}"
    )
    for item in container["commands"]:
        status = "OK" if item["available"] else "MISSING"
        lines.append(f"    [{status}] container/{item['command']}: {item['version']}")
    for reason in payload["blockingReasons"]:
        lines.append(f"- BLOCKED: {reason}")
    if payload["readyForUserApproval"]:
        lines.append("- 실제 backup 실행 전 사용자 승인을 요청할 준비가 되었습니다.")
    else:
        lines.append("- 실제 backup/restore/DB 생성·삭제 단계로 넘어가지 않습니다.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Return 1 unless ready for user approval")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    payload = collect(root)
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else render_text(payload))
    return 1 if args.strict and not payload["readyForUserApproval"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

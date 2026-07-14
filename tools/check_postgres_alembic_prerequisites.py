#!/usr/bin/env python3
"""Read-only local prerequisite checker for PostgreSQL/Alembic work.

The checker does not connect to PostgreSQL, start Docker, read secret values,
change .env, or run migrations. It only checks executable/package/file presence.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    key: str
    required: bool
    ok: bool
    value: str
    help: str


def command_version(command: list[str]) -> tuple[bool, str]:
    executable = shutil.which(command[0])
    if not executable:
        return False, "not found"
    try:
        result = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=10,
            check=False,
        )
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    output = (result.stdout or "").strip().splitlines()
    value = output[0] if output else f"exit={result.returncode}"
    return result.returncode == 0, value


def package_version(distribution: str) -> tuple[bool, str]:
    try:
        return True, importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return False, "not installed"


def collect(root: Path) -> list[Check]:
    docker_ok, docker_value = command_version(["docker", "--version"])
    compose_ok, compose_value = command_version(["docker", "compose", "version"])

    package_specs = [
        ("sqlalchemy", "SQLAlchemy", True),
        ("alembic", "alembic", True),
        ("asyncpg", "asyncpg", True),
        ("psycopg", "psycopg", True),
        ("fastapi", "fastapi", True),
    ]

    checks = [
        Check("python", True, sys.version_info >= (3, 11), platform.python_version(), "Python 3.11 이상 필요"),
        Check(
            "virtualenv",
            True,
            sys.prefix != getattr(sys, "base_prefix", sys.prefix),
            sys.prefix,
            "backend/.venv를 활성화한 Python으로 실행하세요.",
        ),
        Check("docker", True, docker_ok, docker_value, "Docker Desktop 설치 및 실행 필요"),
        Check("docker-compose", True, compose_ok, compose_value, "Docker Compose v2 필요"),
    ]

    for key, distribution, required in package_specs:
        ok, value = package_version(distribution)
        checks.append(
            Check(
                key,
                required,
                ok,
                value,
                'backend 폴더에서 python -m pip install -e ".[dev]" 실행',
            )
        )

    required_files = [
        "docker-compose.yml",
        "backend/pyproject.toml",
        "backend/.env.example",
        "backend/alembic.ini",
        "backend/alembic/env.py",
        "backend/app/db/base.py",
        "backend/app/db/session.py",
    ]
    for relative in required_files:
        exists = (root / relative).exists()
        checks.append(Check(f"file:{relative}", True, exists, "present" if exists else "missing", "ZIP/project files 확인"))

    versions = root / "backend/alembic/versions"
    revisions = list(versions.glob("*.py")) if versions.exists() else []
    checks.append(
        Check(
            "alembic-revisions",
            False,
            bool(revisions),
            f"{len(revisions)} revision(s)",
            "현재는 0개가 예상됩니다. 실제 migration 단계 전까지 경고 항목입니다.",
        )
    )
    return checks


def text_output(checks: list[Check]) -> str:
    lines = ["PostgreSQL/Alembic prerequisite check (read-only)"]
    for item in checks:
        status = "OK" if item.ok else ("MISSING" if item.required else "INFO")
        required = "required" if item.required else "optional/current-state"
        lines.append(f"[{status}] {item.key} ({required}): {item.value}")
        if not item.ok:
            lines.append(f"       -> {item.help}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Return 1 when a required check is missing")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    checks = collect(root)
    required_missing = [item.key for item in checks if item.required and not item.ok]

    if args.json:
        print(
            json.dumps(
                {
                    "readOnly": True,
                    "databaseConnectionAttempted": False,
                    "requiredMissing": required_missing,
                    "checks": [asdict(item) for item in checks],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(text_output(checks))
        print()
        if required_missing:
            print("필수 누락:", ", ".join(required_missing))
        else:
            print("필수 사전 조건이 모두 확인되었습니다. 아직 DB/migration은 실행하지 않았습니다.")

    return 1 if args.strict and required_missing else 0


if __name__ == "__main__":
    raise SystemExit(main())

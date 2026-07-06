"""Local backend readiness checker.

프로젝트 루트에서 실행합니다.

    python tools/check_backend_ready.py

이 스크립트는 로컬 개발환경에서 자주 놓치는 항목을 빠르게 점검합니다.
DB 실제 연결까지 확인하려면 PostgreSQL 컨테이너를 켠 뒤 아래처럼 실행합니다.

    python tools/check_backend_ready.py --db
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"


def run(command: list[str], cwd: Path | None = None) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd or ROOT_DIR),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except FileNotFoundError:
        return 127, f"command not found: {command[0]}"
    return completed.returncode, completed.stdout.strip()


def print_check(ok: bool, label: str, detail: str = "") -> None:
    icon = "OK" if ok else "WARN"
    print(f"[{icon}] {label}")
    if detail:
        print(f"     {detail}")


def check_files() -> bool:
    required_paths = [
        ROOT_DIR / "docker-compose.yml",
        BACKEND_DIR / "pyproject.toml",
        BACKEND_DIR / ".env.example",
        BACKEND_DIR / "app" / "main.py",
        BACKEND_DIR / "app" / "api" / "routes" / "health.py",
    ]
    ok = True
    for path in required_paths:
        exists = path.exists()
        ok = ok and exists
        print_check(exists, f"required file: {path.relative_to(ROOT_DIR)}")
    return ok


def check_env() -> bool:
    env_path = BACKEND_DIR / ".env"
    if env_path.exists():
        print_check(True, "backend/.env exists")
        return True
    print_check(False, "backend/.env is missing", "cp backend/.env.example backend/.env 를 실행하세요.")
    return False


def check_python_imports() -> bool:
    code = "import fastapi, sqlalchemy, pydantic; from app.main import app; print('backend imports ok')"
    returncode, output = run([sys.executable, "-c", code], cwd=BACKEND_DIR)
    print_check(returncode == 0, "Python backend imports", output)
    return returncode == 0


def check_docker() -> bool:
    docker_code, docker_output = run(["docker", "--version"])
    compose_code, compose_output = run(["docker", "compose", "version"])
    config_code, config_output = run(["docker", "compose", "config"], cwd=ROOT_DIR)

    print_check(docker_code == 0, "Docker CLI", docker_output)
    print_check(compose_code == 0, "Docker Compose", compose_output)
    print_check(config_code == 0, "docker-compose.yml config", config_output.splitlines()[0] if config_output else "")
    return docker_code == 0 and compose_code == 0 and config_code == 0


def check_db_connection() -> bool:
    code = """
import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text('SELECT 1'))
        print('db ok:', result.scalar())

asyncio.run(main())
""".strip()
    returncode, output = run([sys.executable, "-c", code], cwd=BACKEND_DIR)
    print_check(returncode == 0, "PostgreSQL DB connection", output)
    return returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", action="store_true", help="also check PostgreSQL connection")
    args = parser.parse_args()

    print("Backend readiness check")
    print(f"Project root: {ROOT_DIR}")
    print()

    checks = [
        check_files(),
        check_env(),
        check_python_imports(),
        check_docker(),
    ]
    if args.db:
        checks.append(check_db_connection())

    print()
    if all(checks):
        print("All requested checks passed.")
        return 0
    print("Some checks need attention. Read the WARN messages above.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

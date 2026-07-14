#!/usr/bin/env python3
"""Guard Alembic's asyncpg-compatible online environment."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = ROOT / "backend/alembic/env.py"
CHECKER_PATH = ROOT / "tools/check_alembic_readonly_state.py"


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"missing {label}: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise AssertionError(f"forbidden {label}: {needle}")


def main() -> None:
    env_text = ENV_PATH.read_text(encoding="utf-8")
    checker_text = CHECKER_PATH.read_text(encoding="utf-8")

    require(env_text, "from sqlalchemy.ext.asyncio import async_engine_from_config", "async engine import")
    require(env_text, "async def run_async_migrations()", "async migration runner")
    require(env_text, "async with connectable.connect() as connection:", "async connection context")
    require(env_text, "await connection.run_sync(do_run_migrations)", "Alembic sync bridge")
    require(env_text, "await connectable.dispose()", "async engine disposal")
    require(env_text, "asyncio.run(run_async_migrations())", "CLI event-loop entry")
    forbid(env_text, "from sqlalchemy import engine_from_config", "sync engine import")
    forbid(env_text, "connectable = engine_from_config(", "sync engine creation")
    forbid(env_text, "\n    with connectable.connect() as connection:", "sync connection context")

    require(checker_text, 'run_command(backend, "history")', "history collection")
    require(checker_text, 'run_command(backend, "heads")', "heads collection")
    require(checker_text, 'run_command(backend, "current")', "current collection")
    for dangerous in ("revision", "upgrade", "downgrade", "stamp"):
        if f'run_command(backend, "{dangerous}")' in checker_text:
            raise AssertionError(f"read-only checker must not run alembic {dangerous}")

    print("[OK] backend Alembic async env smoke")


if __name__ == "__main__":
    main()

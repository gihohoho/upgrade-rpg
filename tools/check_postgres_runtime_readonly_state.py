#!/usr/bin/env python3
"""Collect a non-destructive PostgreSQL/Docker/runtime baseline snapshot.

This tool performs read-only inspection only:
- Docker/Compose status commands that do not start, stop, or remove resources.
- PostgreSQL SELECT/introspection queries through the configured backend database URL.
- Optional GET request to the FastAPI DB health endpoint.

It never creates/drops tables, changes data, edits .env, creates revisions, or runs
Alembic upgrade/downgrade/stamp operations.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator

from _safe_subprocess import run_captured


@dataclass(frozen=True)
class CommandSnapshot:
    command: str
    ok: bool
    returncode: int
    output: str


@dataclass(frozen=True)
class HealthSnapshot:
    url: str
    ok: bool
    status_code: int | None
    output: str


@contextmanager
def working_directory(path: Path) -> Iterator[None]:
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def run_readonly_command(root: Path, command: list[str], timeout: int = 20) -> CommandSnapshot:
    try:
        completed, output = run_captured(
            command,
            cwd=root,
            check=False,
            timeout=timeout,
        )
        return CommandSnapshot(" ".join(command), completed.returncode == 0, completed.returncode, output)
    except Exception as exc:  # pragma: no cover - platform/installation dependent
        return CommandSnapshot(" ".join(command), False, 1, f"{type(exc).__name__}: {exc}")


def fetch_health(url: str, timeout: float) -> HealthSnapshot:
    request = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace").strip()
            return HealthSnapshot(url, 200 <= response.status < 300, response.status, body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace").strip()
        return HealthSnapshot(url, False, exc.code, body or str(exc))
    except Exception as exc:  # pragma: no cover - server may be intentionally stopped
        return HealthSnapshot(url, False, None, f"{type(exc).__name__}: {exc}")


def load_backend_objects(root: Path):
    backend = root / "backend"
    if str(backend) not in sys.path:
        sys.path.insert(0, str(backend))

    # pydantic-settings resolves the relative `.env` path from the current working
    # directory. Import from backend so the same file used by FastAPI is selected.
    with working_directory(backend):
        from app.core.config import settings  # noqa: PLC0415
        from app.db.base import Base  # noqa: PLC0415
        import app.models  # noqa: F401,PLC0415

    return settings, Base


def to_sync_url(database_url: str) -> str:
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


def inspect_database(root: Path, include_counts: bool) -> dict[str, Any]:
    try:
        from sqlalchemy import create_engine, inspect, text  # noqa: PLC0415
        from sqlalchemy.pool import NullPool  # noqa: PLC0415

        settings, Base = load_backend_objects(root)
        model_tables = sorted(table.name for table in Base.metadata.sorted_tables)
        engine = create_engine(to_sync_url(settings.database_url), poolclass=NullPool, future=True)

        try:
            with engine.connect() as connection:
                inspector = inspect(connection)
                public_tables = sorted(inspector.get_table_names(schema="public"))
                public_set = set(public_tables)
                model_set = set(model_tables)

                identity = connection.execute(
                    text(
                        "SELECT current_database(), current_user, current_schema(), "
                        "current_setting('server_version')"
                    )
                ).one()
                size = connection.execute(
                    text(
                        "SELECT pg_database_size(current_database()), "
                        "pg_size_pretty(pg_database_size(current_database()))"
                    )
                ).one()

                counts: dict[str, int] = {}
                if include_counts:
                    preparer = connection.dialect.identifier_preparer
                    schema_sql = preparer.quote_schema("public")
                    for table_name in public_tables:
                        table_sql = preparer.quote(table_name)
                        counts[table_name] = int(
                            connection.execute(text(f"SELECT COUNT(*) FROM {schema_sql}.{table_sql}"))
                            .scalar_one()
                        )

                alembic_rows: list[str] = []
                if "alembic_version" in public_set:
                    alembic_rows = [
                        str(row[0])
                        for row in connection.execute(
                            text("SELECT version_num FROM public.alembic_version ORDER BY version_num")
                        ).all()
                    ]

                missing_model_tables = sorted(model_set - public_set)
                extra_public_tables = sorted(public_set - model_set - {"alembic_version"})
                non_empty_tables = sorted(name for name, count in counts.items() if count > 0)
                total_rows = sum(counts.values())

                if alembic_rows:
                    classification = "alembic-managed"
                    recommendation = "Alembic revision이 기록되어 있습니다. revision 파일과 DB current 일치 여부를 먼저 비교하세요."
                elif missing_model_tables or extra_public_tables:
                    classification = "schema-drift"
                    recommendation = "모델과 실제 public schema가 다릅니다. baseline/stamp 전에 schema diff와 백업이 필요합니다."
                elif public_tables:
                    classification = "existing-schema-without-alembic-baseline"
                    recommendation = (
                        "create_all로 만들어진 기존 schema로 보입니다. 데이터를 보존하고 최초 revision을 별도 빈 DB에서 "
                        "검증한 뒤 baseline/stamp 여부를 결정해야 합니다."
                    )
                else:
                    classification = "empty-database"
                    recommendation = "빈 DB입니다. 최초 revision이 전체 schema를 생성하는 새 DB 전략을 검토할 수 있습니다."

                return {
                    "connected": True,
                    "database": str(identity[0]),
                    "user": str(identity[1]),
                    "schema": str(identity[2]),
                    "serverVersion": str(identity[3]),
                    "databaseSizeBytes": int(size[0]),
                    "databaseSizePretty": str(size[1]),
                    "modelTableCount": len(model_tables),
                    "publicTableCount": len(public_tables),
                    "modelTables": model_tables,
                    "publicTables": public_tables,
                    "missingModelTables": missing_model_tables,
                    "extraPublicTables": extra_public_tables,
                    "tableCountsCollected": include_counts,
                    "tableCounts": counts,
                    "nonEmptyTables": non_empty_tables,
                    "totalRows": total_rows if include_counts else None,
                    "alembicVersionTableExists": "alembic_version" in public_set,
                    "alembicCurrentRevisions": alembic_rows,
                    "classification": classification,
                    "recommendation": recommendation,
                }
        finally:
            engine.dispose()
    except Exception as exc:
        return {
            "connected": False,
            "error": f"{type(exc).__name__}: {exc}",
            "classification": "connection-failed",
            "recommendation": "PostgreSQL container, backend/.env URL, 계정/포트 상태를 확인하세요. DB 변경은 하지 마세요.",
        }


def collect(root: Path, health_url: str, health_timeout: float, include_counts: bool) -> dict[str, Any]:
    docker_commands = [
        ["docker", "compose", "ps"],
        ["docker", "compose", "ls"],
        ["docker", "volume", "ls", "--format", "{{.Name}}"],
    ]
    docker = [asdict(run_readonly_command(root, command)) for command in docker_commands]
    matching_volumes: list[dict[str, Any]] = []
    volume_names = docker[-1]["output"].splitlines() if docker and docker[-1]["ok"] else []
    for name in sorted(item.strip() for item in volume_names if "rpg_postgres_data" in item):
        matching_volumes.append(
            asdict(run_readonly_command(root, ["docker", "volume", "inspect", name]))
        )

    database = inspect_database(root, include_counts=include_counts)
    health = asdict(fetch_health(health_url, health_timeout))
    return {
        "readOnly": True,
        "mutationCommandsExecuted": False,
        "docker": docker,
        "matchingPostgresVolumes": matching_volumes,
        "database": database,
        "health": health,
    }


def render_text(payload: dict[str, Any]) -> str:
    lines = [
        "PostgreSQL runtime state check (read-only)",
        "DB schema/data, Docker resources, .env, and Alembic history are not changed.",
        "",
        "[Docker]",
    ]
    for item in payload["docker"]:
        lines.append(f"- {'OK' if item['ok'] else 'CHECK'}: {item['command']}")
        if item["output"]:
            lines.extend(f"    {line}" for line in item["output"].splitlines())
    if payload["matchingPostgresVolumes"]:
        lines.append("- PostgreSQL volume 후보가 확인되었습니다.")
    else:
        lines.append("- PostgreSQL volume 후보를 찾지 못했거나 Docker 조회가 실패했습니다.")

    database = payload["database"]
    lines.extend(["", "[PostgreSQL]"])
    if database.get("connected"):
        lines.append(f"- 연결: OK ({database['database']} / {database['user']})")
        lines.append(f"- PostgreSQL: {database['serverVersion']}")
        lines.append(f"- DB 크기: {database['databaseSizePretty']}")
        lines.append(
            f"- 테이블: public {database['publicTableCount']}개 / SQLAlchemy model {database['modelTableCount']}개"
        )
        lines.append(f"- 분류: {database['classification']}")
        lines.append(f"- Alembic version table: {'있음' if database['alembicVersionTableExists'] else '없음'}")
        revisions = database["alembicCurrentRevisions"]
        lines.append(f"- 현재 revision: {', '.join(revisions) if revisions else '없음'}")
        if database["missingModelTables"]:
            lines.append(f"- 모델에는 있지만 DB에 없는 테이블: {', '.join(database['missingModelTables'])}")
        if database["extraPublicTables"]:
            lines.append(f"- DB에만 있는 추가 테이블: {', '.join(database['extraPublicTables'])}")
        if database["tableCountsCollected"]:
            lines.append(f"- 전체 row 합계: {database['totalRows']}")
            for table_name, count in database["tableCounts"].items():
                lines.append(f"    {table_name}: {count}")
        lines.append(f"- 다음 판단: {database['recommendation']}")
    else:
        lines.append(f"- 연결: 실패 ({database.get('error', 'unknown error')})")
        lines.append(f"- 다음 판단: {database['recommendation']}")

    health = payload["health"]
    lines.extend(["", "[FastAPI DB health]"])
    lines.append(
        f"- {'OK' if health['ok'] else 'CHECK'}: GET {health['url']}"
        + (f" (HTTP {health['status_code']})" if health["status_code"] else "")
    )
    if health["output"]:
        lines.append(f"    {health['output']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Return 1 when DB connection or schema comparison fails")
    parser.add_argument("--skip-counts", action="store_true", help="Skip exact SELECT COUNT(*) per table")
    parser.add_argument(
        "--health-url",
        default="http://127.0.0.1:8000/api/v1/health/db",
        help="FastAPI read-only DB health endpoint",
    )
    parser.add_argument("--health-timeout", type=float, default=3.0)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    payload = collect(
        root,
        health_url=args.health_url,
        health_timeout=args.health_timeout,
        include_counts=not args.skip_counts,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_text(payload))

    database = payload["database"]
    failed = not database.get("connected") or database.get("classification") == "schema-drift"
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

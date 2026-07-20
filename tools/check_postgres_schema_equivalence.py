#!/usr/bin/env python3
"""Compare the live PostgreSQL schema with SQLAlchemy metadata without mutations.

The checker reads PostgreSQL catalog metadata through SQLAlchemy inspection and
compares table/column/type/nullability/PK/FK/unique/index/check structures. It
never creates, alters, drops, stamps, upgrades, downgrades, or writes rows.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from check_postgres_runtime_readonly_state import load_backend_objects, to_sync_url


@dataclass(frozen=True)
class Difference:
    category: str
    table: str
    detail: str


def normalized_type(type_: Any) -> str:
    """Compile and canonicalize model/reflected PostgreSQL type aliases.

    PostgreSQL treats ``FLOAT`` without a precision as ``DOUBLE PRECISION``.
    Reflection therefore returns ``DOUBLE PRECISION`` for a SQLAlchemy ``Float()``
    column.  Normalize the SQL-standard FLOAT aliases before comparing so this
    representational difference is not reported as schema drift.
    """
    from sqlalchemy.dialects import postgresql  # noqa: PLC0415

    try:
        compiled = str(type_.compile(dialect=postgresql.dialect()))
    except Exception:
        compiled = str(type_)
    normalized = " ".join(compiled.upper().split())

    if normalized == "FLOAT":
        return "DOUBLE PRECISION"

    match = re.fullmatch(r"FLOAT\((\d+)\)", normalized)
    if match:
        precision = int(match.group(1))
        if 1 <= precision <= 24:
            return "REAL"
        if 25 <= precision <= 53:
            return "DOUBLE PRECISION"

    return normalized


def normalize_columns(columns: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(str(item) for item in (columns or []))


def normalize_fk(
    constrained: Iterable[str] | None,
    referred_schema: str | None,
    referred_table: str | None,
    referred_columns: Iterable[str] | None,
    ondelete: str | None,
    onupdate: str | None,
) -> tuple[Any, ...]:
    return (
        normalize_columns(constrained),
        referred_schema or "public",
        referred_table or "",
        normalize_columns(referred_columns),
        (ondelete or "").upper(),
        (onupdate or "").upper(),
    )


def model_signature(table: Any) -> dict[str, Any]:
    from sqlalchemy import CheckConstraint, ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint  # noqa: PLC0415,E501

    columns = {
        column.name: {
            "type": normalized_type(column.type),
            "nullable": bool(column.nullable),
            "primaryKey": bool(column.primary_key),
        }
        for column in table.columns
    }
    primary_key = tuple(column.name for column in table.primary_key.columns)

    foreign_keys = []
    unique_constraints = []
    checks = []
    for constraint in table.constraints:
        if isinstance(constraint, ForeignKeyConstraint):
            elements = list(constraint.elements)
            referred_table = elements[0].column.table if elements else None
            foreign_keys.append(
                normalize_fk(
                    [element.parent.name for element in elements],
                    referred_table.schema if referred_table is not None else None,
                    referred_table.name if referred_table is not None else None,
                    [element.column.name for element in elements],
                    constraint.ondelete,
                    constraint.onupdate,
                )
            )
        elif isinstance(constraint, UniqueConstraint) and not isinstance(constraint, PrimaryKeyConstraint):
            unique_constraints.append(tuple(column.name for column in constraint.columns))
        elif isinstance(constraint, CheckConstraint):
            checks.append(" ".join(str(constraint.sqltext).split()))

    indexes = sorted(
        (
            tuple(column.name for column in index.columns),
            bool(index.unique),
        )
        for index in table.indexes
    )
    return {
        "columns": columns,
        "primaryKey": primary_key,
        "foreignKeys": sorted(foreign_keys),
        "uniqueConstraints": sorted(unique_constraints),
        "indexes": indexes,
        "checks": sorted(checks),
    }


def reflected_signature(inspector: Any, table_name: str) -> dict[str, Any]:
    columns = {
        item["name"]: {
            "type": normalized_type(item["type"]),
            "nullable": bool(item.get("nullable", True)),
            "primaryKey": False,
        }
        for item in inspector.get_columns(table_name, schema="public")
    }
    primary_key_data = inspector.get_pk_constraint(table_name, schema="public") or {}
    primary_key = normalize_columns(primary_key_data.get("constrained_columns"))
    for name in primary_key:
        if name in columns:
            columns[name]["primaryKey"] = True

    foreign_keys = []
    for item in inspector.get_foreign_keys(table_name, schema="public"):
        options = item.get("options") or {}
        foreign_keys.append(
            normalize_fk(
                item.get("constrained_columns"),
                item.get("referred_schema"),
                item.get("referred_table"),
                item.get("referred_columns"),
                options.get("ondelete"),
                options.get("onupdate"),
            )
        )

    unique_constraints = sorted(
        normalize_columns(item.get("column_names"))
        for item in inspector.get_unique_constraints(table_name, schema="public")
        if item.get("column_names")
    )

    indexes = []
    for item in inspector.get_indexes(table_name, schema="public"):
        if item.get("duplicates_constraint"):
            continue
        column_names = item.get("column_names")
        if not column_names or any(name is None for name in column_names):
            continue
        indexes.append((normalize_columns(column_names), bool(item.get("unique", False))))

    checks = sorted(
        " ".join(str(item.get("sqltext") or "").split())
        for item in inspector.get_check_constraints(table_name, schema="public")
        if item.get("sqltext")
    )
    return {
        "columns": columns,
        "primaryKey": primary_key,
        "foreignKeys": sorted(foreign_keys),
        "uniqueConstraints": unique_constraints,
        "indexes": sorted(indexes),
        "checks": checks,
    }


def compare_table(table_name: str, model: dict[str, Any], actual: dict[str, Any]) -> list[Difference]:
    differences: list[Difference] = []
    model_columns = set(model["columns"])
    actual_columns = set(actual["columns"])
    for name in sorted(model_columns - actual_columns):
        differences.append(Difference("missing-column", table_name, name))
    for name in sorted(actual_columns - model_columns):
        differences.append(Difference("extra-column", table_name, name))

    for name in sorted(model_columns & actual_columns):
        expected = model["columns"][name]
        observed = actual["columns"][name]
        if expected["type"] != observed["type"]:
            differences.append(
                Difference("type", table_name, f"{name}: model={expected['type']} db={observed['type']}")
            )
        if expected["nullable"] != observed["nullable"]:
            differences.append(
                Difference(
                    "nullable",
                    table_name,
                    f"{name}: model={expected['nullable']} db={observed['nullable']}",
                )
            )

    categories = (
        ("primary-key", "primaryKey"),
        ("foreign-key", "foreignKeys"),
        ("unique", "uniqueConstraints"),
        ("index", "indexes"),
        ("check", "checks"),
    )
    for category, key in categories:
        if model[key] != actual[key]:
            differences.append(
                Difference(category, table_name, f"model={model[key]!r} db={actual[key]!r}")
            )
    return differences


def collect(root: Path) -> dict[str, Any]:
    try:
        from sqlalchemy import create_engine, inspect  # noqa: PLC0415
        from sqlalchemy.pool import NullPool  # noqa: PLC0415

        settings, Base = load_backend_objects(root)
        model_tables = {table.name: table for table in Base.metadata.sorted_tables}
        engine = create_engine(to_sync_url(settings.database_url), poolclass=NullPool, future=True)
        try:
            with engine.connect() as connection:
                inspector = inspect(connection)
                actual_tables = set(inspector.get_table_names(schema="public")) - {"alembic_version"}
                model_names = set(model_tables)
                differences: list[Difference] = []
                for table_name in sorted(model_names - actual_tables):
                    differences.append(Difference("missing-table", table_name, "model table absent from DB"))
                for table_name in sorted(actual_tables - model_names):
                    differences.append(Difference("extra-table", table_name, "DB table absent from model"))

                compared_tables: list[str] = []
                for table_name in sorted(model_names & actual_tables):
                    compared_tables.append(table_name)
                    differences.extend(
                        compare_table(
                            table_name,
                            model_signature(model_tables[table_name]),
                            reflected_signature(inspector, table_name),
                        )
                    )

                return {
                    "readOnly": True,
                    "schemaChanged": False,
                    "connected": True,
                    "classification": "structurally-equivalent" if not differences else "review-required",
                    "typeNormalization": "postgresql-float-aliases.v1",
                    "modelTableCount": len(model_names),
                    "databaseTableCount": len(actual_tables),
                    "comparedTables": compared_tables,
                    "differenceCount": len(differences),
                    "differences": [item.__dict__ for item in differences],
                }
        finally:
            engine.dispose()
    except Exception as exc:
        return {
            "readOnly": True,
            "schemaChanged": False,
            "connected": False,
            "classification": "connection-failed",
            "differenceCount": None,
            "differences": [],
            "error": f"{type(exc).__name__}: {exc}",
        }


def render_text(payload: dict[str, Any]) -> str:
    lines = [
        "PostgreSQL / SQLAlchemy schema equivalence check (read-only)",
        "No CREATE/ALTER/DROP, row mutation, Alembic revision, upgrade, or stamp is executed.",
        "",
    ]
    if not payload.get("connected"):
        lines.append(f"- 연결: 실패 ({payload.get('error', 'unknown error')})")
        return "\n".join(lines)

    lines.extend(
        [
            "- 연결: OK",
            f"- 비교 테이블: {len(payload['comparedTables'])}개",
            f"- 모델/DB 테이블: {payload['modelTableCount']} / {payload['databaseTableCount']}",
            f"- 분류: {payload['classification']}",
            f"- 타입 정규화: {payload.get('typeNormalization', 'none')}",
            f"- 차이: {payload['differenceCount']}개",
        ]
    )
    for item in payload["differences"]:
        lines.append(f"    [{item['category']}] {item['table']}: {item['detail']}")
    if not payload["differences"]:
        lines.append("- 현재 비교 범위에서 구조 차이가 발견되지 않았습니다.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Return 1 for connection failure or differences")
    parser.add_argument(
        "--skip-database",
        action="store_true",
        help="Skip live database inspection (for offline/static smoke environments)",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    payload = (
        {
            "readOnly": True,
            "schemaChanged": False,
            "connected": False,
            "classification": "skipped",
            "differenceCount": None,
            "differences": [],
            "error": "Database inspection was explicitly skipped.",
        }
        if args.skip_database
        else collect(root)
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else render_text(payload))
    failed = not payload.get("connected") or payload.get("differenceCount") not in (0, None)
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

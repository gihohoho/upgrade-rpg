#!/usr/bin/env python3
"""Static/manual cross-review smoke for the exact v295 initial schema revision."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects import postgresql

ROOT = Path(__file__).resolve().parents[3]
BACKEND = ROOT / "backend"
REVISION = BACKEND / "alembic/versions/v295_initial_schema_initial_postgresql_schema.py"
REVIEW = ROOT / "docs/current/review/v295_initial_schema.manual-review.json"
EXPECTED_SHA = "24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class UpgradeRecorder:
    def __init__(self) -> None:
        self.metadata = sa.MetaData()
        self.tables: dict[str, sa.Table] = {}
        self.indexes: list[sa.Index] = []
        self.operations: list[tuple[Any, ...]] = []

    def f(self, name: str) -> str:
        return name

    def create_table(self, name: str, *items: Any, **kwargs: Any) -> sa.Table:
        self.operations.append(("create_table", name))
        table = sa.Table(name, self.metadata, *items, **kwargs)
        self.tables[name] = table
        return table

    def create_index(
        self, name: str, table_name: str, columns: list[str], unique: bool = False, **kwargs: Any
    ) -> sa.Index:
        self.operations.append(("create_index", name, table_name, tuple(columns), unique))
        table = self.tables[table_name]
        index = sa.Index(name, *[table.c[column] for column in columns], unique=unique, **kwargs)
        self.indexes.append(index)
        return index


class DowngradeRecorder:
    def __init__(self) -> None:
        self.operations: list[tuple[Any, ...]] = []

    def f(self, name: str) -> str:
        return name

    def drop_index(self, name: str, **kwargs: Any) -> None:
        self.operations.append(("drop_index", name, kwargs))

    def drop_table(self, name: str, **kwargs: Any) -> None:
        self.operations.append(("drop_table", name, kwargs))


def type_sql(value: Any) -> str:
    return str(value.compile(dialect=postgresql.dialect()))


def default_arg(value: Any) -> str | None:
    if value is None:
        return None
    return str(getattr(value, "arg", value))


def fk_signature(constraint: ForeignKeyConstraint) -> tuple[Any, ...]:
    return (
        tuple(element.parent.name for element in constraint.elements),
        tuple(element.target_fullname for element in constraint.elements),
        (constraint.ondelete or "").upper(),
        (constraint.onupdate or "").upper(),
        constraint.name,
    )


def unique_signature(constraint: UniqueConstraint) -> tuple[Any, ...]:
    return tuple(column.name for column in constraint.columns), constraint.name


def check_signature(constraint: CheckConstraint) -> tuple[Any, ...]:
    return str(constraint.sqltext), constraint.name


def index_signature(index: sa.Index) -> tuple[Any, ...]:
    return tuple(column.name for column in index.columns), bool(index.unique), index.name


def main() -> None:
    if sha256(REVISION) != EXPECTED_SHA:
        raise AssertionError("reviewed revision SHA-256 changed")
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    if review.get("reviewResult") != "passed" or review.get("revisionSha256") != EXPECTED_SHA:
        raise AssertionError("manual review evidence is not pinned to the reviewed revision")

    sys.path.insert(0, str(BACKEND))
    import app.models  # noqa: F401,PLC0415
    from app.db.base import Base  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("reviewed_initial_revision", REVISION)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load reviewed revision")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    upgrade = UpgradeRecorder()
    module.op = upgrade
    module.upgrade()

    downgrade = DowngradeRecorder()
    module.op = downgrade
    module.downgrade()

    model_tables = Base.metadata.tables
    if set(model_tables) != set(upgrade.tables):
        raise AssertionError("model/revision table set differs")

    for table_name in sorted(model_tables):
        model = model_tables[table_name]
        revision = upgrade.tables[table_name]
        if list(model.c.keys()) != list(revision.c.keys()):
            raise AssertionError(f"{table_name}: column order/set differs")
        for column_name in model.c.keys():
            expected = model.c[column_name]
            actual = revision.c[column_name]
            comparisons = {
                "type": (type_sql(expected.type), type_sql(actual.type)),
                "nullable": (expected.nullable, actual.nullable),
                "primary_key": (expected.primary_key, actual.primary_key),
                "server_default": (
                    default_arg(expected.server_default),
                    default_arg(actual.server_default),
                ),
                "autoincrement": (expected.autoincrement, actual.autoincrement),
                "comment": (expected.comment, actual.comment),
            }
            mismatches = {name: values for name, values in comparisons.items() if values[0] != values[1]}
            if mismatches:
                raise AssertionError(f"{table_name}.{column_name}: {mismatches}")

        expected_fks = sorted(
            fk_signature(item)
            for item in model.constraints
            if isinstance(item, ForeignKeyConstraint)
        )
        actual_fks = sorted(
            fk_signature(item)
            for item in revision.constraints
            if isinstance(item, ForeignKeyConstraint)
        )
        if expected_fks != actual_fks:
            raise AssertionError(f"{table_name}: foreign keys differ")

        expected_unique = sorted(
            unique_signature(item)
            for item in model.constraints
            if isinstance(item, UniqueConstraint) and not isinstance(item, PrimaryKeyConstraint)
        )
        actual_unique = sorted(
            unique_signature(item)
            for item in revision.constraints
            if isinstance(item, UniqueConstraint) and not isinstance(item, PrimaryKeyConstraint)
        )
        if expected_unique != actual_unique:
            raise AssertionError(f"{table_name}: unique constraints differ")

        expected_checks = sorted(
            check_signature(item)
            for item in model.constraints
            if isinstance(item, CheckConstraint)
        )
        actual_checks = sorted(
            check_signature(item)
            for item in revision.constraints
            if isinstance(item, CheckConstraint)
        )
        if expected_checks != actual_checks:
            raise AssertionError(f"{table_name}: check constraints differ")

        expected_indexes = sorted(index_signature(item) for item in model.indexes)
        actual_indexes = sorted(index_signature(item) for item in revision.indexes)
        if expected_indexes != actual_indexes:
            raise AssertionError(f"{table_name}: indexes differ")

    created_indexes = sorted(
        (item[1], item[2], item[3], item[4])
        for item in upgrade.operations
        if item[0] == "create_index"
    )
    dropped_indexes = sorted(
        (item[1], str(item[2].get("table_name") or ""))
        for item in downgrade.operations
        if item[0] == "drop_index"
    )
    expected_dropped_indexes = sorted((name, table_name) for name, table_name, _, _ in created_indexes)
    if dropped_indexes != expected_dropped_indexes:
        raise AssertionError("downgrade index set/table binding differs from upgrade")

    create_order = [item[1] for item in upgrade.operations if item[0] == "create_table"]
    drop_order = [item[1] for item in downgrade.operations if item[0] == "drop_table"]
    if drop_order != list(reversed(create_order)):
        raise AssertionError("downgrade table order is not exact reverse create order")

    create_position = {name: index for index, name in enumerate(create_order)}
    drop_position = {name: index for index, name in enumerate(drop_order)}
    for table in upgrade.tables.values():
        for foreign_key in table.foreign_key_constraints:
            for element in foreign_key.elements:
                parent = element.target_fullname.split(".", 1)[0]
                if create_position[parent] >= create_position[table.name]:
                    raise AssertionError(f"FK parent created after child: {table.name} -> {parent}")
                if drop_position[table.name] >= drop_position[parent]:
                    raise AssertionError(f"FK child dropped after parent: {table.name} -> {parent}")

    if len(model_tables) != 22:
        raise AssertionError("model table count is not 22")
    if sum(len(table.columns) for table in model_tables.values()) != 209:
        raise AssertionError("model column count is not 209")
    if len(upgrade.indexes) != 42:
        raise AssertionError("revision index count is not 42")
    if sum(column.server_default is not None for table in model_tables.values() for column in table.columns) != 0:
        raise AssertionError("unexpected model server default")

    float_columns = sorted(
        f"{table.name}.{column.name}"
        for table in model_tables.values()
        for column in table.columns
        if type_sql(column.type) == "FLOAT"
    )
    if float_columns != [
        "user_profiles.add_attack_speed",
        "user_profiles.farm_atk_bonus",
    ]:
        raise AssertionError(f"FLOAT column baseline changed: {float_columns}")

    print("PostgreSQL initial Alembic revision manual review smoke passed")
    print("- revision SHA-256 pinned")
    print("- tables/columns/indexes: 22 / 209 / 42")
    print("- types/nullability/PK/FK/unique/index/server defaults: matched")
    print("- downgrade dependency order: valid")


if __name__ == "__main__":
    main()

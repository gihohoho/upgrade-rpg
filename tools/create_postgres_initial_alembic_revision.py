#!/usr/bin/env python3
"""Create and automatically review the first Alembic revision against the isolated empty DB.

This is the v297 parser recovery step after v296 correctly reused the empty
`alembic_version` placeholder but misclassified nested `op.f(...)` naming helpers
as migration operations.

Approved mutation boundary:
- MAY create exactly one Alembic revision Python file with revision ID
  `v295_initial_schema` under `backend/alembic/versions/`.
- MAY create a schema-only local review report/bundle under
  `local-review-artifacts/alembic/`.
- MUST point Alembic only at `rpg_game_migration_empty_v290` by an in-process
  `DATABASE_URL` override; `backend/.env` is never edited.
- MUST preserve source/rehearsal/migration databases unchanged.
- MUST NOT run Alembic upgrade/downgrade/stamp, SQL data writes, pg_restore,
  createdb, dropdb, or Docker resource changes.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from sqlalchemy.engine import make_url

from _safe_subprocess import decode_output
from check_postgres_backup_restore_preflight import (
    MIGRATION_TEST_DATABASE,
    RESTORE_REHEARSAL_DATABASE,
    SOURCE_DATABASE,
)
from check_postgres_runtime_readonly_state import inspect_database, load_backend_objects
from create_postgres_migration_test_database import (
    load_verified_restore_evidence,
    MigrationTestDatabaseError,
    sanitize_database_state,
    validate_rehearsal_state,
    validate_source_state,
)
from restore_postgres_rehearsal_database import inspect_named_database

TOOL_VERSION = "v297.postgres-initial-alembic-op-f-parser-recovery"
REVISION_ID = "v295_initial_schema"
REVISION_MESSAGE = "initial PostgreSQL schema"
REVISION_FILENAME = "v295_initial_schema_initial_postgresql_schema.py"
DEFAULT_TIMEOUT_SECONDS = 180
# Alembic renders explicitly normalized constraint/index names as nested op.f(...)
# calls. op.f is a naming helper, not a schema mutation operation, so it must not
# be counted against the upgrade/downgrade operation allowlists.
ALEMBIC_NON_OPERATION_HELPERS = frozenset({"f"})
REVIEW_DIRECTORY = Path("local-review-artifacts/alembic")
REVIEW_JSON_FILENAME = "v295_initial_schema.review.json"
REVIEW_BUNDLE_FILENAME = "v295_initial_schema_review_bundle.zip"


class InitialRevisionError(RuntimeError):
    """Raised when a safety gate, generation, or automated review fails."""


@dataclass(frozen=True)
class OperationCall:
    function: str
    lineno: int
    args: tuple[Any, ...]
    keywords: dict[str, Any]
    raw: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_under(root: Path, path: Path) -> Path:
    root_resolved = root.resolve()
    resolved = path.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise InitialRevisionError(f"unsafe path outside project: {path}")
    return resolved


def literal_value(node: ast.AST | None) -> Any:
    if node is None:
        return None
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        return None


def expression_text(source: str, node: ast.AST) -> str:
    return ast.get_source_segment(source, node) or ast.unparse(node)


def find_assignment(module: ast.Module, name: str) -> Any:
    for node in module.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return literal_value(node.value)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                return literal_value(node.value)
    raise InitialRevisionError(f"generated revision is missing assignment: {name}")


def find_function(module: ast.Module, name: str) -> ast.FunctionDef:
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise InitialRevisionError(f"generated revision is missing function: {name}")


def collect_op_calls(source: str, function: ast.FunctionDef) -> list[OperationCall]:
    calls: list[OperationCall] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "op"
        ):
            continue
        if func.attr in ALEMBIC_NON_OPERATION_HELPERS:
            # op.f(...) is emitted inside create_table/create_index arguments to
            # mark a name as already processed by a naming convention. It does
            # not execute a migration operation and must not appear in operation
            # counts or allowlist checks.
            continue
        calls.append(
            OperationCall(
                function=func.attr,
                lineno=getattr(node, "lineno", 0),
                args=tuple(literal_value(arg) for arg in node.args),
                keywords={item.arg or "**": literal_value(item.value) for item in node.keywords},
                raw=expression_text(source, node),
            )
        )
    return sorted(calls, key=lambda item: item.lineno)


def extract_create_table_details(
    source: str, function: ast.FunctionDef
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "op"
            and func.attr == "create_table"
        ):
            continue
        if not node.args:
            raise InitialRevisionError("op.create_table call is missing table name")
        table_name = literal_value(node.args[0])
        if not isinstance(table_name, str) or not table_name:
            raise InitialRevisionError("op.create_table table name is not a string literal")
        if table_name in result:
            raise InitialRevisionError(f"duplicate op.create_table call: {table_name}")

        columns: dict[str, dict[str, Any]] = {}
        primary_keys: list[tuple[str, ...]] = []
        unique_constraints: list[tuple[str, ...]] = []
        foreign_keys: list[dict[str, Any]] = []
        check_constraints = 0

        for item in node.args[1:]:
            if not isinstance(item, ast.Call):
                continue
            item_func = item.func
            if not (
                isinstance(item_func, ast.Attribute)
                and isinstance(item_func.value, ast.Name)
                and item_func.value.id in {"sa", "postgresql"}
            ):
                continue
            kind = item_func.attr
            if kind == "Column":
                if not item.args:
                    raise InitialRevisionError(f"{table_name}: sa.Column is missing name")
                column_name = literal_value(item.args[0])
                if not isinstance(column_name, str):
                    raise InitialRevisionError(f"{table_name}: column name is not a literal")
                if column_name in columns:
                    raise InitialRevisionError(f"{table_name}: duplicate column {column_name}")
                nullable = None
                for keyword in item.keywords:
                    if keyword.arg == "nullable":
                        nullable = literal_value(keyword.value)
                columns[column_name] = {
                    "nullable": nullable,
                    "expression": expression_text(source, item),
                }
            elif kind == "PrimaryKeyConstraint":
                primary_keys.append(
                    tuple(str(value) for value in (literal_value(arg) for arg in item.args) if value is not None)
                )
            elif kind == "UniqueConstraint":
                unique_constraints.append(
                    tuple(str(value) for value in (literal_value(arg) for arg in item.args) if value is not None)
                )
            elif kind == "ForeignKeyConstraint":
                local_columns = literal_value(item.args[0]) if len(item.args) >= 1 else None
                remote_columns = literal_value(item.args[1]) if len(item.args) >= 2 else None
                ondelete = None
                onupdate = None
                for keyword in item.keywords:
                    if keyword.arg == "ondelete":
                        ondelete = literal_value(keyword.value)
                    elif keyword.arg == "onupdate":
                        onupdate = literal_value(keyword.value)
                foreign_keys.append(
                    {
                        "localColumns": tuple(str(value) for value in (local_columns or [])),
                        "remoteColumns": tuple(str(value) for value in (remote_columns or [])),
                        "onDelete": str(ondelete or "").upper(),
                        "onUpdate": str(onupdate or "").upper(),
                    }
                )
            elif kind == "CheckConstraint":
                check_constraints += 1

        result[table_name] = {
            "columns": columns,
            "primaryKeys": sorted(primary_keys),
            "uniqueConstraints": sorted(unique_constraints),
            "foreignKeys": sorted(
                foreign_keys,
                key=lambda value: (
                    value["localColumns"],
                    value["remoteColumns"],
                    value["onDelete"],
                    value["onUpdate"],
                ),
            ),
            "checkConstraintCount": check_constraints,
        }
    return result


def extract_index_details(calls: Iterable[OperationCall]) -> dict[str, list[dict[str, Any]]]:
    indexes: dict[str, list[dict[str, Any]]] = {}
    for call in calls:
        if call.function != "create_index":
            continue
        if len(call.args) < 3:
            raise InitialRevisionError("op.create_index call has fewer than three arguments")
        table_name = call.args[1]
        columns = call.args[2]
        if not isinstance(table_name, str) or not isinstance(columns, (list, tuple)):
            raise InitialRevisionError("op.create_index table/columns are not literals")
        indexes.setdefault(table_name, []).append(
            {
                "columns": tuple(str(value) for value in columns),
                "unique": bool(call.keywords.get("unique", False)),
            }
        )
    for table_name in indexes:
        indexes[table_name] = sorted(
            indexes[table_name], key=lambda value: (value["columns"], value["unique"])
        )
    return indexes


def model_review_baseline(root: Path) -> dict[str, dict[str, Any]]:
    _, Base = load_backend_objects(root)
    from sqlalchemy import (  # noqa: PLC0415
        CheckConstraint,
        ForeignKeyConstraint,
        PrimaryKeyConstraint,
        UniqueConstraint,
    )

    result: dict[str, dict[str, Any]] = {}
    for table in Base.metadata.sorted_tables:
        foreign_keys: list[dict[str, Any]] = []
        unique_constraints: list[tuple[str, ...]] = []
        check_count = 0
        for constraint in table.constraints:
            if isinstance(constraint, ForeignKeyConstraint):
                foreign_keys.append(
                    {
                        "localColumns": tuple(element.parent.name for element in constraint.elements),
                        "remoteColumns": tuple(
                            f"{element.column.table.name}.{element.column.name}"
                            for element in constraint.elements
                        ),
                        "onDelete": str(constraint.ondelete or "").upper(),
                        "onUpdate": str(constraint.onupdate or "").upper(),
                    }
                )
            elif isinstance(constraint, UniqueConstraint) and not isinstance(
                constraint, PrimaryKeyConstraint
            ):
                unique_constraints.append(tuple(column.name for column in constraint.columns))
            elif isinstance(constraint, CheckConstraint):
                check_count += 1

        result[table.name] = {
            "columns": {
                column.name: {"nullable": bool(column.nullable)} for column in table.columns
            },
            "primaryKeys": [tuple(column.name for column in table.primary_key.columns)],
            "uniqueConstraints": sorted(unique_constraints),
            "foreignKeys": sorted(
                foreign_keys,
                key=lambda value: (
                    value["localColumns"],
                    value["remoteColumns"],
                    value["onDelete"],
                    value["onUpdate"],
                ),
            ),
            "checkConstraintCount": check_count,
            "indexes": sorted(
                [
                    {
                        "columns": tuple(column.name for column in index.columns),
                        "unique": bool(index.unique),
                    }
                    for index in table.indexes
                ],
                key=lambda value: (value["columns"], value["unique"]),
            ),
        }
    return result


def review_revision(root: Path, revision_path: Path) -> dict[str, Any]:
    source = revision_path.read_text(encoding="utf-8")
    try:
        module = ast.parse(source, filename=str(revision_path))
    except SyntaxError as exc:
        raise InitialRevisionError(f"generated revision syntax error: {exc}") from exc

    revision = find_assignment(module, "revision")
    down_revision = find_assignment(module, "down_revision")
    branch_labels = find_assignment(module, "branch_labels")
    depends_on = find_assignment(module, "depends_on")
    if revision != REVISION_ID:
        raise InitialRevisionError(f"revision ID mismatch: {revision!r}")
    if down_revision is not None or branch_labels is not None or depends_on is not None:
        raise InitialRevisionError("first revision must have no parent/branch/dependency")

    upgrade = find_function(module, "upgrade")
    downgrade = find_function(module, "downgrade")
    upgrade_calls = collect_op_calls(source, upgrade)
    downgrade_calls = collect_op_calls(source, downgrade)

    forbidden_any = {
        "execute",
        "bulk_insert",
        "run_async",
    }
    forbidden_upgrade = forbidden_any | {
        "drop_table",
        "drop_column",
        "drop_constraint",
        "drop_index",
        "alter_column",
        "rename_table",
    }
    forbidden_downgrade = forbidden_any | {
        "create_table",
        "add_column",
        "create_index",
        "create_unique_constraint",
        "create_foreign_key",
        "alter_column",
        "rename_table",
    }
    for call in upgrade_calls:
        if call.function in forbidden_upgrade:
            raise InitialRevisionError(
                f"forbidden upgrade operation op.{call.function} at line {call.lineno}"
            )
    for call in downgrade_calls:
        if call.function in forbidden_downgrade:
            raise InitialRevisionError(
                f"forbidden downgrade operation op.{call.function} at line {call.lineno}"
            )

    allowed_upgrade = {
        "create_table",
        "create_index",
        "create_unique_constraint",
        "create_foreign_key",
        "create_check_constraint",
    }
    allowed_downgrade = {"drop_index", "drop_constraint", "drop_table"}
    unexpected_upgrade = sorted({call.function for call in upgrade_calls} - allowed_upgrade)
    unexpected_downgrade = sorted({call.function for call in downgrade_calls} - allowed_downgrade)
    if unexpected_upgrade or unexpected_downgrade:
        raise InitialRevisionError(
            f"unexpected Alembic operations: upgrade={unexpected_upgrade}, downgrade={unexpected_downgrade}"
        )

    model = model_review_baseline(root)
    expected_tables = set(model)
    generated = extract_create_table_details(source, upgrade)
    generated_tables = set(generated)
    dropped_tables = {
        str(call.args[0])
        for call in downgrade_calls
        if call.function == "drop_table" and call.args and isinstance(call.args[0], str)
    }
    if generated_tables != expected_tables:
        raise InitialRevisionError(
            f"upgrade table set mismatch: missing={sorted(expected_tables - generated_tables)}, "
            f"extra={sorted(generated_tables - expected_tables)}"
        )
    if dropped_tables != expected_tables:
        raise InitialRevisionError(
            f"downgrade table set mismatch: missing={sorted(expected_tables - dropped_tables)}, "
            f"extra={sorted(dropped_tables - expected_tables)}"
        )
    if sum(call.function == "drop_table" for call in downgrade_calls) != len(expected_tables):
        raise InitialRevisionError("downgrade must contain exactly one drop_table per model table")

    indexes = extract_index_details(upgrade_calls)
    table_reviews: dict[str, Any] = {}
    for table_name in sorted(expected_tables):
        expected = model[table_name]
        actual = generated[table_name]
        expected_columns = expected["columns"]
        actual_columns = actual["columns"]
        if set(actual_columns) != set(expected_columns):
            raise InitialRevisionError(
                f"{table_name}: column set mismatch: missing={sorted(set(expected_columns) - set(actual_columns))}, "
                f"extra={sorted(set(actual_columns) - set(expected_columns))}"
            )
        nullable_mismatches = []
        for column_name, expected_column in expected_columns.items():
            actual_nullable = actual_columns[column_name]["nullable"]
            if actual_nullable is None:
                raise InitialRevisionError(
                    f"{table_name}.{column_name}: generated nullable flag is not explicit"
                )
            if bool(actual_nullable) != bool(expected_column["nullable"]):
                nullable_mismatches.append(
                    f"{column_name}: model={expected_column['nullable']}, revision={actual_nullable}"
                )
        if nullable_mismatches:
            raise InitialRevisionError(
                f"{table_name}: nullable mismatches: {', '.join(nullable_mismatches)}"
            )
        if actual["primaryKeys"] != expected["primaryKeys"]:
            raise InitialRevisionError(
                f"{table_name}: primary key mismatch: model={expected['primaryKeys']}, "
                f"revision={actual['primaryKeys']}"
            )
        if actual["uniqueConstraints"] != expected["uniqueConstraints"]:
            raise InitialRevisionError(
                f"{table_name}: unique constraint mismatch: model={expected['uniqueConstraints']}, "
                f"revision={actual['uniqueConstraints']}"
            )
        if actual["foreignKeys"] != expected["foreignKeys"]:
            raise InitialRevisionError(
                f"{table_name}: foreign key mismatch: model={expected['foreignKeys']}, "
                f"revision={actual['foreignKeys']}"
            )
        if actual["checkConstraintCount"] != expected["checkConstraintCount"]:
            raise InitialRevisionError(
                f"{table_name}: check constraint count mismatch"
            )
        actual_indexes = indexes.get(table_name, [])
        if actual_indexes != expected["indexes"]:
            raise InitialRevisionError(
                f"{table_name}: index mismatch: model={expected['indexes']}, revision={actual_indexes}"
            )
        table_reviews[table_name] = {
            "columnCount": len(actual_columns),
            "primaryKey": actual["primaryKeys"],
            "foreignKeyCount": len(actual["foreignKeys"]),
            "uniqueConstraintCount": len(actual["uniqueConstraints"]),
            "indexCount": len(actual_indexes),
            "checkConstraintCount": actual["checkConstraintCount"],
        }

    lowered = source.lower()
    forbidden_fragments = (
        SOURCE_DATABASE.lower(),
        RESTORE_REHEARSAL_DATABASE.lower(),
        MIGRATION_TEST_DATABASE.lower(),
        "pg_restore",
        "createdb",
        "dropdb",
        "alembic stamp",
        "alembic upgrade",
        "alembic downgrade",
    )
    present_fragments = [fragment for fragment in forbidden_fragments if fragment in lowered]
    if present_fragments:
        raise InitialRevisionError(
            f"generated revision contains forbidden environment/database text: {present_fragments}"
        )

    total_columns = sum(value["columnCount"] for value in table_reviews.values())
    return {
        "result": "initial-alembic-revision-automated-review-passed",
        "revision": REVISION_ID,
        "downRevision": None,
        "tableCount": len(expected_tables),
        "columnCount": total_columns,
        "upgradeOperationCounts": operation_counts(upgrade_calls),
        "downgradeOperationCounts": operation_counts(downgrade_calls),
        "tables": table_reviews,
        "manualReviewStillRequired": True,
        "upgradeDowngradeStampExecuted": False,
    }


def operation_counts(calls: Iterable[OperationCall]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for call in calls:
        counts[call.function] = counts.get(call.function, 0) + 1
    return dict(sorted(counts.items()))


def validate_revision_workspace_state(
    state: dict[str, Any], *, require_existing_placeholder: bool
) -> dict[str, Any]:
    """Validate the isolated revision workspace without deleting any DB object.

    The failed v295 attempt proved that Alembic's online autogenerate path creates
    an empty `alembic_version` table even though no revision is applied. v296
    therefore treats exactly one empty control table with no revision rows as a
    safe recovery state.  Any application table, row, or recorded revision still
    blocks execution.
    """
    if state.get("connected") is not True:
        raise InitialRevisionError(
            f"migration test database connection failed: {state.get('error', 'unknown error')}"
        )
    if state.get("database") != MIGRATION_TEST_DATABASE:
        raise InitialRevisionError("migration test database boundary mismatch")
    if state.get("user") != "rpg_user":
        raise InitialRevisionError("migration test connection user boundary mismatch")

    tables = tuple(sorted(str(item) for item in (state.get("publicTables") or [])))
    counts = {str(name): int(value) for name, value in (state.get("tableCounts") or {}).items()}
    revisions = tuple(str(item) for item in (state.get("alembicCurrentRevisions") or []))
    public_count = int(state.get("publicTableCount") or 0)
    total_rows = int(state.get("totalRows") or 0)

    if public_count != len(tables):
        raise InitialRevisionError(
            f"migration workspace table count metadata mismatch: count={public_count}, tables={list(tables)}"
        )
    if set(counts) != set(tables) or total_rows != sum(counts.values()):
        raise InitialRevisionError(
            f"migration workspace row metadata mismatch: tables={list(tables)}, counts={counts}, total={total_rows}"
        )

    if not tables:
        if state.get("alembicVersionTableExists") is not False or revisions:
            raise InitialRevisionError("empty migration workspace has inconsistent Alembic metadata")
        classification = "empty-before-autogenerate"
    elif tables == ("alembic_version",):
        if state.get("alembicVersionTableExists") is not True:
            raise InitialRevisionError("alembic_version table metadata is inconsistent")
        if counts != {"alembic_version": 0} or total_rows != 0 or revisions:
            raise InitialRevisionError(
                "alembic_version recovery placeholder must contain zero rows and no revision value"
            )
        classification = "empty-alembic-version-placeholder"
    else:
        raise InitialRevisionError(
            "migration test database contains unexpected objects; "
            f"tables={list(tables)}, counts={counts}, revisions={list(revisions)}"
        )

    if require_existing_placeholder and classification != "empty-alembic-version-placeholder":
        raise InitialRevisionError(
            "v297 recovery requires the sole empty alembic_version placeholder left by the v295 attempt; "
            f"actual={classification}. No DB mutation was attempted."
        )

    result = sanitize_database_state(state)
    result["revisionWorkspaceClassification"] = classification
    result["safeRecoveryPlaceholder"] = classification == "empty-alembic-version-placeholder"
    return result


def target_database_url(root: Path) -> str:
    settings, _ = load_backend_objects(root)
    source_url = make_url(settings.database_url)
    if source_url.database != SOURCE_DATABASE:
        raise InitialRevisionError(
            f"configured source DB mismatch: expected={SOURCE_DATABASE}, actual={source_url.database}"
        )
    target = source_url.set(database=MIGRATION_TEST_DATABASE)
    return target.render_as_string(hide_password=False)


def build_revision_command() -> list[str]:
    return [
        sys.executable,
        "-m",
        "alembic",
        "--config",
        "alembic.ini",
        "revision",
        "--autogenerate",
        "--rev-id",
        REVISION_ID,
        "--message",
        REVISION_MESSAGE,
    ]


def existing_revision_files(versions_dir: Path) -> list[Path]:
    return sorted(
        path for path in versions_dir.glob("*.py") if path.name != "__init__.py"
    )


def run_revision_command(
    root: Path,
    *,
    timeout: int,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> str:
    backend = root / "backend"
    env = os.environ.copy()
    env["DATABASE_URL"] = target_database_url(root)
    env["PYTHONPATH"] = str(backend.resolve()) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    command = build_revision_command()
    try:
        completed = run_process(
            command,
            cwd=backend,
            env=env,
            text=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise InitialRevisionError(
            f"Alembic revision generation timed out after {timeout} seconds"
        ) from exc
    output = decode_output(completed.stdout).strip()
    if completed.returncode != 0:
        raise InitialRevisionError(
            f"Alembic revision generation failed with exit={completed.returncode}: "
            f"{output or 'no output'}"
        )
    return output


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.partial")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def create_review_bundle(
    root: Path,
    revision_path: Path,
    review_path: Path,
    bundle_path: Path,
) -> None:
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = bundle_path.with_name(f".{bundle_path.name}.partial")
    if temporary.exists():
        temporary.unlink()
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(revision_path, arcname=f"backend/alembic/versions/{revision_path.name}")
        archive.write(review_path, arcname=f"review/{review_path.name}")
    with zipfile.ZipFile(temporary, "r") as archive:
        bad = archive.testzip()
        if bad is not None:
            raise InitialRevisionError(f"review bundle CRC failed: {bad}")
    temporary.replace(bundle_path)


def execute_generation(
    root: Path,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    evidence: dict[str, Any] | None = None,
    source_before_raw: dict[str, Any] | None = None,
    source_after_raw: dict[str, Any] | None = None,
    rehearsal_before_raw: dict[str, Any] | None = None,
    rehearsal_after_raw: dict[str, Any] | None = None,
    migration_before_raw: dict[str, Any] | None = None,
    migration_after_raw: dict[str, Any] | None = None,
    run_process: Callable[..., subprocess.CompletedProcess[bytes]] = subprocess.run,
) -> dict[str, Any]:
    root = root.resolve()
    backend = ensure_under(root, root / "backend")
    versions_dir = ensure_under(root, backend / "alembic/versions")
    template_path = ensure_under(root, backend / "alembic/script.py.mako")
    if not template_path.is_file():
        raise InitialRevisionError("backend/alembic/script.py.mako is missing")
    versions_dir.mkdir(parents=True, exist_ok=True)

    current_revisions = existing_revision_files(versions_dir)
    if current_revisions:
        raise InitialRevisionError(
            "Alembic versions directory already contains revision files; "
            f"no generation was attempted: {[path.name for path in current_revisions]}"
        )

    try:
        verified = evidence if evidence is not None else load_verified_restore_evidence(root)
        source_before = validate_source_state(
            source_before_raw
            if source_before_raw is not None
            else inspect_database(root, include_counts=True),
            verified,
        )
        rehearsal_before = validate_rehearsal_state(
            rehearsal_before_raw
            if rehearsal_before_raw is not None
            else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
            verified,
        )
    except MigrationTestDatabaseError as exc:
        raise InitialRevisionError(str(exc)) from exc
    migration_before = validate_revision_workspace_state(
        migration_before_raw
        if migration_before_raw is not None
        else inspect_named_database(root, MIGRATION_TEST_DATABASE),
        require_existing_placeholder=True,
    )

    created_paths: list[Path] = []
    review_artifact_paths: list[Path] = []
    try:
        command_output = run_revision_command(
            root, timeout=timeout, run_process=run_process
        )
        after_files = existing_revision_files(versions_dir)
        if len(after_files) != 1:
            raise InitialRevisionError(
                f"Alembic must create exactly one revision file, actual={len(after_files)}"
            )
        revision_path = after_files[0]
        created_paths.append(revision_path)
        if revision_path.name != REVISION_FILENAME:
            raise InitialRevisionError(
                f"unexpected revision filename: expected={REVISION_FILENAME}, actual={revision_path.name}"
            )
        automated_review = review_revision(root, revision_path)

        try:
            source_after = validate_source_state(
                source_after_raw
                if source_after_raw is not None
                else inspect_database(root, include_counts=True),
                verified,
            )
            rehearsal_after = validate_rehearsal_state(
                rehearsal_after_raw
                if rehearsal_after_raw is not None
                else inspect_named_database(root, RESTORE_REHEARSAL_DATABASE),
                verified,
            )
        except MigrationTestDatabaseError as exc:
            raise InitialRevisionError(str(exc)) from exc
        migration_after = validate_revision_workspace_state(
            migration_after_raw
            if migration_after_raw is not None
            else inspect_named_database(root, MIGRATION_TEST_DATABASE),
            require_existing_placeholder=True,
        )
        if source_before != source_after:
            raise InitialRevisionError("source DB changed during revision generation")
        if rehearsal_before != rehearsal_after:
            raise InitialRevisionError("restore rehearsal DB changed during revision generation")
        if migration_before != migration_after:
            raise InitialRevisionError("migration test DB changed during revision generation")

        revision_sha = sha256_file(revision_path)
        review_dir = ensure_under(root, root / REVIEW_DIRECTORY)
        review_path = ensure_under(root, review_dir / REVIEW_JSON_FILENAME)
        bundle_path = ensure_under(root, review_dir / REVIEW_BUNDLE_FILENAME)
        review_artifact_paths.extend([review_path, bundle_path])
        result = {
            "toolVersion": TOOL_VERSION,
            "result": "initial-alembic-revision-created-and-automatically-reviewed",
            "revisionGenerated": True,
            "revisionId": REVISION_ID,
            "revisionMessage": REVISION_MESSAGE,
            "revisionRelativePath": revision_path.relative_to(root).as_posix(),
            "revisionSha256": revision_sha,
            "databaseTarget": MIGRATION_TEST_DATABASE,
            "databaseUrlOverriddenInProcess": True,
            "environmentFileChanged": False,
            "sourceBefore": source_before,
            "sourceAfter": source_after,
            "rehearsalBefore": rehearsal_before,
            "rehearsalAfter": rehearsal_after,
            "migrationBefore": migration_before,
            "migrationAfter": migration_after,
            "automatedReview": automated_review,
            "alembicCommandOutput": command_output,
            "upgradeExecuted": False,
            "downgradeExecuted": False,
            "stampExecuted": False,
            "databaseCreateDropRestoreExecuted": False,
            "existingAlembicVersionPlaceholderReused": True,
            "alembicVersionRowsWritten": False,
            "manualReviewRequiredBeforeUpgrade": True,
            "reviewJsonRelativePath": review_path.relative_to(root).as_posix(),
            "reviewBundleRelativePath": bundle_path.relative_to(root).as_posix(),
        }
        # Keep the bundle hash outside the report embedded in the bundle to avoid
        # a self-referential checksum cycle. The console result still reports it.
        write_json_atomic(review_path, result)
        create_review_bundle(root, revision_path, review_path, bundle_path)
        result["reviewBundleSha256"] = sha256_file(bundle_path)
        return result
    except Exception:
        for path in [*created_paths, *review_artifact_paths]:
            if path.is_file():
                path.unlink()
            partial = path.with_name(f".{path.name}.partial")
            if partial.is_file():
                partial.unlink()
        pycache = versions_dir / "__pycache__"
        if pycache.exists():
            shutil.rmtree(pycache, ignore_errors=True)
        raise


def render_workspace_inspection(state: dict[str, Any]) -> str:
    return "\n".join(
        [
            "PostgreSQL Alembic revision workspace inspection (read-only)",
            f"- database: {state.get('database')}",
            f"- public tables: {state.get('publicTableCount')} / {state.get('publicTables')}",
            f"- total rows: {state.get('totalRows')}",
            f"- alembic_version exists: {state.get('alembicVersionTableExists')}",
            f"- recorded revisions: {state.get('alembicCurrentRevisions') or []}",
            f"- classification: {state.get('revisionWorkspaceClassification')}",
            f"- v297 recovery ready: {state.get('safeRecoveryPlaceholder')}",
            "- no DB schema/data mutation was executed.",
        ]
    )


def render_plan() -> str:
    return "\n".join(
        [
            "PostgreSQL first Alembic revision generation — execution guard",
            f"- source DB (read-only): {SOURCE_DATABASE}",
            f"- restored rehearsal DB (read-only): {RESTORE_REHEARSAL_DATABASE}",
            f"- migration DB recovery workspace: {MIGRATION_TEST_DATABASE}",
            f"- revision ID: {REVISION_ID}",
            f"- expected file: backend/alembic/versions/{REVISION_FILENAME}",
            "- backend/.env is not edited; DATABASE_URL is overridden only for the child process",
            "- requires exactly one pre-existing empty alembic_version placeholder and reuses it",
            "- creates one revision file and one local schema-only review bundle",
            "- does not drop/create DBs, apply revisions, write version rows, or mutate application tables",
            "- approved command: python tools/create_postgres_initial_alembic_revision.py --execute",
        ]
    )


def render_success(result: dict[str, Any]) -> str:
    review = result["automatedReview"]
    upgrade_counts = review["upgradeOperationCounts"]
    downgrade_counts = review["downgradeOperationCounts"]
    return "\n".join(
        [
            "PostgreSQL first Alembic revision generation and automated review",
            "One revision file was generated against the isolated empty DB; no migration was applied.",
            "",
            f"- result: {result['result']}",
            f"- revision ID: {result['revisionId']}",
            f"- revision file: {result['revisionRelativePath']}",
            f"- revision SHA-256: {result['revisionSha256']}",
            f"- target DB used for autogenerate: {result['databaseTarget']}",
            f"- upgrade create_table: {upgrade_counts.get('create_table', 0)}",
            f"- upgrade create_index: {upgrade_counts.get('create_index', 0)}",
            f"- downgrade drop_table: {downgrade_counts.get('drop_table', 0)}",
            f"- reviewed tables/columns: {review['tableCount']} / {review['columnCount']}",
            f"- migration DB tables before/after: {result['migrationBefore'].get('publicTableCount')} / {result['migrationAfter'].get('publicTableCount')}",
            f"- migration workspace before/after: {result['migrationBefore'].get('revisionWorkspaceClassification')} / {result['migrationAfter'].get('revisionWorkspaceClassification')}",
            f"- migration DB alembic_version before/after: {result['migrationBefore'].get('alembicVersionTableExists')} / {result['migrationAfter'].get('alembicVersionTableExists')}",
            "- alembic_version rows before/after: 0 / 0",
            f"- source tables/rows preserved: {result['sourceBefore'].get('publicTableCount')}/{result['sourceBefore'].get('totalRows')}",
            f"- rehearsal tables/rows preserved: {result['rehearsalBefore'].get('publicTableCount')}/{result['rehearsalBefore'].get('totalRows')}",
            f"- review bundle: {result['reviewBundleRelativePath']}",
            f"- review bundle SHA-256: {result['reviewBundleSha256']}",
            "- manual revision review is still required before any upgrade/downgrade/stamp.",
            "- do not commit the generated revision yet; upload only the review bundle in the next chat step.",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Generate and automatically review the approved first revision",
    )
    parser.add_argument(
        "--inspect-workspace",
        action="store_true",
        help="Read only the isolated migration DB and report whether v297 recovery is safe",
    )
    parser.add_argument("--json", action="store_true", help="Print success result as JSON")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Alembic child-process timeout in seconds",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    if args.inspect_workspace:
        try:
            state = validate_revision_workspace_state(
                inspect_named_database(root, MIGRATION_TEST_DATABASE),
                require_existing_placeholder=False,
            )
        except InitialRevisionError as exc:
            print("PostgreSQL Alembic revision workspace inspection (read-only)")
            print("- result: blocked")
            print(f"- reason: {exc}")
            print("- no DB schema/data mutation was executed.")
            return 1
        print(render_workspace_inspection(state))
        return 0 if state.get("safeRecoveryPlaceholder") is True else 1

    if not args.execute:
        print(render_plan())
        print("\nBLOCKED: --execute is required; no revision file or DB action was attempted.")
        return 2

    try:
        result = execute_generation(root, timeout=args.timeout)
    except InitialRevisionError as exc:
        print("PostgreSQL first Alembic revision generation and automated review")
        print("- result: blocked-or-failed")
        print(f"- reason: {exc}")
        print("- no upgrade, downgrade, stamp, DB create/drop/restore, or automatic retry was attempted.")
        return 1
    except Exception as exc:  # pragma: no cover - environment dependent
        print("PostgreSQL first Alembic revision generation and automated review")
        print("- result: unexpected-error")
        print(f"- reason: {type(exc).__name__}: {exc}")
        print("- no upgrade, downgrade, stamp, DB create/drop/restore, or automatic retry was attempted.")
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_success(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

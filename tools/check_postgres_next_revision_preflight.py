#!/usr/bin/env python3
"""Decide whether a next Alembic revision is needed without generating one.

The v306 preflight is read-only. It verifies the completed v305 baseline, the
single-head revision graph, the approved SQLAlchemy model source snapshot, the
existing canonical schema-equivalence checker, and Alembic's metadata diff API.

It does **not** call ``alembic revision``, ``--autogenerate``, ``upgrade``,
``downgrade``, or ``stamp``. The live metadata comparison runs inside a
PostgreSQL read-only transaction with an SQL statement guard that only permits
catalog/read statements.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable

from check_postgres_backup_restore_preflight import SOURCE_DATABASE
from check_postgres_baseline_completion_state import (
    EXPECTED_REVISION_FILE,
    SUCCESS_RESULT as BASELINE_COMPLETION_RESULT,
    inspect_completion_state,
)
from check_postgres_runtime_readonly_state import load_backend_objects, to_sync_url
from check_postgres_schema_equivalence import collect as collect_schema_equivalence
from upgrade_postgres_migration_test_database import REVISION_ID, REVISION_SHA256

TOOL_VERSION = "v306.postgres-next-revision-readonly-preflight"
NO_REVISION_RESULT = "next-revision-not-required-current-schema-equivalent"
REVIEW_RESULT = "next-revision-review-required-schema-differences-detected"
EXPECTED_HEADS = [REVISION_ID]
EXPECTED_BASES = [REVISION_ID]
EXPECTED_MODEL_SOURCE_SHA256 = {
    "backend/alembic/env.py": "3262c376e9a75763528008c53ee5d4c9efb0c8da2068a684aee735b4b638c434",
    "backend/app/db/base.py": "987edfd9dfe38b2c49492c7d1a4e774015d16b72e2281b018e4160be6b47d560",
    "backend/app/models/__init__.py": "9d813e5241210bdddf1bfadf0e3e87c969e4b3418001271a8c33d53d0c7da85c",
    "backend/app/models/admin.py": "651e478a4d9fcd7f388232afe7c29480471c943e62a457a7ae5b2aca1b23ad5d",
    "backend/app/models/boss.py": "e32ef12911691b5dcabea6979e02116da2b441239a76fda249ed8dd04383c854",
    "backend/app/models/character.py": "a3174d45356aa4606bc179424c35c78901ca49aca9c2a5b3ad0647f530ac770a",
    "backend/app/models/enhancement.py": "9ce2fa7b33db142a7ea48108ead35dbd4242bb6e0b7335b2b0c96f5d6ceb740d",
    "backend/app/models/field.py": "8229cbbdf3ce0bc6ac14c3c399e026ec257c52a9bd6f3981ac4cdf09e0fddd8c",
    "backend/app/models/item.py": "845d5eb41a63ba847c163f97a5b6b6d572d0fcb09be21badb5234acf666d6b75",
    "backend/app/models/mailbox.py": "9f5c0a7a45b9f103de037103fd49fad3ee917b8e34bfc6feb2e98885b8c876c6",
    "backend/app/models/mixins.py": "7df4776b946244b605961b443dacb1775effb3cf14d8fdc7b814620535bce92e",
    "backend/app/models/skill.py": "63933a1c7feac23513ee431ef38e444fa03e62ebdc4b5c7f3d8bf4a58535a83f",
    "backend/app/models/user.py": "2963c256b911266dbd980baabccd3ea2cc881c362376f829433478d62664c938",
}


class NextRevisionPreflightError(RuntimeError):
    """Raised when v306 cannot safely classify the next-revision state."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise NextRevisionPreflightError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_model_source_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative_path in EXPECTED_MODEL_SOURCE_SHA256:
        path = root / relative_path
        if not path.is_file():
            raise NextRevisionPreflightError(
                f"approved model source file is missing: {relative_path}"
            )
        result[relative_path] = sha256_file(path)
    return result


def collect_revision_graph(root: Path) -> dict[str, Any]:
    """Read the local Alembic script graph without opening a DB connection."""
    try:
        from alembic.config import Config  # noqa: PLC0415
        from alembic.script import ScriptDirectory  # noqa: PLC0415

        backend = root / "backend"
        config = Config(str(backend / "alembic.ini"))
        config.set_main_option("script_location", str(backend / "alembic"))
        script = ScriptDirectory.from_config(config)
        revisions = list(script.walk_revisions(base="base", head="heads"))
        return {
            "heads": sorted(script.get_heads()),
            "bases": sorted(script.get_bases()),
            "currentHead": script.get_current_head(),
            "revisionIds": sorted(item.revision for item in revisions),
            "revisionFiles": sorted(
                Path(item.path).resolve().relative_to(root.resolve()).as_posix()
                for item in revisions
                if item.path
            ),
        }
    except Exception as exc:
        raise NextRevisionPreflightError(
            f"Alembic revision graph inspection failed: {type(exc).__name__}: {exc}"
        ) from exc


def _first_sql_keyword(statement: str) -> str:
    text = statement.lstrip()
    while text.startswith("/*"):
        end = text.find("*/")
        if end < 0:
            break
        text = text[end + 2 :].lstrip()
    match = re.match(r"([A-Za-z]+)", text)
    return match.group(1).upper() if match else ""


def _read_only_sql_guard(
    _conn: Any,
    _cursor: Any,
    statement: str,
    _parameters: Any,
    _context: Any,
    _executemany: bool,
) -> None:
    keyword = _first_sql_keyword(statement)
    if keyword not in {"SELECT", "WITH", "SHOW", "SET"}:
        raise NextRevisionPreflightError(
            f"blocked non-read-only SQL during metadata comparison: {keyword or 'unknown'}"
        )


def _flatten_diffs(items: Iterable[Any]) -> list[tuple[Any, ...]]:
    flattened: list[tuple[Any, ...]] = []
    for item in items:
        if isinstance(item, list):
            flattened.extend(_flatten_diffs(item))
        elif isinstance(item, tuple):
            flattened.append(item)
        else:
            flattened.append(("unknown", item))
    return flattened


def _object_name(value: Any) -> str | None:
    name = getattr(value, "name", None)
    return str(name) if name is not None else None


def serialize_diff(item: tuple[Any, ...]) -> dict[str, Any]:
    operation = str(item[0]) if item else "unknown"
    schema: str | None = None
    table: str | None = None
    column: str | None = None
    object_name: str | None = None

    if operation in {"add_table", "remove_table"} and len(item) > 1:
        table_obj = item[1]
        table = _object_name(table_obj)
        schema = getattr(table_obj, "schema", None)
    elif operation in {"add_column", "remove_column"} and len(item) > 3:
        schema = item[1]
        table = str(item[2])
        column = _object_name(item[3])
    elif operation.startswith("modify_") and len(item) > 3:
        schema = item[1]
        table = str(item[2])
        column = str(item[3])
    elif operation in {
        "add_index",
        "remove_index",
        "add_constraint",
        "remove_constraint",
        "add_fk",
        "remove_fk",
    } and len(item) > 1:
        obj = item[1]
        object_name = _object_name(obj)
        table_obj = getattr(obj, "table", None)
        if table_obj is not None:
            table = _object_name(table_obj)
            schema = getattr(table_obj, "schema", None)

    return {
        "operation": operation,
        "schema": str(schema) if schema else "public",
        "table": table,
        "column": column,
        "objectName": object_name,
    }


def _expected_sequence_owners(metadata: Any) -> list[dict[str, str]]:
    from sqlalchemy import Integer  # noqa: PLC0415

    result: list[dict[str, str]] = []
    for table in metadata.sorted_tables:
        for column in table.primary_key.columns:
            if isinstance(column.type, Integer) and column.autoincrement is not False:
                result.append({"table": table.name, "column": column.name})
    return sorted(result, key=lambda item: (item["table"], item["column"]))


def _collect_sequence_inventory(connection: Any) -> list[dict[str, Any]]:
    from sqlalchemy import text  # noqa: PLC0415

    rows = connection.execute(
        text(
            """
            SELECT
                seq_ns.nspname AS sequence_schema,
                seq.relname AS sequence_name,
                tbl_ns.nspname AS table_schema,
                tbl.relname AS table_name,
                attr.attname AS column_name,
                dep.deptype AS dependency_type
            FROM pg_catalog.pg_class AS seq
            JOIN pg_catalog.pg_namespace AS seq_ns
              ON seq_ns.oid = seq.relnamespace
            LEFT JOIN pg_catalog.pg_depend AS dep
              ON dep.objid = seq.oid
             AND dep.classid = 'pg_catalog.pg_class'::regclass
             AND dep.refclassid = 'pg_catalog.pg_class'::regclass
             AND dep.deptype IN ('a', 'i')
            LEFT JOIN pg_catalog.pg_class AS tbl
              ON tbl.oid = dep.refobjid
            LEFT JOIN pg_catalog.pg_namespace AS tbl_ns
              ON tbl_ns.oid = tbl.relnamespace
            LEFT JOIN pg_catalog.pg_attribute AS attr
              ON attr.attrelid = tbl.oid
             AND attr.attnum = dep.refobjsubid
            WHERE seq.relkind = 'S'
              AND seq_ns.nspname = 'public'
            ORDER BY seq.relname, tbl.relname, attr.attname
            """
        )
    ).mappings()
    return [dict(row) for row in rows]


def collect_autogenerate_comparison(root: Path) -> dict[str, Any]:
    """Use Alembic compare_metadata in a forced PostgreSQL read-only transaction."""
    try:
        from alembic.autogenerate import compare_metadata  # noqa: PLC0415
        from alembic.migration import MigrationContext  # noqa: PLC0415
        from sqlalchemy import create_engine, event, text  # noqa: PLC0415
        from sqlalchemy.engine import make_url  # noqa: PLC0415
        from sqlalchemy.pool import NullPool  # noqa: PLC0415

        settings, Base = load_backend_objects(root)
        source_url = make_url(to_sync_url(settings.database_url))
        _require(
            source_url.database == SOURCE_DATABASE,
            f"configured database must be exact source {SOURCE_DATABASE}",
        )
        engine = create_engine(source_url, poolclass=NullPool, future=True)
        event.listen(engine, "before_cursor_execute", _read_only_sql_guard)
        try:
            with engine.connect() as connection:
                transaction = connection.begin()
                try:
                    connection.exec_driver_sql("SET TRANSACTION READ ONLY")
                    observed_database = str(
                        connection.execute(text("SELECT current_database()"))
                        .scalar_one()
                    )
                    _require(
                        observed_database == SOURCE_DATABASE,
                        f"connected database differs from exact source {SOURCE_DATABASE}",
                    )
                    context = MigrationContext.configure(
                        connection=connection,
                        opts={
                            "target_metadata": Base.metadata,
                            "compare_type": True,
                            "compare_server_default": True,
                            "include_schemas": False,
                        },
                    )
                    raw_diffs = compare_metadata(context, Base.metadata)
                    serialized = [
                        serialize_diff(item) for item in _flatten_diffs(raw_diffs)
                    ]
                    operation_counts = dict(
                        sorted(Counter(item["operation"] for item in serialized).items())
                    )
                    sequences = _collect_sequence_inventory(connection)
                    expected_owners = _expected_sequence_owners(Base.metadata)
                    actual_owners = sorted(
                        {
                            (str(item["table_name"]), str(item["column_name"]))
                            for item in sequences
                            if item.get("table_schema") == "public"
                            and item.get("table_name")
                            and item.get("column_name")
                        }
                    )
                    expected_owner_pairs = sorted(
                        (item["table"], item["column"]) for item in expected_owners
                    )
                    return {
                        "readOnlyTransaction": True,
                        "sqlWriteGuard": True,
                        "database": observed_database,
                        "metadataTableCount": len(Base.metadata.tables),
                        "compareType": True,
                        "compareServerDefault": True,
                        "candidateOperationCount": len(serialized),
                        "operationCounts": operation_counts,
                        "operations": serialized,
                        "sequenceCount": len(sequences),
                        "sequenceOwners": [
                            {"table": table, "column": column}
                            for table, column in actual_owners
                        ],
                        "expectedSequenceOwners": expected_owners,
                        "sequenceOwnershipMatches": actual_owners
                        == expected_owner_pairs,
                        "unownedSequences": sorted(
                            str(item["sequence_name"])
                            for item in sequences
                            if not item.get("table_name")
                        ),
                    }
                finally:
                    transaction.rollback()
        finally:
            event.remove(engine, "before_cursor_execute", _read_only_sql_guard)
            engine.dispose()
    except NextRevisionPreflightError:
        raise
    except Exception as exc:
        raise NextRevisionPreflightError(
            f"read-only Alembic metadata comparison failed: {type(exc).__name__}: {exc}"
        ) from exc


def inspect_next_revision_preflight(
    root: Path,
    *,
    completion_state: dict[str, Any] | None = None,
    graph_state: dict[str, Any] | None = None,
    model_source_hashes: dict[str, str] | None = None,
    schema_equivalence: dict[str, Any] | None = None,
    autogenerate_comparison: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the v306 next-revision decision without generating a revision."""
    root = root.resolve()
    completion = completion_state or inspect_completion_state(root)
    graph = graph_state or collect_revision_graph(root)
    hashes = model_source_hashes or collect_model_source_hashes(root)
    equivalence = schema_equivalence or collect_schema_equivalence(root)
    comparison = autogenerate_comparison or collect_autogenerate_comparison(root)

    _require(
        completion.get("result") == BASELINE_COMPLETION_RESULT,
        "v305 baseline completion state is not verified",
    )
    _require(completion.get("readOnly") is True, "v305 completion state is not read-only")
    _require(
        completion.get("sourceCurrentRevision") == [REVISION_ID],
        "source current revision is not the reviewed baseline",
    )
    _require(
        completion.get("revisionSha256") == REVISION_SHA256,
        "reviewed baseline revision SHA-256 changed",
    )
    _require(
        completion.get("revisionFiles") == [EXPECTED_REVISION_FILE],
        "v305 revision file set changed",
    )

    _require(graph.get("heads") == EXPECTED_HEADS, "Alembic graph is not single-head")
    _require(graph.get("bases") == EXPECTED_BASES, "Alembic graph base changed")
    _require(graph.get("currentHead") == REVISION_ID, "Alembic graph head changed")
    _require(
        graph.get("revisionIds") == [REVISION_ID],
        "Alembic graph contains an unreviewed revision",
    )
    _require(
        graph.get("revisionFiles") == [EXPECTED_REVISION_FILE],
        "Alembic graph revision file path changed",
    )

    _require(
        hashes == EXPECTED_MODEL_SOURCE_SHA256,
        "approved SQLAlchemy model/Alembic environment source snapshot changed",
    )

    _require(equivalence.get("readOnly") is True, "canonical schema checker is not read-only")
    _require(equivalence.get("connected") is True, "canonical schema checker could not connect")
    _require(
        equivalence.get("classification") == "structurally-equivalent"
        and equivalence.get("differenceCount") == 0,
        "canonical SQLAlchemy/PostgreSQL schema differences were detected",
    )
    _require(
        equivalence.get("modelTableCount") == 22
        and equivalence.get("databaseTableCount") == 22,
        "canonical schema table boundary is not 22/22",
    )

    _require(comparison.get("readOnlyTransaction") is True, "comparison was not read-only")
    _require(comparison.get("sqlWriteGuard") is True, "SQL write guard was not active")
    _require(
        comparison.get("database") == SOURCE_DATABASE,
        "metadata comparison target differs from exact source rpg_game",
    )
    _require(
        comparison.get("metadataTableCount") == 22,
        "Alembic target metadata does not contain exactly 22 application tables",
    )
    _require(comparison.get("compareType") is True, "type comparison was disabled")
    _require(
        comparison.get("compareServerDefault") is True,
        "server-default comparison was disabled",
    )
    _require(
        comparison.get("sequenceOwnershipMatches") is True,
        "PostgreSQL sequence ownership differs from integer PK metadata expectations",
    )
    _require(
        not comparison.get("unownedSequences"),
        "unowned public PostgreSQL sequences require review",
    )

    candidate_count = int(comparison.get("candidateOperationCount", -1))
    _require(candidate_count >= 0, "invalid Alembic candidate operation count")
    needs_revision = candidate_count > 0
    result = REVIEW_RESULT if needs_revision else NO_REVISION_RESULT

    return {
        "toolVersion": TOOL_VERSION,
        "result": result,
        "readOnly": True,
        "mutationExecuted": False,
        "revisionGenerated": False,
        "autogenerateCommandExecuted": False,
        "upgradeExecuted": False,
        "downgradeExecuted": False,
        "stampExecuted": False,
        "baselineCompletionResult": completion["result"],
        "sourceDatabase": SOURCE_DATABASE,
        "sourceCurrentRevision": completion["sourceCurrentRevision"],
        "revisionId": REVISION_ID,
        "revisionSha256": REVISION_SHA256,
        "revisionGraph": graph,
        "modelSourceSnapshotMatches": True,
        "modelSourceFileCount": len(hashes),
        "canonicalSchemaClassification": equivalence["classification"],
        "canonicalSchemaDifferenceCount": equivalence["differenceCount"],
        "metadataTableCount": comparison["metadataTableCount"],
        "candidateOperationCount": candidate_count,
        "operationCounts": comparison.get("operationCounts", {}),
        "candidateOperations": comparison.get("operations", []),
        "compareType": comparison["compareType"],
        "compareServerDefault": comparison["compareServerDefault"],
        "sequenceCount": comparison.get("sequenceCount"),
        "sequenceOwnershipMatches": comparison["sequenceOwnershipMatches"],
        "unownedSequences": comparison.get("unownedSequences", []),
        "nextRevisionRequired": needs_revision,
        "nextRevisionApproved": False,
        "autogenerateApproved": False,
        "upgradeApproved": False,
        "downgradeApproved": False,
        "nextSafeStage": (
            "keep-single-baseline-no-new-revision"
            if not needs_revision
            else "separate-schema-change-intent-review"
        ),
    }


def render_text(result: dict[str, Any]) -> str:
    lines = [
        "PostgreSQL next Alembic revision preflight (read-only)",
        "No revision generation, autogenerate command, stamp, upgrade, downgrade, DB create/drop/restore, or row write was executed.",
        "",
        f"- baseline completion: {result['baselineCompletionResult']}",
        f"- exact source DB: {result['sourceDatabase']}",
        f"- source current revision: {result['sourceCurrentRevision']}",
        f"- Alembic graph heads/bases: {result['revisionGraph']['heads']}/{result['revisionGraph']['bases']}",
        f"- reviewed revision: {result['revisionId']}",
        f"- revision SHA-256: {result['revisionSha256']}",
        f"- approved model source snapshot: {'matched' if result['modelSourceSnapshotMatches'] else 'changed'} / {result['modelSourceFileCount']} files",
        f"- SQLAlchemy metadata tables: {result['metadataTableCount']}",
        f"- canonical schema: {result['canonicalSchemaClassification']} / differences={result['canonicalSchemaDifferenceCount']}",
        f"- Alembic compare type/server default: {result['compareType']}/{result['compareServerDefault']}",
        f"- PostgreSQL sequences: {result['sequenceCount']} / ownership matches={result['sequenceOwnershipMatches']}",
        f"- Alembic candidate operations: {result['candidateOperationCount']}",
    ]
    if result["operationCounts"]:
        lines.append(f"- candidate operation categories: {result['operationCounts']}")
    for item in result["candidateOperations"]:
        lines.append(
            "    "
            f"[{item['operation']}] table={item.get('table')} "
            f"column={item.get('column')} object={item.get('objectName')}"
        )
    lines.extend(
        [
            f"- next revision required: {'yes' if result['nextRevisionRequired'] else 'no'}",
            "- next revision/autogenerate/upgrade/downgrade approved: no",
            f"- result: {result['result']}",
            f"- next safe stage: {result['nextSafeStage']}",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return 1 when safety checks fail or candidate migration operations exist",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        result = inspect_next_revision_preflight(root)
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render_text(result))
        return 1 if args.strict and result["nextRevisionRequired"] else 0
    except Exception as exc:
        payload = {
            "toolVersion": TOOL_VERSION,
            "result": "blocked-or-failed",
            "readOnly": True,
            "mutationExecuted": False,
            "reason": f"{type(exc).__name__}: {exc}",
        }
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("PostgreSQL next Alembic revision preflight (read-only)")
            print("- result: blocked-or-failed")
            print(f"- reason: {payload['reason']}")
            print("- no revision generation, autogenerate command, stamp, upgrade, downgrade, DB create/drop/restore, or row write was executed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

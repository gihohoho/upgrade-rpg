#!/usr/bin/env python3
"""Smoke checks for v288 read-only PostgreSQL schema equivalence preflight."""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_postgres_schema_equivalence.py"
DOC = ROOT / "docs/current/POSTGRES_SCHEMA_EQUIVALENCE_CHECK.md"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def main() -> int:
    for path in (TOOL, DOC):
        if not path.exists():
            return fail(f"missing file: {path.relative_to(ROOT).as_posix()}")

    source = TOOL.read_text(encoding="utf-8")
    ast.parse(source, filename=str(TOOL))

    sys.path.insert(0, str(ROOT / "tools"))
    from check_postgres_schema_equivalence import normalized_type  # noqa: PLC0415
    from sqlalchemy import Float  # noqa: PLC0415
    from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, REAL  # noqa: PLC0415

    if normalized_type(Float()) != "DOUBLE PRECISION":
        return fail("PostgreSQL FLOAT without precision must normalize to DOUBLE PRECISION")
    if normalized_type(DOUBLE_PRECISION()) != "DOUBLE PRECISION":
        return fail("reflected DOUBLE PRECISION normalization is incorrect")
    if normalized_type(Float(24)) != normalized_type(REAL()):
        return fail("FLOAT(24) must normalize to REAL")
    if normalized_type(Float(25)) != normalized_type(DOUBLE_PRECISION()):
        return fail("FLOAT(25) must normalize to DOUBLE PRECISION")
    for marker in (
        '"readOnly": True',
        '"schemaChanged": False',
        'structurally-equivalent',
        'review-required',
        'inspector.get_columns',
        'inspector.get_foreign_keys',
        'inspector.get_unique_constraints',
        'inspector.get_indexes',
        'inspector.get_check_constraints',
        'postgresql-float-aliases.v1',
        'FLOAT\\((\\d+)\\)',
        '"--skip-database"',
    ):
        if marker not in source:
            return fail(f"schema checker missing marker: {marker}")

    for forbidden in (
        "CREATE TABLE",
        "ALTER TABLE",
        "DROP TABLE",
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
        '"upgrade", "head"',
        '"stamp", "head"',
        '"revision", "--autogenerate"',
    ):
        if forbidden in source:
            return fail(f"schema checker contains mutation marker: {forbidden}")

    run = subprocess.run(
        [sys.executable, str(TOOL), "--json", "--skip-database"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    if run.returncode != 0:
        sys.stdout.write(run.stdout)
        sys.stderr.write(run.stderr)
        return fail("schema checker must return zero without --strict")
    payload = json.loads(run.stdout)
    if payload.get("readOnly") is not True or payload.get("schemaChanged") is not False:
        return fail("schema checker read-only flags are incorrect")
    if payload.get("classification") not in {
        "structurally-equivalent",
        "review-required",
        "connection-failed",
        "skipped",
    }:
        return fail("schema checker classification is invalid")

    doc_text = DOC.read_text(encoding="utf-8")
    for marker in (
        "PostgreSQL schema 동등성 읽기 전용 점검 — v289",
        "python tools/check_postgres_schema_equivalence.py",
        "structurally-equivalent",
        "review-required",
        "stamp head",
    ):
        if marker not in doc_text:
            return fail(f"schema equivalence doc missing: {marker}")

    print("OK: PostgreSQL schema equivalence smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

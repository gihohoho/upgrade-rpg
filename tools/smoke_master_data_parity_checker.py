#!/usr/bin/env python3
"""Static smoke test for the v086 master-data parity checker.

Run from project root:

    python tools/smoke_master_data_parity_checker.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "backend" / "scripts" / "check_master_data_parity.py"
DOC = ROOT / "docs" / "MASTER_DATA_PARITY_CHECKER.md"

REQUIRED_SNIPPETS = [
    "Compare generated JS seed data with the FastAPI master-data API",
    "compare_counts",
    "compare_characters",
    "compare_skills",
    "compare_items",
    "compare_bosses",
    "compare_drop_tables",
    "--include-assets",
]


def main() -> int:
    missing_files = [str(path.relative_to(ROOT)) for path in [CHECKER, DOC] if not path.exists()]
    if missing_files:
        raise SystemExit(f"missing files: {missing_files}")

    text = CHECKER.read_text(encoding="utf-8")
    missing_snippets = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    if missing_snippets:
        raise SystemExit(f"missing snippets in checker: {missing_snippets}")

    doc_text = DOC.read_text(encoding="utf-8")
    for phrase in ["Master Data Parity Checker", "python scripts/check_master_data_parity.py"]:
        if phrase not in doc_text:
            raise SystemExit(f"missing documentation phrase: {phrase}")

    print("master-data parity checker smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Smoke test for seed import script structure.

Run from project root:

    python tools/smoke_seed_import_structure.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
SCRIPT = BACKEND / "scripts" / "setup_dev_db.py"


def main() -> int:
    if not SCRIPT.exists():
        print(f"Missing script: {SCRIPT}")
        return 1
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--dry-run"],
        cwd=BACKEND,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        return result.returncode
    if "characters" not in result.stdout or "drop_table_items" not in result.stdout:
        print(result.stdout)
        print("Dry-run output did not include expected counts.")
        return 1
    print("seed import structure smoke test passed")
    print(result.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

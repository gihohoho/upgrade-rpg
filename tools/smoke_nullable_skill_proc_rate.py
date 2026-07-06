#!/usr/bin/env python3
"""Static smoke test for v087 nullable skill procRate preservation.

Run from project root:

    python tools/smoke_nullable_skill_proc_rate.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETUP_SCRIPT = ROOT / "backend" / "scripts" / "setup_dev_db.py"
SKILL_MODEL = ROOT / "backend" / "app" / "models" / "skill.py"
SCHEMA_DRAFT = ROOT / "backend" / "sql" / "schema_draft.sql"
SKILLS_SEED = ROOT / "backend" / "seeds" / "generated" / "skills.json"
DOC = ROOT / "docs" / "MASTER_DATA_NULLABLE_FIELDS.md"


def load_setup_module():
    spec = importlib.util.spec_from_file_location("setup_dev_db_for_smoke", SETUP_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load setup_dev_db.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    for path in [SETUP_SCRIPT, SKILL_MODEL, SCHEMA_DRAFT, SKILLS_SEED, DOC]:
        if not path.exists():
            raise SystemExit(f"missing file: {path.relative_to(ROOT)}")

    model_text = SKILL_MODEL.read_text(encoding="utf-8")
    if "proc_rate: Mapped[float | None]" not in model_text or "nullable=True" not in model_text:
        raise SystemExit("skills.proc_rate must be nullable in SQLAlchemy model")

    schema_text = SCHEMA_DRAFT.read_text(encoding="utf-8")
    if "proc_rate NUMERIC(8,4) NOT NULL DEFAULT 0" in schema_text:
        raise SystemExit("schema draft still forces proc_rate to NOT NULL DEFAULT 0")

    setup_text = SETUP_SCRIPT.read_text(encoding="utf-8")
    if "as_nullable_decimal" not in setup_text:
        raise SystemExit("setup_dev_db.py must use as_nullable_decimal for nullable proc_rate")

    setup = load_setup_module()
    skills = json.loads(SKILLS_SEED.read_text(encoding="utf-8"))
    lightsabre = next((item for item in skills if item.get("id") == "lightsabre"), None)
    if lightsabre is None:
        raise SystemExit("lightsabre skill missing from generated seed")
    if lightsabre.get("baseProcRate") is not None:
        raise SystemExit("expected lightsabre.baseProcRate to be null in generated seed")

    rows = setup.build_skill_rows([lightsabre])
    if rows[0].get("proc_rate") is not None:
        raise SystemExit("build_skill_rows must preserve lightsabre proc_rate as None")

    print("nullable skill procRate smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

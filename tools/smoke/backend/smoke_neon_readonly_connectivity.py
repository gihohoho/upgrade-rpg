#!/usr/bin/env python3
"""Focused smoke for the sanitized Neon read-only connectivity contract."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_neon_readonly_connectivity.py"


def main() -> int:
    spec = importlib.util.spec_from_file_location("neon_readonly_checker", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    evidence = module._validate_evidence(module.EVIDENCE_FILE)
    assert evidence["result"] == module.RESULT
    assert evidence["nextSafeStage"] == module.NEXT_STAGE

    scheme_and_role = "postgresql" + "://" + "neondb_owner" + ":" + "safe-test-only" + "@"
    direct = module._parse_target(
        "direct",
        scheme_and_role + "ep-example.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require",
        pooled=False,
    )
    pooled = module._parse_target(
        "pooled",
        scheme_and_role + "ep-example-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require",
        pooled=True,
    )
    assert module._same_endpoint(direct, pooled)
    assert direct.password == pooled.password == "safe-test-only"
    assert direct.database == pooled.database == "neondb"
    print("OK: sanitized Neon read-only connectivity contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

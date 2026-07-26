#!/usr/bin/env python3
"""Focused static/unit smoke for the exact-SHA-gated Neon initializer."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/initialize_neon_database.py"


def load_tool():
    tools_dir = str(ROOT / "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    spec = importlib.util.spec_from_file_location("neon_initializer", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expect_guard_failure(module, **overrides: str) -> None:
    values = {
        "preparation_sha": "a" * 40,
        "target": module.EXPECTED_DATABASE,
        "backup_sha": module.EXPECTED_BACKUP_SHA256,
        "revision": module.EXPECTED_REVISION,
        "action": module.EXPECTED_ACTION,
    }
    values.update(overrides)
    try:
        module.require_exact_approval(**values)
    except module.NeonInitializationError:
        return
    raise AssertionError("mutated exact approval input was accepted")


def main() -> int:
    module = load_tool()
    plan = module.load_plan()
    assert plan["schemaVersion"] == module.PLAN_VERSION
    assert plan["executionGate"]["databaseInitializationApproved"] is True
    assert plan["executionGate"]["restoreExecuted"] is True
    assert plan["executionGate"]["stampExecuted"] is False
    assert plan["executionGate"]["stampRecoveryApproved"] is False

    command = module.build_restore_command()
    assert "--exit-on-error" in command
    assert "--single-transaction" in command
    assert "--no-owner" in command
    assert "--no-privileges" in command
    assert "--create" not in command
    assert "--clean" not in command
    assert not any("postgresql://" in item or "npg_" in item for item in command)

    psql = module.build_psql_readonly_command()
    assert "BEGIN TRANSACTION READ ONLY" in psql[-1]
    assert "ROLLBACK" in psql[-1]
    assert not any("postgresql://" in item or "npg_" in item for item in psql)

    stamp = module.build_stamp_command()
    assert stamp[-2:] == ["stamp", module.EXPECTED_REVISION]
    assert "upgrade" not in stamp and "downgrade" not in stamp

    original_git_output = module.git_output
    module.git_output = lambda *args: {
        ("branch", "--show-current"): "main",
        ("rev-parse", "HEAD"): "a" * 40,
        ("rev-parse", "--verify", "origin/main"): "a" * 40,
        ("status", "--porcelain"): "",
    }[args]
    try:
        module.require_exact_approval(
            preparation_sha="a" * 40,
            target=module.EXPECTED_DATABASE,
            backup_sha=module.EXPECTED_BACKUP_SHA256,
            revision=module.EXPECTED_REVISION,
            action=module.EXPECTED_ACTION,
        )
        expect_guard_failure(module, preparation_sha="A" * 40)
        expect_guard_failure(module, target="postgres")
        expect_guard_failure(module, backup_sha="b" * 64)
        expect_guard_failure(module, revision="head")
        expect_guard_failure(module, action="restore")
    finally:
        module.git_output = original_git_output

    original_application_signature = module.application_signature
    module.application_signature = lambda _signature: {
        "tableCount": len(module.EXPECTED_APP_TABLES),
        "rowCount": module.EXPECTED_APP_ROWS,
        "schemaDigest": module.EXPECTED_SCHEMA_DIGEST,
        "dataDigest": module.EXPECTED_DATA_DIGEST,
    }
    try:
        restored = {
            "publicTables": sorted(module.EXPECTED_APP_TABLES),
            "alembicRevisions": [],
            "tables": {name: {} for name in module.EXPECTED_APP_TABLES},
        }
        module.require_application_restore(restored, stamped=False)
        stamped = {
            "publicTables": sorted([*module.EXPECTED_APP_TABLES, "alembic_version"]),
            "alembicRevisions": [module.EXPECTED_REVISION],
            "tables": {
                **{name: {} for name in module.EXPECTED_APP_TABLES},
                "alembic_version": {"rowCount": 1},
            },
        }
        module.require_application_restore(stamped, stamped=True)
        stamped["alembicRevisions"] = ["wrong_revision"]
        try:
            module.require_application_restore(stamped, stamped=True)
        except module.NeonInitializationError:
            pass
        else:
            raise AssertionError("wrong final Alembic revision was accepted")
    finally:
        module.application_signature = original_application_signature

    print("Neon database initialization guard smoke")
    print("- exact SHA/target/backup/revision/action confirmations: enforced")
    print("- restore single transaction + no create/clean: enforced")
    print("- completed restore retry: forbidden; stamp-only recovery: gated")
    print("- exact stamp only; upgrade/downgrade absent: enforced")
    print("- final Alembic revision value: exact v295 enforced")
    print("- database connection or mutation attempted: no")
    print("- result: neon-database-initialization-guard-verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

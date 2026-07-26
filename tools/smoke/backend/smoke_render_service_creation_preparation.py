#!/usr/bin/env python3
"""Focused secret-safe smoke for Render service creation preparation."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/prepare_render_local_environment.py"


def load_tool():
    tools_dir = str(ROOT / "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    spec = importlib.util.spec_from_file_location("render_environment_preparer", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_tool()
    direct = module.ConnectionTarget(
        label="direct",
        host="ep-example.ap-southeast-1.aws.neon.tech",
        port=5432,
        database="neondb",
        user="neondb_owner",
        password="fake password:/?#[]@",
        pooled=False,
        sslmode="require",
    )
    values = {
        "NEON_DIRECT_DATABASE_URL": "stored-only",
        "NEON_POOLED_DATABASE_URL": "stored-only",
        **module.NON_SECRET_VALUES,
        "DATABASE_URL": module.build_asyncpg_url(direct),
        "JWT_SECRET_KEY": module.generate_secret(),
        "ADMIN_WRITE_DEV_KEY": module.generate_secret(),
    }
    summary = module.validate_render_values(values, direct)

    assert values["DATABASE_URL"].startswith("postgresql+asyncpg://")
    assert "sslmode=" not in values["DATABASE_URL"]
    assert "fake password" not in values["DATABASE_URL"]
    assert values["JWT_SECRET_KEY"] != values["ADMIN_WRITE_DEV_KEY"]
    assert len(values["JWT_SECRET_KEY"]) >= 43
    assert summary["actualValuesDisplayed"] is False
    assert summary["result"] == module.RESULT
    assert summary["nextSafeStage"] == module.NEXT_STAGE

    bad = dict(values)
    bad["DATABASE_URL"] += "?sslmode=require"
    try:
        module.validate_render_values(bad, direct)
    except module.RenderEnvironmentError:
        pass
    else:
        raise AssertionError("DATABASE_URL TLS query mutation was accepted")

    bad = dict(values)
    bad["ADMIN_WRITE_DEV_KEY"] = bad["JWT_SECRET_KEY"]
    try:
        module.validate_render_values(bad, direct)
    except module.RenderEnvironmentError:
        pass
    else:
        raise AssertionError("identical JWT/admin secrets were accepted")

    original_git_output = module.git_output
    module.git_output = lambda *args: {
        ("branch", "--show-current"): "main",
        ("status", "--porcelain"): "",
        ("rev-parse", "HEAD"): "a" * 40,
        ("rev-parse", "--verify", "origin/main"): "a" * 40,
    }[args]
    try:
        module.require_exact_execution_approval(
            preparation_sha="a" * 40,
            service=module.SERVICE_NAME,
            image=module.IMAGE_REFERENCE,
            action=module.EXECUTION_ACTION,
        )
        try:
            module.require_exact_execution_approval(
                preparation_sha="A" * 40,
                service=module.SERVICE_NAME,
                image=module.IMAGE_REFERENCE,
                action=module.EXECUTION_ACTION,
            )
        except module.RenderEnvironmentError:
            pass
        else:
            raise AssertionError("mutated exact SHA was accepted")
    finally:
        module.git_output = original_git_output

    print("Render service creation preparation smoke")
    print("- direct asyncpg URL encoding and query-free policy: enforced")
    print("- production JWT/admin strength and separation: enforced")
    print("- exact SHA/service/image/single-deploy approval guard: enforced")
    print("- actual secret or endpoint displayed: no")
    print("- Render resource or database mutation: no")
    print(f"- result: {module.RESULT}")
    print(f"- next safe stage: {module.NEXT_STAGE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

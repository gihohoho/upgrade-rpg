#!/usr/bin/env python3
"""Regression smoke for multiline create_async_engine(settings.database_url)."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "tools/check_postgres_deployment_runtime_readiness.py"
SESSION = ROOT / "backend/app/db/session.py"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_tool():  # type: ignore[no-untyped-def]
    tools_dir = str(ROOT / "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    spec = importlib.util.spec_from_file_location("v309_runtime_binding", TOOL)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load runtime readiness tool")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    tool = load_tool()
    actual = tool.inspect_runtime_sources(ROOT)
    if actual.get("databaseUrlFromSettings") is not True:
        return fail("actual multiline runtime engine binding was not detected")
    if actual.get("databaseUrlBindingInspection") != tool.RUNTIME_ENGINE_BINDING_INSPECTOR:
        return fail("AST binding inspector version marker is missing")

    multiline = """
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
)
"""
    keyword = "engine = create_async_engine(url=settings.database_url)"
    one_line = "engine = create_async_engine(settings.database_url)"
    literal = "engine = create_async_engine('postgresql+asyncpg://example/test')"
    wrong_setting = "engine = create_async_engine(settings.audit_database_url)"
    unrelated_safe_call = """
probe = create_async_engine(settings.database_url)
engine = create_async_engine('postgresql+asyncpg://example/unsafe')
"""

    for source in (multiline, keyword, one_line):
        if tool._call_uses_settings_database_url(source) is not True:
            return fail("approved settings.database_url binding was not detected")
    for source in (literal, wrong_setting, unrelated_safe_call):
        if tool._call_uses_settings_database_url(source) is not False:
            return fail("unsafe/non-runtime URL binding was incorrectly accepted")

    checker_source = TOOL.read_text(encoding="utf-8")
    brittle = '"create_async_engine(settings.database_url" in session_text'
    if brittle in checker_source:
        return fail("brittle single-line string binding check still exists")

    session_source = SESSION.read_text(encoding="utf-8")
    if "create_async_engine(\n" not in session_source:
        return fail("regression fixture must keep the multiline engine call")

    print("OK: runtime engine source-binding inspector smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

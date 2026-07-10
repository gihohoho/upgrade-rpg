from __future__ import annotations

import pathlib
import sys

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.11+ project
    print("[FAIL] Python 3.11+ is required for tomllib", file=sys.stderr)
    raise

ROOT = pathlib.Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "backend" / "pyproject.toml"

assert PYPROJECT.exists(), f"missing: {PYPROJECT}"
with PYPROJECT.open("rb") as fh:
    data = tomllib.load(fh)

build_system = data.get("build-system", {})
assert build_system.get("build-backend") == "setuptools.build_meta", build_system
assert "setuptools>=68" in build_system.get("requires", []), build_system

find_config = data.get("tool", {}).get("setuptools", {}).get("packages", {}).get("find", {})
assert find_config.get("where") == ["."], find_config
assert find_config.get("include") == ["app*"], find_config
for excluded in ("alembic*", "seeds*", "sql*", "tests*"):
    assert excluded in find_config.get("exclude", []), find_config

assert (ROOT / "backend" / "app" / "__init__.py").exists()
print("backend packaging contract smoke test passed")

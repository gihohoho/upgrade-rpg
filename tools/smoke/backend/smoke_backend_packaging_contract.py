from __future__ import annotations

import pathlib
import sys

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.11+ project
    print("[FAIL] Python 3.11+ is required for tomllib", file=sys.stderr)
    raise

ROOT = pathlib.Path(__file__).resolve().parents[3]
PYPROJECT = ROOT / "backend" / "pyproject.toml"
RUNTIME_INPUT = ROOT / "backend" / "requirements" / "runtime.in"
REQUIRED_EMAIL_DEPENDENCIES = (
    "email-validator==2.3.0",
    "dnspython==2.8.0",
)

assert PYPROJECT.exists(), f"missing: {PYPROJECT}"
with PYPROJECT.open("rb") as fh:
    data = tomllib.load(fh)

assert "email-validator==2.3.0" in data.get("project", {}).get("dependencies", []), data.get("project", {})
runtime_input = RUNTIME_INPUT.read_text(encoding="utf-8").splitlines()
assert "email-validator==2.3.0" in runtime_input, runtime_input

build_system = data.get("build-system", {})
assert build_system.get("build-backend") == "setuptools.build_meta", build_system
assert build_system.get("requires") == ["setuptools==80.10.2", "wheel==0.46.3"], build_system
for lock_name in (
    "pip-bootstrap.lock",
    "runtime-linux-amd64-py311.lock",
    "runtime-musllinux-amd64-py311.lock",
    "dev-linux-amd64-py311.lock",
):
    lock = ROOT / "backend" / "requirements" / lock_name
    assert lock.is_file(), f"missing dependency lock: {lock}"
    lock_text = lock.read_text(encoding="utf-8")
    assert "--hash=sha256:" in lock_text, lock
    if lock_name != "pip-bootstrap.lock":
        for dependency in REQUIRED_EMAIL_DEPENDENCIES:
            assert f"\n{dependency} " in lock_text, f"{lock_name} missing exact dependency: {dependency}"

find_config = data.get("tool", {}).get("setuptools", {}).get("packages", {}).get("find", {})
assert find_config.get("where") == ["."], find_config
assert find_config.get("include") == ["app*"], find_config
for excluded in ("alembic*", "seeds*", "sql*", "tests*"):
    assert excluded in find_config.get("exclude", []), find_config

assert (ROOT / "backend" / "app" / "__init__.py").exists()
print("backend packaging contract smoke test passed")

#!/usr/bin/env python3
"""Generate or statically check Linux/amd64 CPython 3.11 dependency locks."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


TARGET_PLATFORMS = ("manylinux_2_17_x86_64", "manylinux2014_x86_64", "any")
TARGET_ABIS = ("cp311", "abi3", "none")
LOCKS = {
    "pip-bootstrap": "pip-bootstrap.in",
    "runtime-linux-amd64-py311": "runtime.in",
    "dev-linux-amd64-py311": "dev.in",
}
PIN_RE = re.compile(r"^([A-Za-z0-9_.-]+)(?:\[[A-Za-z0-9_,.-]+\])?==([^\s;]+)$")
LOCK_PIN_RE = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s\\]+) \\$")
HASH_RE = re.compile(r"^    --hash=sha256:([0-9a-f]{64})$")


class LockError(RuntimeError):
    pass


def canonical_name(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def read_input_pins(path: Path, seen: set[Path] | None = None) -> dict[str, str]:
    seen = set() if seen is None else seen
    resolved = path.resolve()
    if resolved in seen:
        raise LockError(f"recursive requirement include: {path}")
    seen.add(resolved)
    pins: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r "):
            pins.update(read_input_pins(path.parent / line[3:].strip(), seen))
            continue
        match = PIN_RE.fullmatch(line)
        if match is None:
            raise LockError(f"input requirement must use exact == pin: {path}: {line}")
        name, version = canonical_name(match.group(1)), match.group(2)
        if name in pins and pins[name] != version:
            raise LockError(f"conflicting direct pin for {name}")
        pins[name] = version
    seen.remove(resolved)
    return pins


def parse_lock(path: Path) -> dict[str, tuple[str, str]]:
    if not path.is_file():
        raise LockError(f"lock file is missing: {path}")
    meaningful = [
        line.rstrip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(meaningful) % 2:
        raise LockError(f"lock entries must have a pin line and one hash line: {path}")
    entries: dict[str, tuple[str, str]] = {}
    for index in range(0, len(meaningful), 2):
        pin_match = LOCK_PIN_RE.fullmatch(meaningful[index])
        hash_match = HASH_RE.fullmatch(meaningful[index + 1])
        if pin_match is None or hash_match is None:
            raise LockError(f"invalid lock entry near line {index + 1}: {path}")
        name = canonical_name(pin_match.group(1))
        if name in entries:
            raise LockError(f"duplicate lock entry: {name}")
        entries[name] = (pin_match.group(2), hash_match.group(1))
    if not entries:
        raise LockError(f"lock file is empty: {path}")
    return entries


def check_locks(root: Path) -> dict[str, str]:
    requirements = root / "backend/requirements"
    parsed: dict[str, dict[str, tuple[str, str]]] = {}
    digests: dict[str, str] = {}
    for output_stem, input_name in LOCKS.items():
        input_path = requirements / input_name
        output_path = requirements / f"{output_stem}.lock"
        direct_pins = read_input_pins(input_path)
        entries = parse_lock(output_path)
        for name, version in direct_pins.items():
            if entries.get(name, (None,))[0] != version:
                raise LockError(f"direct pin is missing or changed in {output_path}: {name}=={version}")
        parsed[output_stem] = entries
        digests[output_path.relative_to(root).as_posix()] = hashlib.sha256(output_path.read_bytes()).hexdigest()

    if set(parsed["pip-bootstrap"]) != {"pip"}:
        raise LockError("pip bootstrap lock must contain only pip")
    runtime = parsed["runtime-linux-amd64-py311"]
    dev = parsed["dev-linux-amd64-py311"]
    for name, value in runtime.items():
        if dev.get(name) != value:
            raise LockError(f"dev lock must contain the exact runtime entry: {name}")
    return digests


def resolve_report(input_path: Path, report_path: Path) -> dict[str, object]:
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--dry-run",
        "--ignore-installed",
        "--only-binary=:all:",
    ]
    for platform in TARGET_PLATFORMS:
        command.extend(("--platform", platform))
    command.extend(("--python-version", "3.11", "--implementation", "cp"))
    for abi in TARGET_ABIS:
        command.extend(("--abi", abi))
    command.extend(("--report", str(report_path), "-r", str(input_path)))
    completed = subprocess.run(command, check=False)
    if completed.returncode != 0:
        raise LockError(f"pip resolution failed for {input_path}")
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    if payload.get("version") != "1" or not isinstance(payload.get("install"), list):
        raise LockError(f"unexpected pip report format for {input_path}")
    return payload


def render_lock(input_name: str, payload: dict[str, object]) -> str:
    entries: list[tuple[str, str, str]] = []
    for item in payload["install"]:  # type: ignore[index]
        if not isinstance(item, dict) or item.get("is_yanked") is True:
            raise LockError(f"invalid or yanked resolved package in {input_name}")
        metadata = item.get("metadata")
        download = item.get("download_info")
        if not isinstance(metadata, dict) or not isinstance(download, dict):
            raise LockError(f"pip report entry is incomplete for {input_name}")
        archive = download.get("archive_info")
        hashes = archive.get("hashes") if isinstance(archive, dict) else None
        sha256 = hashes.get("sha256") if isinstance(hashes, dict) else None
        name, version = metadata.get("name"), metadata.get("version")
        if not isinstance(name, str) or not isinstance(version, str):
            raise LockError(f"pip report metadata is incomplete for {input_name}")
        if not isinstance(sha256, str) or re.fullmatch(r"[0-9a-f]{64}", sha256) is None:
            raise LockError(f"resolved artifact has no SHA-256: {name}=={version}")
        entries.append((canonical_name(name), version, sha256))

    entries.sort()
    if len({name for name, _, _ in entries}) != len(entries):
        raise LockError(f"duplicate resolved distribution in {input_name}")
    lines = [
        "# Generated by tools/generate_backend_linux_dependency_locks.py --write",
        f"# Source: backend/requirements/{input_name}",
        "# Target: CPython 3.11 / linux/amd64 / binary wheels only",
        "# Do not edit by hand. Regenerate and review the complete diff.",
        "",
    ]
    for name, version, sha256 in entries:
        lines.extend((f"{name}=={version} \\", f"    --hash=sha256:{sha256}"))
    return "\n".join(lines) + "\n"


def write_locks(root: Path) -> None:
    requirements = root / "backend/requirements"
    with tempfile.TemporaryDirectory(prefix="upgrade-rpg-lock-") as temporary:
        report_dir = Path(temporary)
        for output_stem, input_name in LOCKS.items():
            payload = resolve_report(requirements / input_name, report_dir / f"{output_stem}.json")
            output = requirements / f"{output_stem}.lock"
            output.write_text(render_lock(input_name, payload), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="resolve from PyPI and rewrite locks")
    mode.add_argument("--check", action="store_true", help="check committed locks without network")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if args.write:
            write_locks(root)
        digests = check_locks(root)
    except (LockError, OSError, json.JSONDecodeError) as exc:
        print(f"backend dependency lock check failed: {exc}")
        return 1
    print("backend dependency locks verified")
    for path, digest in sorted(digests.items()):
        print(f"- {path}: sha256:{digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

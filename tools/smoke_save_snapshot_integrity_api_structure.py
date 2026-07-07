"""Static smoke test for save snapshot integrity metadata.

Run from the project root:

    python tools/smoke_save_snapshot_integrity_api_structure.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATTERNS = {
    "backend/app/schemas/game.py": [
        "SAVE_SLOT_KEY_PATTERN",
        "validate_slot_key",
        "max_length=80",
        "slotKey는 영문/숫자/점(.)/언더바(_)/하이픈(-)만 사용할 수 있습니다.",
    ],
    "backend/app/services/game_service.py": [
        "SAVE_SNAPSHOT_WARN_SIZE_BYTES",
        "stable_json_string",
        "_build_save_integrity",
        "snapshotSha256",
        "snapshotBytes",
        "saveVersion_mismatch",
        "snapshot_missing_player",
        "defaultSlot",
        "latestSlot",
    ],
    "backend/app/api/routes/game.py": [
        '"integrity": save_data.get("integrity")',
        '"integrity": saved.get("integrity")',
        '"defaultSlot": slots_data.get("defaultSlot")',
    ],
    "backend/scripts/check_save_snapshot_api.py": [
        "snapshotSha256",
        "integrity",
        "invalid_slot_url",
    ],
}


def main() -> int:
    failures: list[str] = []
    for relative_path, patterns in REQUIRED_PATTERNS.items():
        path = ROOT / relative_path
        if not path.exists():
            failures.append(f"missing file: {relative_path}")
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in patterns:
            if pattern not in text:
                failures.append(f"{relative_path}: missing pattern {pattern!r}")

    if failures:
        print("save snapshot integrity API structure smoke test failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("save snapshot integrity API structure smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

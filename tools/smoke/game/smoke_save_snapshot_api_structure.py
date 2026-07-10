"""Static smoke test for the save snapshot API structure.

Run from the project root:

    python tools/smoke/game/smoke_save_snapshot_api_structure.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

REQUIRED_PATTERNS = {
    "backend/app/models/user.py": [
        "class UserSaveSnapshot",
        "__tablename__ = \"user_save_snapshots\"",
        "snapshot_json",
        "summary_json",
        "uq_user_save_snapshot_slot",
    ],
    "backend/app/models/__init__.py": ["UserSaveSnapshot"],
    "backend/app/schemas/game.py": ["class GameSaveSnapshotRequest", "snapshot", "slot_key"],
    "backend/app/services/game_service.py": [
        "save_game_snapshot",
        "_serialize_save_snapshot",
        "_ensure_local_user",
        "UserSaveSnapshot",
    ],
    "backend/app/api/routes/game.py": [
        "GameSaveSnapshotRequest",
        "@router.get(\"/load\")",
        "@router.post(\"/save\")",
        "service.save_game_snapshot",
    ],
    "backend/scripts/setup_dev_db.py": ["UserSaveSnapshot"],
    "backend/sql/schema_draft.sql": ["CREATE TABLE user_save_snapshots"],
    "backend/scripts/check_save_snapshot_api.py": ["save snapshot API check passed"],
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
        print("save snapshot API structure smoke test failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("save snapshot API structure smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

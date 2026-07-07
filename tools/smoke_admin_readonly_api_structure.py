"""Static smoke test for admin read-only overview API.

Run from the project root:

    python tools/smoke_admin_readonly_api_structure.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATTERNS = {
    "backend/app/api/routes/admin.py": [
        '@router.get("/overview")',
        '@router.get("/save-snapshots")',
        'type="admin.overview"',
        'type="admin.save_snapshots"',
        'readOnly',
        'snapshot_json 원본은 내려주지 않습니다',
    ],
    "backend/app/services/admin_service.py": [
        "get_readonly_overview",
        "list_save_snapshot_summaries",
        "MASTER_DATA_MODELS",
        "safeForAdminReadOnlyUi",
        "safeForAdminWriteUi",
        "rawSnapshotReturned",
        "UserSaveSnapshot",
    ],
    "src/api/game-api-client.js": [
        "fetchAdminOverview",
        "listAdminSaveSnapshots",
    ],
    "backend/scripts/check_admin_readonly_api.py": [
        "admin/overview",
        "admin/save-snapshots",
        "rawSnapshotReturned",
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
        print("admin read-only API structure smoke test failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("admin read-only API structure smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

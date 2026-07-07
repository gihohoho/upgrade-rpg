"""Check the local admin read-only preparation API.

Run from the backend folder while FastAPI is running:

    python scripts/check_admin_readonly_api.py
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "http://127.0.0.1:8000/api/v1"


def request_json(method: str, url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, method=method, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code}: {detail}") from error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    overview_url = f"{base_url}/admin/overview"
    snapshots_url = f"{base_url}/admin/save-snapshots?limit={args.limit}"
    default_snapshots_url = f"{base_url}/admin/save-snapshots?limit={args.limit}&defaultOnly=true&sort=updated_desc"

    overview = request_json("GET", overview_url)
    snapshots = request_json("GET", snapshots_url)
    default_snapshots = request_json("GET", default_snapshots_url)

    failures: list[str] = []
    if not overview.get("ok"):
        failures.append("overview ok=false")
    if not snapshots.get("ok"):
        failures.append("save-snapshots ok=false")
    if overview.get("type") != "admin.overview":
        failures.append("overview type mismatch")
    if snapshots.get("type") != "admin.save_snapshots":
        failures.append("save-snapshots type mismatch")
    if default_snapshots.get("type") != "admin.save_snapshots":
        failures.append("filtered save-snapshots type mismatch")

    overview_payload = overview.get("payload") or {}
    snapshots_payload = snapshots.get("payload") or {}
    default_snapshots_payload = default_snapshots.get("payload") or {}
    if overview_payload.get("readOnly") is not True:
        failures.append("overview readOnly should be true")
    if snapshots_payload.get("readOnly") is not True:
        failures.append("save-snapshots readOnly should be true")
    if default_snapshots_payload.get("readOnly") is not True:
        failures.append("filtered save-snapshots readOnly should be true")
    filters = snapshots_payload.get("filters") or {}
    default_filters = default_snapshots_payload.get("filters") or {}
    if not isinstance(filters, dict):
        failures.append("save-snapshots filters missing")
    if default_filters.get("defaultOnly") is not True or default_filters.get("slotKey") != "default":
        failures.append("defaultOnly filter should resolve to default slot")
    if "totalAll" not in snapshots_payload:
        failures.append("save-snapshots totalAll missing")
    readiness = overview_payload.get("readiness") or {}
    if readiness.get("safeForAdminReadOnlyUi") is not True:
        failures.append("safeForAdminReadOnlyUi should be true")
    if readiness.get("safeForAdminWriteUi") is not False:
        failures.append("safeForAdminWriteUi should be false until change log/rollback are ready")
    if not isinstance(overview_payload.get("masterData"), dict):
        failures.append("overview masterData missing")
    if not isinstance(overview_payload.get("saveSnapshots"), dict):
        failures.append("overview saveSnapshots missing")
    snapshot_rows = snapshots_payload.get("snapshots") or []
    default_snapshot_rows = default_snapshots_payload.get("snapshots") or []
    if not isinstance(snapshot_rows, list):
        failures.append("snapshots should be a list")
    for row in snapshot_rows:
        if row.get("rawSnapshotReturned") is not False:
            failures.append("rawSnapshotReturned should be false for every snapshot summary")
            break
        if "snapshot" in row or "snapshot_json" in row:
            failures.append("raw snapshot data leaked into admin snapshot summary")
            break
    for row in default_snapshot_rows:
        if row.get("slotKey") != "default":
            failures.append("defaultOnly filtered rows should all be default slot")
            break
        if row.get("rawSnapshotReturned") is not False:
            failures.append("filtered rawSnapshotReturned should be false")
            break

    result = {
        "ok": not failures,
        "overviewUrl": overview_url,
        "snapshotsUrl": snapshots_url,
        "defaultSnapshotsUrl": default_snapshots_url,
        "overview": overview.get("data"),
        "readiness": readiness,
        "saveSnapshots": snapshots.get("data"),
        "defaultSaveSnapshots": default_snapshots.get("data"),
        "failures": failures,
    }

    if failures:
        print("admin read-only API check failed")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    print("admin read-only API check passed")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

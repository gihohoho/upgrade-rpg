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


def request_json(method: str, url: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
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
    master_domains_url = f"{base_url}/admin/master-data/domains"
    master_catalog_url = f"{base_url}/admin/master-data/catalog?domain=itemTemplates&limit=10&sort=code_asc"
    master_detail_url = None
    master_relations_url = None
    master_edit_preview_url = None
    master_edit_apply_url = None
    admin_change_logs_url = f"{base_url}/admin/change-logs?limit=10"

    overview = request_json("GET", overview_url)
    snapshots = request_json("GET", snapshots_url)
    default_snapshots = request_json("GET", default_snapshots_url)
    master_domains = request_json("GET", master_domains_url)
    master_catalog = request_json("GET", master_catalog_url)
    first_catalog_row = ((master_catalog.get("payload") or {}).get("rows") or [None])[0]
    if first_catalog_row and first_catalog_row.get("id"):
        master_detail_url = f"{base_url}/admin/master-data/detail?domain=itemTemplates&id={first_catalog_row.get('id')}"
        master_relations_url = f"{base_url}/admin/master-data/relations?domain=itemTemplates&id={first_catalog_row.get('id')}&limit=10"
        master_edit_preview_url = f"{base_url}/admin/master-data/edit-preview"
        master_edit_apply_url = f"{base_url}/admin/master-data/edit-apply"
        master_detail = request_json("GET", master_detail_url)
        master_relations = request_json("GET", master_relations_url)
        master_edit_preview = request_json("POST", master_edit_preview_url, {"domain": "itemTemplates", "id": first_catalog_row.get("id"), "draft": {"name": "dry-run smoke name"}, "dryRun": True})
        # 기본 live check는 실제 DB 변경을 하지 않습니다. 일부러 틀린 확인 문구로 guarded apply 차단만 확인합니다.
        master_edit_apply = request_json("POST", master_edit_apply_url, {"domain": "itemTemplates", "id": first_catalog_row.get("id"), "draft": {"name": "blocked apply smoke name"}, "confirmText": "WRONG", "dryRun": False})
    else:
        master_detail = None
        master_relations = None
        master_edit_preview = None
        master_edit_apply = None
    admin_change_logs = request_json("GET", admin_change_logs_url)

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
    if master_domains.get("type") != "admin.master_data.domains":
        failures.append("master-data domains type mismatch")
    if master_catalog.get("type") != "admin.master_data.catalog":
        failures.append("master-data catalog type mismatch")
    if master_detail is not None and master_detail.get("type") != "admin.master_data.detail":
        failures.append("master-data detail type mismatch")
    if master_relations is not None and master_relations.get("type") != "admin.master_data.relations":
        failures.append("master-data relations type mismatch")
    if master_edit_preview is not None and master_edit_preview.get("type") != "admin.master_data.edit_preview":
        failures.append("master-data edit-preview type mismatch")
    if master_edit_apply is not None and master_edit_apply.get("type") != "admin.master_data.edit_apply":
        failures.append("master-data edit-apply type mismatch")
    if admin_change_logs.get("type") != "admin.change_logs":
        failures.append("admin change-logs type mismatch")

    overview_payload = overview.get("payload") or {}
    snapshots_payload = snapshots.get("payload") or {}
    default_snapshots_payload = default_snapshots.get("payload") or {}
    master_domains_payload = master_domains.get("payload") or {}
    master_catalog_payload = master_catalog.get("payload") or {}
    master_detail_payload = master_detail.get("payload") if master_detail else None
    master_relations_payload = master_relations.get("payload") if master_relations else None
    master_edit_preview_payload = master_edit_preview.get("payload") if master_edit_preview else None
    master_edit_apply_payload = master_edit_apply.get("payload") if master_edit_apply else None
    admin_change_logs_payload = admin_change_logs.get("payload") or {}
    if overview_payload.get("readOnly") is not True:
        failures.append("overview readOnly should be true")
    if snapshots_payload.get("readOnly") is not True:
        failures.append("save-snapshots readOnly should be true")
    if default_snapshots_payload.get("readOnly") is not True:
        failures.append("filtered save-snapshots readOnly should be true")
    if master_domains_payload.get("readOnly") is not True:
        failures.append("master-data domains readOnly should be true")
    if master_catalog_payload.get("readOnly") is not True:
        failures.append("master-data catalog readOnly should be true")
    if master_detail_payload is not None and master_detail_payload.get("readOnly") is not True:
        failures.append("master-data detail readOnly should be true")
    if master_relations_payload is not None and master_relations_payload.get("readOnly") is not True:
        failures.append("master-data relations readOnly should be true")
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
        failures.append("safeForAdminWriteUi should be false for general write UI")
    if readiness.get("guardedMasterEditApplyReady") is not True:
        failures.append("guardedMasterEditApplyReady should be true")
    if not isinstance(overview_payload.get("masterData"), dict):
        failures.append("overview masterData missing")
    if not isinstance(overview_payload.get("saveSnapshots"), dict):
        failures.append("overview saveSnapshots missing")
    if not isinstance(master_domains_payload.get("domains"), list) or not master_domains_payload.get("domains"):
        failures.append("master-data domains list missing")
    if master_catalog_payload.get("domain") != "itemTemplates":
        failures.append("master-data catalog domain should be itemTemplates")
    if master_catalog_payload.get("rawJsonReturned") is not False or master_catalog_payload.get("assetsReturned") is not False:
        failures.append("master-data catalog should hide raw JSON and assets")
    if not isinstance(master_catalog_payload.get("columns"), list):
        failures.append("master-data catalog columns missing")
    if master_detail_payload is not None:
        if master_detail_payload.get("rawJsonReturned") is not False or master_detail_payload.get("assetsReturned") is not False:
            failures.append("master-data detail should hide raw JSON and assets")
        if master_detail_payload.get("sanitizedJsonReturned") is not True:
            failures.append("master-data detail should return sanitized JSON preview")
        if not isinstance(master_detail_payload.get("fields"), list):
            failures.append("master-data detail fields missing")
        if not isinstance(master_detail_payload.get("jsonFields"), list):
            failures.append("master-data detail jsonFields missing")
    if master_edit_preview_payload is not None:
        if master_edit_preview_payload.get("readOnly") is not True or master_edit_preview_payload.get("dryRun") is not True:
            failures.append("master-data edit-preview should be readOnly dryRun")
        if master_edit_preview_payload.get("writeBlocked") is not True or master_edit_preview_payload.get("safeForAdminWriteUi") is not False:
            failures.append("master-data edit-preview write should remain blocked")
        if master_edit_preview_payload.get("rawJsonReturned") is not False or master_edit_preview_payload.get("assetsReturned") is not False:
            failures.append("master-data edit-preview should hide raw JSON and assets")
        if not isinstance(master_edit_preview_payload.get("acceptedChanges"), list):
            failures.append("master-data edit-preview acceptedChanges missing")
    if master_edit_apply_payload is not None:
        if master_edit_apply_payload.get("status") != "confirmation_required":
            failures.append("master-data edit-apply should be blocked with wrong confirmText")
        if master_edit_apply_payload.get("applied") is not False or master_edit_apply_payload.get("writeBlocked") is not True:
            failures.append("master-data edit-apply wrong confirmText must not apply")
    if admin_change_logs_payload.get("readOnly") is not True:
        failures.append("admin change logs should be readOnly")
    if not isinstance(admin_change_logs_payload.get("rows"), list):
        failures.append("admin change logs rows missing")
    if master_relations_payload is not None:
        if master_relations_payload.get("rawJsonReturned") is not False or master_relations_payload.get("assetsReturned") is not False:
            failures.append("master-data relations should hide raw JSON and assets")
        if master_relations_payload.get("safeForAdminWriteUi") is not False:
            failures.append("master-data relations write UI should remain blocked")
        if not isinstance(master_relations_payload.get("groups"), list):
            failures.append("master-data relations groups missing")
        for group in master_relations_payload.get("groups") or []:
            if group.get("rawJsonReturned") is not False or group.get("assetsReturned") is not False:
                failures.append("master-data relation groups should hide raw JSON and assets")
                break
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
    for row in master_catalog_payload.get("rows") or []:
        if row.get("rawJsonReturned") is not False or row.get("assetsReturned") is not False:
            failures.append("master-data catalog rows should hide raw JSON and assets")
            break

    result = {
        "ok": not failures,
        "overviewUrl": overview_url,
        "snapshotsUrl": snapshots_url,
        "defaultSnapshotsUrl": default_snapshots_url,
        "masterDomainsUrl": master_domains_url,
        "masterCatalogUrl": master_catalog_url,
        "masterDetailUrl": master_detail_url,
        "masterRelationsUrl": master_relations_url,
        "masterEditPreviewUrl": master_edit_preview_url,
        "masterEditApplyUrl": master_edit_apply_url,
        "adminChangeLogsUrl": admin_change_logs_url,
        "overview": overview.get("data"),
        "readiness": readiness,
        "saveSnapshots": snapshots.get("data"),
        "defaultSaveSnapshots": default_snapshots.get("data"),
        "masterDomains": master_domains.get("data"),
        "masterCatalog": master_catalog.get("data"),
        "masterDetail": master_detail.get("data") if master_detail else None,
        "masterRelations": master_relations.get("data") if master_relations else None,
        "masterEditPreview": master_edit_preview.get("data") if master_edit_preview else None,
        "masterEditApply": master_edit_apply.get("data") if master_edit_apply else None,
        "adminChangeLogs": admin_change_logs.get("data"),
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

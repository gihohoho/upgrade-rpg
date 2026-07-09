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
        '@router.get("/master-data/domains")',
        '@router.get("/master-data/catalog")',
        '@router.get("/master-data/detail")',
        '@router.get("/master-data/relations")',
        '@router.post("/master-data/edit-preview")',
        '@router.post("/master-data/edit-apply")',
        '@router.get("/change-logs")',
        '@router.get("/change-logs/{change_log_id}")',
        '@router.post("/change-logs/{change_log_id}/rollback-preview")',
        '@router.post("/change-logs/{change_log_id}/rollback-apply")',
        'type="admin.overview"',
        'type="admin.save_snapshots"',
        'type="admin.master_data.domains"',
        'type="admin.master_data.catalog"',
        'type="admin.master_data.detail"',
        'type="admin.master_data.relations"',
        'type="admin.master_data.edit_preview"',
        'type="admin.master_data.edit_apply"',
        'type="admin.change_logs"',
        'type="admin.change_log.detail"',
        'type="admin.change_log.rollback_preview"',
        'type="admin.change_log.rollback_apply"',
        'readOnly',
        'snapshot_json 원본은 내려주지 않습니다',
    ],
    "backend/app/services/admin_service.py": [
        "AdminOverviewSnapshotsService",
        "AdminMasterCatalogService",
        "class AdminService(",
        "MASTER_DATA_MODELS",
        "safeForAdminReadOnlyUi",
        "safeForAdminWriteUi",
        "guardedMasterEditApplyReady",
        "MASTER_CATALOG_DOMAINS",
        "preview_master_data_edit",
        "apply_master_data_edit",
        "list_admin_change_logs",
        "get_admin_change_log_detail",
        "preview_admin_change_log_rollback",
        "apply_admin_change_log_rollback",
        "AdminChangeLog",
        "MASTER_EDIT_APPLY_CONFIRM_TEXT",
        "MASTER_EDIT_ROLLBACK_CONFIRM_TEXT",
        "_normalize_master_edit_value",
        "assetsReturned",
    ],

    "backend/app/services/admin/admin_master_catalog_service.py": [
        "class AdminMasterCatalogService",
        "list_master_catalog_domains",
        "list_master_catalog_rows",
        "get_master_catalog_detail",
        "get_master_catalog_relations",
        "_build_master_relation_groups",
        "_fetch_master_relation_group",
        "_serialize_master_detail_scalar_fields",
        "_sanitize_json_preview",
        "assetsReturned",
        "sanitizedJsonReturned",
    ],
    "backend/app/services/admin/admin_overview_snapshots_service.py": [
        "class AdminOverviewSnapshotsService",
        "get_readonly_overview",
        "list_save_snapshot_summaries",
        "_build_snapshot_filters",
        "_build_snapshot_where_clauses",
        "_snapshot_order_by",
        "totalAll",
        "hasActiveFilters",
        "rawSnapshotReturned",
        "UserSaveSnapshot",
    ],
    "src/api/game-api-client.js": [
        "fetchAdminOverview",
        "listAdminSaveSnapshots",
        "defaultOnly",
        "slotKey",
        "userId",
        "listAdminMasterCatalogDomains",
        "listAdminMasterCatalogRows",
        "fetchAdminMasterDataDetail",
        "fetchAdminMasterDataRelations",
        "previewAdminMasterDataEdit",
        "applyAdminMasterDataEdit",
        "listAdminChangeLogs",
        "fetchAdminChangeLogDetail",
        "previewAdminChangeLogRollback",
        "applyAdminChangeLogRollback",
    ],
    "backend/scripts/check_admin_readonly_api.py": [
        "admin/overview",
        "admin/save-snapshots",
        "defaultOnly=true",
        "filters",
        "rawSnapshotReturned",
        "admin/master-data/domains",
        "admin/master-data/catalog",
        "admin/master-data/detail",
        "admin/master-data/relations",
        "admin/master-data/edit-preview",
        "admin/master-data/edit-apply",
        "admin/change-logs",
        "dryRun",
        "assetsReturned",
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

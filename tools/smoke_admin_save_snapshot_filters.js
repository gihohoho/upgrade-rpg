const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");

function read(file) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  return fs.readFileSync(fullPath, "utf8");
}

function assertContains(file, patterns) {
  const text = read(file);
  for (const pattern of patterns) {
    if (!text.includes(pattern)) throw new Error(`${file}: missing pattern ${pattern}`);
  }
}

assertContains("admin.html", [
  "최근 세이브 스냅샷 필터",
  "data-admin-filter-limit",
  "data-admin-filter-user-id",
  "data-admin-filter-slot-key",
  "data-admin-filter-source",
  "data-admin-filter-sort",
  "data-admin-filter-default-only",
  "data-admin-action=\"apply-snapshot-filters\"",
  "data-admin-action=\"reset-snapshot-filters\"",
  "원본 snapshot_json은 계속 숨김 상태입니다",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v116.admin-master-data-detail",
  "readSnapshotFiltersFromDom",
  "resetSnapshotFilters",
  "describeSnapshotFilters",
  "apply-snapshot-filters",
  "reset-snapshot-filters",
  "snapshotFilterReady",
  "totalAllNote",
  "filters.hasActiveFilters",
]);

assertContains("src/api/game-api-client.js", [
  "userId",
  "slotKey",
  "source",
  "defaultOnly",
  "sort",
  "request(\"/admin/save-snapshots\"",
]);

assertContains("backend/app/api/routes/admin.py", [
  "user_id: int | None = Query(default=None, alias=\"userId\", ge=1)",
  "slot_key: str | None = Query(default=None, alias=\"slotKey\", max_length=80)",
  "default_only: bool = Query(default=False, alias=\"defaultOnly\")",
  "sort: str = Query(default=\"updated_desc\", max_length=30)",
  "filters\": snapshots[\"filters\"]",
]);

assertContains("backend/app/services/admin_service.py", [
  "_build_snapshot_filters",
  "_build_snapshot_where_clauses",
  "_snapshot_order_by",
  "_count_save_snapshots",
  "slotKey_ignored_unsafe",
  "totalAll",
  "hasActiveFilters",
]);

console.log("admin save snapshot filters smoke test passed");

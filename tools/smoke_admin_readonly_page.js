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
  "Upgrade RPG 관리자 페이지",
  "Read-only Admin Preview",
  "data-admin-action=\"refresh\"",
  "data-admin-api-base-url",
  "data-admin-cards",
  "data-admin-master-table",
  "data-admin-master-domain",
  "data-admin-master-catalog-table",
  "data-admin-snapshot-table",
  "data-admin-filter-limit",
  "data-admin-filter-user-id",
  "data-admin-filter-slot-key",
  "data-admin-filter-source",
  "data-admin-filter-sort",
  "data-admin-filter-default-only",
  "data-admin-action=\"apply-snapshot-filters\"",
  "data-admin-action=\"reset-snapshot-filters\"",
  "data-admin-readiness",
  "src/api/game-api-client.js",
  "src/api/admin-page-readonly.js",
  "DB/localStorage/게임 런타임을 수정하지 않습니다",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v121.admin-value-hints",
  "fetchAdminReadOnlyPageData",
  "refreshAdminReadOnlyPage",
  "checkAdminReadOnlyPageReady",
  "fetchAdminOverview",
  "listAdminSaveSnapshots",
  "listAdminMasterCatalogRows",
  "rawSnapshotReturned",
  "saveApiBaseUrlFromInput",
  "resetApiBaseUrl",
  "getCurrentAdminPageUrl",
  "getGamePageUrl",
  "copyCurrentAdminPageUrl",
  "syncLocationHints",
  "readSnapshotFiltersFromDom",
  "resetSnapshotFilters",
  "describeSnapshotFilters",
  "snapshotFilterReady",
  "masterCatalogReady",
  "readMasterCatalogFiltersFromDom",
]);

assertContains("src/api/admin-readonly-overview.js", [
  "v113.admin-readonly-overview-url-helper",
  "openAdminReadOnlyPage",
  "getAdminReadOnlyPageUrl",
  "copyAdminReadOnlyPageUrl",
  "관리자 페이지 열기",
  "현재 게임 주소 기준 관리자 페이지 주소",
  "new URL(\"admin.html\", window.location.href)",
]);

console.log("admin read-only page smoke test passed");

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");

function assertContains(file, patterns) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  const text = fs.readFileSync(fullPath, "utf8");
  for (const pattern of patterns) {
    if (!text.includes(pattern)) throw new Error(`${file}: missing pattern ${pattern}`);
  }
}

assertContains("src/api/game-api-client.js", [
  "fetchAdminOverview",
  "listAdminSaveSnapshots",
  'request("/admin/overview"',
  'request("/admin/save-snapshots"',
]);

assertContains("src/api/admin-readonly-overview.js", [
  "v113.admin-readonly-overview-url-helper",
  "fetchAdminReadOnlyOverview",
  "listAdminReadOnlySaveSnapshots",
  "openAdminReadOnlyOverviewModal",
  "checkAdminReadOnlyOverviewReady",
  "openAdminReadOnlyPage",
  "getAdminReadOnlyPageUrl",
  "copyAdminReadOnlyPageUrl",
  "rawSnapshotReturned",
  "관리자 페이지로 넘어가기 전 DB 상태를 조회만 합니다",
]);

assertContains("src/api/save-data-dev-badge.js", [
  "v111.backend-save-data-dev-badge-admin-overview",
  'data-sd-action="admin"',
  "openAdminReadOnlyOverviewModal",
]);

assertContains("index.html", [
  'src/api/admin-readonly-overview.js',
  'src/api/save-data-dev-badge.js',
]);

console.log("admin read-only overview frontend smoke test passed");

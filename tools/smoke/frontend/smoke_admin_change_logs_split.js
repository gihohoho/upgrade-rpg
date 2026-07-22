const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");

function read(file) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  return fs.readFileSync(fullPath, "utf8");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function assertContains(file, patterns) {
  const text = read(file);
  for (const pattern of patterns) {
    assert(text.includes(pattern), `${file}: missing pattern ${pattern}`);
  }
}

const adminHtml = read("admin.html");
const gameApiIndex = adminHtml.indexOf("src/api/game-api-client.js");
const layoutIndex = adminHtml.indexOf("src/api/admin-layout-shell.js");
const changeLogsIndex = adminHtml.indexOf("src/api/admin/admin-change-logs.js");
const adminPageIndex = adminHtml.indexOf("src/api/admin-page-readonly.js");

assert(gameApiIndex >= 0, "admin.html: missing game-api-client.js script");
assert(layoutIndex >= 0, "admin.html: missing admin-layout-shell.js script");
assert(changeLogsIndex >= 0, "admin.html: missing admin/admin-change-logs.js script");
assert(adminPageIndex >= 0, "admin.html: missing admin-page-readonly.js script");
assert(gameApiIndex < layoutIndex && layoutIndex < changeLogsIndex && changeLogsIndex < adminPageIndex, "admin.html: script order must be game api -> layout shell -> change logs -> admin page");

assertContains("src/api/admin/admin-change-logs.js", [
  "v187.admin-change-logs-split",
  "window.RpgAdminChangeLogs",
  "configure",
  "getReadiness",
  "readChangeLogFiltersFromDom",
  "resetChangeLogFilters",
  "describeChangeLogFilters",
  "renderAdminChangeLogs",
  "renderAdminChangeLogDetail",
  "openAdminChangeLogDetail",
  "previewAdminChangeLogRollback",
  "applyAdminChangeLogRollback",
  "previewAdminCreateDeleteRollback",
  "applyAdminCreateDeleteRollback",
  "previewAdminCreateDeleteRestore",
  "applyAdminCreateDeleteRestore",
  "applyAdminChangeLogActionShortcut",
  "currentAdminChangeLogDetailPayload",
  "data-admin-action=\"open-admin-change-log-detail\"",
  "data-admin-create-delete-result",
  "data-admin-create-delete-restore-result",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v187.admin-change-logs-split",
  "getAdminChangeLogsApi",
  "configureAdminChangeLogs",
  "getAdminChangeLogsReadiness",
  "RpgAdminChangeLogs is not loaded",
  "changeLogsExternalReady",
  "window.getAdminChangeLogsReadiness = getAdminChangeLogsReadiness",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke/frontend/smoke_admin_change_logs_split.js",
]);

assertContains("docs/archive/stage-notes/ADMIN_CHANGE_LOGS_SPLIT.md", [
  "Admin Change Logs Split",
  "v187",
  "src/api/admin/admin-change-logs.js",
  "DB reset / seed",
]);

console.log("admin change logs split smoke test passed");

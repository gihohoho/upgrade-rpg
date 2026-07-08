const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");

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

assertContains("admin.html", [
  "section-admin-js-split-readiness",
  "data-admin-js-split-readiness",
  "v186 change logs contract",
  "section-change-logs",
  "data-admin-change-log-table",
  "data-admin-change-log-detail",
  "data-admin-change-log-filter-action",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v186.admin-change-log-split-contract",
  "v185.admin-layout-shell-split",
  "ADMIN_CHANGE_LOG_SPLIT_CONTRACT",
  "contract-frozen-v186",
  "src/api/admin/admin-change-logs.js",
  "requiredApiMethods",
  "requiredWindowExports",
  "domTargets",
  "delegatedActions",
  "getAdminChangeLogSplitContractReadiness",
  "renderAdminChangeLogSplitContractReadiness",
  "changeLogSplitContractReady",
  "changeLogSplitContract",
  "window.getAdminChangeLogSplitContractReadiness",
  "window.renderAdminChangeLogSplitContractReadiness",
]);

assertContains("src/api/admin-page-readonly.js", [
  "listAdminChangeLogs",
  "fetchAdminChangeLogDetail",
  "previewAdminChangeLogRollback",
  "applyAdminChangeLogRollback",
  "previewAdminCreateDeleteRollback",
  "applyAdminCreateDeleteRollback",
  "previewAdminCreateDeleteRestore",
  "applyAdminCreateDeleteRestore",
  "readChangeLogFiltersFromDom",
  "renderAdminChangeLogs",
  "renderAdminChangeLogDetail",
  "renderAdminCreateDeleteRestoreResult",
  "applyAdminChangeLogActionShortcut",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke_admin_change_log_split_contract.js",
]);

assertContains("docs/ADMIN_CHANGE_LOG_SPLIT_CONTRACT.md", [
  "Admin Change Log Split Contract",
  "v186",
  "contract-frozen-v186",
  "src/api/admin/admin-change-logs.js",
  "DB reset / seed",
]);

console.log("admin change log split contract smoke test passed");

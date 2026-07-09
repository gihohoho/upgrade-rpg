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
  "v182 result summary helper",
  "create-result-banner",
  "create-result-metric-grid",
  "create-result-blocker-list",
  "v182 admin create lifecycle result summary",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v182.admin-create-lifecycle-result-summary",
  "renderAdminOperationResultBanner",
  "renderAdminCreateLifecycleMetric",
  "renderAdminCreateDeleteBlockerSummary",
  "createLifecycleResultSummaryReady",
  "dependencyCheckCount",
  "dependencyBlockerGuardCount",
  "restoreConflictCount",
  "생성 row 삭제 차단",
  "삭제 row 복원 차단",
]);

assertContains("backend/app/services/admin_service_legacy_markers.py", [
  "dependencyCheckCount",
  "dependencyBlockerGuardCount",
  "restoreConflictCount",
  "blocker_guard_count",
  "restore_conflict_count",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke_admin_create_lifecycle_result_summary.js",
]);

assertContains("docs/ADMIN_CREATE_LIFECYCLE_RESULT_SUMMARY.md", [
  "Admin Create Lifecycle Result Summary",
  "dependencyCheckCount",
  "restoreConflictCount",
  "DB reset / seed",
]);

console.log("admin create lifecycle result summary smoke test passed");

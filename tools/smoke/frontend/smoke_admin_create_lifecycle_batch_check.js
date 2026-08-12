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

assertContains("admin.html", [
  "v183 batch lifecycle check",
  "create-lifecycle-batch-card",
  "create-lifecycle-batch-controls",
  "v183 admin create lifecycle batch check",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v183.admin-create-lifecycle-batch-check",
  "ADMIN_CREATE_LIFECYCLE_BATCH_CONFIRM_TEXT",
  "RUN CREATE DELETE RESTORE CHECK",
  "readAdminCreateLifecycleBatchControls",
  "renderAdminCreateLifecycleBatchResult",
  "runAdminCreateLifecycleBatchCheck",
  "data-admin-create-lifecycle-batch-confirm",
  "data-admin-create-lifecycle-batch-result",
  "run-create-lifecycle-batch-check",
  "previewAdminMasterDataCreate",
  "applyAdminMasterDataCreate",
  "previewAdminCreateDeleteRollback",
  "applyAdminCreateDeleteRollback",
  "previewAdminCreateDeleteRestore",
  "applyAdminCreateDeleteRestore",
  "createLifecycleBatchCheckReady",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke/frontend/smoke_admin_create_lifecycle_batch_check.js",
]);

assertContains("docs/archive/history/ADMIN_AND_BACKEND_HISTORY.md", [
  "Admin Create Lifecycle Batch Check",
  "RUN CREATE DELETE RESTORE CHECK",
  "생성 preview",
  "삭제 apply",
  "복원 apply",
  "DB reset / seed",
]);

console.log("admin create lifecycle batch check smoke test passed");

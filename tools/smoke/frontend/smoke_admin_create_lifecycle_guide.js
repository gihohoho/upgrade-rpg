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
  "section-create-lifecycle-guide",
  "data-admin-create-lifecycle-guide",
  "신규 row 생성·삭제·복원 점검",
  "v181 dependency/action helper",
  "create_delete_restore",
  "v181 admin create lifecycle guard helper",
  "v180 admin create lifecycle guide",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v181.admin-create-lifecycle-guard-helper",
  "v180.admin-create-lifecycle-guide",
  "v179.admin-create-apply-level-links",
  "ADMIN_CHANGE_LOG_ACTION_FILTERS",
  "renderAdminCreateLifecycleGuide",
  "getAdminCreateLifecycleGuideReadiness",
  "renderAdminCreateLifecycleDependencyGuards",
  "applyAdminChangeLogActionShortcut",
  "createLifecycleGuideReady",
  "createLifecycleDependencyGuideReady",
  "createLifecycle",
  "browserCheckOrder",
  "deleteDependencyGuards",
  "deleteGuardMode",
  "CREATE MASTER DATA ROW",
  "DELETE CREATED MASTER DATA ROW",
  "RESTORE DELETED CREATED ROW",
]);

assertContains("backend/app/services/admin_service_legacy_markers.py", [
  "ADMIN_CHANGE_LOG_ACTION_FILTERS",
  "_master_create_lifecycle_payload",
  "createLifecycle",
  "identityMode",
  "deleteRestoreKey",
  "_master_create_lifecycle_dependency_guards",
  "deleteDependencyGuards",
  "deleteGuardMode",
  "browserCheckOrder",
  "deleteDependencyGuards",
  "deleteGuardMode",
  "create_delete_restore",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke/frontend/smoke_admin_create_lifecycle_guide.js",
]);

assertContains("docs/archive/stage-notes/ADMIN_CREATE_LIFECYCLE_GUIDE.md", [
  "Admin Create Lifecycle Guide",
  "v181",
  "v180",
  "생성→삭제→복원",
  "change log action filter",
  "DB reset / seed",
]);

console.log("admin create lifecycle guide smoke test passed");

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
  "v181 dependency/action helper",
  "create-lifecycle-guard-list",
  "create-lifecycle-actions",
  "v181 admin create lifecycle guard helper",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v181.admin-create-lifecycle-guard-helper",
  "renderAdminCreateLifecycleDependencyGuards",
  "renderAdminCreateLifecycleActionShortcuts",
  "applyAdminChangeLogActionShortcut",
  "set-change-log-action-filter",
  "data-admin-change-log-action-shortcut",
  "createLifecycleDependencyGuideReady",
  "deleteDependencyGuards",
  "deleteGuardMode",
]);

assertContains("backend/app/services/admin_service.py", [
  "_master_create_lifecycle_dependency_guards",
  "deleteDependencyGuards",
  "deleteDependencyGuardCount",
  "deleteDependencyBlockerGuardCount",
  "deleteGuardMode",
  "dependency-blocking",
  "leaf-id-current-match",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke_admin_create_lifecycle_guard_helper.js",
]);

console.log("admin create lifecycle guard helper smoke test passed");

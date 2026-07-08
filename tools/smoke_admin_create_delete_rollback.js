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

assertContains("backend/app/services/admin_service.py", [
  "MASTER_CREATE_DELETE_CONFIRM_TEXT",
  "DELETE CREATED MASTER DATA ROW",
  "MASTER_CREATE_DELETE_ALLOWED_DOMAINS",
  "preview_admin_create_delete_rollback",
  "apply_admin_create_delete_rollback",
  "_build_create_delete_dependency_checks",
  "create_delete_preview_ready",
  "create_delete_blocked",
  "currentMatchesCreateValues",
  "dependencyBlockerCount",
  "action=\"create_delete\"",
  "create_delete_restore_not_enabled",
]);

assertContains("backend/app/api/routes/admin.py", [
  "AdminCreateDeletePreviewRequest",
  "AdminCreateDeleteApplyRequest",
  "@router.post(\"/change-logs/{change_log_id}/create-delete-preview\")",
  "@router.post(\"/change-logs/{change_log_id}/create-delete-apply\")",
  "require_admin_write_dev_key",
  "admin.change_log.create_delete_preview",
  "admin.change_log.create_delete_apply",
]);

assertContains("backend/app/schemas/admin.py", [
  "AdminCreateDeletePreviewRequest",
  "AdminCreateDeleteApplyRequest",
  "confirmText",
]);

assertContains("src/api/game-api-client.js", [
  "previewAdminCreateDeleteRollback",
  "applyAdminCreateDeleteRollback",
  "/create-delete-preview",
  "/create-delete-apply",
  "getAdminWriteHeaders()",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v168.admin-create-delete-rollback",
  "ADMIN_CREATE_DELETE_CONFIRM_TEXT",
  "DELETE CREATED MASTER DATA ROW",
  "previewAdminCreateDeleteRollback",
  "applyAdminCreateDeleteRollback",
  "data-admin-create-delete-confirm",
  "data-admin-create-delete-result",
  "createDeleteRollbackReady",
]);

assertContains("docs/ADMIN_CREATE_DELETE_ROLLBACK.md", [
  "Admin Create Delete Rollback",
  "DELETE CREATED MASTER DATA ROW",
  "dependencyBlockerCount",
  "DB reset / seed",
]);

console.log("admin create delete rollback smoke test passed");

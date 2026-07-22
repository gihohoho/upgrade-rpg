const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");

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

assertContains("backend/app/services/admin_service_legacy_markers.py", [
  "MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT",
  "RESTORE DELETED CREATED ROW",
  "preview_admin_create_delete_restore",
  "apply_admin_create_delete_restore",
  "create_delete_restore_preview_ready",
  "create_delete_restore_blocked",
  "idConflict",
  "codeConflict",
  "validationErrorCount",
  "fieldZones",
  "action=\"create_delete_restore\"",
]);

assertContains("backend/app/api/routes/admin_change_log_routes.py", [
  "AdminCreateDeleteRestorePreviewRequest",
  "AdminCreateDeleteRestoreApplyRequest",
  "@router.post(\"/change-logs/{change_log_id}/create-delete-restore-preview\")",
  "@router.post(\"/change-logs/{change_log_id}/create-delete-restore-apply\")",
  "admin.change_log.create_delete_restore_preview",
  "admin.change_log.create_delete_restore_apply",
]);

assertContains("backend/app/schemas/admin.py", [
  "AdminCreateDeleteRestorePreviewRequest",
  "AdminCreateDeleteRestoreApplyRequest",
  "confirmText",
]);

assertContains("src/api/game-api-client.js", [
  "previewAdminCreateDeleteRestore",
  "applyAdminCreateDeleteRestore",
  "/create-delete-restore-preview",
  "/create-delete-restore-apply",
  "getAdminWriteHeaders()",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v171.admin-create-delete-restore",
  "ADMIN_CREATE_DELETE_RESTORE_CONFIRM_TEXT",
  "RESTORE DELETED CREATED ROW",
  "previewAdminCreateDeleteRestore",
  "applyAdminCreateDeleteRestore",
  "data-admin-create-delete-restore-confirm",
  "data-admin-create-delete-restore-result",
  "createDeleteRestoreReady",
]);

assertContains("docs/archive/stage-notes/ADMIN_CREATE_DELETE_RESTORE.md", [
  "Admin Create Delete Restore",
  "RESTORE DELETED CREATED ROW",
  "idConflict",
  "codeConflict",
  "DB reset / seed",
]);

console.log("admin create delete restore smoke test passed");

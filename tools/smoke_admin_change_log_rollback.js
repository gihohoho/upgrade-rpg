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

assertContains("backend/app/api/routes/admin.py", [
  '@router.get("/change-logs/{change_log_id}")',
  '@router.post("/change-logs/{change_log_id}/rollback-preview")',
  '@router.post("/change-logs/{change_log_id}/rollback-apply")',
  "AdminChangeLogRollbackPreviewRequest",
  "AdminChangeLogRollbackApplyRequest",
  "get_admin_change_log_detail",
  "preview_admin_change_log_rollback",
  "apply_admin_change_log_rollback",
  'type="admin.change_log.detail"',
  'type="admin.change_log.rollback_preview"',
  'type="admin.change_log.rollback_apply"',
]);

assertContains("backend/app/services/admin_service.py", [
  "MASTER_EDIT_ROLLBACK_CONFIRM_TEXT",
  "ROLLBACK MASTER DATA EDIT",
  "get_admin_change_log_detail",
  "preview_admin_change_log_rollback",
  "apply_admin_change_log_rollback",
  "current_db_values_do_not_match_change_log_after_values",
  "rollback_confirm_text_mismatch",
  "rollbackChangeLogId",
  "action=\"rollback\"",
  "guardedRollbackReady",
]);

assertContains("backend/app/schemas/admin.py", [
  "AdminChangeLogRollbackPreviewRequest",
  "AdminChangeLogRollbackApplyRequest",
  "confirm_text",
  "confirmText",
]);

assertContains("src/api/game-api-client.js", [
  "fetchAdminChangeLogDetail",
  "previewAdminChangeLogRollback",
  "applyAdminChangeLogRollback",
  'request(`/admin/change-logs/${id}`',
  'request(`/admin/change-logs/${id}/rollback-preview`',
  'request(`/admin/change-logs/${id}/rollback-apply`',
]);

assertContains("src/api/admin-page-readonly.js", [
  "v134.admin-safe-selects",
  "ADMIN_ROLLBACK_CONFIRM_TEXT",
  "ROLLBACK MASTER DATA EDIT",
  "openAdminChangeLogDetail",
  "previewAdminChangeLogRollback",
  "applyAdminChangeLogRollback",
  "readAdminRollbackControls",
  "renderAdminRollbackResult",
  "data-admin-action=\"open-admin-change-log-detail\"",
  "data-admin-action=\"preview-admin-change-log-rollback\"",
  "data-admin-action=\"apply-admin-change-log-rollback\"",
  "stackable / 겹치기 가능 여부",
]);

assertContains("admin.html", [
  "Guarded Admin + API Verify",
  "data-admin-change-log-detail",
  "stackable / 겹치기 가능 여부",
  "v134 admin safe selects",
]);

console.log("admin change log rollback smoke test passed");

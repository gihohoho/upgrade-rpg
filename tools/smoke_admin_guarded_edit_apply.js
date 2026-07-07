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
  '@router.post("/master-data/edit-apply")',
  '@router.get("/change-logs")',
  "AdminMasterDataEditApplyRequest",
  "apply_master_data_edit",
  'type="admin.master_data.edit_apply"',
  'type="admin.change_logs"',
  "확인 문구와 allow-list",
]);

assertContains("backend/app/services/admin_service.py", [
  "MASTER_EDIT_APPLY_CONFIRM_TEXT",
  "APPLY MASTER DATA EDIT",
  "MASTER_EDIT_ALLOWED_FIELDS",
  "apply_master_data_edit",
  "list_admin_change_logs",
  "AdminChangeLog",
  "confirm_text_mismatch",
  "game_runtime_requires_reload",
  "rollback_json",
  "await session.commit()",
]);

const serviceText = read("backend/app/services/admin_service.py");
const previewEnd = serviceText.includes("async def apply_master_data_edit")
  ? serviceText.indexOf("async def apply_master_data_edit")
  : serviceText.indexOf("async def get_readonly_overview");
const previewMethod = serviceText.slice(serviceText.indexOf("async def preview_master_data_edit"), previewEnd);
if (/\.commit\s*\(/.test(previewMethod) || /\.flush\s*\(/.test(previewMethod)) {
  throw new Error("preview_master_data_edit must remain dry-run without commit/flush");
}

assertContains("backend/app/schemas/admin.py", [
  "AdminMasterDataEditApplyRequest",
  "confirm_text",
  "confirmText",
  "dry_run: bool = Field(default=False",
]);

assertContains("src/api/game-api-client.js", [
  "applyAdminMasterDataEdit",
  'request("/admin/master-data/edit-apply"',
  "confirmText",
  "listAdminChangeLogs",
  'request("/admin/change-logs"',
]);

assertContains("src/api/admin-page-readonly.js", [
  "v126.admin-edit-impact-guide",
  "ADMIN_EDIT_APPLY_CONFIRM_TEXT",
  "ADMIN_EDIT_ALLOWED_FIELDS",
  "isAdminEditApplyAllowedField",
  "applyAdminEditDraft",
  "readAdminEditApplyControls",
  "refreshAdminChangeLogs",
  "data-admin-action=\"apply-admin-edit-draft\"",
  "APPLY MASTER DATA EDIT",
  "guardedApply",
]);

assertContains("admin.html", [
  "Guarded Admin Rollback",
  "data-admin-change-log-table",
  "data-admin-action=\"refresh-admin-change-logs\"",
  "v126 admin edit impact guide",
  "allow-list 필드",
]);

assertContains("docs/ADMIN_GUARDED_EDIT_APPLY.md", [
  "Admin Guarded Edit Apply",
  "POST /api/v1/admin/master-data/edit-apply",
  "APPLY MASTER DATA EDIT",
  "admin_change_logs",
  "DB reset / seed 필요 없음",
]);

console.log("admin guarded edit apply smoke test passed");

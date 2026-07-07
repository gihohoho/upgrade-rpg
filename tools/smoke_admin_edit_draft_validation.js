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
  '@router.post("/master-data/edit-preview")',
  "AdminMasterDataEditPreviewRequest",
  'type="admin.master_data.edit_preview"',
  "DB를 수정하지 않습니다",
]);

assertContains("backend/app/services/admin_service.py", [
  "preview_master_data_edit",
  "_empty_edit_preview",
  "_normalize_master_edit_value",
  "writeBlocked",
  "dryRun",
  "json_edit_not_enabled_yet",
  "asset_edit_not_enabled_yet",
]);

const serviceText = read("backend/app/services/admin_service.py");
const previewEnd = serviceText.includes("async def apply_master_data_edit")
  ? serviceText.indexOf("async def apply_master_data_edit")
  : serviceText.indexOf("async def get_readonly_overview");
const previewMethod = serviceText.slice(serviceText.indexOf("async def preview_master_data_edit"), previewEnd);
if (/\.commit\s*\(/.test(previewMethod) || /\.flush\s*\(/.test(previewMethod)) {
  throw new Error("preview_master_data_edit must not commit or flush");
}

assertContains("backend/app/schemas/admin.py", [
  "AdminMasterDataEditPreviewRequest",
  "dryRun",
  "draft: dict[str, Any]",
]);

assertContains("src/api/game-api-client.js", [
  "previewAdminMasterDataEdit",
  'request("/admin/master-data/edit-preview"',
  "dryRun: true",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v133.admin-edit-input-ui",
  "previewAdminEditDraft",
  "readAdminEditDraftValues",
  "resetAdminEditDraft",
  "renderAdminEditPreviewResult",
  'data-admin-action="preview-admin-edit-draft"',
  "초안 검증",
  "fieldsEditable",
  "guardedApply",
]);

assertContains("admin.html", [
  "v133 admin edit input UI",
  ".edit-draft-result",
  ".draft-preview-summary",
  "확인 문구",
]);

assertContains("docs/ADMIN_EDIT_DRAFT_VALIDATION.md", [
  "Admin Edit Draft Validation",
  "POST /api/v1/admin/master-data/edit-preview",
  "DB를 수정하지 않는다",
  "previewAdminEditDraft",
]);

console.log("admin edit draft validation smoke test passed");

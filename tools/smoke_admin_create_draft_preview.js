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

assertContains("src/api/admin-page-readonly.js", [
  "v165.admin-create-apply-limited",
  "renderAdminCreateDraft",
  "data-admin-create-draft",
  "readAdminCreateDraftValues",
  "previewAdminCreateDraft",
  "renderAdminCreatePreviewResult",
  "applyAdminCreateRelationOptionFilter",
  "refreshDependentAdminCreateRelationSelects",
  "createDraftPreviewReady",
]);

assertContains("src/api/game-api-client.js", [
  "previewAdminMasterDataCreate",
  "/admin/master-data/create-preview",
  "dryRun: true",
]);

assertContains("backend/app/services/admin_service_legacy_markers.py", [
  "preview_master_data_create",
  "_empty_create_preview",
  "_exists_duplicate_unique_value",
  "_validate_master_create_relations",
  "duplicate_skill_code_level",
  "owner_code_not_found_for_owner_type",
  "preview-only",
]);

assertContains("backend/app/schemas/admin.py", [
  "AdminMasterDataCreatePreviewRequest",
  "dryRun",
]);

console.log("admin create draft preview smoke test passed");

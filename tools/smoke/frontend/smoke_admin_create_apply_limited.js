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
  "MASTER_CREATE_APPLY_CONFIRM_TEXT",
  "CREATE MASTER DATA ROW",
  "MASTER_CREATE_APPLY_ALLOWED_DOMAINS",
  "characters",
  "enhancementGroups",
  "fieldZones",
  "apply_master_data_create",
  "create_domain_locked",
  "create_confirmation_required",
  "action=\"create\"",
  "MASTER_CREATE_DELETE_CONFIRM_TEXT",
]);

assertContains("backend/app/api/routes/admin_master_data_routes.py", [
  "AdminMasterDataCreateApplyRequest",
  "@router.post(\"/master-data/create-apply\")",
  "apply_admin_master_data_create",
  "ADMIN_WRITE_GUARD_DEP",
  "admin.master_data.create_apply",
]);

assertContains("backend/app/api/routes/admin_route_params.py", [
  "require_admin_write_dev_key",
]);

assertContains("backend/app/schemas/admin.py", [
  "AdminMasterDataCreateApplyRequest",
  "confirmText",
  "dryRun",
]);

assertContains("src/api/game-api-client.js", [
  "applyAdminMasterDataCreate",
  "/admin/master-data/create-apply",
  "confirmText",
  "getAdminWriteHeaders()",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v171.admin-create-delete-restore",
  "ADMIN_CREATE_APPLY_CONFIRM_TEXT",
  "CREATE MASTER DATA ROW",
  "applyAdminCreateDraft",
  "apply-admin-create-draft",
  "data-admin-create-confirm",
  "createApplyUnlocked",
  "createApplyReady",
  "createDeleteRollbackReady",
]);

assertContains("docs/ADMIN_CREATE_APPLY_LIMITED.md", [
  "Admin Create Apply Limited",
  "CREATE MASTER DATA ROW",
  "characters",
  "enhancementGroups",
  "fieldZones",
  "bosses",
  "skills",
  "dropTables",
  "DB reset / seed",
]);

console.log("admin create apply limited smoke test passed");

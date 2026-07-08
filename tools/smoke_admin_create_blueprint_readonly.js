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

assertContains("admin.html", [
  "v162 admin create draft preview",
  "section-create-blueprint",
  "data-admin-create-domain",
  "data-admin-create-blueprint",
  "load-create-blueprint",
  "insert API locked",
]);

assertContains("src/api/game-api-client.js", [
  "fetchAdminMasterCreateBlueprint",
  "/admin/master-data/create-blueprint",
  "previewAdminMasterDataCreate",
  "/admin/master-data/create-preview",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v162.admin-create-draft-preview",
  "readAdminCreateBlueprintFiltersFromDom",
  "renderAdminCreateBlueprint",
  "refreshAdminCreateBlueprint",
  "getAdminCreateBlueprintFieldInputKind",
  "getAdminCreateBlueprintRequiredKeys",
  "getAdminCreateBlueprintDefaultDraft",
  "createBlueprintReady",
  "window.getAdminCreateBlueprintReadiness",
  "readAdminCreateDraftValues",
  "previewAdminCreateDraft",
  "renderAdminCreatePreviewResult",
  "createDraftPreviewReady",
  "preview-admin-create-draft",
  "data-admin-create-draft",
]);

assertContains("docs/ADMIN_CREATE_BLUEPRINT_READONLY.md", [
  "Admin Create Blueprint Read-only",
  "create-blueprint",
  "DB reset / seed",
]);

assertContains("docs/CHANGELOG.md", [
  "v162 - Admin Create Draft Preview",
  "생성 초안",
]);

console.log("admin create blueprint readonly smoke test passed");

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
  "v159 admin create blueprint readonly",
  "section-create-blueprint",
  "data-admin-create-domain",
  "data-admin-create-blueprint",
  "load-create-blueprint",
  "insert API locked",
]);

assertContains("src/api/game-api-client.js", [
  "fetchAdminMasterCreateBlueprint",
  "/admin/master-data/create-blueprint",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v159.admin-create-blueprint-readonly",
  "readAdminCreateBlueprintFiltersFromDom",
  "renderAdminCreateBlueprint",
  "refreshAdminCreateBlueprint",
  "getAdminCreateBlueprintFieldInputKind",
  "getAdminCreateBlueprintRequiredKeys",
  "getAdminCreateBlueprintDefaultDraft",
  "createBlueprintReady",
  "window.getAdminCreateBlueprintReadiness",
]);

assertContains("docs/ADMIN_CREATE_BLUEPRINT_READONLY.md", [
  "Admin Create Blueprint Read-only",
  "create-blueprint",
  "DB reset / seed",
]);

assertContains("docs/CHANGELOG.md", [
  "v159 - Admin Create Blueprint Read-only",
  "신규 row 생성 준비",
]);

console.log("admin create blueprint readonly smoke test passed");

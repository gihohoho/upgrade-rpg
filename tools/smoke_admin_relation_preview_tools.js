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
  "v153.admin-relation-preview-tools",
  "getAdminDraftRelationOptionsForValues",
  "getAdminRelationValueDisplay",
  "formatAdminChangeValueText",
  "renderAdminChangeValueCell",
  "renderAdminRelationOpenButton",
  "getAdminRelationOpenTarget",
  "openAdminMasterDataDetailByCode",
  "open-master-detail-by-code",
  "relationPreviewReady",
  "relationCount",
  "window.formatAdminChangeValueText",
  "window.getAdminRelationValueDisplay",
]);

assertContains("admin.html", [
  "v153 admin relation preview tools",
  "relation-value-cell",
  "relation-jump-btn",
]);

assertContains("docs/ADMIN_RELATION_PREVIEW_TOOLS.md", [
  "Admin Relation Preview Tools",
  "relation label",
  "대상 열기",
  "DB reset / seed",
]);

assertContains("docs/CHANGELOG.md", [
  "v153 - Admin Relation Preview Tools",
  "relation 변경 개수",
]);

console.log("admin relation preview tools smoke test passed");

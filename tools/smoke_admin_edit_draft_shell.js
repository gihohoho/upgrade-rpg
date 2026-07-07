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
  "renderMasterEditDraft",
  "getAdminEditDraftReadiness",
  "data-admin-edit-draft",
  "data-admin-edit-draft-field",
  "변경 저장 잠김",
  "writeLocked: true",
]);

assertContains("admin.html", [
  "admin-jump-nav",
  "#section-master-detail",
  "상세/편집 초안",
  ".edit-draft-grid",
  ".draft-field",
]);

assertContains("docs/ADMIN_EDIT_DRAFT_SHELL.md", [
  "Admin Edit Draft Shell",
  "읽기 전용",
  "getAdminEditDraftReadiness",
  "dryRun=true",
]);

console.log("admin edit draft shell smoke test passed");

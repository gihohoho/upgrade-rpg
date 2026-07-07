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
  "v147.admin-owner-code-relation-tools",
  "getAdminEditImpactHint",
  "buildAdminEditImpactGuide",
  "renderAdminEditImpactGuide",
  "refreshAdminEditImpactGuide",
  "collectLocalDraftChangesForImpact",
  "stackable",
  "인벤토리 겹치기 동작 변경",
  "보스 체력 변경",
  "드랍 확률/수량 변경",
  "data-admin-edit-impact",
  "게임 새로고침",
]);

assertContains("admin.html", [
  "v147 admin owner code relation tools",
  "edit-draft-impact",
  "impact-summary",
  "impact-row",
  "impact-high",
  "인게임 영향 안내",
]);

assertContains("docs/ADMIN_EDIT_IMPACT_GUIDE.md", [
  "Admin Edit Impact Guide",
  "stackable",
  "보스 체력",
  "드랍 확률",
  "DB reset / seed 필요 없음",
]);

console.log("admin edit impact guide smoke test passed");

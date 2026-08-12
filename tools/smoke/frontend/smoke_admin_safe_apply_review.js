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

assertContains("src/api/admin-page-readonly.js", [
  "v165.admin-create-apply-limited",
  "ADMIN_EDIT_HIGH_RISK_CONFIRM_TEXT",
  "HIGH RISK EDIT",
  "buildAdminEditDraftReview",
  "renderAdminEditDraftReview",
  "refreshAdminEditReviewAndImpact",
  "sortAdminChangesByRisk",
  "data-admin-edit-risk-confirm",
  "고위험 변경이 있어서 추가 확인 문구",
  "markSelectedMasterCatalogRow",
  "catalog-row-selected",
]);

assertContains("admin.html", [
  "v165 admin create apply limited",
  "edit-draft-review",
  "draft-review-banner",
  "draft-review-danger",
  "draft-review-row-high",
  "data-admin-master-row-selected",
  "catalog-row-selected",
]);

assertContains("docs/archive/history/ADMIN_AND_BACKEND_HISTORY.md", [
  "Admin Safe Apply Review",
  "HIGH RISK EDIT",
  "before/after",
  "DB reset / seed는 필요 없습니다",
]);

assertContains("docs/archive/history/ADMIN_AND_BACKEND_HISTORY.md", [
  "Admin Catalog Selection Helper",
  "선택됨",
  "markSelectedMasterCatalogRow",
  "DB reset / seed는 필요 없습니다",
]);

console.log("admin safe apply review smoke test passed");

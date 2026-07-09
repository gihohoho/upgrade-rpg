const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");

function read(file) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  return fs.readFileSync(fullPath, "utf8");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function assertContains(file, patterns) {
  const text = read(file);
  for (const pattern of patterns) {
    assert(text.includes(pattern), `${file}: missing pattern ${pattern}`);
  }
}

assertContains("admin.html", [
  "section-admin-js-split-readiness",
  "data-admin-js-split-readiness",
  "v190 edit draft contract",
  "section-master-detail",
  "data-admin-master-detail",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v190.admin-edit-draft-split-contract",
  "v189.1.admin-create-lifecycle-split-hotfix",
  "ADMIN_EDIT_DRAFT_SPLIT_CONTRACT",
  "contract-frozen-v190",
  "src/api/admin/admin-edit-draft.js",
  "requiredApiMethods",
  "requiredWindowExports",
  "dynamicDomTargets",
  "confirmTexts",
  "delegatedActions",
  "getAdminEditDraftSplitContractReadiness",
  "renderAdminEditDraftSplitContractReadiness",
  "editDraftSplitContractReady",
  "editDraftSplitContract",
  "window.getAdminEditDraftSplitContractReadiness",
  "window.renderAdminEditDraftSplitContractReadiness",
]);

assertContains("src/api/admin-page-readonly.js", [
  "previewAdminMasterDataEdit",
  "applyAdminMasterDataEdit",
  "renderMasterEditDraft",
  "readAdminEditDraftValues",
  "resetAdminEditDraft",
  "previewAdminEditDraft",
  "applyAdminEditDraft",
  "renderAdminEditPreviewResult",
  "readAdminEditApplyControls",
  "buildAdminEditDraftReview",
  "renderAdminEditDraftReview",
  "buildAdminEditImpactGuide",
  "renderAdminEditImpactGuide",
  "refreshAdminEditImpactGuide",
  "getAdminRelationEditOptionDefinitions",
  "refreshDependentAdminRelationSelects",
  "APPLY MASTER DATA EDIT",
  "HIGH RISK EDIT",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke_admin_edit_draft_split_contract.js",
]);

assertContains("docs/ADMIN_EDIT_DRAFT_SPLIT_CONTRACT.md", [
  "Admin Edit Draft Split Contract",
  "v190",
  "contract-frozen-v190",
  "src/api/admin/admin-edit-draft.js",
  "DB reset / seed",
]);

console.log("admin edit draft split contract smoke test passed");

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");

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
  "v188 create lifecycle contract",
  "section-create-blueprint",
  "data-admin-create-domain",
  "data-admin-create-blueprint",
  "section-create-lifecycle-guide",
  "data-admin-create-lifecycle-guide",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v188.admin-create-lifecycle-split-contract",
  "v187.admin-change-logs-split",
  "ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT",
  "contract-frozen-v188",
  "src/api/admin/admin-create-lifecycle.js",
  "requiredApiMethods",
  "requiredWindowExports",
  "domTargets",
  "dynamicDomTargets",
  "confirmTexts",
  "delegatedActions",
  "getAdminCreateLifecycleSplitContractReadiness",
  "renderAdminCreateLifecycleSplitContractReadiness",
  "createLifecycleSplitContractReady",
  "createLifecycleSplitContract",
  "window.getAdminCreateLifecycleSplitContractReadiness",
  "window.renderAdminCreateLifecycleSplitContractReadiness",
]);

assertContains("src/api/admin-page-readonly.js", [
  "fetchAdminMasterCreateBlueprint",
  "previewAdminMasterDataCreate",
  "applyAdminMasterDataCreate",
  "readAdminCreateBlueprintFiltersFromDom",
  "refreshAdminCreateBlueprint",
  "renderAdminCreateBlueprint",
  "readAdminCreateDraftValues",
  "previewAdminCreateDraft",
  "applyAdminCreateDraft",
  "renderAdminCreatePreviewResult",
  "renderAdminCreateLifecycleGuide",
  "renderAdminCreateLifecycleDependencyGuards",
  "renderAdminCreateLifecycleBatchResult",
  "runAdminCreateLifecycleBatchCheck",
  "CREATE MASTER DATA ROW",
  "DELETE CREATED MASTER DATA ROW",
  "RESTORE DELETED CREATED ROW",
  "RUN CREATE DELETE RESTORE CHECK",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke/frontend/smoke_admin_create_lifecycle_split_contract.js",
]);

assertContains("docs/archive/stage-notes/ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT.md", [
  "Admin Create Lifecycle Split Contract",
  "v188",
  "contract-frozen-v188",
  "src/api/admin/admin-create-lifecycle.js",
  "DB reset / seed",
]);

console.log("admin create lifecycle split contract smoke test passed");

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

assertContains("src/api/admin/admin-create-lifecycle.js", [
  "v189.admin-create-lifecycle-split",
  "RpgAdminCreateLifecycle",
  "configure",
  "getReadiness",
  "ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT",
  "extracted-v189",
  "renderAdminCreateBlueprint",
  "refreshAdminCreateBlueprint",
  "readAdminCreateDraftValues",
  "previewAdminCreateDraft",
  "applyAdminCreateDraft",
  "renderAdminCreatePreviewResult",
  "renderAdminCreateLifecycleGuide",
  "renderAdminCreateLifecycleDependencyGuards",
  "renderAdminCreateLifecycleBatchResult",
  "runAdminCreateLifecycleBatchCheck",
  "renderAdminOperationResultBanner",
  "renderAdminCreateDeleteBlockerSummary",
  "getAdminCreateLifecycleSplitContractReadiness",
  "renderAdminCreateLifecycleSplitContractReadiness",
  "RUN CREATE DELETE RESTORE CHECK",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v189.admin-create-lifecycle-split",
  "getAdminCreateLifecycleApi",
  "configureAdminCreateLifecycle",
  "getAdminCreateLifecycleReadiness",
  "createLifecycleExternalReady",
  "window.getAdminCreateLifecycleReadiness",
  "RpgAdminCreateLifecycle",
  "admin/admin-create-lifecycle.js",
]);

assertContains("admin.html", [
  "src/api/admin/admin-change-logs.js",
  "src/api/admin/admin-create-lifecycle.js",
  "src/api/admin-page-readonly.js",
]);

const adminHtml = read("admin.html");
const order = [
  "src/api/game-api-client.js",
  "src/api/admin-layout-shell.js",
  "src/api/admin/admin-change-logs.js",
  "src/api/admin/admin-create-lifecycle.js",
  "src/api/admin-page-readonly.js",
].map((needle) => adminHtml.indexOf(needle));
if (order.some((index) => index < 0)) throw new Error("admin.html: missing expected admin script source");
for (let i = 1; i < order.length; i += 1) {
  if (order[i - 1] >= order[i]) throw new Error("admin.html: admin script order is not safe for create lifecycle split");
}

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke_admin_create_lifecycle_split.js",
]);

console.log("admin create lifecycle split smoke test passed");

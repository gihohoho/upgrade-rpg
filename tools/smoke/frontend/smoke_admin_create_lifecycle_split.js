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

assertContains("src/api/admin/admin-create-lifecycle.js", [
  "v189.1.admin-create-lifecycle-split-hotfix",
  "RpgAdminCreateLifecycle",
  "configure",
  "getReadiness",
  "ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT",
  "extracted-v189",
  "readAdminCreateBlueprintFiltersFromDom",
  "syncAdminCreateDomainFromCatalog",
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
  "v189.1.admin-create-lifecycle-split-hotfix",
  "getAdminCreateLifecycleApi",
  "configureAdminCreateLifecycle",
  "getAdminCreateLifecycleReadiness",
  "createLifecycleExternalReady",
  "window.getAdminCreateLifecycleReadiness",
  "RpgAdminCreateLifecycle",
  "createLifecycle.version === \"v189.1.admin-create-lifecycle-split-hotfix\"",
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
  "node tools/smoke/frontend/smoke_admin_create_lifecycle_split.js",
]);


const vm = require("vm");
const createLifecycleText = read("src/api/admin/admin-create-lifecycle.js");
const fakeElements = new Map([
  ["[data-admin-create-domain]", { value: "skillLevels" }],
  ["[data-admin-master-domain]", { value: "itemTemplates" }],
  ["[data-admin-create-blueprint]", { innerHTML: "" }],
  ["[data-admin-create-draft]", { querySelectorAll: () => [] }],
]);
const sandbox = {
  window: {},
  document: {
    querySelector(selector) {
      return fakeElements.get(selector) || null;
    },
    querySelectorAll() {
      return [];
    },
  },
  console,
  setTimeout,
  clearTimeout,
};
sandbox.window = sandbox;
sandbox.RpgGameApi = {
  fetchAdminMasterCreateBlueprint() {},
  previewAdminMasterDataCreate() {},
  applyAdminMasterDataCreate() {},
  previewAdminCreateDeleteRollback() {},
  applyAdminCreateDeleteRollback() {},
  previewAdminCreateDeleteRestore() {},
  applyAdminCreateDeleteRestore() {},
};
vm.createContext(sandbox);
vm.runInContext(createLifecycleText, sandbox, { filename: "src/api/admin/admin-create-lifecycle.js" });
if (!sandbox.RpgAdminCreateLifecycle) throw new Error("RpgAdminCreateLifecycle was not registered on window");
sandbox.RpgAdminCreateLifecycle.configure({
  querySelector: sandbox.document.querySelector.bind(sandbox.document),
  DEFAULT_MASTER_DOMAIN: "itemTemplates",
});
const filters = sandbox.RpgAdminCreateLifecycle.readAdminCreateBlueprintFiltersFromDom();
if (!filters || filters.domain !== "skillLevels") throw new Error("create lifecycle split: blueprint filter reader did not work after extraction");
const readiness = sandbox.RpgAdminCreateLifecycle.getAdminCreateBlueprintReadiness();
if (!readiness || readiness.domain !== "skillLevels") throw new Error("create lifecycle split: blueprint readiness should not throw and should return selected domain");
const syncFilters = sandbox.RpgAdminCreateLifecycle.syncAdminCreateDomainFromCatalog();
if (!syncFilters || syncFilters.domain !== "itemTemplates") throw new Error("create lifecycle split: catalog domain sync did not return synced domain");

console.log("admin create lifecycle split smoke test passed");

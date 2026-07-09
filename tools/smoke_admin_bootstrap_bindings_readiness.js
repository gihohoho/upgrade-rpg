const fs = require("fs");
const path = require("path");
const vm = require("vm");

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

const expectedActions = [
  "refresh",
  "apply-snapshot-filters",
  "apply-master-catalog-filters",
  "load-create-blueprint",
  "sync-create-domain-from-catalog",
  "preview-admin-create-draft",
  "reset-admin-create-draft",
  "apply-admin-create-draft",
  "run-create-lifecycle-batch-check",
  "master-catalog-first-page",
  "master-catalog-prev-page",
  "master-catalog-next-page",
  "master-catalog-last-page",
  "apply-change-log-filters",
  "set-change-log-action-filter",
  "open-master-detail",
  "open-master-detail-by-code",
  "open-master-relations",
  "preview-admin-edit-draft",
  "apply-admin-edit-draft",
  "refresh-admin-change-logs",
  "open-admin-change-log-detail",
  "preview-admin-change-log-rollback",
  "apply-admin-change-log-rollback",
  "preview-admin-create-delete",
  "apply-admin-create-delete",
  "preview-admin-create-delete-restore",
  "apply-admin-create-delete-restore",
  "verify-master-api-target",
  "reset-admin-edit-draft",
  "reset-master-catalog-filters",
  "reset-snapshot-filters",
  "reset-change-log-filters",
  "save-admin-write-dev-key",
  "clear-admin-write-dev-key",
  "save-api-base-url",
  "reset-api-base-url",
  "copy-admin-url",
];

assertContains("src/api/admin-page-readonly.js", [
  "v194.admin-bootstrap-bindings-readiness",
  "ADMIN_BOOTSTRAP_BINDING_CONTRACT",
  "contract-frozen-v194",
  "getAdminBootstrapBindingReadiness",
  "renderAdminBootstrapBindingReadiness",
  "bootstrapBindingReady",
  "bootstrap/bindEvents 계약 고정 완료",
  "window.getAdminBootstrapBindingReadiness",
  "window.renderAdminBootstrapBindingReadiness",
]);

assertContains("src/api/admin-page-readonly.js", expectedActions.map((action) => `action === "${action}"`));
assertContains("src/api/admin-page-readonly.js", expectedActions.map((action) => `"${action}"`));
assertContains("src/api/admin-page-readonly.js", [
  "document.addEventListener(\"input\"",
  "document.addEventListener(\"keydown\"",
  "document.addEventListener(\"change\"",
  "document.addEventListener(\"click\"",
  "document.addEventListener(\"DOMContentLoaded\"",
  "bindEvents();",
  "initializeAdminLayoutShell();",
  "renderAdminJsSplitReadiness();",
  "refreshAdminReadOnlyPage();",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke_admin_bootstrap_bindings_readiness.js",
]);

const adminPageText = read("src/api/admin-page-readonly.js");
const scripts = [
  "src/api/game-api-client.js",
  "src/api/admin-layout-shell.js",
  "src/api/admin/admin-change-logs.js",
  "src/api/admin/admin-create-lifecycle.js",
  "src/api/admin/admin-edit-draft.js",
  "src/api/admin/admin-master-catalog.js",
  "src/api/admin/admin-overview-snapshots.js",
  "src/api/admin-page-readonly.js",
];
const domSelectors = new Set([
  "[data-admin-cards]",
  "[data-admin-status]",
  "[data-admin-current-url]",
  "[data-admin-js-split-readiness]",
  "[data-admin-master-domain]",
  "[data-admin-create-domain]",
  "[data-admin-write-dev-key]",
  "[data-admin-api-base-url]",
]);
const staticActionElements = expectedActions.slice(0, 8).map((action) => ({
  getAttribute(name) {
    return name === "data-admin-action" ? action : null;
  },
}));
const fakeDocument = {
  readyState: "loading",
  addEventListener() {},
  querySelector(selector) {
    return domSelectors.has(selector) ? { value: "", innerHTML: "", textContent: "" } : null;
  },
  querySelectorAll(selector) {
    if (selector === "script[src]") {
      return scripts.map((src) => ({ getAttribute: (name) => (name === "src" ? src : null) }));
    }
    if (selector === "[data-admin-action]") return staticActionElements;
    return [];
  },
};

function makeModule(version) {
  return {
    VERSION: version,
    configure() {},
    getReadiness() { return { ok: true, version }; },
  };
}

const gameApiMethods = [
  "fetchAdminOverview",
  "listAdminSaveSnapshots",
  "listAdminMasterCatalogDomains",
  "listAdminMasterCatalogRows",
  "fetchAdminMasterCreateBlueprint",
  "previewAdminMasterDataCreate",
  "applyAdminMasterDataCreate",
  "fetchAdminMasterDataDetail",
  "fetchAdminMasterDataRelations",
  "previewAdminMasterDataEdit",
  "applyAdminMasterDataEdit",
  "listAdminChangeLogs",
  "fetchAdminChangeLogDetail",
  "previewAdminChangeLogRollback",
  "applyAdminChangeLogRollback",
  "previewAdminCreateDeleteRollback",
  "applyAdminCreateDeleteRollback",
  "previewAdminCreateDeleteRestore",
  "applyAdminCreateDeleteRestore",
  "fetchMasterData",
  "setAdminWriteDevKey",
  "hasAdminWriteDevKey",
];
const RpgGameApi = Object.fromEntries(gameApiMethods.map((key) => [key, () => ({})]));
RpgGameApi.hasAdminWriteDevKey = () => false;

const sandbox = {
  window: {},
  document: fakeDocument,
  console,
  navigator: { clipboard: { writeText() {} } },
  URL,
};
sandbox.window = sandbox;
sandbox.location = { href: "http://localhost/admin.html" };
sandbox.RpgGameApi = RpgGameApi;
sandbox.RpgAdminLayoutShell = {
  VERSION: "v185.admin-layout-shell-split",
  configure() {},
  getAdminLayoutShellReadiness() { return { ok: true, version: "v185.admin-layout-shell-split" }; },
  initializeAdminLayoutShell() {},
  getAdminDefaultCollapsedSectionKeys() { return []; },
  updateAdminStickyLayoutOffsets() {},
  setAdminSectionCollapsed() {},
  setAdminActiveSidebarLink() {},
};
sandbox.RpgAdminChangeLogs = makeModule("v187.admin-change-logs-split");
sandbox.RpgAdminCreateLifecycle = Object.assign(makeModule("v189.1.admin-create-lifecycle-split-hotfix"), {
  getAdminCreateLifecycleSplitContractReadiness() { return { ok: true, status: "contract-frozen-v188", requiredApiMethods: [], requiredWindowExports: [], domTargets: [], dynamicDomTargets: [], confirmTexts: [], delegatedActions: [], splitBoundary: [], missingApiMethods: [], missingWindowExports: [], missingDomTargets: [], missingConfirmTexts: [], apiMethodCount: 0, windowExportCount: 0, domTargetCount: 0, dynamicDomTargetCount: 0, confirmTextCount: 0, delegatedActionCount: 0, currentFile: "", nextFile: "" }; },
  renderAdminCreateLifecycleSplitContractReadiness() { return ""; },
});
sandbox.RpgAdminEditDraft = makeModule("v191.admin-edit-draft-split");
sandbox.RpgAdminMasterCatalog = makeModule("v192.admin-master-catalog-detail-split");
sandbox.RpgAdminOverviewSnapshots = makeModule("v193.admin-overview-snapshots-split");

vm.createContext(sandbox);
vm.runInContext(adminPageText, sandbox, { filename: "src/api/admin-page-readonly.js" });
assert(typeof sandbox.getAdminBootstrapBindingReadiness === "function", "global getAdminBootstrapBindingReadiness should be exported");
const readiness = sandbox.getAdminBootstrapBindingReadiness();
assert(readiness.ok, `bootstrap binding readiness should be ok: ${JSON.stringify(readiness)}`);
assert(readiness.status === "contract-frozen-v194", "bootstrap binding status should be frozen for v194");
assert(readiness.delegatedActionCount === expectedActions.length, "delegated action count should match expected action map");
assert(readiness.staticActionCount === staticActionElements.length, "static action count should be collected from DOM");
assert(readiness.unknownStaticActions.length === 0, "static HTML actions should all be represented in contract");
assert(sandbox.RpgAdminReadOnlyPage.VERSION === "v194.admin-bootstrap-bindings-readiness", "RpgAdminReadOnlyPage should expose v194 version");

console.log("admin bootstrap/bindEvents readiness smoke test passed");

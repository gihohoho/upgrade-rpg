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
  "v197.admin-settings-helpers-split",
  "ADMIN_THIN_ENTRY_CLEANUP_CONTRACT",
  "cleaned-v195",
  "centralized-map-v195",
  "getAdminClickActionHandlers",
  "handleAdminClickAction",
  "registerAdminReadOnlyPageExports",
  "configureAdminExternalModules",
  "getAdminThinEntryCleanupReadiness",
  "renderAdminThinEntryCleanupReadiness",
  "thinEntryCleanupReady",
  "window.getAdminThinEntryCleanupReadiness",
]);

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke_admin_thin_entry_cleanup.js",
]);

const text = read("src/api/admin-page-readonly.js");
for (const action of expectedActions) {
  assert(text.includes(`"${action}":`), `action handler map should include ${action}`);
}
assert(text.includes("ADMIN_CLICK_ACTION_LEGACY_SMOKE_MARKERS"), "legacy action smoke marker should remain");
assert(text.includes("function registerAdminReadOnlyPageExports()"), "window export registration should be grouped");
assert(text.includes("function configureAdminExternalModules()"), "external module configure calls should be grouped");

const scripts = [
  "src/api/game-api-client.js",
  "src/api/admin-layout-shell.js",
  "src/api/admin/admin-field-help.js",
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
const staticActionElements = expectedActions.map((action) => ({
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
sandbox.RpgAdminFieldHelp = Object.assign(makeModule("v196.admin-field-help-split"), {
  getAdminFieldHelp() { return null; },
  listAdminFieldHelp() { return []; },
  renderFieldHelpBadge() { return ""; },
  renderFieldHelpInline() { return ""; },
  getAdminFieldValueHint() { return null; },
  renderFieldValueHintInline() { return ""; },
  formatValueWithFieldHint(_key, value) { return String(value ?? ""); },
  getAdminEquipSlotDisplayName(value) { return String(value || ""); },
});
sandbox.RpgAdminChangeLogs = makeModule("v187.admin-change-logs-split");
sandbox.RpgAdminCreateLifecycle = Object.assign(makeModule("v189.1.admin-create-lifecycle-split-hotfix"), {
  getAdminCreateLifecycleSplitContractReadiness() { return { ok: true, status: "contract-frozen-v188", requiredApiMethods: [], requiredWindowExports: [], domTargets: [], dynamicDomTargets: [], confirmTexts: [], delegatedActions: [], splitBoundary: [], missingApiMethods: [], missingWindowExports: [], missingDomTargets: [], missingConfirmTexts: [], apiMethodCount: 0, windowExportCount: 0, domTargetCount: 0, dynamicDomTargetCount: 0, confirmTextCount: 0, delegatedActionCount: 0, currentFile: "", nextFile: "" }; },
  renderAdminCreateLifecycleSplitContractReadiness() { return ""; },
});
sandbox.RpgAdminEditDraft = makeModule("v191.admin-edit-draft-split");
sandbox.RpgAdminMasterCatalog = makeModule("v192.admin-master-catalog-detail-split");
sandbox.RpgAdminOverviewSnapshots = makeModule("v193.admin-overview-snapshots-split");
sandbox.RpgAdminSettingsHelpers = Object.assign(makeModule("v197.admin-settings-helpers-split"), {
  getApiInput() { return fakeDocument.querySelector("[data-admin-api-base-url]"); },
  buildSiblingPageUrl(fileName) { return `http://localhost/${fileName}`; },
  getCurrentAdminPageUrl() { return "http://localhost/admin.html"; },
  getGamePageUrl() { return "http://localhost/index.html"; },
  syncLocationHints() {},
  copyCurrentAdminPageUrl() { return { ok: true, copied: true }; },
  syncApiInput() {},
  getAdminWriteKeyInput() { return fakeDocument.querySelector("[data-admin-write-dev-key]"); },
  hasAdminWriteDevKey() { return false; },
  renderAdminWriteKeyStatus() {},
  syncAdminWriteDevKeyInput() {},
  saveAdminWriteDevKeyFromInput() { return "local-admin-dev-key"; },
  clearAdminWriteDevKey() { return ""; },
  requireAdminWriteDevKeyForUi() { return true; },
  saveApiBaseUrlFromInput() { return "http://localhost:8000"; },
  resetApiBaseUrl() { return "http://localhost:8000"; },
});

vm.createContext(sandbox);
vm.runInContext(text, sandbox, { filename: "src/api/admin-page-readonly.js" });
assert(sandbox.RpgAdminReadOnlyPage.VERSION === "v212.backend-admin-route-data-meta-helpers", "RpgAdminReadOnlyPage should expose v212 version");
assert(typeof sandbox.getAdminClickActionHandlers === "function", "getAdminClickActionHandlers should be exported");
const handlers = sandbox.getAdminClickActionHandlers();
for (const action of expectedActions) {
  assert(typeof handlers[action] === "function", `runtime action handler missing ${action}`);
}
assert(Object.keys(handlers).length === expectedActions.length, "runtime action handler count should match contract action count");
const readiness = sandbox.getAdminThinEntryCleanupReadiness();
assert(readiness.ok, `thin entry cleanup readiness should be ok: ${JSON.stringify(readiness)}`);
assert(readiness.status === "cleaned-v195", "thin entry cleanup status should be cleaned-v195");
assert(readiness.actionHandlerMode === "centralized-map-v195", "action handler mode should be centralized-map-v195");
assert(readiness.actionHandlerCount === readiness.delegatedActionCount, "action handler count should match delegated action count");
assert(text.includes("thinEntryCleanupReady"), "page readiness should include thinEntryCleanupReady field");

console.log("admin thin entry cleanup smoke test passed");

const fs = require("fs");
const path = require("path");
const vm = require("vm");

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

assertContains("src/api/admin/admin-master-catalog.js", [
  "v192.admin-master-catalog-detail-split",
  "RpgAdminMasterCatalog",
  "configure",
  "getReadiness",
  "readMasterCatalogFiltersFromDom",
  "resetMasterCatalogFilters",
  "describeMasterCatalogFilters",
  "syncMasterDomainOptions",
  "renderMasterTable",
  "renderMasterCatalogTable",
  "openAdminMasterDataDetail",
  "openAdminMasterDataDetailByCode",
  "openAdminMasterDataRelations",
  "verifySelectedMasterDataApi",
  "runPostWriteMasterApiVerification",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v192.admin-master-catalog-detail-split",
  "getAdminMasterCatalogApi",
  "configureAdminMasterCatalog",
  "getAdminMasterCatalogExternalReadiness",
  "masterCatalogExternalReady",
  "RpgAdminMasterCatalog",
  "masterCatalogExternal.version === \"v192.admin-master-catalog-detail-split\"",
  "window.getAdminMasterCatalogExternalReadiness",
  "admin/admin-master-catalog.js",
]);

assertContains("admin.html", [
  "src/api/admin/admin-change-logs.js",
  "src/api/admin/admin-create-lifecycle.js",
  "src/api/admin/admin-edit-draft.js",
  "src/api/admin/admin-master-catalog.js",
  "src/api/admin-page-readonly.js",
]);

const adminHtml = read("admin.html");
const order = [
  "src/api/game-api-client.js",
  "src/api/admin-layout-shell.js",
  "src/api/admin/admin-change-logs.js",
  "src/api/admin/admin-create-lifecycle.js",
  "src/api/admin/admin-edit-draft.js",
  "src/api/admin/admin-master-catalog.js",
  "src/api/admin-page-readonly.js",
].map((needle) => adminHtml.indexOf(needle));
assert(!order.some((index) => index < 0), "admin.html: missing expected admin script source");
for (let i = 1; i < order.length; i += 1) {
  assert(order[i - 1] < order[i], "admin.html: admin script order is not safe for master catalog split");
}

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke/frontend/smoke_admin_master_catalog_split.js",
]);

const masterCatalogText = read("src/api/admin/admin-master-catalog.js");
const fakeElements = new Map([
  ["[data-admin-master-domain]", { value: "skills", innerHTML: "" }],
  ["[data-admin-master-limit]", { value: "10" }],
  ["[data-admin-master-query]", { value: "fire" }],
  ["[data-admin-master-enabled]", { value: "all" }],
  ["[data-admin-master-sort]", { value: "id_asc" }],
  ["[data-admin-master-page]", { value: "2" }],
  ["[data-admin-master-catalog-table]", { innerHTML: "" }],
  ["[data-admin-master-detail]", { innerHTML: "" }],
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
  listAdminMasterCatalogRows() {},
  fetchAdminMasterDataDetail() {},
  fetchAdminMasterDataRelations() {},
  fetchMasterData() {},
};
vm.createContext(sandbox);
vm.runInContext(masterCatalogText, sandbox, { filename: "src/api/admin/admin-master-catalog.js" });
assert(sandbox.RpgAdminMasterCatalog, "RpgAdminMasterCatalog was not registered on window");
sandbox.RpgAdminMasterCatalog.configure({
  querySelector: sandbox.document.querySelector.bind(sandbox.document),
  DEFAULT_MASTER_DOMAIN: "itemTemplates",
  DEFAULT_MASTER_LIMIT: 10,
  DEFAULT_MASTER_SORT: "id_asc",
});
const readiness = sandbox.RpgAdminMasterCatalog.getReadiness({ log: false });
assert(readiness && readiness.version === "v192.admin-master-catalog-detail-split", "master catalog readiness should return v192 version");
assert(readiness.ok === true, "master catalog readiness should be ok with fake DOM/API");
const filters = sandbox.RpgAdminMasterCatalog.readMasterCatalogFiltersFromDom();
assert(filters.domain === "skills" && filters.page === 2 && filters.query === "fire", "master catalog filters should be read from fake DOM");
const described = sandbox.RpgAdminMasterCatalog.describeMasterCatalogFilters(filters);
assert(described.includes("domain=skills") && described.includes("query=fire") && described.includes("page=2"), "master catalog filter description should include active values");

console.log("admin master catalog/detail split smoke test passed");

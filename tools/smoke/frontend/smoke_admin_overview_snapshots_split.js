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

assertContains("src/api/admin/admin-overview-snapshots.js", [
  "v193.admin-overview-snapshots-split",
  "RpgAdminOverviewSnapshots",
  "configure",
  "getReadiness",
  "readSnapshotFiltersFromDom",
  "resetSnapshotFilters",
  "describeSnapshotFilters",
  "renderAdminOverviewCards",
  "renderAdminSnapshotTable",
  "renderAdminReadiness",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v193.admin-overview-snapshots-split",
  "getAdminOverviewSnapshotsApi",
  "configureAdminOverviewSnapshots",
  "getAdminOverviewSnapshotsExternalReadiness",
  "overviewSnapshotsExternalReady",
  "RpgAdminOverviewSnapshots",
  "overviewSnapshotsExternal.version === \"v193.admin-overview-snapshots-split\"",
  "window.getAdminOverviewSnapshotsExternalReadiness",
  "admin/admin-overview-snapshots.js",
]);

assertContains("admin.html", [
  "src/api/admin/admin-master-catalog.js",
  "src/api/admin/admin-overview-snapshots.js",
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
  "src/api/admin/admin-overview-snapshots.js",
  "src/api/admin-page-readonly.js",
].map((needle) => adminHtml.indexOf(needle));
assert(!order.some((index) => index < 0), "admin.html: missing expected admin script source");
for (let i = 1; i < order.length; i += 1) {
  assert(order[i - 1] < order[i], "admin.html: admin script order is not safe for overview/snapshots split");
}

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke/frontend/smoke_admin_overview_snapshots_split.js",
]);

const overviewText = read("src/api/admin/admin-overview-snapshots.js");
const fakeElements = new Map([
  ["[data-admin-filter-limit]", { value: "10" }],
  ["[data-admin-filter-user-id]", { value: "7" }],
  ["[data-admin-filter-slot-key]", { value: "slotA" }],
  ["[data-admin-filter-source]", { value: "manual" }],
  ["[data-admin-filter-default-only]", { checked: true }],
  ["[data-admin-filter-sort]", { value: "updated_asc" }],
  ["[data-admin-cards]", { innerHTML: "" }],
  ["[data-admin-snapshot-table]", { innerHTML: "" }],
  ["[data-admin-snapshot-meta]", { textContent: "" }],
  ["[data-admin-readiness]", { innerHTML: "" }],
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
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(overviewText, sandbox, { filename: "src/api/admin/admin-overview-snapshots.js" });
assert(sandbox.RpgAdminOverviewSnapshots, "RpgAdminOverviewSnapshots was not registered on window");
sandbox.RpgAdminOverviewSnapshots.configure({
  querySelector: sandbox.document.querySelector.bind(sandbox.document),
  DEFAULT_SNAPSHOT_LIMIT: 30,
  DEFAULT_SNAPSHOT_SORT: "updated_desc",
  formatValue: (value) => (value === null || value === undefined || value === "" ? "-" : String(value)),
  formatClock: (value) => (value ? `clock:${value}` : "-"),
  hasAdminWriteDevKey: () => true,
});
const filters = sandbox.RpgAdminOverviewSnapshots.readSnapshotFiltersFromDom();
assert(filters.limit === 10, "snapshot filters should read limit from DOM");
assert(filters.userId === 7, "snapshot filters should read userId from DOM");
assert(filters.slotKey === "slotA", "snapshot filters should read slotKey from DOM");
assert(filters.source === "manual", "snapshot filters should read source from DOM");
assert(filters.defaultOnly === true, "snapshot filters should read defaultOnly from DOM");
assert(filters.sort === "updated_asc", "snapshot filters should read sort from DOM");
assert(sandbox.RpgAdminOverviewSnapshots.describeSnapshotFilters(filters).includes("userId=7"), "snapshot filters should be describable");
sandbox.RpgAdminOverviewSnapshots.resetSnapshotFilters({ silent: true });
assert(fakeElements.get("[data-admin-filter-limit]").value === "30", "reset should restore default snapshot limit");
sandbox.RpgAdminOverviewSnapshots.renderAdminOverviewCards({
  readOnly: true,
  masterData: { summary: { totalRows: 12 } },
  saveSnapshots: { totalSlots: 3, usersWithSaves: 2, latestUpdatedAt: "2026-01-01T00:00:00Z" },
  users: { total: 4, admins: 1 },
  readiness: { safeForAdminWriteUi: false, guardedMasterEditApplyReady: true, guardedRollbackReady: true },
});
assert(fakeElements.get("[data-admin-cards]").innerHTML.includes("마스터 행 수"), "overview cards should render into target");
sandbox.RpgAdminOverviewSnapshots.renderAdminSnapshotTable({
  total: 1,
  totalAll: 1,
  filters: {},
  snapshots: [{ id: 1, userId: 7, slotKey: "slotA", isDefault: true, saveVersion: "v1", summary: { gold: 100, level: 2 }, counts: { inventoryItems: 3, storageItems: 4 }, source: "manual", rawSnapshotReturned: false, updatedAt: "2026-01-01T00:00:00Z" }],
});
assert(fakeElements.get("[data-admin-snapshot-table]").innerHTML.includes("slotA"), "snapshot table should render rows");
sandbox.RpgAdminOverviewSnapshots.renderAdminReadiness({
  safeForAdminReadOnlyUi: true,
  safeForAdminWriteUi: false,
  guardedMasterEditApplyReady: true,
  guardedRollbackReady: true,
  warnings: [],
});
assert(fakeElements.get("[data-admin-readiness]").innerHTML.includes("read-only UI"), "readiness should render into target");
const readiness = sandbox.RpgAdminOverviewSnapshots.getReadiness({ log: false });
assert(readiness && readiness.ok, "overview/snapshots readiness should be ok after configure");
assert(readiness.version === "v193.admin-overview-snapshots-split", "overview/snapshots readiness should return v193 version");

console.log("admin overview/snapshots split smoke test passed");

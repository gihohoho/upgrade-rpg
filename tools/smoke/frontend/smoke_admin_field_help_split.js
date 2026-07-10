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

assertContains("src/api/admin/admin-field-help.js", [
  "v196.admin-field-help-split",
  "RpgAdminFieldHelp",
  "ADMIN_FIELD_HELP_DEFINITIONS",
  "ADMIN_EQUIP_SLOT_PRESET_LABELS",
  "getAdminFieldHelp",
  "listAdminFieldHelp",
  "renderFieldHelpBadge",
  "renderFieldHelpInline",
  "getAdminFieldValueHint",
  "renderFieldValueHintInline",
  "formatValueWithFieldHint",
  "getAdminEquipSlotDisplayName",
  "grade / 등급 숫자",
  "기존 JS 아이템의 tier 값을 옮겨 담은 숫자형 진행 등급",
  '"6": "특수무기"',
  '"14": "휘장"',
]);

assertContains("src/api/admin-page-readonly.js", [
  "v196.admin-field-help-split",
  "getAdminFieldHelpApi",
  "configureAdminFieldHelp",
  "getAdminFieldHelpExternalReadiness",
  "fieldHelpExternalReady",
  "RpgAdminFieldHelp",
  "ADMIN_FIELD_HELP_EXTERNAL_IMPL_MARKERS",
]);

assertContains("admin.html", [
  "src/api/admin/admin-field-help.js",
  "src/api/admin/admin-change-logs.js",
  "src/api/admin-page-readonly.js",
]);

const adminHtml = read("admin.html");
const order = [
  "src/api/game-api-client.js",
  "src/api/admin-layout-shell.js",
  "src/api/admin/admin-field-help.js",
  "src/api/admin/admin-change-logs.js",
  "src/api/admin/admin-create-lifecycle.js",
  "src/api/admin/admin-edit-draft.js",
  "src/api/admin/admin-master-catalog.js",
  "src/api/admin/admin-overview-snapshots.js",
  "src/api/admin-page-readonly.js",
].map((needle) => adminHtml.indexOf(needle));
assert(!order.some((index) => index < 0), "admin.html: missing expected admin script source");
for (let i = 1; i < order.length; i += 1) {
  assert(order[i - 1] < order[i], "admin.html: admin script order is not safe for field help split");
}

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke/frontend/smoke_admin_field_help_split.js",
]);

const fieldHelpText = read("src/api/admin/admin-field-help.js");
const sandbox = {
  window: {},
  document: {},
  console,
};
sandbox.window = sandbox;
vm.createContext(sandbox);
vm.runInContext(fieldHelpText, sandbox, { filename: "src/api/admin/admin-field-help.js" });
assert(sandbox.RpgAdminFieldHelp, "RpgAdminFieldHelp was not registered on window");
const api = sandbox.RpgAdminFieldHelp;
api.configure({
  escapeHtml(value) {
    return String(value === null || value === undefined ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");
  },
  formatValue(value) {
    return value === null || value === undefined || value === "" ? "-" : String(value);
  },
});
assert(api.VERSION === "v196.admin-field-help-split", "field help module should expose v196 version");
assert(api.getAdminFieldHelp("admin_note").title.includes("관리자 메모"), "admin_note help should be available");
assert(api.listAdminFieldHelp().length >= 10, "field help list should include known definitions");
assert(api.renderFieldHelpBadge("grade").includes("field-help-badge"), "field help badge should render");
assert(api.renderFieldHelpInline("grade").includes("field-help-inline"), "field help inline should render");
assert(api.getAdminFieldValueHint("grade", 12).label === "tier 12", "grade value hint should explain tier value");
assert(api.getAdminFieldValueHint("equip_slot", "14").label.includes("휘장"), "equip_slot hint should use label map");
assert(api.getAdminEquipSlotDisplayName("6") === "특수무기", "special weapon slot label should resolve");
assert(api.getAdminEquipSlotDisplayName("14") === "휘장", "emblem slot label should resolve");
assert(api.formatValueWithFieldHint("grade", 1).includes("field-value-hint"), "formatValueWithFieldHint should append hint html");
const readiness = api.getReadiness({ log: false });
assert(readiness.ok, `field help readiness should be ok: ${JSON.stringify(readiness)}`);
assert(readiness.version === "v196.admin-field-help-split", "field help readiness should return v196 version");

console.log("admin field help split smoke test passed");

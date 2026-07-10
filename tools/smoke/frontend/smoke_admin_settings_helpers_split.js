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

assertContains("src/api/admin/admin-settings-helpers.js", [
  "v197.admin-settings-helpers-split",
  "RpgAdminSettingsHelpers",
  "getCurrentAdminPageUrl",
  "getGamePageUrl",
  "syncLocationHints",
  "copyCurrentAdminPageUrl",
  "syncApiInput",
  "saveApiBaseUrlFromInput",
  "resetApiBaseUrl",
  "syncAdminWriteDevKeyInput",
  "saveAdminWriteDevKeyFromInput",
  "clearAdminWriteDevKey",
  "requireAdminWriteDevKeyForUi",
  "ADMIN_WRITE_DEV_KEY_EXAMPLE",
  "local-admin-dev-key",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v197.admin-settings-helpers-split",
  "getAdminSettingsHelpersApi",
  "configureAdminSettingsHelpers",
  "getAdminSettingsHelpersExternalReadiness",
  "settingsHelpersExternalReady",
  "RpgAdminSettingsHelpers",
  "src/api/admin/admin-settings-helpers.js",
]);

assertContains("admin.html", [
  "src/api/admin/admin-field-help.js",
  "src/api/admin/admin-settings-helpers.js",
  "src/api/admin/admin-change-logs.js",
  "src/api/admin-page-readonly.js",
]);

const adminHtml = read("admin.html");
const order = [
  "src/api/game-api-client.js",
  "src/api/admin-layout-shell.js",
  "src/api/admin/admin-field-help.js",
  "src/api/admin/admin-settings-helpers.js",
  "src/api/admin/admin-change-logs.js",
  "src/api/admin/admin-create-lifecycle.js",
  "src/api/admin/admin-edit-draft.js",
  "src/api/admin/admin-master-catalog.js",
  "src/api/admin/admin-overview-snapshots.js",
  "src/api/admin-page-readonly.js",
].map((needle) => adminHtml.indexOf(needle));
assert(!order.some((index) => index < 0), "admin.html: missing expected admin script source");
for (let i = 1; i < order.length; i += 1) {
  assert(order[i - 1] < order[i], "admin.html: admin script order is not safe for settings helper split");
}

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke/frontend/smoke_admin_settings_helpers_split.js",
]);

const elements = new Map();
function makeElement(initial) {
  return Object.assign({
    value: "",
    textContent: "",
    innerHTML: "",
    href: "",
    checked: false,
    style: {},
    setAttribute(name, value) { this[name] = value; },
    select() { this.selected = true; },
  }, initial || {});
}
[
  "[data-admin-current-url]",
  "[data-admin-game-url]",
  "[data-admin-api-base-url]",
  "[data-admin-write-dev-key]",
  "[data-admin-write-key-status]",
  "[data-admin-status]",
  "[data-admin-edit-draft-result]",
].forEach((selector) => elements.set(selector, makeElement()));

elements.get("[data-admin-api-base-url]").value = "http://localhost:9000";
elements.get("[data-admin-write-dev-key]").value = "local-admin-dev-key";

const fakeDocument = {
  querySelector(selector) {
    return elements.get(selector) || null;
  },
  createElement() {
    return makeElement();
  },
  body: {
    appendChild() {},
    removeChild() {},
  },
  execCommand() { return true; },
};

let apiBaseUrl = "http://localhost:8000";
let writeKey = "";
const sandbox = {
  window: {},
  document: fakeDocument,
  navigator: { clipboard: { writeText(value) { sandbox.copied = value; } } },
  console,
  URL,
};
sandbox.window = sandbox;
sandbox.location = { href: "http://localhost/admin.html" };
sandbox.RpgGameApi = {
  DEFAULT_API_BASE_URL: "http://localhost:8000",
  getApiBaseUrl() { return apiBaseUrl; },
  setApiBaseUrl(value) { apiBaseUrl = value || this.DEFAULT_API_BASE_URL; return apiBaseUrl; },
  getAdminWriteDevKey() { return writeKey; },
  setAdminWriteDevKey(value) { writeKey = value; },
  clearAdminWriteDevKey() { writeKey = ""; },
  hasAdminWriteDevKey() { return !!writeKey; },
};

vm.createContext(sandbox);
vm.runInContext(read("src/api/admin/admin-settings-helpers.js"), sandbox, { filename: "src/api/admin/admin-settings-helpers.js" });
assert(sandbox.RpgAdminSettingsHelpers, "RpgAdminSettingsHelpers should register on window");
const api = sandbox.RpgAdminSettingsHelpers;
let lastStatus = null;
api.configure({
  querySelector: (selector) => fakeDocument.querySelector(selector),
  escapeHtml: (value) => String(value).replace(/</g, "&lt;"),
  setStatus(message, kind) { lastStatus = { message, kind }; },
  ensureApi() { return sandbox.RpgGameApi; },
});
assert(api.VERSION === "v197.admin-settings-helpers-split", "settings helper module should expose v197 version");
assert(api.getCurrentAdminPageUrl() === "http://localhost/admin.html", "current admin URL should resolve");
assert(api.getGamePageUrl() === "http://localhost/index.html", "game URL should resolve next to admin.html");
api.syncLocationHints();
assert(elements.get("[data-admin-current-url]").textContent === "http://localhost/admin.html", "current URL hint should sync");
assert(elements.get("[data-admin-game-url]").href === "http://localhost/index.html", "game URL link should sync");
api.syncApiInput();
assert(elements.get("[data-admin-api-base-url]").value === "http://localhost:8000", "API input should sync from RpgGameApi");
elements.get("[data-admin-api-base-url]").value = "http://localhost:9100";
assert(api.saveApiBaseUrlFromInput() === "http://localhost:9100", "API URL should save through RpgGameApi");
assert(lastStatus.kind === "ok", "saving API URL should set ok status");
assert(api.resetApiBaseUrl() === "http://localhost:8000", "API URL should reset to default");
assert(!api.hasAdminWriteDevKey(), "write key should start empty");
elements.get("[data-admin-write-dev-key]").value = "local-admin-dev-key";
api.saveAdminWriteDevKeyFromInput();
assert(api.hasAdminWriteDevKey(), "write key should save from input");
assert(api.renderAdminWriteKeyStatus() === true, "write key status should render true when key exists");
api.clearAdminWriteDevKey();
assert(!api.hasAdminWriteDevKey(), "write key should clear");
elements.get("[data-admin-write-dev-key]").value = "local-admin-dev-key";
let blocked = false;
try {
  api.requireAdminWriteDevKeyForUi("테스트 쓰기");
} catch (error) {
  blocked = String(error.message).includes("dev key");
}
assert(blocked, "requireAdminWriteDevKeyForUi should block without key");
api.saveAdminWriteDevKeyFromInput();
assert(api.requireAdminWriteDevKeyForUi("테스트 쓰기") === true, "requireAdminWriteDevKeyForUi should pass with key");
const readiness = api.getReadiness({ log: false });
assert(readiness.ok, `settings helper readiness should be ok: ${JSON.stringify(readiness)}`);
assert(readiness.version === "v197.admin-settings-helpers-split", "settings helper readiness should return v197 version");

console.log("admin settings helpers split smoke test passed");

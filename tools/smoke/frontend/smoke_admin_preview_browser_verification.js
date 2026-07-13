const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..", "..", "..");
const sourcePath = path.join(root, "src/api/admin/admin-preview-verification.js");
const source = fs.readFileSync(sourcePath, "utf8");
const html = fs.readFileSync(path.join(root, "admin.html"), "utf8");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

for (const marker of [
  "v255.admin-preview-browser-verification",
  "readOnlyFixtures: true",
  "apiCalls: 0",
  "writeOperations: 0",
  "create-ready",
  "create-blocked",
  "edit-ready",
  "edit-stale",
  "rollback-ready",
  "snapshot-mismatch",
  "delete-dependency-blocked",
  "restore-conflict",
]) assert(source.includes(marker), `preview verification marker missing: ${marker}`);

assert(!source.includes("RpgGameApi."), "fixture verification must not call admin API");
assert(!source.includes("fetch("), "fixture verification must not use fetch");
assert(html.includes('id="section-preview-verification"'), "admin verification section missing");
assert(html.includes('data-admin-preview-verification-scenarios'), "scenario button target missing");
assert(html.includes('data-admin-preview-verification-result'), "scenario result target missing");
assert(html.indexOf('admin-preview-diff.js') < html.indexOf('admin-preview-verification.js'), "shared renderer must load before verification script");

const noop = () => {};
const fakeDocument = {
  readyState: "loading",
  addEventListener: noop,
  querySelector: () => null,
  querySelectorAll: () => [],
};
const context = { window: {}, document: fakeDocument };
vm.createContext(context);
vm.runInContext(source, context, { filename: sourcePath });
const moduleApi = context.window.RpgAdminPreviewVerification;
assert(moduleApi, "verification global missing");
assert(moduleApi.SCENARIOS.length === 8, "verification must expose eight scenarios");
const readiness = moduleApi.getReadiness();
assert(readiness.ok === true, "verification readiness must be true");
assert(readiness.readOnlyFixtures === true, "verification must be read-only fixtures");
assert(readiness.apiCalls === 0, "verification API call count must be zero");
assert(readiness.writeOperations === 0, "verification write count must be zero");

console.log("admin preview browser verification smoke test passed");

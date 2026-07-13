const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..", "..", "..");
const sourcePath = path.join(root, "src/api/admin/admin-workspace-navigation.js");
const source = fs.readFileSync(sourcePath, "utf8");
const html = fs.readFileSync(path.join(root, "admin.html"), "utf8");
const runSmoke = fs.readFileSync(path.join(root, "tools/run_smoke_core.sh"), "utf8");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

for (const marker of [
  "v258.admin-workspace-navigation",
  "ADMIN_WORKSPACE_MODES",
  "lookup",
  "create",
  "edit",
  "preview",
  "rollback",
  "writeOperations: 0",
  "apiBodyChanges: 0",
  "routeChanges: 0",
  "initializeAdminWorkspaceNavigation",
  "getAdminWorkspaceNavigationReadiness",
  "setWorkspaceMode",
  "openWorkspaceModal",
]) assert(source.includes(marker), `workspace navigation marker missing: ${marker}`);

for (const marker of [
  "data-admin-workspace-hub",
  "data-admin-workspace-mode-grid",
  "data-admin-workspace-modal",
  "data-admin-workspace-sidebar-actions",
  "Admin Workspace",
  "작업 시작",
  "관리자 작업 시작 허브",
  "admin-workspace-navigation.js",
]) assert(html.includes(marker), `admin.html workspace marker missing: ${marker}`);

assert(html.indexOf("admin-layout-shell.js") < html.indexOf("admin/admin-workspace-navigation.js"), "workspace navigation must load after layout shell");
assert(html.indexOf("admin/admin-workspace-navigation.js") < html.indexOf("admin-page-readonly.js"), "workspace navigation must load before admin entry");
assert(!source.includes("fetch("), "workspace navigation must not call fetch");
assert(!source.includes("RpgGameApi."), "workspace navigation must not call admin API");
assert(!source.includes("applyAdmin"), "workspace navigation must not call write apply helpers");
assert(runSmoke.includes("node tools/smoke/frontend/smoke_admin_workspace_navigation.js"), "run_smoke_core must include workspace navigation smoke");

const noop = () => {};
const fakeDocument = {
  readyState: "loading",
  addEventListener: noop,
  querySelector: () => null,
  querySelectorAll: () => [],
  getElementById: () => null,
};
const context = { window: {}, document: fakeDocument, console };
vm.createContext(context);
vm.runInContext(source, context, { filename: sourcePath });
assert(context.window.RpgAdminWorkspaceNavigation, "workspace navigation global missing");
assert(context.window.RpgAdminWorkspaceNavigation.VERSION === "v258.admin-workspace-navigation", "workspace version mismatch");
assert(context.window.RpgAdminWorkspaceNavigation.ADMIN_WORKSPACE_MODES.length === 5, "workspace must expose five task modes");
const keys = context.window.RpgAdminWorkspaceNavigation.ADMIN_WORKSPACE_MODES.map((mode) => mode.key).join(",");
assert(keys === "lookup,create,edit,preview,rollback", `unexpected workspace mode keys: ${keys}`);

console.log("admin workspace navigation smoke test passed");

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

assertContains("src/api/admin/admin-edit-draft.js", [
  "v191.admin-edit-draft-split",
  "RpgAdminEditDraft",
  "configure",
  "getReadiness",
  "renderMasterEditDraft",
  "readAdminEditDraftValues",
  "resetAdminEditDraft",
  "previewAdminEditDraft",
  "applyAdminEditDraft",
  "renderAdminEditPreviewResult",
  "readAdminEditApplyControls",
  "buildAdminEditDraftReview",
  "renderAdminEditDraftReview",
  "buildAdminEditImpactGuide",
  "renderAdminEditImpactGuide",
  "refreshAdminEditImpactGuide",
  "getAdminRelationEditOptionDefinitions",
  "refreshDependentAdminRelationSelects",
  "APPLY MASTER DATA EDIT",
  "HIGH RISK EDIT",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v191.admin-edit-draft-split",
  "getAdminEditDraftApi",
  "configureAdminEditDraft",
  "getAdminEditDraftExternalReadiness",
  "editDraftExternalReady",
  "RpgAdminEditDraft",
  "editDraftExternal.version === \"v191.admin-edit-draft-split\"",
  "window.getAdminEditDraftExternalReadiness",
  "admin/admin-edit-draft.js",
]);

assertContains("admin.html", [
  "src/api/admin/admin-change-logs.js",
  "src/api/admin/admin-create-lifecycle.js",
  "src/api/admin/admin-edit-draft.js",
  "src/api/admin-page-readonly.js",
]);

const adminHtml = read("admin.html");
const order = [
  "src/api/game-api-client.js",
  "src/api/admin-layout-shell.js",
  "src/api/admin/admin-change-logs.js",
  "src/api/admin/admin-create-lifecycle.js",
  "src/api/admin/admin-edit-draft.js",
  "src/api/admin-page-readonly.js",
].map((needle) => adminHtml.indexOf(needle));
assert(!order.some((index) => index < 0), "admin.html: missing expected admin script source");
for (let i = 1; i < order.length; i += 1) {
  assert(order[i - 1] < order[i], "admin.html: admin script order is not safe for edit draft split");
}

assertContains("tools/run_smoke_core.sh", [
  "node tools/smoke_admin_edit_draft_split.js",
]);

const editDraftText = read("src/api/admin/admin-edit-draft.js");
const fakeFields = [];
const fakeDraft = {
  getAttribute(name) {
    if (name === "data-admin-edit-draft-domain") return "skills";
    if (name === "data-admin-edit-draft-id") return "101";
    return "";
  },
  querySelectorAll(selector) {
    return selector === "[data-admin-edit-draft-field]" ? fakeFields : [];
  },
  querySelector(selector) {
    if (selector === '[data-admin-action="preview-admin-edit-draft"]') return { disabled: false };
    if (selector === '[data-admin-action="apply-admin-edit-draft"]') return { disabled: false };
    return null;
  },
};
const fakeElements = new Map([
  ["[data-admin-edit-draft]", fakeDraft],
  ["[data-admin-edit-apply-confirm]", { value: "" }],
  ["[data-admin-edit-risk-confirm]", { value: "" }],
  ["[data-admin-edit-apply-reason]", { value: "" }],
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
  previewAdminMasterDataEdit() {},
  applyAdminMasterDataEdit() {},
};
vm.createContext(sandbox);
vm.runInContext(editDraftText, sandbox, { filename: "src/api/admin/admin-edit-draft.js" });
assert(sandbox.RpgAdminEditDraft, "RpgAdminEditDraft was not registered on window");
sandbox.RpgAdminEditDraft.configure({
  querySelector: sandbox.document.querySelector.bind(sandbox.document),
  DEFAULT_MASTER_DOMAIN: "itemTemplates",
  hasAdminWriteDevKey: () => true,
});
const readiness = sandbox.RpgAdminEditDraft.getAdminEditDraftReadiness({ log: false });
assert(readiness && readiness.version === "v191.admin-edit-draft-split", "edit draft readiness should return v191 version");
assert(readiness.hasDraft === true, "edit draft readiness should see fake draft");
const values = sandbox.RpgAdminEditDraft.readAdminEditDraftValues();
assert(values && values.domain === "skills" && values.id === 101, "edit draft value reader should read domain/id without throwing");

console.log("admin edit draft split smoke test passed");

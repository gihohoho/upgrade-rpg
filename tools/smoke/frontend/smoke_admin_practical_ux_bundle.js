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

const html = read("admin.html");
const catalogText = read("src/api/admin/admin-master-catalog.js");
const longValueText = read("src/api/admin/admin-long-value-modal.js");
const buttonSafetyText = read("src/api/admin/admin-button-safety.js");
const detailShortcutsText = read("src/api/admin/admin-detail-shortcuts.js");
const smokeCore = read("tools/run_smoke_core.sh");

[
  "data-admin-start-guide",
  "처음 사용하는 추천 순서",
  "버튼 색상 기준",
  "data-admin-long-value-modal",
  "admin-long-value-modal.js",
  "admin-button-safety.js",
  "admin-detail-shortcuts.js",
  "v266 admin practical UX polish",
].forEach((marker) => assert(html.includes(marker), `admin.html missing practical UX polish marker: ${marker}`));

assert(!html.includes("data-admin-master-view-mode"), "catalog view-mode select should be removed again");
assert(!html.includes("보기 방식"), "catalog view-mode label should be removed again");
assert(html.indexOf("admin/admin-long-value-modal.js") < html.indexOf("admin/admin-master-catalog.js"), "long value modal must load before master catalog");
assert(html.indexOf("admin/admin-button-safety.js") < html.indexOf("admin-page-readonly.js"), "button safety must load before admin entry observes dynamic DOM");
assert(html.indexOf("admin/admin-detail-shortcuts.js") > html.indexOf("admin/admin-master-catalog.js"), "detail shortcuts should load after master catalog helper");

[
  "readMasterCatalogViewModeFromDom",
  "filterCatalogColumnsForView",
  "getCatalogViewModeLabel",
  "renderCatalogLongValueCell",
  "data-admin-master-catalog-view-mode",
  "detail-quick-summary",
  "detail-section-guide",
  "data-admin-detail-jump-target",
  "data-admin-detail-target",
].forEach((marker) => assert(catalogText.includes(marker), `catalog missing practical UX polish marker: ${marker}`));

[
  "v266.admin-long-value-modal-compact",
  "renderLongValueTrigger",
  "openLongValueModal",
  "writeOperations: 0",
  "apiBodyChanges: 0",
  "routeChanges: 0",
].forEach((marker) => assert(longValueText.includes(marker), `long value modal missing marker: ${marker}`));

[
  "v266.admin-button-safety-color-only",
  "classifyButton",
  "applyButtonRiskLabels",
  "data-admin-button-risk",
  "existingChip.remove",
  "MutationObserver",
  "writeOperations: 0",
  "apiBodyChanges: 0",
  "routeChanges: 0",
].forEach((marker) => assert(buttonSafetyText.includes(marker), `button safety missing marker: ${marker}`));

[
  "v266.admin-detail-shortcuts",
  "data-admin-detail-scroll-target",
  "data-admin-detail-jump-target",
  "scrollIntoView",
  "writeOperations: 0",
  "apiBodyChanges: 0",
  "routeChanges: 0",
].forEach((marker) => assert(detailShortcutsText.includes(marker), `detail shortcuts missing marker: ${marker}`));

assert(!longValueText.includes("fetch("), "long value modal must not call fetch");
assert(!buttonSafetyText.includes("fetch("), "button safety must not call fetch");
assert(!detailShortcutsText.includes("fetch("), "detail shortcuts must not call fetch");
assert(!longValueText.includes("RpgGameApi"), "long value modal must not call API");
assert(!buttonSafetyText.includes("RpgGameApi"), "button safety must not call API");
assert(!detailShortcutsText.includes("RpgGameApi"), "detail shortcuts must not call API");
assert(smokeCore.includes("node tools/smoke/frontend/smoke_admin_practical_ux_bundle.js"), "core smoke should include practical UX bundle smoke");

const fakeDocument = {
  readyState: "loading",
  addEventListener: () => undefined,
  querySelector: () => null,
  querySelectorAll: () => [],
  createElement: () => ({ innerHTML: "", get value() { return this.innerHTML; } }),
};
const sandbox = {
  console,
  window: { setTimeout: () => undefined },
  document: fakeDocument,
  MutationObserver: function MutationObserver() { this.observe = () => undefined; },
};
sandbox.global = sandbox;
vm.createContext(sandbox);
vm.runInContext(longValueText, sandbox, { filename: "src/api/admin/admin-long-value-modal.js" });
vm.runInContext(buttonSafetyText, sandbox, { filename: "src/api/admin/admin-button-safety.js" });
vm.runInContext(catalogText, sandbox, { filename: "src/api/admin/admin-master-catalog.js" });
vm.runInContext(detailShortcutsText, sandbox, { filename: "src/api/admin/admin-detail-shortcuts.js" });

assert(sandbox.window.RpgAdminLongValueModal, "long value modal global missing");
assert(sandbox.window.RpgAdminButtonSafety, "button safety global missing");
assert(sandbox.window.RpgAdminMasterCatalog, "master catalog global missing");
assert(sandbox.window.RpgAdminDetailShortcuts, "detail shortcuts global missing");

const longHtml = sandbox.window.RpgAdminLongValueModal.renderLongValueTrigger("설명 전체 보기", "a".repeat(90));
assert(longHtml.includes("data-admin-long-value-open"), "long value trigger should open modal");
assert(longHtml.includes("전체"), "long value trigger should include whole-view button");
const previewText = longHtml.match(/<span class="catalog-cell-preview"[^>]*>(.*?)<\/span>/s)?.[1] || "";
assert(previewText.length <= 30, "long value preview should be shorter than previous width");

const catalog = sandbox.window.RpgAdminMasterCatalog;
catalog.configure({
  querySelector: () => null,
  escapeHtml: (value) => String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;"),
  formatValue: (value) => value === null || value === undefined || value === "" ? "-" : String(value),
});

const columns = [
  { key: "id" }, { key: "code" }, { key: "name" }, { key: "description" }, { key: "itemType" }, { key: "equipSlot" }, { key: "jsonKeys" }, { key: "updated_at" }
];
const allColumns = catalog.filterCatalogColumnsForView("itemTemplates", columns, "detail").map((column) => column.key);
assert(allColumns.length === columns.length, "catalog should use the existing single all-column view again");
assert(allColumns.includes("description") && allColumns.includes("jsonKeys"), "single catalog view should keep all returned columns");

const longCell = catalog.formatCatalogCellValue("description", "긴 설명 ".repeat(20));
assert(longCell.includes("data-admin-long-value-open") || longCell.includes("catalog-cell-preview"), "long catalog values should be compacted");

const fakeButton = {
  getAttribute: (name) => name === "data-admin-action" ? "apply-admin-change-log-rollback" : "",
  textContent: "Rollback 적용",
  setAttribute: () => undefined,
  hasAttribute: () => false,
  querySelector: () => null,
  classList: { contains: () => false },
};
assert(sandbox.window.RpgAdminButtonSafety.classifyButton(fakeButton) === "danger", "rollback apply button should be danger");

console.log("admin practical UX bundle smoke test passed");

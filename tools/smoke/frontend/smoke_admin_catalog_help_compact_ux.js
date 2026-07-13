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

const adminHtml = read("admin.html");
const fieldHelpText = read("src/api/admin/admin-field-help.js");
const catalogText = read("src/api/admin/admin-master-catalog.js");

const masterCatalogTitleCount = (adminHtml.match(/<h2 class="section-title">마스터 데이터 카탈로그<\/h2>/g) || []).length;
assert(masterCatalogTitleCount === 1, "master catalog should have one visible section title");
assert(!adminHtml.includes('id="section-master-catalog-table"'), "separate master catalog table section should be merged into the main catalog section");
assert(adminHtml.includes('data-admin-section-key="master-catalog"'), "merged catalog section should use one section key");
assert(adminHtml.includes("master-catalog-filter-body"), "merged catalog should keep filters inside the same panel");
assert(adminHtml.includes("목록은 핵심값만 보여주고"), "catalog guidance should explain compact values");

[
  "field-help-section-title",
  "code / 코드",
  "item type / 아이템 분류",
  "proc rate / 발동 확률",
  "owner type / owner code",
  "success rate / gold cost",
].forEach((pattern) => assert(adminHtml.includes(pattern), `admin.html missing expanded field help: ${pattern}`));

[
  "ownertype",
  "ownercode",
  "itemtemplatecode",
  "procrate",
  "cooldownseconds",
  "damagemultiplier",
  "enemyhp",
  "goldreward",
  "successrate",
  "jsonkeys",
  "field-value-hint compact",
  "updated at / 수정 시각",
].forEach((pattern) => assert(fieldHelpText.includes(pattern), `field help missing ${pattern}`));

assert(catalogText.includes("formatCatalogCellValue"), "catalog should expose compact value formatter");
assert(catalogText.includes("formatCatalogUpdatedAtCell"), "catalog should render updated_at date-only cells");
assert(catalogText.includes("formatCatalogJsonKeysCell"), "catalog should render compact json keys cells");
assert(catalogText.includes("catalog-time-badge"), "updated_at cell should include time tooltip badge");
assert(catalogText.includes("json-key-more"), "json keys cell should include hidden count chip");
assert(catalogText.includes("field-value-compact"), "catalog should render compact value hints");
assert(catalogText.includes("getAdminFieldValueHint"), "catalog should consume field value hints directly");
assert(!catalogText.includes("<td>${formatValueWithFieldHint(column.key, cells[column.key])}</td>"), "catalog table should not render long inline field hints");

const sandbox = {
  console,
  window: {},
  document: {
    querySelector: () => null,
    querySelectorAll: () => [],
  },
};
sandbox.global = sandbox;
vm.createContext(sandbox);
vm.runInContext(fieldHelpText, sandbox, { filename: "src/api/admin/admin-field-help.js" });
vm.runInContext(catalogText, sandbox, { filename: "src/api/admin/admin-master-catalog.js" });

const fieldHelp = sandbox.window.RpgAdminFieldHelp;
const catalog = sandbox.window.RpgAdminMasterCatalog;
assert(fieldHelp && typeof fieldHelp.getAdminFieldHelp === "function", "field help API should load");
assert(catalog && typeof catalog.formatCatalogCellValue === "function", "catalog compact formatter should export");

fieldHelp.configure({});
catalog.configure({
  escapeHtml: (value) => String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;"),
  formatValue: (value) => value === null || value === undefined || value === "" ? "-" : String(value),
  getAdminFieldHelp: fieldHelp.getAdminFieldHelp,
  getAdminFieldValueHint: fieldHelp.getAdminFieldValueHint,
  renderFieldHelpBadge: fieldHelp.renderFieldHelpBadge,
});

const itemTypeHtml = catalog.formatCatalogCellValue("itemType", "normal");
assert(itemTypeHtml.includes("normal · 일반 장비"), "item type compact label should be visible");
assert(!itemTypeHtml.includes("</strong> —"), "item type body text should not be rendered as visible inline copy");
assert(itemTypeHtml.includes("title="), "compact catalog value should keep details in tooltip");

const equipSlotHtml = catalog.formatCatalogCellValue("equipSlot", "6");
assert(equipSlotHtml.includes("6 · 특수무기"), "equip slot compact label should be visible");
assert(!equipSlotHtml.includes("</strong> —"), "equip slot body text should not be rendered as visible inline copy");

const updatedHtml = catalog.formatCatalogCellValue("updated_at", "2026-07-06T13:24:51.789Z");
assert(updatedHtml.includes("2026-07-06"), "updated_at catalog cell should show date only");
assert(!updatedHtml.includes("13:24:51</strong>"), "updated_at visible value should not show time inside main label");
assert(updatedHtml.includes("13:24:51 UTC"), "updated_at tooltip should keep full second-level time");
assert(updatedHtml.includes("catalog-time-badge"), "updated_at should include a ? badge for full time");

const jsonKeysHtml = catalog.formatCatalogCellValue("jsonKeys", "baseStats, options, rules, conditions, effects");
assert(jsonKeysHtml.includes("baseStats") && jsonKeysHtml.includes("options") && jsonKeysHtml.includes("rules"), "json keys should show first three keys");
assert(jsonKeysHtml.includes("외 2개"), "json keys should collapse remaining keys into count");
assert(jsonKeysHtml.includes("전체 JSON 키 5개"), "json keys tooltip should include full key count");

console.log("admin catalog/help compact UX smoke test passed");

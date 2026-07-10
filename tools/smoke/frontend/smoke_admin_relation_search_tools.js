const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");

function read(file) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  return fs.readFileSync(fullPath, "utf8");
}

function assertContains(file, patterns) {
  const text = read(file);
  for (const pattern of patterns) {
    if (!text.includes(pattern)) throw new Error(`${file}: missing pattern ${pattern}`);
  }
}

assertContains("src/api/admin-page-readonly.js", [
  "v165.admin-create-apply-limited",
  "relation-option-filter",
  "data-admin-relation-option-filter",
  "filterAdminDraftSelectOptions",
  "applyAdminRelationOptionFilter",
  "clearAdminRelationOptionFilter",
  "getAdminRelationSelectMetaText",
  "renderAdminDraftSelectOptionsHtml",
  "keepSelected",
  "window.applyAdminRelationOptionFilter",
  "relationSearchReady",
  "data-admin-master-query",
  "syncMasterCatalogPageInput(1)",
]);

assertContains("admin.html", [
  "v165 admin create apply limited",
  "relation-select-tools",
  "relation-option-filter",
  "relation-option-meta",
]);

assertContains("docs/ADMIN_RELATION_SEARCH_TOOLS.md", [
  "Admin Relation Search Tools",
  "relation select",
  "코드/이름",
  "현재 선택값",
  "DB reset / seed",
]);

assertContains("docs/CHANGELOG.md", [
  "v153 - Admin Relation Preview Tools",
  "relation select 검색",
]);

console.log("admin relation search tools smoke test passed");

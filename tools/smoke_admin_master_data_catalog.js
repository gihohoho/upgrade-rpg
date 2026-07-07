const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");

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

assertContains("backend/app/api/routes/admin.py", [
  '@router.get("/master-data/domains")',
  '@router.get("/master-data/catalog")',
  'type="admin.master_data.domains"',
  'type="admin.master_data.catalog"',
  'rawJsonReturned',
  'assetsReturned',
]);

assertContains("backend/app/services/admin_service.py", [
  "MASTER_CATALOG_DOMAINS",
  "list_master_catalog_domains",
  "list_master_catalog_rows",
  "_build_master_catalog_where_clauses",
  "_master_catalog_columns",
  "_serialize_master_catalog_row",
  "rawJsonReturned",
  "assetsReturned",
  "itemTemplates",
]);

assertContains("src/api/game-api-client.js", [
  "listAdminMasterCatalogDomains",
  "listAdminMasterCatalogRows",
  'request("/admin/master-data/domains"',
  'request("/admin/master-data/catalog"',
  "domain",
  "enabled",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v115.admin-master-data-catalog",
  "readMasterCatalogFiltersFromDom",
  "resetMasterCatalogFilters",
  "describeMasterCatalogFilters",
  "syncMasterDomainOptions",
  "renderMasterCatalogTable",
  "apply-master-catalog-filters",
  "reset-master-catalog-filters",
  "masterCatalogReady",
]);

assertContains("admin.html", [
  "마스터 데이터 카탈로그",
  "data-admin-master-domain",
  "data-admin-master-limit",
  "data-admin-master-query",
  "data-admin-master-enabled",
  "data-admin-master-sort",
  "data-admin-master-catalog-table",
  "data-admin-action=\"apply-master-catalog-filters\"",
  "원본 JSON과 이미지 data URL은 숨깁니다",
]);

console.log("admin master data catalog smoke test passed");

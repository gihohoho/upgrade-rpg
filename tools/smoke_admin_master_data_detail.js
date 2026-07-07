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
  '@router.get("/master-data/detail")',
  "get_admin_master_catalog_detail",
  'type="admin.master_data.detail"',
  "sanitizedJsonReturned",
  "safeForAdminWriteUi",
]);

assertContains("backend/app/services/admin_service.py", [
  "get_master_catalog_detail",
  "_serialize_master_detail_scalar_fields",
  "_serialize_master_detail_json_fields",
  "_build_master_detail_relation_hints",
  "_sanitize_json_preview",
  "[asset hidden:data-url]",
  "rawJsonReturned",
  "assetsReturned",
  "sanitizedJsonReturned",
]);

assertContains("src/api/game-api-client.js", [
  "fetchAdminMasterDataDetail",
  'request("/admin/master-data/detail"',
  "rowId",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v141.admin-relation-safe-edit",
  "renderMasterDetail",
  "openAdminMasterDataDetail",
  "fetchAdminMasterDataDetail",
  "open-master-detail",
  "data-admin-detail-domain",
  "data-admin-detail-id",
  "masterDetailReady",
  "JSON 미리보기",
]);

assertContains("admin.html", [
  "선택한 마스터 데이터 상세",
  "data-admin-master-detail",
  "data-admin-master-detail-meta",
  ".json-preview",
  ".detail-grid",
  "v141 admin relation safe edit",
]);

assertContains("backend/scripts/check_admin_readonly_api.py", [
  "admin/master-data/detail",
  "masterDetailUrl",
  "sanitizedJsonReturned",
  "master-data detail should hide raw JSON and assets",
]);

console.log("admin master data detail smoke test passed");

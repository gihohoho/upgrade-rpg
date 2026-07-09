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

assertContains("backend/app/api/routes/admin_master_data_routes.py", [
  '@router.get("/master-data/relations")',
  "get_admin_master_catalog_relations",
  'type="admin.master_data.relations"',
]);

assertContains("backend/app/api/routes/admin_response_data_helpers.py", [
  "groupCount",
  "totalRelatedRows",
  "safeForAdminWriteUi",
]);

assertContains("backend/app/services/admin_service.py", [
  "get_master_catalog_relations",
  "_build_master_relation_groups",
  "_fetch_master_relation_group",
  "_serialize_master_relation_row",
  "rawJsonReturned",
  "assetsReturned",
  "safeForAdminWriteUi",
  "DropTableItem.item_template_code",
  "EnhancementLevel.group_code",
  "CharacterSkill.skill_code",
]);

assertContains("src/api/game-api-client.js", [
  "fetchAdminMasterDataRelations",
  'request("/admin/master-data/relations"',
  "limit,",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v165.admin-create-apply-limited",
  "renderMasterRelations",
  "openAdminMasterDataRelations",
  "fetchAdminMasterDataRelations",
  "open-master-relations",
  "data-admin-relation-domain",
  "data-admin-relation-id",
  "실제 연결 항목",
  "relation-table-wrap",
]);

assertContains("admin.html", [
  "선택한 마스터 데이터 상세",
  "data-admin-master-detail",
  ".relation-table-wrap",
  "v165 admin create apply limited",
]);

assertContains("backend/scripts/check_admin_readonly_api.py", [
  "admin/master-data/relations",
  "masterRelationsUrl",
  "master-data relations should hide raw JSON and assets",
  "master-data relations groups missing",
]);

console.log("admin master data relations smoke test passed");

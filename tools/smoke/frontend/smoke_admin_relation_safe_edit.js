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
  "relation-select",
  "relationEditOptions",
  "getAdminRelationEditOptionDefinition",
  "isAdminRelationEditField",
  "renderAdminRelationEditOptionsNote",
  "enhance_group_code",
  "item_template_code",
  "owner_type",
  "아이템 강화 그룹 연결 변경",
  "드랍 아이템 연결 변경",
]);

assertContains("backend/app/services/admin_service_legacy_markers.py", [
  "MASTER_RELATION_EDIT_FIELDS",
  '"itemTemplates": {"enhance_group_code"}',
  '"dropTableItems": {"drop_table_code", "item_template_code"}',
  '"dropTables": {"owner_type", "owner_code"}',
  "_validate_master_relation_edit_value",
  "_build_master_relation_edit_options",
  "relation_target_not_found_enhancement_group",
  "relation_target_not_found_item_template",
  "owner_code_not_found_for_owner_type",
  "relationEditOptions",
]);

assertContains("admin.html", [
  "v165 admin create apply limited",
  "relation-edit-note",
  "draft-field-relation-select",
]);

assertContains("docs/archive/history/ADMIN_AND_BACKEND_HISTORY.md", [
  "Admin Relation Safe Edit",
  "relation select",
  "itemTemplates.enhance_group_code",
  "dropTableItems.item_template_code",
  "dropTables.owner_type",
  "DB reset / seed는 필요 없습니다",
]);

console.log("admin relation safe edit smoke test passed");

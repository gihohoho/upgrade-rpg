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

assertContains("src/api/admin-page-readonly.js", [
  "v147.admin-owner-code-relation-tools",
  "getAdminRelationComboGuardLabels",
  "중복 조합 검사",
  "skill_code + level",
  "group_code + from_level",
  "character_code + skill_code",
  "drop_table_code",
  "스킬 레벨 조합 변경",
  "강화 단계 조합 변경",
  "캐릭터 스킬 연결 변경",
]);

assertContains("backend/app/services/admin_service.py", [
  "MASTER_COMBO_GUARDED_FIELDS",
  '"skillLevels": {"skill_code", "level"}',
  '"enhancementLevels": {"group_code", "from_level"}',
  '"characterSkills": {"character_code", "skill_code"}',
  '"dropTableItems": {"drop_table_code", "item_template_code"}',
  "_build_proposed_combo_values",
  "_exists_duplicate_combo",
  "duplicate_skill_code_level",
  "duplicate_enhancement_group_from_level",
  "duplicate_character_skill_pair",
  "relation_target_not_found_drop_table",
]);

assertContains("admin.html", [
  "v147 admin owner code relation tools",
  "relation-edit-note",
]);

assertContains("docs/ADMIN_COMBO_RELATION_GUARD.md", [
  "Admin Combo Relation Guard",
  "skill_code + level",
  "group_code + from_level",
  "character_code + skill_code",
  "DB reset / seed는 필요 없습니다",
]);

console.log("admin combo relation guard smoke test passed");

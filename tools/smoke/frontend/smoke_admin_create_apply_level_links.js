const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");

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

function parseSet(text, name) {
  const match = text.match(new RegExp(`${name}: set\\[str\\] = \\{([^}]+)\\}`));
  assert(match, `missing set: ${name}`);
  return match[1]
    .split(",")
    .map((value) => value.trim().replace(/^[ '\"]|[ '\"]$/g, ""))
    .filter(Boolean)
    .sort();
}

const service = read("backend/app/services/admin_service_legacy_markers.py");
const createAllowed = parseSet(service, "MASTER_CREATE_APPLY_ALLOWED_DOMAINS");
const deleteAllowed = parseSet(service, "MASTER_CREATE_DELETE_ALLOWED_DOMAINS");
const expectedAllowed = ["bosses", "characters", "characterSkills", "dropTables", "dropTableItems", "enhancementGroups", "enhancementLevels", "fieldZones", "itemTemplates", "skillLevels", "skills"].sort();

assert(JSON.stringify(createAllowed) === JSON.stringify(expectedAllowed), `create allow-list mismatch: ${createAllowed.join(",")}`);
assert(JSON.stringify(deleteAllowed) === JSON.stringify(expectedAllowed), `delete/restore allow-list mismatch: ${deleteAllowed.join(",")}`);

assertContains("backend/app/services/admin_service_legacy_markers.py", [
  "skill_levels.id",
  "enhancement_levels.id",
  "character_skills.id",
  "duplicate_skill_code_level",
  "duplicate_enhancement_group_from_level",
  "duplicate_character_skill_pair",
  "invalid_enhancement_to_level",
  "invalid_enhancement_success_rate",
  "invalid_character_skill_sort_order",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v179.admin-create-apply-level-links",
  "v178.admin-create-apply-items-dropitems",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills",
]);

assertContains("admin.html", [
  "v179 admin create apply level/link tables",
  "v178 admin create apply itemTemplates/dropTableItems",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems/skillLevels/enhancementLevels/characterSkills",
  "<option value=\"skillLevels\">스킬 레벨</option>",
  "<option value=\"enhancementLevels\">강화 단계</option>",
  "<option value=\"characterSkills\">캐릭터 스킬</option>",
]);

assertContains("docs/ADMIN_CREATE_APPLY_LEVEL_LINKS.md", [
  "Admin Create Apply Level and Link Tables",
  "skillLevels",
  "enhancementLevels",
  "characterSkills",
  "id 기반",
  "skill_code + level",
  "group_code + from_level",
  "character_code + skill_code",
  "DB reset / seed",
]);

console.log("admin create apply level/link tables smoke test passed");

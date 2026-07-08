const fs = require("fs");
const path = require("path");

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

function parseSet(text, name) {
  const match = text.match(new RegExp(`${name}: set\\[str\\] = \\{([^}]+)\\}`));
  assert(match, `missing set: ${name}`);
  return match[1]
    .split(",")
    .map((value) => value.trim().replace(/^[ '\"]|[ '\"]$/g, ""))
    .filter(Boolean)
    .sort();
}

const service = read("backend/app/services/admin_service.py");
const createAllowed = parseSet(service, "MASTER_CREATE_APPLY_ALLOWED_DOMAINS");
const deleteAllowed = parseSet(service, "MASTER_CREATE_DELETE_ALLOWED_DOMAINS");
const expectedAllowed = ["bosses", "characters", "dropTables", "dropTableItems", "enhancementGroups", "fieldZones", "itemTemplates", "skills"].sort();
const lockedDomains = ["skillLevels", "enhancementLevels", "characterSkills"];

assert(JSON.stringify(createAllowed) === JSON.stringify(expectedAllowed), `create allow-list mismatch: ${createAllowed.join(",")}`);
assert(JSON.stringify(deleteAllowed) === JSON.stringify(expectedAllowed), `delete/restore allow-list mismatch: ${deleteAllowed.join(",")}`);
lockedDomains.forEach((domain) => {
  assert(!createAllowed.includes(domain), `${domain} must stay locked for create apply`);
  assert(!deleteAllowed.includes(domain), `${domain} must stay locked for create delete/restore`);
});

assertContains("backend/app/services/admin_service.py", [
  "if domain == \"skills\"",
  "SkillLevel, \"skill_code\"",
  "CharacterSkill, \"skill_code\"",
  "UserCharacterSkill, \"skill_code\"",
  "if domain == \"dropTables\"",
  "DropTableItem, \"drop_table_code\"",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v177.admin-create-apply-skills-droptables",
  "v176.admin-create-apply-bosses",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
]);

assertContains("admin.html", [
  "v177 admin create apply skills/dropTables",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
  "<option value=\"skills\">스킬</option>",
  "<option value=\"dropTables\">드랍 테이블</option>",
]);

assertContains("docs/ADMIN_CREATE_APPLY_SKILLS_DROPTABLES.md", [
  "Admin Create Apply Skills and DropTables",
  "skills",
  "dropTables",
  "skillLevels.skill_code",
  "characterSkills.skill_code",
  "userCharacterSkills.skill_code",
  "dropTableItems.drop_table_code",
  "itemTemplates",
  "dropTableItems",
  "DB reset / seed",
]);

console.log("admin create apply skills/dropTables smoke test passed");

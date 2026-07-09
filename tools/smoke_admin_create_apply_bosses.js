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

const service = read("backend/app/services/admin_service_legacy_markers.py");
const createAllowed = parseSet(service, "MASTER_CREATE_APPLY_ALLOWED_DOMAINS");
const deleteAllowed = parseSet(service, "MASTER_CREATE_DELETE_ALLOWED_DOMAINS");
const expectedAllowed = ["bosses", "characters", "characterSkills", "dropTables", "dropTableItems", "enhancementGroups", "enhancementLevels", "fieldZones", "itemTemplates", "skillLevels", "skills"].sort();
assert(JSON.stringify(createAllowed) === JSON.stringify(expectedAllowed), `create allow-list mismatch: ${createAllowed.join(",")}`);
assert(JSON.stringify(deleteAllowed) === JSON.stringify(expectedAllowed), `delete/restore allow-list mismatch: ${deleteAllowed.join(",")}`);

assertContains("backend/app/services/admin_service_legacy_markers.py", [
  "if domain == \"bosses\"",
  "DropTable.owner_type == \"boss\"",
  "DropTable.owner_code == code_text",
  "drop_tables.owner_type=boss + owner_code",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
  "fieldZones/bosses는 dropTables(owner_type=field/boss)",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v177.admin-create-apply-skills-droptables",
  "v176.admin-create-apply-bosses",
  "v175.admin-create-apply-fieldzones",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
]);

assertContains("admin.html", [
  "v177 admin create apply skills/dropTables",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
  "<option value=\"bosses\">보스</option>",
]);

assertContains("docs/ADMIN_CREATE_APPLY_BOSSES.md", [
  "Admin Create Apply Bosses",
  "bosses",
  "dropTables.owner_type = boss",
  "dropTables.owner_code = bosses.code",
  "itemTemplates",
  "dropTableItems",
  "DB reset / seed",
]);

console.log("admin create apply bosses smoke test passed");

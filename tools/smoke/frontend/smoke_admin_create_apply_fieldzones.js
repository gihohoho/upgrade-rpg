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
    .map((value) => value.trim().replace(/^['\"]|['\"]$/g, ""))
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
  "if domain == \"fieldZones\"",
  "DropTable.owner_type == \"field\"",
  "DropTable.owner_code == code_text",
  "drop_tables.owner_type=field + owner_code",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
  "create_delete_restore_preview_enabled",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v177.admin-create-apply-skills-droptables",
  "v176.admin-create-apply-bosses",
  "v175.admin-create-apply-fieldzones",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
  "v174.admin-collapsed-panel-style-fix",
]);

assertContains("admin.html", [
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
  "<option value=\"fieldZones\">필드</option>",
  "<option value=\"enhancementGroups\">강화 그룹</option>",
]);

assertContains("docs/archive/stage-notes/ADMIN_CREATE_APPLY_FIELDZONES.md", [
  "Admin Create Apply FieldZones",
  "fieldZones",
  "dropTables.owner_type = field",
  "dropTables.owner_code = fieldZones.code",
  "itemTemplates",
  "dropTableItems",
  "DB reset / seed",
]);

console.log("admin create apply fieldZones smoke test passed");

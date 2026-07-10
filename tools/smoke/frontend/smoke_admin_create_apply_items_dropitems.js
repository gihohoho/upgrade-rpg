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
  "if domain == \"itemTemplates\"",
  "DropTableItem, \"item_template_code\"",
  "ItemInstance, \"template_code\"",
  "if domain == \"dropTableItems\"",
  "drop_table_items.id",
  "invalid_drop_rate",
  "invalid_min_quantity",
  "max_quantity_less_than_min_quantity",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v178.admin-create-apply-items-dropitems",
  "v177.admin-create-apply-skills-droptables",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
]);

assertContains("admin.html", [
  "v178 admin create apply itemTemplates/dropTableItems",
  "characters/enhancementGroups/fieldZones/bosses/skills/dropTables/itemTemplates/dropTableItems",
  "<option value=\"itemTemplates\" selected>아이템 템플릿</option>",
  "<option value=\"dropTableItems\">드랍 아이템</option>",
]);

assertContains("docs/ADMIN_CREATE_APPLY_ITEMS_DROPITEMS.md", [
  "Admin Create Apply ItemTemplates and DropTableItems",
  "itemTemplates",
  "dropTableItems",
  "base_stats_json",
  "options_json",
  "conditions_json",
  "dropTableItems.item_template_code",
  "itemInstances.template_code",
  "id 기반",
  "DB reset / seed",
]);

console.log("admin create apply itemTemplates/dropTableItems smoke test passed");

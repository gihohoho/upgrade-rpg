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
  "dropTables: [\"owner_type\", \"owner_code\", \"description\", \"is_enabled\"]",
  "getAdminDraftRelationOptionGroupKey",
  "getAdminDraftRelationOptions",
  "refreshDependentAdminRelationSelects",
  "definition.optionGroups",
  "definition.dependsOn",
  "ownercode",
  "드랍 테이블 소유자 변경",
  "formatAdminChangeAfterValue",
  "window.refreshDependentAdminRelationSelects",
]);

assertContains("backend/app/services/admin_service_legacy_markers.py", [
  '"dropTables": {"owner_type", "owner_code", "description", "is_enabled"}',
  '"dropTables": {"owner_type", "owner_code"}',
  'key in {"owner_type", "owner_code"}',
  '["owner_type", "owner_code"]',
  '"field": "owner_code"',
  '"dependsOn": "owner_type"',
  '"optionGroups"',
  'Boss if owner_type == "boss" else FieldZone',
]);

assertContains("admin.html", [
  "v165 admin create apply limited",
]);

assertContains("docs/ADMIN_OWNER_CODE_RELATION_TOOLS.md", [
  "Admin Owner Code Relation Tools",
  "dropTables.owner_code",
  "owner_type=boss",
  "owner_type=field",
  "DB reset / seed",
]);

assertContains("docs/CHANGELOG.md", [
  "v147 - Admin Owner Code Relation Tools",
  "owner_type + owner_code",
]);

console.log("admin owner_code relation tools smoke test passed");

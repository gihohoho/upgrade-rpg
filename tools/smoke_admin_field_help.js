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

assertContains("admin.html", [
  "v122 admin guarded edit apply",
  "data-admin-field-help",
  "필드 용어 도움말",
  "grade / 등급",
  "enhance group code / 강화그룹 코드",
  "admin note / 관리자 메모",
  ".field-help-panel",
  ".field-help-badge",
  ".field-help-inline",
]);

assertContains("src/api/admin-page-readonly.js", [
  "v122.admin-guarded-edit-apply",
  "ADMIN_FIELD_HELP_DEFINITIONS",
  "getAdminFieldHelp",
  "listAdminFieldHelp",
  "renderFieldHelpBadge",
  "renderFieldHelpInline",
  "fieldHelpReady",
  "grade / 등급",
  "enhance group code / 강화그룹 코드",
  "admin note / 관리자 메모",
]);

assertContains("docs/ADMIN_FIELD_HELP.md", [
  "Admin Field Help",
  "grade",
  "enhance group code",
  "admin note",
  "DB reset/seed는 필요 없습니다",
]);

console.log("admin field help smoke test passed");

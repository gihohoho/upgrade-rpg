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
  "v153.admin-relation-preview-tools",
  "ADMIN_DRAFT_BOOLEAN_FIELDS",
  "ADMIN_DRAFT_NUMBER_FIELDS",
  "ADMIN_DRAFT_TEXTAREA_FIELDS",
  "getAdminDraftFieldInputKind",
  "boolean-select",
  "type=\"number\" inputmode=\"decimal\" step=\"any\"",
  "description/admin_note",
  "renderAdminDraftLockedFields",
  "data-admin-edit-locked-fields",
  "getAdminDraftLockedReason",
  "window.getAdminDraftFieldInputKind",
  "field.value === \"true\"",
]);

assertContains("admin.html", [
  "v153 admin relation preview tools",
  ".draft-field select",
  ".draft-field-heading",
  ".locked-field-panel",
  ".locked-field-card",
  "타입별 입력 UI",
]);

assertContains("docs/ADMIN_EDIT_INPUT_UI.md", [
  "Admin Edit Input UI",
  "boolean 필드는 checkbox 대신",
  "number 필드는",
  "description`, `admin_note`",
  "읽기 전용/잠금 필드",
  "DB reset / seed는 필요 없습니다",
]);

assertContains("docs/CHANGELOG.md", [
  "v133 - Admin Edit Input UI",
  "true/false select",
  "number input",
  "textarea",
  "DB reset / seed는 필요 없습니다",
]);

console.log("admin edit input UI smoke test passed");

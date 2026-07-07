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
  "getAdminFieldValueHint",
  "renderFieldValueHintInline",
  "formatValueWithFieldHint",
  "grade / 등급 숫자",
  "기존 JS 아이템의 tier 값을 옮겨 담은 숫자형 진행 등급",
  "normal_equipment",
  "talisman_emblem",
  "window.getAdminFieldValueHint",
]);

assertContains("admin.html", [
  "v153 admin relation preview tools",
  "field-value-hint",
  "grade / 등급 숫자",
  "기존 JS 아이템의 <strong>tier 숫자</strong>",
  "값 해석 힌트",
]);

assertContains("docs/ADMIN_VALUE_HINTS.md", [
  "Admin Value Hints",
  "itemTemplates.grade = 기존 JS item.tier",
  "grade=1",
  "grade=12",
  "getAdminFieldValueHint",
  "DB reset/seed는 필요 없습니다",
]);

assertContains("docs/ADMIN_FIELD_HELP.md", [
  "기존 JS 아이템의 `tier` 값을 옮겨 담은 숫자형 진행 등급",
  "rarity",
]);

console.log("admin value hints smoke test passed");

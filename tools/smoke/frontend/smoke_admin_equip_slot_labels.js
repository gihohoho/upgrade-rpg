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
  "ADMIN_EQUIP_SLOT_PRESET_LABELS",
  "getAdminEquipSlotDisplayName",
  '"6": "특수무기"',
  '"7": "특수목걸이"',
  '"8": "특수반지"',
  '"9": "무기아바타"',
  '"10": "오라아바타"',
  '"11": "클론 레어 아바타"',
  '"12": "탈리스만 A"',
  '"13": "탈리스만 B"',
  '"14": "휘장"',
  '6 · 특수무기',
  '14 · 휘장',
  "window.getAdminEquipSlotDisplayName",
]);

assertContains("docs/ADMIN_MASTER_CATALOG_PAGINATION.md", [
  "6: 특수무기",
  "12: 탈리스만 A",
  "14: 휘장",
  "DB reset / seed",
]);

console.log("admin equip slot labels smoke test passed");

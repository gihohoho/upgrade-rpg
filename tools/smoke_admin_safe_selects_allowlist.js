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
  "v162.admin-create-draft-preview",
  "ADMIN_DRAFT_SELECT_FIELD_OPTIONS",
  "preset-select",
  "getAdminDraftSelectOptions",
  "getAdminDraftFieldRisk",
  "renderAdminDraftRiskBadge",
  "draft-field-badges",
  "item_type",
  "equip_slot",
  "slot_key",
  "현재 DB 값",
  "renderAdminDraftRiskBadge",
  "아이템 분류/장착 슬롯 변경",
  "스킬 슬롯 배치 변경",
  "window.getAdminDraftSelectOptions",
  "window.getAdminDraftFieldRisk",
]);

assertContains("backend/app/services/admin_service.py", [
  '"itemTemplates": {"name", "item_type", "description", "grade", "stackable", "equip_slot", "enhance_group_code", "admin_note"}',
  '"skills": {"slot_key", "name", "description", "proc_rate", "cooldown_seconds"}',
  "MASTER_EDIT_ALLOWED_FIELDS",
]);

assertContains("admin.html", [
  "v162 admin create draft preview",
  ".draft-field-badges",
]);

assertContains("docs/ADMIN_SAFE_SELECTS_ALLOWLIST.md", [
  "Admin Safe Selects + Allow-list Expansion",
  "itemTemplates.item_type",
  "itemTemplates.equip_slot",
  "skills.slot_key",
  "preset select",
  "risk high",
  "DB reset / seed는 필요 없습니다",
]);

assertContains("docs/CHANGELOG.md", [
  "v134 - Admin Safe Selects + Allow-list Expansion",
  "preset select",
  "itemTemplates.item_type",
  "skills.slot_key",
]);

console.log("admin safe selects allow-list smoke test passed");

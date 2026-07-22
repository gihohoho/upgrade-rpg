const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");
function read(rel) {
  return fs.readFileSync(path.join(root, rel), "utf8");
}
function assertIncludes(file, text) {
  const content = read(file);
  if (!content.includes(text)) {
    console.error(`${file}에 필요한 문자열이 없습니다: ${text}`);
    process.exit(1);
  }
}
function assertOrder(file, first, second) {
  const content = read(file);
  const a = content.indexOf(first);
  const b = content.indexOf(second);
  if (a < 0 || b < 0 || a > b) {
    console.error(`${file} 로딩 순서가 올바르지 않습니다: ${first} -> ${second}`);
    process.exit(1);
  }
}

assertIncludes("backend/app/api/routes/game.py", '@router.get("/save-slots")');
assertIncludes("backend/app/api/routes/game.py", "service.list_save_slots");
assertIncludes("backend/app/api/routes/game.py", 'type="game.save_slots"');
assertIncludes("backend/app/services/game_service.py", "async def list_save_slots");
assertIncludes("backend/app/services/game_service.py", "def _serialize_save_slot");
assertIncludes("backend/app/services/game_service.py", "UserSaveSnapshot.updated_at.desc()");
assertIncludes("src/api/game-api-client.js", "listGameSaveSlots");
assertIncludes("src/api/game-api-client.js", 'request("/game/save-slots"');
assertIncludes("src/api/save-data-slots.js", "v109.backend-save-data-slot-list");
assertIncludes("src/api/save-data-slots.js", "listBackendSaveSlots");
assertIncludes("src/api/save-data-slots.js", "openBackendSaveSlotsModal");
assertIncludes("src/api/save-data-slots.js", "DB 세이브 슬롯 목록");
assertIncludes("src/api/save-data-dev-badge.js", 'data-sd-action="slots"');
assertIncludes("src/api/save-data-dev-badge.js", "openBackendSaveSlotsModal");
assertIncludes("index.html", "src/api/save-data-slots.js");
assertOrder("index.html", "src/api/game-api-client.js", "src/api/save-data-slots.js");
assertOrder("index.html", "src/api/save-data-slots.js", "src/api/save-data-dev-badge.js");
assertIncludes("docs/archive/stage-notes/SAVE_DATA_SLOT_LIST.md", "Save Data Slot List");

console.log("save data slot list smoke test passed");

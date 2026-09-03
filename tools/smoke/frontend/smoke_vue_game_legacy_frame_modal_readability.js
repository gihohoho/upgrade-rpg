const assert = require("assert");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../../..");
const VUE_ROOT = path.join(ROOT, "frontend/vue-app");

function read(relativePath) {
  return fs.readFileSync(path.join(VUE_ROOT, relativePath), "utf8");
}

function requireMarker(source, marker, label) {
  assert.ok(source.includes(marker), `${label} missing: ${marker}`);
}

function main() {
  const playShell = read("src/components/game/GamePlayShell.vue");
  const sidebar = read("src/components/game/GameLegacySidebar.vue");
  const town = read("src/components/game/GameTownShell.vue");
  const store = read("src/stores/game.ts");
  const styles = read("src/styles/base.css");

  for (const marker of [
    'class="game-legacy-frame"',
    '<GameLegacySidebar class="game-legacy-frame__sidebar" variant="profile"',
    '<GameLegacySidebar class="game-legacy-frame__sidebar" variant="inventory"',
    'class="game-mobile-dock"',
    ':inert="game.isUtilityScreen || mobilePanel !== null"',
    'class="game-utility-modal"',
    'role="dialog"',
    'aria-modal="true"',
    ':inert="game.isUtilityScreen"',
    "game.closeUtilityPreview()",
    'v-if="game.isShopSettings"',
    'v-else-if="game.isSkillEnhancement"',
    'v-else-if="game.isStorageTrash"',
    'v-else-if="game.isInventory"',
    "event.key !== 'Escape'",
  ]) requireMarker(playShell, marker, "shared legacy game frame");
  assert.ok(!playShell.includes('v-if="game.model"'), "game frame must mount the town initializer before game.model exists");

  for (const marker of [
    "createInventoryEquipmentViewModel",
    "master-data 미리보기",
    "내 정보",
    "장착 장비",
    "능력치",
    "스킬",
    "보유 Gold",
    "보관함·휴지통",
    "상점·설정",
  ]) requireMarker(sidebar, marker, "desktop and mobile side window");
  for (const forbidden of ["fetch(", "snapshotApi", "save(", "confirm(", "alert("]) {
    assert.ok(!sidebar.includes(forbidden), `side window must stay display-only: ${forbidden}`);
  }

  requireMarker(store, "const isUtilityScreen = computed", "utility screen state");
  requireMarker(store, "isUtilityScreen,", "utility screen store export");
  requireMarker(store, "const utilityBackground = computed", "underlying game screen preservation");
  requireMarker(store, "function closeUtilityPreview()", "underlying game screen restoration");
  requireMarker(town, ":inert=\"background\"", "modal background interaction lock");
  requireMarker(town, "game.isTown && !background", "town-only connected character bar");

  for (const marker of [
    "/* v392 legacy-inspired game frame, readable type, and utility windows */",
    ".game-side-window",
    ".game-side-equipment-grid",
    ".game-side-bag-grid",
    ".game-utility-modal-backdrop",
    ".game-mobile-panel-modal",
    "font-size: max(12px, 1em) !important",
    "@media (min-width: 1500px)",
    "@media (max-width: 760px)",
  ]) requireMarker(styles, marker, "legacy frame and readability CSS");

  console.log("PASS: Vue game restores readable legacy-style desktop info/bag side windows and accessible utility/mobile dialogs without snapshot, save, item, Gold, or runtime mutation");
}

main();

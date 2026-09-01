const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../../..");
const VUE_ROOT = path.join(ROOT, "frontend/vue-app");
const REQUIRED_FILES = [
  "src/game/adapters/inventoryEquipment.ts",
  "src/components/game/GamePlayShell.vue",
  "src/components/game/GameInventoryEquipmentShell.vue",
];

function read(relativePath) {
  return fs.readFileSync(path.join(VUE_ROOT, relativePath), "utf8");
}

function requireMarker(source, marker, label) {
  assert.ok(source.includes(marker), `${label} missing: ${marker}`);
}

function loadAdapters() {
  const esbuild = require(path.join(VUE_ROOT, "node_modules/esbuild"));
  const output = esbuild.buildSync({
    stdin: {
      contents: [
        "import * as town from './src/game/adapters/townHud.ts';",
        "import * as inventory from './src/game/adapters/inventoryEquipment.ts';",
        "globalThis.__gameAdapters = { town, inventory };",
      ].join("\n"),
      resolveDir: VUE_ROOT,
      sourcefile: "inventory-equipment-smoke-harness.ts",
      loader: "ts",
    },
    bundle: true,
    platform: "node",
    format: "iife",
    target: "node20",
    write: false,
  });
  const context = {};
  vm.createContext(context);
  vm.runInContext(output.outputFiles[0].text, context);
  return context.__gameAdapters;
}

function assertStaticBoundary() {
  for (const relative of REQUIRED_FILES) {
    assert.ok(fs.existsSync(path.join(VUE_ROOT, relative)), `missing Vue inventory/equipment file: ${relative}`);
  }

  const adapter = read("src/game/adapters/inventoryEquipment.ts");
  for (const forbidden of [
    /from\s+["'](?:vue|pinia|vue-router)["']/,
    /\b(?:window|document|localStorage|sessionStorage)\b/,
    /\bfetch\s*\(/,
    /\bMath\.random\s*\(/,
    /\bDate\.now\s*\(/,
    /\b(?:setTimeout|setInterval)\s*\(/,
  ]) {
    assert.ok(!forbidden.test(adapter), `inventory adapter contains forbidden dependency: ${forbidden}`);
  }
  for (const marker of [
    "compactItemSlots",
    "countOccupiedItemSlots",
    "findFirstEmptyItemSlot",
    "placeItemInFirstEmptySlot",
    "mode: 'display-only'",
  ]) requireMarker(adapter, marker, "inventory/equipment adapter");

  const store = read("src/stores/game.ts");
  for (const forbidden of ["fetch(", "localStorage", "sessionStorage", "setInterval", "setTimeout", "Date.now"]) {
    assert.ok(!store.includes(forbidden), `game store must remain runtime-free: ${forbidden}`);
  }
  for (const marker of [
    "inventoryModel",
    "enterInventoryPreview",
    "selectInventoryPreview",
    "toggleInventoryCompactPreview",
    "createdAt: 0",
  ]) requireMarker(store, marker, "inventory game store");

  const playShell = read("src/components/game/GamePlayShell.vue");
  requireMarker(playShell, 'v-if="game.isInventory"', "game screen switch");
  requireMarker(playShell, "GameInventoryEquipmentShell", "game screen switch");

  const component = read("src/components/game/GameInventoryEquipmentShell.vue");
  for (const marker of [
    'data-zone="inventory"',
    'aria-label="일반 장비 슬롯"',
    'aria-label="특수 장비 슬롯"',
    'aria-label="가방 아이템 슬롯"',
    "game.selectInventoryPreview",
    "game.toggleInventoryCompactPreview",
    "game.returnTown",
    "실제 보유 목록이 아니라 master-data 샘플",
    "snapshot load/save·장착·사용·판매·강화·보관함 이동·휴지통 이동",
  ]) requireMarker(component, marker, "inventory/equipment component");
  assert.ok(!component.includes("town-session-bar"), "connected character bar must remain town-only");

  const accountStore = read("src/stores/account.ts");
  requireMarker(accountStore, "itemTemplates.value", "master-data item template reuse");
  const townComponent = read("src/components/game/GameTownShell.vue");
  requireMarker(townComponent, "game.enterInventoryPreview(account.itemTemplates)", "town to inventory navigation");

  const styles = read("src/styles/base.css");
  for (const selector of [
    ".inventory-command-bar",
    ".inventory-workspace",
    ".equipment-slot-grid",
    ".inventory-slot-grid",
    ".inventory-detail",
    ".inventory-data-boundary",
    ".item-frame--luminous.has-item",
    "@media (max-width: 480px)",
  ]) requireMarker(styles, selector, "inventory/equipment responsive CSS");
}

function makeItem(code, name, itemType, options, stackable = false) {
  return {
    code,
    name,
    itemType,
    grade: null,
    description: `${name} 설명`,
    stackable,
    equipSlot: null,
    options,
  };
}

function assertAdapterBehavior() {
  const adapters = loadAdapters();
  const townSource = {
    accountCharacterId: "d".repeat(32),
    slotKey: "character-4",
    characterName: "기호검성",
    characterCode: "weapon_master",
    characterLabel: "검성",
    progress: { gold: 73500, level: 19, currentZoneIndex: null, currentZoneType: "town", updatedAt: null },
  };
  const itemTemplates = [
    makeItem("normal_skill_1", "[기본] 모든 피해 검", "normal", { equipGroup: "skill_all", tier: 21 }),
    makeItem("normal_attack_1", "빛나는 공격력 검", "normal", { equipGroup: "atk_inc", tier: 22 }),
    makeItem("normal_damage_1", "-초월- 평타 피해 검", "normal", { equipGroup: "normal_dmg", tier: 23 }),
    makeItem("normal_chance_1", "강력한 스킬 확률 검", "normal", { equipGroup: "skill_chance", tier: 21 }),
    makeItem("normal_skill_2", "빛나는 모든 피해 검", "normal", { equipGroup: "skill_all", tier: 22 }),
    makeItem("normal_skill_3", "-초월- 모든 피해 검", "normal", { equipGroup: "skill_all", tier: 23 }),
    makeItem("normal_attack_2", "해방 공격력 검", "normal", { equipGroup: "atk_inc", tier: 36 }),
    makeItem("normal_damage_2", "찬란한 평타 피해 검", "normal", { equipGroup: "normal_dmg", tier: 35 }),
    makeItem("normal_chance_2", "짙은 스킬 확률 검", "normal", { equipGroup: "skill_chance", tier: 31 }),
    makeItem("special_weapon_1", "특수 무기 원형", "special_equip", { specialSlotIdx: 6, tier: 1 }),
    makeItem("special_necklace_1", "특수 목걸이 원형", "special_equip", { specialSlotIdx: 7, tier: 1 }),
    makeItem("special_weapon_2", "찬란한 특수 무기", "special_equip", { specialSlotIdx: 6, tier: 2 }),
    makeItem("skill_q", "Q 스킬강화권", "skill_book", { tier: 1 }, true),
    makeItem("skill_w", "W 스킬강화권", "skill_book", { tier: 1 }, true),
  ];
  const before = JSON.stringify({ townSource, itemTemplates });
  const town = adapters.town.createTownHudViewModel(townSource);
  const original = adapters.inventory.createInventoryEquipmentViewModel({
    town,
    itemTemplates,
    compactPreview: false,
    preferredItemCode: "skill_q",
    createdAt: 0,
  });
  const compact = adapters.inventory.createInventoryEquipmentViewModel({
    town,
    itemTemplates,
    compactPreview: true,
    preferredItemCode: "skill_q",
    createdAt: 0,
  });

  assert.strictEqual(original.zoneType, "inventory");
  assert.strictEqual(original.equipmentSlots.length, 15);
  assert.strictEqual(original.inventorySlots.length, 24);
  assert.strictEqual(original.totalCapacity, 60);
  assert.strictEqual(original.nextEmptySlotNumber, 2);
  assert.strictEqual(original.selectedItem.code, "skill_q");
  assert.strictEqual(original.selectedLocation, "inventory");
  assert.strictEqual(original.action.type, "inventory.preview.open");
  assert.strictEqual(original.masterDataConnected, true);
  assert.strictEqual(original.snapshotConnected, false);
  assert.strictEqual(original.itemMutationConnected, false);

  const originalOrder = original.inventorySlots.filter((slot) => slot.item).map((slot) => slot.item.code);
  const compactOrder = compact.inventorySlots.filter((slot) => slot.item).map((slot) => slot.item.code);
  assert.deepStrictEqual(compactOrder, originalOrder, "compact preview must preserve relative item order");
  assert.strictEqual(compact.occupiedCount, original.occupiedCount);
  assert.strictEqual(compact.nextEmptySlotNumber, compact.occupiedCount + 1);
  assert.ok(compact.compactMovedCount > 0);
  assert.strictEqual(compact.action.type, "inventory.preview.compact");
  assert.strictEqual(compact.selectedItem.code, "skill_q");
  assert.strictEqual(JSON.stringify({ townSource, itemTemplates }), before, "inventory adapter mutated source input");
}

function main() {
  assertStaticBoundary();
  assertAdapterBehavior();
  console.log("PASS: Vue inventory/equipment UI preserves sparse-slot and compact-preview rules without snapshot or item mutation");
}

main();

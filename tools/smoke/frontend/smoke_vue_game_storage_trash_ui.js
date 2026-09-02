const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../../..");
const VUE_ROOT = path.join(ROOT, "frontend/vue-app");
const REQUIRED_FILES = [
  "src/game/adapters/storageTrash.ts",
  "src/components/game/GamePlayShell.vue",
  "src/components/game/GameStorageTrashShell.vue",
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
        "import * as storageTrash from './src/game/adapters/storageTrash.ts';",
        "globalThis.__gameAdapters = { town, inventory, storageTrash };",
      ].join("\n"),
      resolveDir: VUE_ROOT,
      sourcefile: "storage-trash-smoke-harness.ts",
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
    assert.ok(fs.existsSync(path.join(VUE_ROOT, relative)), `missing Vue storage/trash file: ${relative}`);
  }

  const adapter = read("src/game/adapters/storageTrash.ts");
  for (const forbidden of [
    /from\s+["'](?:vue|pinia|vue-router)["']/,
    /\b(?:window|document|localStorage|sessionStorage)\b/,
    /\bfetch\s*\(/,
    /\bMath\.random\s*\(/,
    /\bDate\.now\s*\(/,
    /\b(?:setTimeout|setInterval)\s*\(/,
  ]) assert.ok(!forbidden.test(adapter), `storage/trash adapter contains forbidden dependency: ${forbidden}`);
  for (const marker of [
    "compactItemSlots",
    "countOccupiedItemSlots",
    "findFirstEmptyItemSlot",
    "placeItemInFirstEmptySlot",
    "mode: 'display-only'",
    "permanentDeleteConnected: false",
  ]) requireMarker(adapter, marker, "storage/trash adapter");

  const store = read("src/stores/game.ts");
  for (const forbidden of ["fetch(", "localStorage", "sessionStorage", "setInterval", "setTimeout", "Date.now"]) {
    assert.ok(!store.includes(forbidden), `game store must remain runtime-free: ${forbidden}`);
  }
  for (const marker of [
    "storageTrashModel",
    "enterStorageTrashPreview",
    "selectStorageTrashPreview",
    "toggleStorageTrashCompactPreview",
    "returnInventoryPreview",
    "createdAt: 0",
  ]) requireMarker(store, marker, "storage/trash game store");

  const playShell = read("src/components/game/GamePlayShell.vue");
  requireMarker(playShell, 'v-else-if="game.isStorageTrash"', "game screen switch");
  requireMarker(playShell, "GameStorageTrashShell", "game screen switch");

  const inventoryComponent = read("src/components/game/GameInventoryEquipmentShell.vue");
  requireMarker(inventoryComponent, "game.enterStorageTrashPreview", "inventory to storage/trash navigation");
  requireMarker(inventoryComponent, "보관함·휴지통", "inventory navigation label");

  const component = read("src/components/game/GameStorageTrashShell.vue");
  for (const marker of [
    'data-zone="storage-trash"',
    'aria-label="보관함 아이템 슬롯"',
    'aria-label="휴지통 아이템 슬롯"',
    "game.selectStorageTrashPreview('storage'",
    "game.selectStorageTrashPreview('trash'",
    "game.toggleStorageTrashCompactPreview('storage')",
    "game.toggleStorageTrashCompactPreview('trash')",
    "game.returnInventoryPreview",
    "휴지통 비우기",
    "snapshot load/save·가방/보관함 이동·휴지통 이동·복구·영구 삭제",
  ]) requireMarker(component, marker, "storage/trash component");
  assert.ok(!component.includes("town-session-bar"), "connected character bar must remain town-only");
  assert.ok(component.includes('type="button" disabled'), "destructive and mutation actions must remain disabled");

  const styles = read("src/styles/base.css");
  for (const selector of [
    ".storage-trash-command-bar",
    ".storage-trash-workspace",
    ".container-preview--storage",
    ".container-preview--trash",
    ".container-slot-grid",
    ".storage-trash-flow",
    ".storage-trash-data-boundary",
    "@media (max-width: 480px)",
  ]) requireMarker(styles, selector, "storage/trash responsive CSS");
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
    accountCharacterId: "e".repeat(32),
    slotKey: "character-5",
    characterName: "기호검성",
    characterCode: "weapon_master",
    characterLabel: "검성",
    progress: { gold: 88000, level: 21, currentZoneIndex: null, currentZoneType: "town", updatedAt: null },
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
  const inventory = adapters.inventory.createInventoryEquipmentViewModel({
    town,
    itemTemplates,
    compactPreview: false,
    preferredItemCode: null,
    createdAt: 0,
  });
  const original = adapters.storageTrash.createStorageTrashViewModel({
    inventory,
    itemTemplates,
    storageCompactPreview: false,
    trashCompactPreview: false,
    preferredItemCode: null,
    preferredContainer: null,
    lastActionContainer: null,
    createdAt: 0,
  });
  const selectedTrashCode = original.trash.slots.find((slot) => slot.item).item.code;
  const compactStorage = adapters.storageTrash.createStorageTrashViewModel({
    inventory,
    itemTemplates,
    storageCompactPreview: true,
    trashCompactPreview: false,
    preferredItemCode: original.selectedItem.code,
    preferredContainer: "storage",
    lastActionContainer: "storage",
    createdAt: 0,
  });
  const compactTrash = adapters.storageTrash.createStorageTrashViewModel({
    inventory,
    itemTemplates,
    storageCompactPreview: false,
    trashCompactPreview: true,
    preferredItemCode: selectedTrashCode,
    preferredContainer: "trash",
    lastActionContainer: "trash",
    createdAt: 0,
  });

  assert.strictEqual(original.zoneType, "storage-trash");
  assert.strictEqual(original.storage.slots.length, 20);
  assert.strictEqual(original.trash.slots.length, 20);
  assert.strictEqual(original.storage.capacity, 60);
  assert.strictEqual(original.trash.capacity, 60);
  assert.strictEqual(original.storage.nextEmptySlotNumber, 2);
  assert.strictEqual(original.trash.nextEmptySlotNumber, 2);
  assert.strictEqual(original.action.type, "storage-trash.preview.open");
  assert.strictEqual(original.snapshotConnected, false);
  assert.strictEqual(original.itemMutationConnected, false);
  assert.strictEqual(original.permanentDeleteConnected, false);

  const originalStorageOrder = original.storage.slots.filter((slot) => slot.item).map((slot) => slot.item.code);
  const compactStorageOrder = compactStorage.storage.slots.filter((slot) => slot.item).map((slot) => slot.item.code);
  assert.deepStrictEqual(compactStorageOrder, originalStorageOrder, "storage compact must preserve relative item order");
  assert.strictEqual(compactStorage.storage.nextEmptySlotNumber, compactStorage.storage.occupiedCount + 1);
  assert.strictEqual(compactStorage.trash.nextEmptySlotNumber, 2);
  assert.ok(compactStorage.storage.compactMovedCount > 0);
  assert.strictEqual(compactStorage.action.type, "storage-trash.preview.compact-storage");
  assert.strictEqual(compactStorage.selectedItem.code, original.selectedItem.code);

  const originalTrashOrder = original.trash.slots.filter((slot) => slot.item).map((slot) => slot.item.code);
  const compactTrashOrder = compactTrash.trash.slots.filter((slot) => slot.item).map((slot) => slot.item.code);
  assert.deepStrictEqual(compactTrashOrder, originalTrashOrder, "trash compact must preserve relative item order");
  assert.strictEqual(compactTrash.trash.nextEmptySlotNumber, compactTrash.trash.occupiedCount + 1);
  assert.ok(compactTrash.trash.compactMovedCount > 0);
  assert.strictEqual(compactTrash.action.type, "storage-trash.preview.compact-trash");
  assert.strictEqual(compactTrash.selectedContainer, "trash");
  assert.strictEqual(compactTrash.selectedItem.code, selectedTrashCode);
  assert.strictEqual(JSON.stringify({ townSource, itemTemplates }), before, "storage/trash adapter mutated source input");
}

function main() {
  assertStaticBoundary();
  assertAdapterBehavior();
  console.log("PASS: Vue storage/trash UI preserves sparse slots and independent compaction without move, restore, delete, snapshot, or save mutation");
}

main();

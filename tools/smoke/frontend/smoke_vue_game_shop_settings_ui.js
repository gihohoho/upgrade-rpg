const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../../..");
const VUE_ROOT = path.join(ROOT, "frontend/vue-app");
const REQUIRED_FILES = [
  "src/game/adapters/shopSettings.ts",
  "src/components/game/GamePlayShell.vue",
  "src/components/game/GameShopSettingsShell.vue",
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
        "import * as shopSettings from './src/game/adapters/shopSettings.ts';",
        "globalThis.__gameAdapters = { town, shopSettings };",
      ].join("\n"),
      resolveDir: VUE_ROOT,
      sourcefile: "shop-settings-smoke-harness.ts",
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
    assert.ok(fs.existsSync(path.join(VUE_ROOT, relative)), `missing Vue shop/settings file: ${relative}`);
  }

  const adapter = read("src/game/adapters/shopSettings.ts");
  for (const forbidden of [
    /from\s+["'](?:vue|pinia|vue-router)["']/,
    /\b(?:window|document|localStorage|sessionStorage)\b/,
    /\bfetch\s*\(/,
    /\bMath\.random\s*\(/,
    /\bDate\.now\s*\(/,
    /\b(?:setTimeout|setInterval)\s*\(/,
  ]) assert.ok(!forbidden.test(adapter), `shop/settings adapter contains forbidden dependency: ${forbidden}`);
  for (const marker of [
    "purchasePriceLabel: '구매 가격 미등록'",
    "commerceConnected: false",
    "runtimeConnected: false",
    "persistenceConnected: false",
    "autoBossSummon: false",
    "autoSpecialBossEnabled: false",
    "equipDropEnabled: true",
    "mode: 'display-only'",
  ]) requireMarker(adapter, marker, "shop/settings adapter");

  const store = read("src/stores/game.ts");
  for (const forbidden of ["fetch(", "localStorage", "sessionStorage", "setInterval", "setTimeout", "Date.now", "Math.random"]) {
    assert.ok(!store.includes(forbidden), `game store must remain runtime-free: ${forbidden}`);
  }
  for (const marker of [
    "shopSettingsModel",
    "enterShopSettingsPreview",
    "selectShopCategory",
    "selectShopItem",
    "toggleSettingPreview",
    "resetSettingPreview",
    "createdAt: 0",
  ]) requireMarker(store, marker, "shop/settings game store");

  const playShell = read("src/components/game/GamePlayShell.vue");
  requireMarker(playShell, 'v-if="game.isShopSettings"', "game screen switch");
  requireMarker(playShell, "GameShopSettingsShell", "game screen switch");

  for (const navigation of ["src/components/game/GameTownShell.vue", "src/components/game/GameInventoryEquipmentShell.vue"]) {
    const source = read(navigation);
    requireMarker(source, "game.enterShopSettingsPreview", `${navigation} navigation`);
    requireMarker(source, "상점·설정", `${navigation} navigation label`);
  }

  const component = read("src/components/game/GameShopSettingsShell.vue");
  for (const marker of [
    'data-zone="shop-settings"',
    'aria-label="카탈로그 분류"',
    'aria-label="아이템 선택"',
    'role="switch"',
    "game.selectShopCategory",
    "game.selectShopItem",
    "game.toggleSettingPreview",
    "legacy 화면의 “판매”는 Gold를 지급하지 않고 휴지통으로 이동합니다.",
    "구매·판매·Gold/아이템 변경·설정 저장·snapshot load/save·자동 저장·전투 runtime",
  ]) requireMarker(component, marker, "shop/settings component");
  assert.ok(!component.includes("town-session-bar"), "connected character bar must remain town-only");
  assert.ok(!component.includes("v-html"), "master-data descriptions must render as text, not raw HTML");
  assert.ok((component.match(/type="button" disabled/g) || []).length >= 4, "commerce and data mutation controls must remain disabled");

  const styles = read("src/styles/base.css");
  for (const selector of [
    ".shop-settings-command-bar",
    ".shop-catalog-grid",
    ".shop-item-detail",
    ".settings-card-grid",
    ".settings-data-controls",
    ".shop-settings-data-boundary",
    "@media (max-width: 480px)",
  ]) requireMarker(styles, selector, "shop/settings responsive CSS");
}

function makeItem(code, name, itemType, options) {
  return {
    code,
    name,
    itemType,
    grade: null,
    description: `${name} 설명`,
    stackable: itemType === "skill_book",
    equipSlot: null,
    options,
  };
}

function assertAdapterBehavior() {
  const adapters = loadAdapters();
  const townSource = {
    accountCharacterId: "1".repeat(32),
    slotKey: "character-1",
    characterName: "기호검성",
    characterCode: "weapon_master",
    characterLabel: "검성",
    progress: { gold: 73500, level: 19, currentZoneIndex: null, currentZoneType: "town", updatedAt: null },
  };
  const itemTemplates = [
    makeItem("normal_sword", "샤이닝 인텔리전스", "normal", { equipGroup: "skill_all", tier: 1, baseCost: 20000 }),
    makeItem("special_talisman", "찬란한 탈리스만", "special_equip", { specialSlotIdx: 12, tier: 2, raw: { sellPrice: 0 } }),
    makeItem("skill_q", "Q 스킬강화권", "skill_book", { tier: 1 }),
  ];
  const settingPreview = { autoBossSummon: true, autoSpecialBossEnabled: false, equipDropEnabled: false };
  const before = JSON.stringify({ townSource, itemTemplates, settingPreview });
  const town = adapters.town.createTownHudViewModel(townSource);
  const model = adapters.shopSettings.createShopSettingsViewModel({
    town,
    itemTemplates,
    preferredCategory: "special_equip",
    preferredItemCode: "special_talisman",
    settingPreview,
    lastAction: "일반 보스 장비 드랍 OFF",
    createdAt: 0,
  });

  assert.strictEqual(model.zoneType, "shop-settings");
  assert.strictEqual(model.catalogItems.length, 3);
  assert.deepStrictEqual(Array.from(model.categories, (category) => category.key), ["all", "normal", "special_equip", "skill_book"]);
  assert.strictEqual(model.selectedCategory, "special_equip");
  assert.strictEqual(model.visibleItems.length, 1);
  assert.strictEqual(model.selectedItem.code, "special_talisman");
  assert.strictEqual(model.selectedItem.purchasePriceLabel, "구매 가격 미등록");
  assert.strictEqual(model.selectedItem.baseCost, null);
  assert.strictEqual(model.selectedItem.sellPrice, 0);
  assert.strictEqual(model.selectedItem.sellPriceLabel, "0 Gold");
  assert.strictEqual(model.changedSettingCount, 2);
  assert.strictEqual(model.settings.find((setting) => setting.key === "autoBossSummon").enabled, true);
  assert.strictEqual(model.settings.find((setting) => setting.key === "equipDropEnabled").enabled, false);
  assert.strictEqual(model.action.type, "shop-settings.preview");
  assert.strictEqual(model.masterDataConnected, true);
  assert.strictEqual(model.commerceConnected, false);
  assert.strictEqual(model.runtimeConnected, false);
  assert.strictEqual(model.persistenceConnected, false);
  assert.strictEqual(JSON.stringify({ townSource, itemTemplates, settingPreview }), before, "shop/settings adapter mutated source input");
}

function main() {
  assertStaticBoundary();
  assertAdapterBehavior();
  console.log("PASS: Vue shop/settings UI exposes only master-data pricing references and local setting previews without commerce, runtime, persistence, snapshot, or save mutation");
}

main();

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../../..");
const VUE_ROOT = path.join(ROOT, "frontend/vue-app");
const REQUIRED_FILES = [
  "src/game/adapters/fieldCombat.ts",
  "src/components/game/GamePlayShell.vue",
  "src/components/game/GameFieldCombatShell.vue",
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
        "import * as field from './src/game/adapters/fieldCombat.ts';",
        "globalThis.__gameAdapters = { town, field };",
      ].join("\n"),
      resolveDir: VUE_ROOT,
      sourcefile: "field-combat-smoke-harness.ts",
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
    assert.ok(fs.existsSync(path.join(VUE_ROOT, relative)), `missing Vue field combat file: ${relative}`);
  }

  const adapter = read("src/game/adapters/fieldCombat.ts");
  for (const forbidden of [
    /from\s+["'](?:vue|pinia|vue-router)["']/,
    /\b(?:window|document|localStorage|sessionStorage)\b/,
    /\bfetch\s*\(/,
    /\bMath\.random\s*\(/,
    /\bDate\.now\s*\(/,
    /\b(?:setTimeout|setInterval)\s*\(/,
  ]) {
    assert.ok(!forbidden.test(adapter), `field adapter contains forbidden dependency: ${forbidden}`);
  }
  for (const marker of ["resolveFieldEnemyState", "calculateBasicAttackDamage", "createGameActionResult", "mode: 'display-only'"]) {
    requireMarker(adapter, marker, "field combat adapter");
  }

  const store = read("src/stores/game.ts");
  for (const forbidden of ["fetch(", "localStorage", "sessionStorage", "setInterval", "setTimeout", "Date.now"]) {
    assert.ok(!store.includes(forbidden), `game store must remain runtime-free: ${forbidden}`);
  }
  for (const marker of ["fieldModel", "enterFieldPreview", "selectFieldPreview", "returnTown", "createdAt: 0"]) {
    requireMarker(store, marker, "field game store");
  }

  const playShell = read("src/components/game/GamePlayShell.vue");
  requireMarker(playShell, 'v-else-if="game.isField || game.utilityBackground === \'field\'"', "game screen switch");
  requireMarker(playShell, "GameFieldCombatShell", "game screen switch");

  const component = read("src/components/game/GameFieldCombatShell.vue");
  for (const marker of [
    'data-zone="field"',
    'role="progressbar"',
    'aria-label="필드 구역 목록"',
    'aria-label="전투 준비 HUD"',
    "game.selectFieldPreview",
    "game.returnTown",
    "구역을 눌러도 실제 전투나 저장은 시작되지 않습니다",
    "snapshot load/save·자동 저장·전투 timer·난수 판정은 아직 연결하지 않습니다",
  ]) {
    requireMarker(component, marker, "field combat component");
  }
  assert.ok(!component.includes("town-session-bar"), "connected character bar must remain town-only");

  const accountStore = read("src/stores/account.ts");
  requireMarker(accountStore, "fieldZones.value", "master-data field zone reuse");
  const townComponent = read("src/components/game/GameTownShell.vue");
  requireMarker(townComponent, "game.enterFieldPreview(account.fieldZones)", "town to field navigation");

  const styles = read("src/styles/base.css");
  for (const selector of [
    ".field-command-bar",
    ".field-arena",
    ".field-enemy__hp",
    ".field-zone-browser__rail",
    ".field-combat-dashboard",
    ".field-data-boundary",
    "@media (max-width: 480px)",
  ]) {
    requireMarker(styles, selector, "field combat responsive CSS");
  }

  const tsconfig = JSON.parse(read("tsconfig.json"));
  assert.ok(!Object.prototype.hasOwnProperty.call(tsconfig.compilerOptions, "baseUrl"), "deprecated baseUrl must be removed");
  assert.deepStrictEqual(tsconfig.compilerOptions.paths["@/*"], ["./src/*"]);
}

function assertAdapterBehavior() {
  const adapters = loadAdapters();
  const townSource = {
    accountCharacterId: "b".repeat(32),
    slotKey: "character-3",
    characterName: "기호검신",
    characterCode: "weapon_master",
    characterLabel: "검신",
    progress: {
      gold: "12500",
      level: 7,
      currentZoneIndex: 1,
      currentZoneType: "field",
      updatedAt: "2026-09-01T00:00:00Z",
    },
  };
  const fieldZones = [
    {
      code: "field_1",
      name: "마그토늄 노가다",
      sortOrder: 1,
      enemyHp: 50000,
      goldReward: 1500,
      description: "첫 필드",
      entryRules: { text: "순수공격력 1000 미만" },
      farmRules: {},
      isEnabled: true,
    },
    {
      code: "field_2",
      name: "마그토늄 노가다 [5회]",
      sortOrder: 2,
      enemyHp: "250000",
      goldReward: "7500",
      description: null,
      entryRules: { text: "순수공격력 1000 미만" },
      farmRules: { prob: 0.5, gain: 5, capText: "12B" },
      isEnabled: true,
    },
  ];
  const before = JSON.stringify({ townSource, fieldZones });
  const town = adapters.town.createTownHudViewModel(townSource);
  const field = adapters.field.createFieldCombatViewModel({ town, fieldZones, preferredIndex: 1, createdAt: 0 });

  assert.strictEqual(field.zoneType, "field");
  assert.strictEqual(field.selectedIndex, 1);
  assert.strictEqual(field.selectedZone.code, "field_2");
  assert.strictEqual(field.selectedZone.enemyHpLabel, "25B");
  assert.strictEqual(field.selectedZone.goldRewardLabel, "7500A");
  assert.strictEqual(field.enemyHp, 250000);
  assert.strictEqual(field.enemyHpPercent, 100);
  assert.strictEqual(field.basicAttackLabel, "1250A");
  assert.strictEqual(field.action.type, "field.preview.select");
  assert.ok(field.action.logs[0].message.includes("미리보기"));
  assert.strictEqual(field.masterDataConnected, true);
  assert.strictEqual(field.snapshotConnected, false);
  assert.strictEqual(field.runtimeConnected, false);
  assert.strictEqual(JSON.stringify({ townSource, fieldZones }), before, "field adapter mutated source input");
}

function main() {
  assertStaticBoundary();
  assertAdapterBehavior();
  console.log("PASS: Vue field combat UI remains display-only without snapshot, timer, or random runtime");
}

main();

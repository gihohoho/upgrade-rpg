const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../../..");
const VUE_ROOT = path.join(ROOT, "frontend/vue-app");
const REQUIRED_FILES = [
  "src/game/adapters/bossCombat.ts",
  "src/components/game/GamePlayShell.vue",
  "src/components/game/GameBossCombatShell.vue",
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
        "import * as boss from './src/game/adapters/bossCombat.ts';",
        "globalThis.__gameAdapters = { town, boss };",
      ].join("\n"),
      resolveDir: VUE_ROOT,
      sourcefile: "boss-combat-smoke-harness.ts",
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
    assert.ok(fs.existsSync(path.join(VUE_ROOT, relative)), `missing Vue boss combat file: ${relative}`);
  }
  const adapter = read("src/game/adapters/bossCombat.ts");
  for (const forbidden of [
    /from\s+["'](?:vue|pinia|vue-router)["']/,
    /\b(?:window|document|localStorage|sessionStorage)\b/,
    /\bfetch\s*\(/,
    /\bMath\.random\s*\(/,
    /\bDate\.now\s*\(/,
    /\b(?:setTimeout|setInterval)\s*\(/,
  ]) assert.ok(!forbidden.test(adapter), `boss adapter contains forbidden dependency: ${forbidden}`);
  for (const marker of ["getNormalBossSkillDropRate", "isFirstEquipSkillGuaranteeBoss", "createGameActionResult", "mode: 'display-only'"]) {
    requireMarker(adapter, marker, "boss combat adapter");
  }

  const store = read("src/stores/game.ts");
  for (const marker of ["bossModel", "enterBossPreview", "selectBossPreview", "returnTown", "createdAt: 0"]) {
    requireMarker(store, marker, "boss game store");
  }
  const playShell = read("src/components/game/GamePlayShell.vue");
  requireMarker(playShell, 'v-if="game.isBoss || game.utilityBackground === \'boss\'"', "game screen switch");
  requireMarker(playShell, "GameBossCombatShell", "game screen switch");

  const component = read("src/components/game/GameBossCombatShell.vue");
  for (const marker of [
    'data-zone="boss"',
    'role="progressbar"',
    'aria-label="보스 종류"',
    'aria-label="보스 목록"',
    "game.selectBossPreview",
    "game.returnTown",
    'aria-label="클라이언트 전투 실행 상태"',
    "game.pauseCombatRuntime('manual')",
    "game.resumeCombatRuntime('manual')",
    "기본 공격 timer는 동작하지만 서버 캐릭터와 보상에는 반영되지 않습니다",
    "snapshot load/save·자동 저장·난수 드랍·보상·쿨타임 변경·자동 재소환은 아직 연결하지 않습니다",
  ]) requireMarker(component, marker, "boss combat component");
  assert.ok(!component.includes("town-session-bar"), "connected character bar must remain town-only");

  const accountStore = read("src/stores/account.ts");
  requireMarker(accountStore, "bosses.value", "master-data boss reuse");
  const townComponent = read("src/components/game/GameTownShell.vue");
  requireMarker(townComponent, "game.enterBossPreview(account.bosses)", "town to boss navigation");

  const styles = read("src/styles/base.css");
  for (const selector of [
    ".boss-command-bar",
    ".boss-arena",
    ".boss-enemy__hp",
    ".boss-browser__rail",
    ".boss-dashboard",
    ".boss-data-boundary",
    ".combat-runtime-panel",
    "@media (max-width: 480px)",
  ]) requireMarker(styles, selector, "boss combat responsive CSS");
}

function assertAdapterBehavior() {
  const adapters = loadAdapters();
  const townSource = {
    accountCharacterId: "c".repeat(32),
    slotKey: "character-2",
    characterName: "기호검신",
    characterCode: "weapon_master",
    characterLabel: "검신",
    progress: { gold: 12500, level: 7, currentZoneIndex: null, currentZoneType: "town", updatedAt: null },
  };
  const bosses = [
    {
      code: "boss_2", name: "불을 먹는 안톤", tier: 2, bossType: "normal", hp: "1800000000",
      description: "[02단계] 안톤 소환하기", summonRules: {
        desc1: "보스존에 불을 먹는 안톤이 등장합니다.", reqLvl: "필요 아이템 레벨: <span>150 레벨</span>",
        dropsList: ["*장비 A (6.00%)"], dropRateDoubled: true,
        raw: { skillDropRate: 0.06, dropRateDoubled: true },
      }, cooldownSeconds: 0, isEnabled: true,
    },
    {
      code: "boss_101", name: "심연의 감시자", tier: 101, bossType: "special", hp: 1000000000000,
      description: "특수 보스", summonRules: { raw: { skillDropRate: 0.015 } }, cooldownSeconds: 1200, isEnabled: true,
    },
  ];
  const before = JSON.stringify({ townSource, bosses });
  const town = adapters.town.createTownHudViewModel(townSource);
  const normal = adapters.boss.createBossCombatViewModel({ town, bosses, preferredIndex: 0, createdAt: 0 });
  const special = adapters.boss.createBossCombatViewModel({ town, bosses, preferredIndex: 1, createdAt: 0 });

  assert.strictEqual(normal.zoneType, "boss");
  assert.strictEqual(normal.selectedBoss.code, "boss_2");
  assert.strictEqual(normal.selectedBoss.hpLabel, "18C");
  assert.strictEqual(normal.bossHpPercent, 100);
  assert.strictEqual(normal.selectedBoss.skillDropRateLabel, "1.5% 기본 스킬북");
  assert.strictEqual(normal.selectedBoss.equipmentSkillGuarantee, true);
  assert.ok(normal.selectedBoss.entryCondition.includes("150 레벨"));
  assert.strictEqual(special.selectedBoss.cooldownLabel, "20분 쿨타임");
  assert.strictEqual(special.selectedBoss.skillDropRateLabel, "1.5% 기본 스킬북");
  assert.strictEqual(normal.action.type, "boss.preview.select");
  assert.strictEqual(normal.masterDataConnected, true);
  assert.strictEqual(normal.snapshotConnected, false);
  assert.strictEqual(normal.runtimeConnected, false);
  assert.strictEqual(normal.randomConnected, false);
  assert.strictEqual(JSON.stringify({ townSource, bosses }), before, "boss adapter mutated source input");
}

function main() {
  assertStaticBoundary();
  assertAdapterBehavior();
  console.log("PASS: Vue boss combat UI connects client-only deterministic basic-attack runtime without snapshot, save, random, reward, cooldown, or respawn mutation");
}

main();

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../../..");
const VUE_ROOT = path.join(ROOT, "frontend/vue-app");
const DOMAIN_ROOT = path.join(VUE_ROOT, "src/game/domain");
const DOMAIN_FILES = [
  "action-result.ts",
  "combat-math.ts",
  "field-state.ts",
  "index.ts",
  "inventory-slots.ts",
  "rules.ts",
  "state.ts",
  "types.ts",
];
const FORBIDDEN = [
  /\bwindow\b/,
  /\bdocument\b/,
  /\b(?:localStorage|sessionStorage)\b/,
  /\bfetch\s*\(/,
  /\bMath\.random\s*\(/,
  /\bDate\.now\s*\(/,
  /\b(?:setTimeout|setInterval)\s*\(/,
  /from\s+["'](?:vue|pinia|vue-router)["']/,
];

function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, canonicalize(value[key])]));
  }
  return value;
}

function json(value) {
  return JSON.stringify(canonicalize(value));
}

function read(relativePath) {
  return fs.readFileSync(path.join(ROOT, relativePath), "utf8");
}

function loadDomain() {
  const esbuild = require(path.join(VUE_ROOT, "node_modules/esbuild"));
  const output = esbuild.buildSync({
    stdin: {
      contents: "import * as domain from './src/game/domain/index.ts'; globalThis.__domain = domain;",
      resolveDir: VUE_ROOT,
      sourcefile: "domain-smoke-harness.ts",
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
  return context.__domain;
}

function loadLegacy() {
  const fixedNow = 1_000;
  const context = {
    console,
    Date: { now: () => fixedNow },
    setTimeout: () => 1,
    clearTimeout: () => {},
    setInterval: () => 1,
    clearInterval: () => {},
  };
  context.window = context;
  vm.createContext(context);
  for (const source of [
    "src/state/game-state.js",
    "src/systems/stat-system.js",
    "src/systems/combat-system.js",
    "src/rules/abyss-fragment-rules.js",
    "src/rules/boss-drop-rules.js",
    "src/systems/action-result-system.js",
  ]) {
    vm.runInContext(read(source), context, { filename: source });
  }
  return context;
}

function legacyJson(context, expression) {
  return json(JSON.parse(vm.runInContext(`JSON.stringify(${expression})`, context)));
}

function assertPureBoundary() {
  for (const file of DOMAIN_FILES) {
    const absolute = path.join(DOMAIN_ROOT, file);
    assert.ok(fs.existsSync(absolute), `missing typed domain file: ${file}`);
    const source = fs.readFileSync(absolute, "utf8");
    for (const pattern of FORBIDDEN) {
      assert.ok(!pattern.test(source), `${file} contains forbidden runtime dependency: ${pattern}`);
    }
  }
}

function assertStateParity(domain, legacy) {
  assert.strictEqual(json(domain.createDefaultPlayerState()), legacyJson(legacy, "createDefaultPlayerState()"));
  assert.strictEqual(json(domain.createDefaultServerState()), legacyJson(legacy, "createDefaultServerState()"));
  assert.strictEqual(json(domain.createDefaultClientState()), legacyJson(legacy, "createDefaultClientState()"));
  assert.strictEqual(json(domain.createDefaultRuntimeState()), legacyJson(legacy, "createDefaultRuntimeState()"));
  assert.strictEqual(
    json(domain.createServerSavePayload(domain.createDefaultServerState(), "v384")),
    legacyJson(legacy, "(() => { const original = window.gameState.server; window.gameState.server = createDefaultServerState(); const value = getServerSavePayload('v384'); window.gameState.server = original; return value; })()"),
  );

  const fixture = {
    gold: 91,
    equipment: [{ name: "검" }, null],
    inventory: [null, { name: "물약" }],
    maxInventorySize: 3,
    records: { totalBossKills: 4 },
    skills: { lightsabre: { level: 3 } },
  };
  assert.strictEqual(
    json(domain.normalizePlayerState(fixture)),
    legacyJson(legacy, `ensurePlayerStateShape(${json(fixture)})`),
  );

  const saveFixture = {
    player: fixture,
    currentZoneIndex: "4",
    currentZoneType: "boss",
    fieldEnemyHp: { 4: 321 },
    fieldRespawnEndAt: { 4: 9000 },
  };
  assert.strictEqual(
    json(domain.applyServerSavePayload(saveFixture)),
    legacyJson(legacy, `(() => { applyServerSavePayload(${json(saveFixture)}); return gameState.server; })()`),
  );
}

function assertSlotParity(domain, legacy) {
  const original = [{ id: "a" }, null, { id: "b" }, null];
  assert.strictEqual(domain.countOccupiedItemSlots(original), vm.runInContext(`countOccupiedItemSlots(${json(original)})`, legacy));
  assert.strictEqual(domain.findFirstEmptyItemSlot(original, 6), vm.runInContext(`findFirstEmptyItemSlot(${json(original)}, 6)`, legacy));
  assert.strictEqual(domain.hasEmptyItemSlot(original, 6), vm.runInContext(`hasEmptyItemSlot(${json(original)}, 6)`, legacy));

  const placed = domain.placeItemInFirstEmptySlot(original, { id: "c" }, 6);
  const legacyPlaced = legacyJson(legacy, `(() => { const slots = ${json(original)}; const index = placeItemInFirstEmptySlot(slots, {id:'c'}, 6); return {slots, index}; })()`);
  assert.strictEqual(json(placed), legacyPlaced);

  const cleared = domain.clearItemSlot(original, 2);
  const legacyCleared = legacyJson(legacy, `(() => { const slots = ${json(original)}; const item = clearItemSlot(slots, 2); return {slots, index: item ? 2 : -1, item}; })()`);
  assert.strictEqual(json(cleared), legacyCleared);

  const compacted = domain.compactItemSlots(original);
  const legacyCompacted = legacyJson(legacy, `(() => { const slots = ${json(original)}; const result = compactItemSlots(slots); return {slots, ...result}; })()`);
  assert.strictEqual(json(compacted), legacyCompacted);
  assert.strictEqual(json(original), json([{ id: "a" }, null, { id: "b" }, null]), "typed slot helpers mutated input");
}

function assertCalculationParity(domain, legacy) {
  for (const value of [0, 149, 150, 201.5, 400, 999, "bad"]) {
    legacy.player.addAttackSpeed = value;
    assert.strictEqual(domain.clampFieldAttackSpeed(value), vm.runInContext("getClampedFieldAttackSpeed()", legacy));
    assert.strictEqual(domain.getBaseAttackByAttackSpeed(value), vm.runInContext("getBaseAttackByAttackSpeed()", legacy));
    assert.strictEqual(domain.getBasicAttackIntervalMs(value), vm.runInContext("getTotals().aspdMs", legacy));
  }
  for (const value of [0, 1, 9999, 10000, 123456789, -987654]) {
    assert.strictEqual(domain.formatCompactNumber(value), vm.runInContext(`formatCompactNumber(${value})`, legacy));
  }

  const totals = { attack: 100, basicAtkDmgInc: 25, allDmgInc: 40, basicCritDmg: 75 };
  const legacyDamage = vm.runInContext(`(() => { const t = ${json(totals)}; const baseDamage = Math.max(t.attack, 1); const critMult = 1 + t.basicCritDmg / 100; const damage = baseDamage * (1 + t.basicAtkDmgInc / 100) * (1 + t.allDmgInc / 100) * critMult; return isNaN(damage) ? 0 : damage; })()`, legacy);
  assert.strictEqual(domain.calculateBasicAttackDamage(totals, true), legacyDamage);
  assert.strictEqual(domain.rollChance(0.2, 50, 0.3), true);

  legacy.zones = [{ maxHp: 250 }];
  legacy.fieldEnemyHp = { 0: 0 };
  legacy.fieldRespawnEndAt = { 0: 1000 };
  const legacyField = legacyJson(legacy, `(() => ({ hp: getFieldEnemyHp(0), enemyHpByZone: fieldEnemyHp, respawnEndAtByZone: fieldRespawnEndAt, respawnPending: Boolean(fieldRespawnEndAt['0']) }))()`);
  const field = domain.resolveFieldEnemyState({ enemyHpByZone: { 0: 0 }, respawnEndAtByZone: { 0: 1000 } }, 0, 250, 1000);
  assert.strictEqual(json({ hp: field.hp, enemyHpByZone: field.enemyHpByZone, respawnEndAtByZone: field.respawnEndAtByZone, respawnPending: field.respawnPending }), legacyField);
}

function assertRuleAndResultParity(domain, legacy) {
  for (const boss of [null, { id: 1, skillDropRate: 0.4 }, { id: 10, skillDropRate: 0.4 }, { id: 2, isSpecial: true, skillDropRate: 0.4 }]) {
    assert.strictEqual(domain.getNormalBossSkillDropRate(boss), vm.runInContext(`getNormalBossSkillDropRate(${json(boss)})`, legacy));
    assert.strictEqual(domain.isFirstEquipSkillGuaranteeBoss(boss), vm.runInContext(`isFirstEquipSkillGuaranteeBoss(${json(boss)})`, legacy));
  }
  for (const name of [null, "심연의 편린 반지", "심연의 편린 목걸이", "심연의 편린 스태프", "기타"]) {
    assert.strictEqual(json(domain.getAbyssFragmentSpecialStats(name)), legacyJson(legacy, `getAbyssFragmentSpecialStats(${json(name)})`));
  }

  const result = domain.createGameActionResult("item.test", { itemName: "검" }, 1000);
  domain.addResultLog(result, "획득", true);
  domain.addResultEffect(result, { type: "itemDropText", itemName: "검" });
  domain.requestUiRefresh(result, "inventory");
  const legacyResult = legacyJson(legacy, `(() => { const result = createGameActionResult('item.test', {itemName:'검'}); addResultLog(result, '획득', true); addResultEffect(result, {type:'itemDropText', itemName:'검'}); requestUiRefresh(result, 'inventory'); return result; })()`);
  assert.strictEqual(json(result), legacyResult);

  assert.strictEqual(
    json(domain.failGameActionResult("item.test", "실패", { itemName: "검" }, 1000)),
    legacyJson(legacy, "failGameActionResult('item.test', '실패', {itemName:'검'})"),
  );
}

function main() {
  assertPureBoundary();
  const domain = loadDomain();
  const legacy = loadLegacy();
  assertStateParity(domain, legacy);
  assertSlotParity(domain, legacy);
  assertCalculationParity(domain, legacy);
  assertRuleAndResultParity(domain, legacy);
  console.log("PASS: Vue game domain foundation is pure and legacy-equivalent for fixed fixtures");
}

main();

const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "../../..");
const VUE_ROOT = path.join(ROOT, "frontend/vue-app");
const REQUIRED_FILES = [
  "src/game/adapters/skillEnhancement.ts",
  "src/components/game/GamePlayShell.vue",
  "src/components/game/GameSkillEnhancementShell.vue",
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
        "import * as skillEnhancement from './src/game/adapters/skillEnhancement.ts';",
        "globalThis.__gameAdapters = { town, skillEnhancement };",
      ].join("\n"),
      resolveDir: VUE_ROOT,
      sourcefile: "skill-enhancement-smoke-harness.ts",
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
    assert.ok(fs.existsSync(path.join(VUE_ROOT, relative)), `missing Vue skill/enhancement file: ${relative}`);
  }

  const adapter = read("src/game/adapters/skillEnhancement.ts");
  for (const forbidden of [
    /from\s+["'](?:vue|pinia|vue-router)["']/,
    /\b(?:window|document|localStorage|sessionStorage)\b/,
    /\bfetch\s*\(/,
    /\bMath\.random\s*\(/,
    /\bDate\.now\s*\(/,
    /\b(?:setTimeout|setInterval)\s*\(/,
  ]) assert.ok(!forbidden.test(adapter), `skill/enhancement adapter contains forbidden dependency: ${forbidden}`);
  for (const marker of [
    "const SLOT_ORDER = ['Q', 'W', 'E', 'R', 'T', 'F', 'D', 'SQ', 'SW', 'M']",
    "firstUseResultLevel",
    "기존 ${input.slotKey === 'SQ' ? 'Q' : 'W'} 레벨과 관계없이 첫 전용 강화권 결과는 Lv.1입니다.",
    "bonusLevel = 0",
    "Math.pow(2, nonNegativeInteger(step.fromLevel))",
    "mode: 'display-only'",
    "randomResultConnected: false",
    "saveConnected: false",
  ]) requireMarker(adapter, marker, "skill/enhancement adapter");

  const contracts = read("src/api/contracts.ts");
  for (const marker of [
    "export interface SkillOption",
    "export interface CharacterSkillOption",
    "export interface SkillLevelOption",
    "export interface EnhancementGroupOption",
    "export interface EnhancementLevelOption",
    "enhancementLevels?: EnhancementLevelOption[]",
  ]) requireMarker(contracts, marker, "master-data contracts");

  const account = read("src/stores/account.ts");
  for (const marker of ["const skills", "const characterSkills", "const skillLevels", "const enhancementGroups", "const enhancementLevels"]) {
    requireMarker(account, marker, "account master-data store");
  }

  const store = read("src/stores/game.ts");
  for (const forbidden of ["fetch(", "localStorage", "sessionStorage", "setInterval", "setTimeout", "Date.now", "Math.random"]) {
    assert.ok(!store.includes(forbidden), `game store must remain runtime-free: ${forbidden}`);
  }
  for (const marker of [
    "skillEnhancementModel",
    "enterSkillEnhancementPreview",
    "selectSkillEnhancementSkill",
    "selectEnhancementItem",
    "selectEnhancementLevel",
    "createdAt: 0",
  ]) requireMarker(store, marker, "skill/enhancement game store");

  const playShell = read("src/components/game/GamePlayShell.vue");
  requireMarker(playShell, 'v-else-if="game.isSkillEnhancement"', "game screen switch");
  requireMarker(playShell, "GameSkillEnhancementShell", "game screen switch");

  for (const navigation of ["src/components/game/GameTownShell.vue", "src/components/game/GameInventoryEquipmentShell.vue"]) {
    const source = read(navigation);
    requireMarker(source, "game.enterSkillEnhancementPreview", `${navigation} navigation`);
    requireMarker(source, "스킬·강화", `${navigation} navigation label`);
  }

  const component = read("src/components/game/GameSkillEnhancementShell.vue");
  for (const marker of [
    'data-zone="skill-enhancement"',
    'aria-label="스킬 선택"',
    "Q → W → E → R → T → F → D → SQ → SW → M",
    "탈리스만 A/B 레벨 보너스를 계승하지 않습니다.",
    'aria-label="강화 아이템 선택"',
    'aria-label="강화 단계 선택"',
    "game.selectSkillEnhancementSkill",
    "game.selectEnhancementItem",
    "game.selectEnhancementLevel",
    "스킬강화권 사용·장비 강화·Gold/재료 소비·난수 결과·snapshot load/save·자동 저장·전투 runtime",
  ]) requireMarker(component, marker, "skill/enhancement component");
  assert.ok(!component.includes("town-session-bar"), "connected character bar must remain town-only");
  assert.ok(!component.includes("v-html"), "master-data descriptions must render as text, not raw HTML");
  assert.ok((component.match(/type="button" disabled/g) || []).length >= 3, "skill and enhancement mutation actions must remain disabled");

  const styles = read("src/styles/base.css");
  for (const selector of [
    ".skill-enhancement-command-bar",
    ".skill-browser__grid",
    ".skill-detail__rule",
    ".enhancement-layout",
    ".enhancement-ladder",
    ".enhancement-detail__chance",
    ".skill-enhancement-data-boundary",
    "@media (max-width: 480px)",
  ]) requireMarker(styles, selector, "skill/enhancement responsive CSS");
}

function makeSkill(code, slotKey, name, options = {}, procRate = null, cooldownSeconds = null) {
  return { code, slotKey, name, description: `${name} 설명`, procRate, cooldownSeconds, options };
}

function makeItem(code, name, itemType, groupCode, options) {
  return {
    code,
    name,
    itemType,
    grade: "1",
    description: `${name} 설명`,
    stackable: false,
    equipSlot: null,
    enhanceGroupCode: groupCode,
    options,
  };
}

function assertAdapterBehavior() {
  const adapters = loadAdapters();
  const townSource = {
    accountCharacterId: "f".repeat(32),
    slotKey: "character-6",
    characterName: "기호검성",
    characterCode: "weapon_master",
    characterLabel: "검성",
    progress: { gold: 96000, level: 27, currentZoneIndex: null, currentZoneType: "town", updatedAt: null },
  };
  const skills = [
    makeSkill("lightsabre", "Q", "광검 마스터리", {
      skillType: "passive_damage",
      effectHtml: "-기본 공격 피해<br>-계수 적용",
      damageMultiplier: 1,
      bonusGroup: null,
      raw: { maxLevel: 7 },
      awakening: { slotKey: "SQ", name: "극 귀검술 - 유성락", description: "유성락", effectHtml: "-0.5% 발동<br>-강력한 피해", baseProcRate: 0.5, damageMultiplier: 200000, bonusGroup: null },
    }),
    makeSkill("ironStrike", "W", "극 귀검술 - 참철식", {
      skillType: "passive_damage",
      effectHtml: "-참철식 피해",
      damageMultiplier: 500,
      raw: { maxLevel: 7 },
      awakening: { slotKey: "SW", name: "극 발검술 - 무형참", description: "무형참", effectHtml: "-0.5% 발동", baseProcRate: 0.5, damageMultiplier: 320000, bonusGroup: null },
    }, 3),
    makeSkill("overdrive", "E", "오버 드라이브", { skillType: "proc_buff_damage", effectHtml: "-버프 피해", damageMultiplier: 150, raw: { maxLevel: 7 } }, 2),
    makeSkill("baldo", "R", "발도", { skillType: "proc_damage", effectHtml: "-발도 피해", damageMultiplier: 4000, bonusGroup: "talismanA", raw: { maxLevel: 7 } }, 3),
    makeSkill("illusionSword", "T", "환영검무", { skillType: "proc_damage", effectHtml: "-검무 피해", damageMultiplier: 12000, bonusGroup: "talismanA", raw: { maxLevel: 7 } }, 2),
    makeSkill("deepSword", "F", "심검", { skillType: "proc_damage", effectHtml: "-심검 피해", damageMultiplier: 16000, bonusGroup: "talismanB", raw: { maxLevel: 7 } }, 2),
    makeSkill("tempestStrike", "D", "폭풍식", { skillType: "proc_damage", effectHtml: "-폭풍식 피해", damageMultiplier: 42000, bonusGroup: "talismanB", raw: { maxLevel: 7 } }, 1.2),
    makeSkill("heavenlyStrike", "M", "천제극섬", { skillType: "ultimate_proc_damage", effectHtml: "-궁극 피해", damageMultiplier: 11000000, raw: { maxLevel: 7 } }, 5, 300),
  ];
  const characterSkills = skills.map((skill, index) => ({ characterCode: "weapon_master", skillCode: skill.code, sortOrder: index, isDefault: index === 0 }));
  const skillLevels = skills.flatMap((skill) => Array.from({ length: 8 }, (_, level) => ({ skillCode: skill.code, level, damageMultiplier: 1, procRateBonus: 0 })));
  const itemTemplates = [
    makeItem("normal_sword", "샤이닝 인텔리전스", "normal", "normal_equipment", { equipGroup: "skill_all", tier: 1, baseCost: 20000 }),
    makeItem("talisman_a", "탈리스만 원형", "special_equip", "talisman_emblem", { specialSlotIdx: 12, tier: 1 }),
  ];
  const enhancementGroups = [
    { code: "normal_equipment", name: "일반 장비 강화", description: "일반 장비 규칙", maxLevel: 20, rules: {}, isEnabled: true },
    { code: "talisman_emblem", name: "탈리스만/빛나는 휘장 강화", description: "동일 장비 재료 규칙", maxLevel: 6, rules: {}, isEnabled: true },
  ];
  const enhancementLevels = [
    { groupCode: "normal_equipment", fromLevel: 0, toLevel: 1, successRate: 1, goldCost: 0, materialRules: {}, resultStats: { statProgression: { atk: 460, sdmg: 10.1, alldmg: 5.1 } }, failRules: { note: "실패 시 하락 없음" } },
    { groupCode: "normal_equipment", fromLevel: 3, toLevel: 4, successRate: 0.3, goldCost: 0, materialRules: {}, resultStats: { statProgression: { atk: 550 } }, failRules: {} },
    { groupCode: "talisman_emblem", fromLevel: 0, toLevel: 1, successRate: 0, goldCost: 0, materialRules: { costFormula: "2^currentLevel" }, resultStats: {}, failRules: {} },
    { groupCode: "talisman_emblem", fromLevel: 2, toLevel: 3, successRate: 0, goldCost: 0, materialRules: { costFormula: "2^currentLevel" }, resultStats: {}, failRules: {} },
  ];
  const before = JSON.stringify({ townSource, skills, characterSkills, skillLevels, itemTemplates, enhancementGroups, enhancementLevels });
  const town = adapters.town.createTownHudViewModel(townSource);
  town.serverState.player.skills.lightsabre.level = 4;
  town.serverState.player.skills.ironStrike.level = 5;

  const normal = adapters.skillEnhancement.createSkillEnhancementViewModel({
    town, skills, characterSkills, skillLevels, itemTemplates, enhancementGroups, enhancementLevels,
    preferredSkillId: "lightsabre:sq", preferredItemCode: "normal_sword", preferredEnhancementLevel: 0, createdAt: 0,
  });
  const talisman = adapters.skillEnhancement.createSkillEnhancementViewModel({
    town, skills, characterSkills, skillLevels, itemTemplates, enhancementGroups, enhancementLevels,
    preferredSkillId: "ironStrike:sw", preferredItemCode: "talisman_a", preferredEnhancementLevel: 2, createdAt: 0,
  });

  assert.strictEqual(normal.zoneType, "skill-enhancement");
  assert.deepStrictEqual(Array.from(normal.skills, (skill) => skill.slotKey), ["Q", "W", "E", "R", "T", "F", "D", "SQ", "SW", "M"]);
  assert.strictEqual(normal.skills.length, 10);
  assert.strictEqual(normal.selectedSkill.slotKey, "SQ");
  assert.strictEqual(normal.selectedSkill.currentLevel, 0);
  assert.strictEqual(normal.selectedSkill.firstUseResultLevel, 1, "SQ first dedicated book must preview level 1 regardless of Q level");
  assert.strictEqual(normal.selectedSkill.bonusGroup, null, "SQ must not inherit talisman A");
  assert.strictEqual(normal.selectedSkill.bonusLevel, 0);
  assert.strictEqual(talisman.selectedSkill.slotKey, "SW");
  assert.strictEqual(talisman.selectedSkill.firstUseResultLevel, 1, "SW first dedicated book must preview level 1 regardless of W level");
  assert.strictEqual(talisman.selectedSkill.bonusGroup, null, "SW must not inherit talisman B");
  assert.strictEqual(normal.selectedEnhancementStep.successRateLabel, "100%");
  assert.strictEqual(normal.selectedEnhancementStep.goldCost, 20000, "normal enhancement should preview item base cost when level cost is zero");
  assert.strictEqual(normal.selectedEnhancementStep.costSourceLabel, "아이템 기본 비용");
  assert.strictEqual(normal.selectedEnhancementStep.resultStats[0].value, "460");
  assert.strictEqual(talisman.selectedEnhancementStep.materialCount, 4, "talisman +2 step must require 2^2 matching +0 items");
  assert.strictEqual(talisman.selectedEnhancementStep.materialLabel, "동일한 +0 장비 4개");
  assert.strictEqual(talisman.selectedEnhancementStep.successRateLabel, "100%", "legacy talisman material enhancement must remain guaranteed despite the current DB placeholder rate");
  assert.strictEqual(normal.action.type, "skill-enhancement.preview.open");
  assert.strictEqual(normal.snapshotConnected, false);
  assert.strictEqual(normal.skillMutationConnected, false);
  assert.strictEqual(normal.itemMutationConnected, false);
  assert.strictEqual(normal.randomResultConnected, false);
  assert.strictEqual(normal.saveConnected, false);
  assert.strictEqual(JSON.stringify({ townSource, skills, characterSkills, skillLevels, itemTemplates, enhancementGroups, enhancementLevels }), before, "adapter mutated source master-data");
}

function main() {
  assertStaticBoundary();
  assertAdapterBehavior();
  console.log("PASS: Vue skill/enhancement UI preserves SQ/SW level-1 awakening and enhancement preview rules without skill, item, random, snapshot, or save mutation");
}

main();

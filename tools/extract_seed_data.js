#!/usr/bin/env node
/**
 * tools/extract_seed_data.js
 *
 * 현재 브라우저 JS 마스터 데이터를 PostgreSQL seed 준비용 JSON으로 추출합니다.
 * 이 스크립트는 DB에 직접 넣지 않고, 백엔드가 읽을 수 있는 seed 초안을 생성합니다.
 *
 * 실행:
 *   node tools/extract_seed_data.js
 *
 * 출력:
 *   backend/seeds/generated/*.json
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..");
const OUT_DIR = path.join(ROOT, "backend", "seeds", "generated");

const SCRIPT_PATHS = [
  "src/data/skills.js",
  "src/state/game-state.js",
  "src/utils/icon-utils.js",
  "src/data/boss-factories.js",
  "src/data/bosses.js",
  "src/rules/abyss-fragment-rules.js",
  "src/rules/boss-display-rules.js",
  "src/rules/boss-drop-rules.js",
  "src/data/boss-bootstrap.js",
  "src/data/zones.js",
  "src/systems/stat-system.js",
];

function loadBrowserScripts() {
  const context = {
    console,
    Math,
    Date,
    JSON,
    Number,
    String,
    Boolean,
    Array,
    Object,
    parseInt,
    parseFloat,
    isNaN,
    setTimeout() {},
    clearTimeout() {},
  };
  context.window = context;
  context.globalThis = context;
  context.document = {
    getElementById() { return null; },
    querySelector() { return null; },
    querySelectorAll() { return []; },
  };

  vm.createContext(context);
  SCRIPT_PATHS.forEach((relPath) => {
    const absPath = path.join(ROOT, relPath);
    const code = fs.readFileSync(absPath, "utf8");
    vm.runInContext(code, context, { filename: relPath });
  });
  return context;
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function safeFileName(name) {
  return String(name).replace(/[^a-zA-Z0-9가-힣_.-]+/g, "_").replace(/^_+|_+$/g, "");
}

function getRawData(context) {
  return vm.runInContext(`({
    bossList,
    specialBossList,
    zones,
    characterMasterData,
    skillMasterData,
    skillBookMasterData,
    enhanceTable,
    curveAtkInc,
    curveSmult,
    extraSmult,
    getNormalBossSkillDropRate,
    getBaseEnhanceProb,
  })`, context);
}

function normalizeCharacters(raw) {
  return Object.values(raw.characterMasterData).map((character) => ({
    id: character.id,
    name: character.name,
    description: character.description || "",
    skillIds: character.skillIds || [],
    isDefault: character.id === "weapon_master",
  }));
}

function normalizeSkills(raw) {
  return Object.values(raw.skillMasterData).map((skill) => ({
    id: skill.id,
    slotKey: skill.slotKey,
    name: skill.name,
    img: skill.img || null,
    description: skill.description || "",
    effectHtml: skill.effectHtml || "",
    maxLevel: skill.maxLevel || 7,
    skillType: skill.skillType || null,
    baseProcRate: skill.baseProcRate ?? null,
    damageMultiplier: skill.damageMultiplier ?? null,
    cooldownMs: skill.cooldownMs ?? null,
    bonusGroup: skill.bonusGroup ?? null,
    awakening: skill.awakening || null,
  }));
}

function normalizeSkillBooks(raw) {
  return Object.values(raw.skillBookMasterData).map((book) => ({ ...book }));
}

function getItemTemplateKey(item) {
  const parts = [
    item.name || "unknown",
    item.type || "unknown",
    item.tier ?? "no-tier",
    item.equipGroup ?? "no-group",
    item.specialSlotIdx ?? "no-special-slot",
    item.isTalisman ? "talisman" : "",
    item.isEmblem ? "emblem" : "",
  ].filter(Boolean);
  return safeFileName(parts.join("__"));
}

function normalizeItemTemplates(allBosses) {
  const map = new Map();
  allBosses.forEach((boss) => {
    (boss.drops || []).forEach((drop) => {
      const key = getItemTemplateKey(drop);
      if (!map.has(key)) {
        map.set(key, {
          templateKey: key,
          name: drop.name,
          type: drop.type || null,
          tier: drop.tier ?? boss.id ?? null,
          img: drop.img || null,
          equipGroup: drop.equipGroup || null,
          equipLimit: drop.equipLimit ?? null,
          equipText: drop.equipText || null,
          specialSlotIdx: drop.specialSlotIdx ?? null,
          isTalisman: !!drop.isTalisman,
          isEmblem: !!drop.isEmblem,
          sellPrice: drop.sellPrice ?? null,
          baseCost: drop.baseCost ?? null,
          baseIlv: drop.baseIlv ?? null,
          baseStats: {},
          specialStats: drop.specialStats || null,
          raw: clone(drop),
          sourceBossIds: [],
        });
      }
      const existing = map.get(key);
      if (!existing.sourceBossIds.includes(boss.id)) existing.sourceBossIds.push(boss.id);
    });
  });

  const statKeys = [
    "baseAtk",
    "baseSdmg",
    "baseAllDmg",
    "baseAtkInc",
    "baseNdmg",
    "baseSchance",
    "baseSmult",
    "baseNcRate",
    "baseNcDmg",
    "skillProcChanceInc",
    "skillCoefficientInc",
    "skillCooldownReductionInc",
    "allSkillDamageInc",
    "allBuffValueInc",
    "cloneCountInc",
    "cloneAttackSpeedInc",
    "maxAttackSpeedCapInc",
  ];

  return [...map.values()].map((item) => {
    statKeys.forEach((key) => {
      if (item.raw[key] !== undefined) item.baseStats[key] = item.raw[key];
    });
    return item;
  });
}

function getDropRate(raw, boss, drop) {
  if (drop.individualDropRate !== undefined) return drop.individualDropRate;
  if (drop.type === "skill_book") {
    if (boss.isSpecial) return boss.skillDropRate || 0;
    return raw.getNormalBossSkillDropRate(boss) || 0;
  }
  if (drop.isTalisman || (drop.name && drop.name.includes("탈리스만"))) return boss.talismanDropRate || boss.equipDropRate || 0;
  if (drop.isEmblem || (drop.name && drop.name.includes("빛나는 휘장"))) return boss.emblemDropRate || boss.equipDropRate || 0;
  return boss.equipDropRate || 0;
}

function normalizeDropTables(raw, allBosses) {
  const dropTables = [];
  const dropTableItems = [];
  allBosses.forEach((boss) => {
    const tableId = `boss_${boss.id}_default`;
    dropTables.push({
      id: tableId,
      bossId: boss.id,
      bossName: boss.name,
      bossType: boss.isSpecial ? "special" : "normal",
      title: boss.dropTitle || "[획득 가능 아이템]",
      rawEquipDropRate: boss.equipDropRate ?? null,
      rawSkillDropRate: boss.skillDropRate ?? null,
      rawTalismanDropRate: boss.talismanDropRate ?? null,
      rawEmblemDropRate: boss.emblemDropRate ?? null,
    });

    (boss.drops || []).forEach((drop, index) => {
      dropTableItems.push({
        id: `${tableId}_${index + 1}`,
        dropTableId: tableId,
        bossId: boss.id,
        itemTemplateKey: getItemTemplateKey(drop),
        itemName: drop.name,
        itemType: drop.type || null,
        rate: getDropRate(raw, boss, drop),
        quantityMin: 1,
        quantityMax: drop.count || 1,
        sortOrder: index + 1,
        raw: clone(drop),
      });
    });
  });
  return { dropTables, dropTableItems };
}

function normalizeBosses(allBosses) {
  return allBosses.map((boss) => ({
    id: boss.id,
    isSpecial: !!boss.isSpecial,
    name: boss.name,
    title: boss.title || null,
    desc1: boss.desc1 || null,
    desc2: boss.desc2 || null,
    desc3: boss.desc3 || null,
    reqLvl: boss.reqLvl || null,
    img: boss.img || null,
    maxHp: boss.maxHp,
    cooldownMs: boss.cooldownMs ?? null,
    equipDropRate: boss.equipDropRate ?? null,
    skillDropRate: boss.skillDropRate ?? null,
    talismanDropRate: boss.talismanDropRate ?? null,
    emblemDropRate: boss.emblemDropRate ?? null,
    dropRateDoubled: !!boss.dropRateDoubled,
    dropsList: boss.dropsList || [],
  }));
}

function normalizeFieldZones(raw) {
  return raw.zones.map((zone) => ({
    level: zone.level,
    name: zone.name,
    enemyName: zone.enemyName || "",
    img: zone.img || null,
    maxHp: zone.maxHp,
    goldReward: zone.goldReward,
    req: zone.req || null,
    farm: zone.farm || null,
  }));
}

function normalizeEnhancementRules(raw) {
  const normalProbLevels = [];
  for (let level = 0; level <= 20; level += 1) {
    normalProbLevels.push({
      level,
      successRate: raw.getBaseEnhanceProb(level),
    });
  }
  return {
    normalEquipment: {
      maxLevel: 20,
      successRatesByCurrentLevel: normalProbLevels,
      statProgression: raw.enhanceTable,
      curveAtkInc: raw.curveAtkInc,
      curveSmult: raw.curveSmult,
      extraSmult: raw.extraSmult,
    },
    talismanAndEmblem: {
      maxLevel: 6,
      materialRule: "same_item_zero_level_material",
      materialCostFormula: "2^currentLevel",
      note: "탈리스만/빛나는 휘장은 0강 재료를 소모해서 강화합니다. 실제 성공 확률/세부 수치는 item-system.js에서 추가 DB화 대상입니다.",
    },
  };
}

function writeJson(fileName, value) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(path.join(OUT_DIR, fileName), `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function main() {
  const context = loadBrowserScripts();
  const raw = getRawData(context);
  const normalBosses = clone(raw.bossList);
  const specialBosses = clone(raw.specialBossList);
  const allBosses = [...normalBosses, ...specialBosses];

  const characters = normalizeCharacters(raw);
  const skills = normalizeSkills(raw);
  const skillBooks = normalizeSkillBooks(raw);
  const bosses = normalizeBosses(allBosses);
  const fieldZones = normalizeFieldZones(raw);
  const itemTemplates = normalizeItemTemplates(allBosses);
  const { dropTables, dropTableItems } = normalizeDropTables(raw, allBosses);
  const enhancementRules = normalizeEnhancementRules(raw);

  const manifest = {
    generatedAt: new Date().toISOString(),
    source: "current browser JS master data",
    counts: {
      characters: characters.length,
      skills: skills.length,
      skillBooks: skillBooks.length,
      bosses: bosses.length,
      normalBosses: normalBosses.length,
      specialBosses: specialBosses.length,
      fieldZones: fieldZones.length,
      itemTemplates: itemTemplates.length,
      dropTables: dropTables.length,
      dropTableItems: dropTableItems.length,
    },
    files: [
      "characters.json",
      "skills.json",
      "skill_books.json",
      "bosses.json",
      "field_zones.json",
      "item_templates.json",
      "drop_tables.json",
      "drop_table_items.json",
      "enhancement_rules.json",
    ],
  };

  writeJson("characters.json", characters);
  writeJson("skills.json", skills);
  writeJson("skill_books.json", skillBooks);
  writeJson("bosses.json", bosses);
  writeJson("field_zones.json", fieldZones);
  writeJson("item_templates.json", itemTemplates);
  writeJson("drop_tables.json", dropTables);
  writeJson("drop_table_items.json", dropTableItems);
  writeJson("enhancement_rules.json", enhancementRules);
  writeJson("manifest.json", manifest);

  console.log("Seed data extracted:");
  Object.entries(manifest.counts).forEach(([key, value]) => console.log(`- ${key}: ${value}`));
  console.log(`Output: ${path.relative(ROOT, OUT_DIR)}`);
}

main();

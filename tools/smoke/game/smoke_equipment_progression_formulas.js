const fs = require("fs");
const path = require("path");
const vm = require("vm");
const crypto = require("crypto");

const root = path.resolve(__dirname, "..", "..", "..");

function read(file) {
  return fs.readFileSync(path.join(root, file), "utf8");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function assertEqual(actual, expected, label) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${expected}, got ${actual}`);
  }
}

function round1(value) {
  return Number(value.toFixed(1));
}

const context = { console, Date, Math };
context.window = context;
vm.createContext(context);

for (const file of [
  "src/utils/icon-utils.js",
  "src/data/boss-factories.js",
  "src/data/bosses.js",
  "src/systems/stat-system.js",
]) {
  vm.runInContext(read(file), context, { filename: file });
}

vm.runInContext(
  "globalThis.__bossList = bossList; globalThis.__specialBossList = specialBossList; globalThis.__calcItemStats = calcItemStats; globalThis.__calcSpecialEquipStats = calcSpecialEquipStats; globalThis.__isEnhanceableSpecialEquip = isEnhanceableSpecialEquip; globalThis.__getEquipGroup = getEquipGroup; globalThis.__enhanceTable = enhanceTable;",
  context,
);

const bossList = context.__bossList;
const specialBossList = context.__specialBossList;
const calcItemStats = context.__calcItemStats;
const calcSpecialEquipStats = context.__calcSpecialEquipStats;
const isEnhanceableSpecialEquip = context.__isEnhanceableSpecialEquip;
const getEquipGroup = context.__getEquipGroup;
const enhanceTable = context.__enhanceTable;
const expectedGroups = ["skill_all", "atk_inc", "normal_dmg", "skill_chance", "normal_crit"];

const tierAudit = [
  { tier: 1, attack: [450, 6950], skill: [10, 58.5], all: [5, 31.5], atkInc: [10, 23.3], normal: [40, 525], skillMult: [500, 43555], crit: [200, 4080] },
  { tier: 2, attack: [684, 10564], skill: [20, 97.6], all: [10, 44.5], atkInc: [15, 41.5], normal: [50, 923], skillMult: [1000, 58388], crit: [300, 8060] },
  { tier: 3, attack: [1040, 16057], skill: [30, 136.7], all: [15, 57.4], atkInc: [20, 59.8], normal: [60, 1321], skillMult: [1500, 79815], crit: [390, 12030] },
  { tier: 4, attack: [1580, 24406], skill: [40, 175.8], all: [20, 70.3], atkInc: [25, 78], normal: [75, 1724], skillMult: [3900, 107100], crit: [508, 16157] },
  { tier: 5, attack: [2135, 36831], skill: [50, 214.9], all: [25, 83.3], atkInc: [30, 96.3], normal: [100, 2137], skillMult: [5400, 143000], crit: [711, 21941] },
  { tier: 6, attack: [3245, 55983], skill: [60, 254], all: [30, 96.3], atkInc: [35, 114], normal: [125, 2550], skillMult: [7600, 195700], crit: [900, 29575] },
  { tier: 7, attack: [4933, 85096], skill: [70, 293.1], all: [35, 109.2], atkInc: [40, 132.8], normal: [150, 2963], skillMult: [10700, 264570], crit: [1200, 39985] },
  { tier: 8, attack: [7498, 129346], skill: [80, 332.2], all: [40, 122.2], atkInc: [45, 151], normal: [175, 3376], skillMult: [15060, 357825], crit: [1749, 54019] },
  { tier: 9, attack: [11400, 196608], skill: [90, 371.3], all: [45, 135.1], atkInc: [50, 169.3], normal: [200, 3789], skillMult: [21080, 483815], crit: [2361, 72576] },
  { tier: 10, attack: [17300, 298817], skill: [100, 410.4], all: [50, 148.1], atkInc: [55, 187.5], normal: [225, 4202], skillMult: [29520, 654255], crit: [3187, 98302] },
  { tier: 11, attack: [26300, 454206], skill: [110, 449.5], all: [55, 161], atkInc: [60, 205.8], normal: [250, 4615], skillMult: [41320, 884660], crit: [4303, 132773] },
  { tier: 12, attack: [40000, 691000], skill: [120, 607], all: [60, 173.9], atkInc: [65, 224], normal: [275, 5028], skillMult: [45450, 1057562], crit: [5809, 179119] },
];

function normalDropsForTier(tier) {
  const boss = bossList.find((candidate) => candidate.id === tier && !candidate.isSpecial);
  assert(boss, `tier ${tier}: normal boss is missing`);
  return boss.drops.filter((item) => item.type === "normal");
}

for (const expected of tierAudit) {
  const drops = normalDropsForTier(expected.tier);
  assertEqual(drops.length, 5, `tier ${expected.tier}: normal equipment count`);
  assertEqual(
    drops.map((item) => getEquipGroup(item)).join(","),
    expectedGroups.join(","),
    `tier ${expected.tier}: equipment group order`,
  );

  const at0 = drops.map((item) => calcItemStats({ ...item, level: 0 }));
  const at20 = drops.map((item) => calcItemStats({ ...item, level: 20 }));

  for (let index = 0; index < drops.length; index += 1) {
    assertEqual(drops[index].tier, expected.tier, `tier ${expected.tier} item ${index + 1}: tier`);
    assertEqual(at0[index].attack, expected.attack[0], `tier ${expected.tier} item ${index + 1}: attack +0`);
    assertEqual(at20[index].attack, expected.attack[1], `tier ${expected.tier} item ${index + 1}: attack +20`);
  }

  assertEqual(at0[0].skillDmgInc, expected.skill[0], `tier ${expected.tier}: skill damage +0`);
  assertEqual(at20[0].skillDmgInc, expected.skill[1], `tier ${expected.tier}: skill damage +20`);
  assertEqual(at0[0].allDmgInc, expected.all[0], `tier ${expected.tier}: all damage +0`);
  assertEqual(at20[0].allDmgInc, expected.all[1], `tier ${expected.tier}: all damage +20`);
  assertEqual(at0[1].atkInc, expected.atkInc[0], `tier ${expected.tier}: attack increase +0`);
  assertEqual(at20[1].atkInc, expected.atkInc[1], `tier ${expected.tier}: attack increase +20`);
  assertEqual(at0[2].basicAtkDmgInc, expected.normal[0], `tier ${expected.tier}: normal damage +0`);
  assertEqual(at20[2].basicAtkDmgInc, expected.normal[1], `tier ${expected.tier}: normal damage +20`);
  assertEqual(at0[3].addSkillAtkChance, 20, `tier ${expected.tier}: extra skill chance +0`);
  assertEqual(at20[3].addSkillAtkChance, 20, `tier ${expected.tier}: extra skill chance +20`);
  assertEqual(at0[3].addSkillAtkMult, expected.skillMult[0], `tier ${expected.tier}: extra skill multiplier +0`);
  assertEqual(at20[3].addSkillAtkMult, expected.skillMult[1], `tier ${expected.tier}: extra skill multiplier +20`);
  assertEqual(at0[4].basicCritChance, 35, `tier ${expected.tier}: normal crit chance +0`);
  assertEqual(at20[4].basicCritChance, 35, `tier ${expected.tier}: normal crit chance +20`);
  assertEqual(at0[4].basicCritDmg, expected.crit[0], `tier ${expected.tier}: normal crit damage +0`);
  assertEqual(at20[4].basicCritDmg, expected.crit[1], `tier ${expected.tier}: normal crit damage +20`);

  for (let index = 0; index < drops.length; index += 1) {
    let previous = calcItemStats({ ...drops[index], level: 0 });
    for (let level = 1; level <= 20; level += 1) {
      const current = calcItemStats({ ...drops[index], level });
      assert(current.attack >= previous.attack, `tier ${expected.tier} item ${index + 1}: attack decreased at +${level}`);
      for (const key of ["skillDmgInc", "allDmgInc", "atkInc", "basicAtkDmgInc", "addSkillAtkMult", "basicCritDmg"]) {
        assert(current[key] >= previous[key], `tier ${expected.tier} item ${index + 1}: ${key} decreased at +${level}`);
      }
      previous = current;
    }
  }
}

const tier1To12SpecialEquipment = bossList
  .filter((boss) => boss.id >= 1 && boss.id <= 12 && !boss.isSpecial)
  .flatMap((boss) => boss.drops)
  .filter((item) => item.type === "special_equip");
assertEqual(tier1To12SpecialEquipment.length, 5, "tier 1-12: special equipment count");

for (const item of tier1To12SpecialEquipment) {
  assert(item.isTalisman || item.name.includes("탈리스만"), `${item.name}: expected talisman`);
  assertEqual(calcItemStats({ ...item, level: 6 }), null, `${item.name}: normal stat calculation boundary`);
  for (const level of [0, 6]) {
    const stats = calcSpecialEquipStats({ ...item, level });
    for (const [key, value] of Object.entries(stats)) {
      assertEqual(value, 0, `${item.name}: ${key} should remain zero at +${level}`);
    }
  }
}

assert(
  read("src/systems/item-system.js").includes("currentItem.level >= 6"),
  "talisman/emblem enhancement max +6 boundary changed",
);
assert(
  read("src/systems/combat-system.js").includes("return isTalisman ? (parseInt(eq.level) || 0) + 1 : 0;"),
  "talisman skill level bonus must remain enhancement level +1",
);

const anchorTier = 12;
const anchorTarget20 = 607;
const tier16Target20 = 2121;
const level20Delta = enhanceTable[20].sdmg - enhanceTable[0].sdmg;
const highTierTargetRatio = Math.pow(tier16Target20 / anchorTarget20, 1 / (16 - anchorTier));

function expectedHighTierSkillDamage20(tier) {
  return round1(anchorTarget20 * Math.pow(highTierTargetRatio, tier - anchorTier));
}

function expectedHighTierSkillDamage(tier, level) {
  const base = 10 * tier;
  const delta = enhanceTable[level].sdmg - enhanceTable[0].sdmg;
  const progress = delta / level20Delta;
  return round1(base + (expectedHighTierSkillDamage20(tier) - base) * progress);
}

let previousTier20 = 0;
for (let tier = 12; tier <= 39; tier += 1) {
  const drops = normalDropsForTier(tier);
  const skillDrops = drops.filter((item) => getEquipGroup(item) === "skill_all");
  assertEqual(skillDrops.length, 1, `tier ${tier}: skill_all equipment count`);

  const skillItem = skillDrops[0];
  for (let level = 0; level <= 20; level += 1) {
    const stats = calcItemStats({ ...skillItem, level });
    assertEqual(stats.skillDmgInc, expectedHighTierSkillDamage(tier, level), `tier ${tier}: skill damage +${level}`);
    const expectedAllDamage = round1(
      5 * tier
      + (enhanceTable[level].alldmg - enhanceTable[0].alldmg) * (1 + 0.3 * (tier - 1)),
    );
    assertEqual(stats.allDmgInc, expectedAllDamage, `tier ${tier}: unchanged all damage +${level}`);
  }

  const at20 = calcItemStats({ ...skillItem, level: 20 });
  assert(at20.skillDmgInc > previousTier20, `tier ${tier}: +20 skill damage is not increasing`);
  previousTier20 = at20.skillDmgInc;

  for (const item of drops.filter((candidate) => getEquipGroup(candidate) !== "skill_all")) {
    const at0 = calcItemStats({ ...item, level: 0 });
    const max = calcItemStats({ ...item, level: 20 });
    assertEqual(at0.skillDmgInc, 0, `tier ${tier} ${item.name}: unexpected skill damage +0`);
    assertEqual(max.skillDmgInc, 0, `tier ${tier} ${item.name}: unexpected skill damage +20`);
  }
}

const nonTargetFields = [
  "attack",
  "allDmgInc",
  "atkInc",
  "basicAtkDmgInc",
  "addSkillAtkChance",
  "addSkillAtkMult",
  "basicCritChance",
  "basicCritDmg",
  "ilv",
];
const highTierNonTargetRows = [];
for (let tier = 12; tier <= 39; tier += 1) {
  const drops = normalDropsForTier(tier);
  for (let index = 0; index < drops.length; index += 1) {
    const group = getEquipGroup(drops[index]);
    for (let level = 0; level <= 20; level += 1) {
      const stats = calcItemStats({ ...drops[index], level });
      highTierNonTargetRows.push([
        tier,
        index,
        group,
        level,
        ...nonTargetFields.map((key) => stats[key]),
      ]);
    }
  }
}
const highTierNonTargetDigest = crypto
  .createHash("sha256")
  .update(JSON.stringify(highTierNonTargetRows))
  .digest("hex");
assertEqual(
  highTierNonTargetDigest,
  "2fcd38c6412c7b713409b180bce0538bb37425da47f3956225b78e97cfc2fa34",
  "tier 12-39 non-target stat digest",
);

assertEqual(expectedHighTierSkillDamage(12, 20), 607, "tier 12 anchor");
assertEqual(expectedHighTierSkillDamage(13, 20), 829.9, "tier 13 projection");
assertEqual(expectedHighTierSkillDamage(14, 20), 1134.7, "tier 14 projection");
assertEqual(expectedHighTierSkillDamage(15, 20), 1551.3, "tier 15 projection");
assertEqual(expectedHighTierSkillDamage(16, 20), 2121, "tier 16 anchor");
assertEqual(expectedHighTierSkillDamage(17, 20), 2899.9, "tier 17 projection");
assertEqual(expectedHighTierSkillDamage(18, 20), 3964.8, "tier 18 projection");
assertEqual(expectedHighTierSkillDamage(39, 20), 2823673.9, "tier 39 projection");

const tier16Drops = normalDropsForTier(16);
const tier16Skill = tier16Drops.find((item) => getEquipGroup(item) === "skill_all");
const tier16At20 = calcItemStats({ ...tier16Skill, level: 20 });
const tier16ExpectedByLevel = [
  160, 164, 172.1, 184.3, 200.4, 220.6, 244.9,
  273.2, 305.6, 341.9, 382.4, 447.1, 536, 649.2,
  786.7, 948.4, 1134.4, 1344.7, 1579.2, 1838, 2121,
];
assertEqual(tier16Skill.name, "무의식 : 넥스의 몽환의 어둠", "tier 16 skill item name");
assertEqual(tier16At20.attack, 3690000, "tier 16 skill item attack +20");
assertEqual(tier16At20.skillDmgInc, 2121, "tier 16 skill item skill damage +20");
assertEqual(tier16At20.allDmgInc, 225.8, "tier 16 skill item unchanged all damage +20");
for (let level = 0; level <= 20; level += 1) {
  assertEqual(
    calcItemStats({ ...tier16Skill, level }).skillDmgInc,
    tier16ExpectedByLevel[level],
    `tier 16 skill item explicit progression +${level}`,
  );
}

const tier17Drops = normalDropsForTier(17);
const tier17SkillChanceItem = tier17Drops.find((item) => getEquipGroup(item) === "skill_chance");
const tier17NormalCritItem = tier17Drops.find((item) => getEquipGroup(item) === "normal_crit");
const tier17SkillChance = calcItemStats({ ...tier17SkillChanceItem, level: 20 });
const tier17NormalCrit = calcItemStats({ ...tier17NormalCritItem, level: 20 });
assertEqual(tier17SkillChanceItem.name, "-진- 원초의 꿈 : 스태프", "tier 17 staff name");
assertEqual(tier17NormalCritItem.name, "-진- 원초의 꿈 : 창", "tier 17 spear name");
assertEqual(tier17SkillChance.skillDmgInc, 0, "tier 17 staff unchanged skill damage +20");
assertEqual(tier17NormalCrit.skillDmgInc, 0, "tier 17 spear unchanged skill damage +20");
assertEqual(tier17SkillChance.addSkillAtkMult, 2097179, "tier 17 staff extra skill multiplier +20");
assertEqual(tier17NormalCrit.basicCritDmg, 803447, "tier 17 spear normal crit damage +20");

const tier18Drops = normalDropsForTier(18);
const tier18NormalDamageItem = tier18Drops.find((item) => getEquipGroup(item) === "normal_dmg");
const tier18NormalDamageAt20 = calcItemStats({ ...tier18NormalDamageItem, level: 20 });
assertEqual(tier18NormalDamageItem.name, "★연옥★ 군신의 가호가 담긴 보석", "tier 18 normal damage item name");
assertEqual(tier18NormalDamageAt20.attack, 8510000, "tier 18 normal damage item attack +20");
assertEqual(tier18NormalDamageAt20.skillDmgInc, 0, "tier 18 normal damage item unchanged skill damage +20");
assertEqual(tier18NormalDamageAt20.basicAtkDmgInc, 7506, "tier 18 normal damage +20");

const avatarTargets = {
  "무기 아바타": { basicCritDmgAmp: 33.0 },
  "오라 아바타": { addSkillAtkMultAmp: 33.0 },
  "클론 레어 아바타": { skillCritChance: 10.0, skillCritDmg: 150.0 },
};
const avatarItems = specialBossList
  .flatMap((boss) => boss.drops || [])
  .filter((item) => Object.prototype.hasOwnProperty.call(avatarTargets, item.name));
assertEqual(avatarItems.length, 3, "base avatar equipment count");
for (const item of avatarItems) {
  assert(isEnhanceableSpecialEquip(item), `${item.name}: must be enhanceable`);
  let previous = calcSpecialEquipStats({ ...item, level: 0 });
  for (let level = 1; level <= 20; level += 1) {
    const current = calcSpecialEquipStats({ ...item, level });
    assert(current.attack >= previous.attack, `${item.name}: attack decreased at +${level}`);
    for (const key of Object.keys(avatarTargets[item.name])) {
      assert(current[key] >= previous[key], `${item.name}: ${key} decreased at +${level}`);
    }
    previous = current;
  }
  const at20 = calcSpecialEquipStats({ ...item, level: 20 });
  assertEqual(at20.attack, 882000, `${item.name}: attack +20`);
  for (const [key, value] of Object.entries(avatarTargets[item.name])) {
    assertEqual(at20[key], value, `${item.name}: ${key} +20`);
  }
}

context.player = {
  farmAtkBonus: 0,
  addAttackSpeed: 150,
  basicAtkDmgInc: 0,
  skillDmgInc: 0,
  allDmgInc: 0,
  addSkillAtkChance: 0,
  addSkillAtkMult: 1000,
  basicCritChance: 0,
  basicCritDmg: 200,
  skillCritChance: 0,
  skillCritDmg: 0,
  equipment: new Array(15).fill(null),
};
context.activeBuffs = {};
for (const item of avatarItems) {
  context.player.equipment[item.specialSlotIdx] = { ...item, level: 20 };
}
vm.runInContext("globalThis.__avatarTotals = getTotals();", context);
assertEqual(context.__avatarTotals.basicCritDmg, 266, "weapon avatar final normal crit damage amplification");
assertEqual(context.__avatarTotals.addSkillAtkMult, 1330, "aura avatar final extra skill coefficient amplification");
assertEqual(context.__avatarTotals.skillCritChance, 10, "clone rare avatar final skill crit chance");
assertEqual(context.__avatarTotals.skillCritDmg, 150, "clone rare avatar final skill crit damage");

const futureTier40Item = {
  name: "합성 40단계 스킬 피해 장비",
  type: "normal",
  tier: 40,
  equipGroup: "skill_all",
  baseAtk: 1,
  baseSdmg: 400,
  baseAllDmg: 200,
};
const futureTier40At0 = calcItemStats({ ...futureTier40Item, level: 0 });
const futureTier40At20 = calcItemStats({ ...futureTier40Item, level: 20 });
assertEqual(futureTier40At0.skillDmgInc, 400, "future tier 40: skill damage +0");
assertEqual(futureTier40At0.allDmgInc, 200, "future tier 40: all damage +0");
assertEqual(futureTier40At20.skillDmgInc, expectedHighTierSkillDamage(40, 20), "future tier 40: skill damage +20");
assertEqual(expectedHighTierSkillDamage(40, 20), 3860579.8, "future tier 40 projection");

const itemTemplates = JSON.parse(read("backend/seeds/generated/item_templates.json"));
const dropTableItems = JSON.parse(read("backend/seeds/generated/drop_table_items.json"));

for (let tier = 1; tier <= 39; tier += 1) {
  const expectedBaseSkill = 10 * tier;
  const expectedBaseAllDamage = 5 * tier;
  const sourceItems = normalDropsForTier(tier).filter((item) => getEquipGroup(item) === "skill_all");
  assertEqual(sourceItems.length, 1, `tier ${tier}: source skill_all item count`);
  assertEqual(sourceItems[0].baseSdmg, expectedBaseSkill, `tier ${tier}: source baseSdmg`);
  assertEqual(sourceItems[0].baseAllDmg, expectedBaseAllDamage, `tier ${tier}: source baseAllDmg`);

  const templates = itemTemplates.filter(
    (item) => item.type === "normal" && item.tier === tier && item.equipGroup === "skill_all",
  );
  assertEqual(templates.length, 1, `tier ${tier}: generated skill_all template count`);
  assertEqual(templates[0].baseStats.baseSdmg, expectedBaseSkill, `tier ${tier}: template baseStats.baseSdmg`);
  assertEqual(templates[0].raw.baseSdmg, expectedBaseSkill, `tier ${tier}: template raw.baseSdmg`);
  assertEqual(templates[0].baseStats.baseAllDmg, expectedBaseAllDamage, `tier ${tier}: template baseStats.baseAllDmg`);
  assertEqual(templates[0].raw.baseAllDmg, expectedBaseAllDamage, `tier ${tier}: template raw.baseAllDmg`);

  const dropRows = dropTableItems.filter(
    (item) => item.bossId === tier && item.itemType === "normal" && item.raw.equipGroup === "skill_all",
  );
  assertEqual(dropRows.length, 1, `tier ${tier}: generated skill_all drop count`);
  assertEqual(dropRows[0].raw.baseSdmg, expectedBaseSkill, `tier ${tier}: drop raw.baseSdmg`);
  assertEqual(dropRows[0].raw.baseAllDmg, expectedBaseAllDamage, `tier ${tier}: drop raw.baseAllDmg`);
}

console.log(JSON.stringify({
  ok: true,
  result: "avatar-enhancement-item-qol-field-gain-halved-cache-refresh-ready-static-deploy-gate-preparation-required",
  auditedEquipment: 60,
  auditedSpecialEquipment: 5,
  auditedAvatarEquipment: avatarItems.length,
  highTierSkillEquipment: 28,
  seedSkillEquipment: 39,
  highTierNonTargetDigest,
  tier12: { attackRaw: 691000, attackDisplayB: 69.1, skillDamage: 607, allDamage: 173.9 },
  tier13SkillDamage20: 829.9,
  tier14SkillDamage20: 1134.7,
  tier15SkillDamage20: 1551.3,
  tier16: { attackRaw: 3690000, attackDisplayB: 369, skillDamage: 2121, allDamage: 225.8 },
  tier17: { skillDamage: 2899.9, extraSkillMultiplier: 2097179, normalCritDamage: 803447 },
  tier18: { attackRaw: 8510000, attackDisplayB: 851, skillDamage: 3964.8, normalDamage: 7506 },
  tier39SkillDamage20: 2823673.9,
  futureTier40SkillDamage20: 3860579.8,
}));

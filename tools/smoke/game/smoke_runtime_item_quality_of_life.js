const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..", "..", "..");

function read(file) {
  return fs.readFileSync(path.join(root, file), "utf8");
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function assertContains(file, patterns) {
  const text = read(file);
  for (const pattern of patterns) {
    assert(text.includes(pattern), `${file}: missing pattern ${pattern}`);
  }
}

assertContains("src/systems/item-system.js", [
  'requestUiRefresh(result, "refreshActionPanelStats")',
  'requestUiRefresh(result, "consumedSkillBook"',
  "function getSpecialResetRefundCount(level)",
  "function actionDismantleSpecialToZero()",
  "function closeSpecialResetModal()",
  "function confirmSpecialReset()",
  "function applySpecialResetToZero(item, level, refundCount)",
  "선택한 장비가 달라져 강화 초기화를 취소했습니다.",
]);
assertContains("src/ui/render-ui.js", [
  "function showConsumedSkillBookPanel(item)",
  "function getSpecialEquipCategoryPresentation(item)",
  'label: `[${avatarCategory}]`',
  'color: "#6eb4ff"',
  "ui.apPanel.classList.add(\"is-stack-special-action\")",
  "btn.style.display = \"none\"",
  "강화 초기화",
  "+0 ${refundCount}개로 복원",
]);
assertContains("index.html", [
  'id="btn-ap-dismantle-zero"',
  'onclick="actionDismantleSpecialToZero()"',
  'id="special-reset-modal"',
  'onclick="confirmSpecialReset()"',
  'onclick="closeSpecialResetModal()"',
]);
assertContains("src/styles/style.css", [
  "#item-action-panel.is-stack-special-action .action-btns",
  ".special-reset-summary",
  ".special-reset-confirm",
]);
assertContains("src/systems/combat-system.js", [
  "gain *= 0.5;",
  "const isSkillCrit = Math.random() <= t.skillCritChance / 100;",
]);

const logs = [];
const context = {
  console,
  Date,
  Math,
  player: {
    inventory: [],
    storage: [],
    trash: [],
    equipment: new Array(15).fill(null),
    maxInventorySize: 60,
    maxStorageSize: 60,
  },
  selectedSlot: { type: "inv", index: 0 },
  addLog: (message) => logs.push(message),
  updateFullUI: () => {},
  refreshActionPanelStats: () => {},
};
vm.createContext(context);
vm.runInContext(read("src/systems/item-system.js"), context, { filename: "src/systems/item-system.js" });

const refundCounts = vm.runInContext(
  "[1, 2, 3, 4, 5, 6].map((level) => getSpecialResetRefundCount(level))",
  context
);
assert(
  JSON.stringify(Array.from(refundCounts)) === JSON.stringify([2, 4, 8, 16, 32, 64]),
  "reset refund must reconstruct all +0 source items with 2^level"
);

const enhancedStack = {
  name: "찬란한 힘의 탈리스만",
  type: "special_equip",
  isTalisman: true,
  specialSlotIdx: 12,
  level: 3,
  count: 2,
};
const zeroStack = {
  name: "찬란한 힘의 탈리스만",
  type: "special_equip",
  isTalisman: true,
  specialSlotIdx: 12,
  level: 0,
  count: 4,
};
context.player.inventory = [enhancedStack, zeroStack];
context.selectedSlot = { type: "inv", index: 0 };
vm.runInContext("applySpecialResetToZero(player.inventory[0], 3, getSpecialResetRefundCount(3))", context);
assert(enhancedStack.count === 1, "resetting one enhanced stack item must leave the other enhanced item");
assert(zeroStack.count === 12, "+3 reset must merge eight reconstructed +0 items into the existing stack");
assert(context.selectedSlot.index === 1, "selection must move to the resulting +0 stack");

const equippedEmblem = {
  name: "빛나는 휘장",
  type: "special_equip",
  isEmblem: true,
  specialSlotIdx: 14,
  level: 6,
  count: 1,
};
const zeroEmblem = {
  name: "빛나는 휘장",
  type: "special_equip",
  isEmblem: true,
  specialSlotIdx: 14,
  level: 0,
  count: 2,
};
context.player.inventory = [zeroEmblem];
context.player.equipment[14] = equippedEmblem;
context.selectedSlot = { type: "equip", index: 14 };
vm.runInContext("applySpecialResetToZero(player.equipment[14], 6, getSpecialResetRefundCount(6))", context);
assert(context.player.equipment[14] === null, "equipped emblem must be removed after reset");
assert(zeroEmblem.count === 66, "+6 reset must merge sixty-four reconstructed +0 items");
assert(context.selectedSlot.type === "inv" && context.selectedSlot.index === 0, "resulting +0 emblem must remain selected");
assert(logs.some((message) => message.includes("+0 64개로 되돌렸습니다")), "reset log must report the reconstructed count");

const zoneContext = { Math };
vm.createContext(zoneContext);
vm.runInContext(`${read("src/data/zones.js")};this.__zones = customZones;`, zoneContext, {
  filename: "src/data/zones.js",
});
const sourceZones = Array.from(zoneContext.__zones);
const generatedZones = JSON.parse(read("backend/seeds/generated/field_zones.json"));
assert(sourceZones.length === 40 && generatedZones.length === 40, "both field datasets must contain all 40 zones");

let farmZoneCount = 0;
for (let index = 0; index < sourceZones.length; index += 1) {
  const sourceFarm = sourceZones[index].farm || null;
  const generatedFarm = generatedZones[index].farm || null;
  assert(
    JSON.stringify(sourceFarm) === JSON.stringify(generatedFarm),
    `field ${index + 1} farm rule differs between static and generated data`
  );
  if (sourceFarm) farmZoneCount += 1;
}
assert(farmZoneCount === 33, "fields 8 through 40 must all have a pure-attack reward rule");

const combatSource = read("src/systems/combat-system.js");
assert(
  /if \(f\.specialThreshold[\s\S]*?gain \*= 1 \+[\s\S]*?gain = Math\.floor\(gain\);[\s\S]*?gain \*= 0\.5;[\s\S]*?player\.farmAtkBonus \+= gain;/.test(combatSource),
  "every zoneData.farm reward must pass threshold, bonus, floor, and common 50% reduction before being granted"
);
assertContains("src/api/master-data-adapter.js", [
  "farm: farmRules && Object.keys(farmRules).length ? cloneJson(farmRules) : null",
]);

console.log(
  `runtime item quality-of-life smoke test passed (reset refunds 2^level; field rewards halved for all ${farmZoneCount} farm-enabled fields)`
);

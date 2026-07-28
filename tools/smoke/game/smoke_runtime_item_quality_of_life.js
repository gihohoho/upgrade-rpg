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
  "function actionDismantleSpecialToZero()",
  "강화에 사용한 재료는 환급되지 않습니다.",
]);
assertContains("src/ui/render-ui.js", [
  "function showConsumedSkillBookPanel(item)",
  'btnDismantleZero.innerText = "+0으로 분해"',
]);
assertContains("index.html", [
  'id="btn-ap-dismantle-zero"',
  'onclick="actionDismantleSpecialToZero()"',
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
  window: { confirm: () => true },
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
vm.runInContext("actionDismantleSpecialToZero()", context);
assert(enhancedStack.count === 1, "dismantling one enhanced stack item must leave the other enhanced item");
assert(zeroStack.count === 5, "dismantled item must merge into the existing +0 stack");
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
vm.runInContext("actionDismantleSpecialToZero()", context);
assert(context.player.equipment[14] === null, "equipped emblem must be removed after dismantling");
assert(zeroEmblem.count === 3, "equipped emblem must merge into the inventory +0 stack");
assert(context.selectedSlot.type === "inv" && context.selectedSlot.index === 0, "resulting +0 emblem must remain selected");
assert(logs.some((message) => message.includes("강화 재료 환급 없음")), "dismantle result log must explain no material refund");

console.log("runtime item quality-of-life smoke test passed");

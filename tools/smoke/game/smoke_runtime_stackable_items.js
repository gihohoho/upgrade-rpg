const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..", "..", "..");

function read(file) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  return fs.readFileSync(fullPath, "utf8");
}

function assertContains(file, patterns) {
  const text = read(file);
  for (const pattern of patterns) {
    if (!text.includes(pattern)) throw new Error(`${file}: missing pattern ${pattern}`);
  }
}

assertContains("src/api/master-data-adapter.js", [
  "applyTemplateRuntimeFields",
  "drop.stackable = !!(template && template.stackable)",
  "drop.templateKey",
  "stackable: !!item.stackable",
]);

assertContains("src/systems/combat-system.js", [
  "addStackableItemToInventory(newItem)",
  "dropType: \"equipment\"",
  "현재 겹침",
]);

assertContains("src/systems/item-system.js", [
  "isTemplateStackableItem",
  "isTruthyStackableFlag",
  "isSameStackableItem",
  "splitGenericStackableForEnhanceIfNeeded",
  "기존 세이브 아이템에는 stackable/templateKey가 없을 수 있으므로",
]);

assertContains("src/ui/render-ui.js", [
  "let countText = !equipped && item.count && item.count > 1 ? ` x${item.count}`",
]);

const context = {
  console,
  Date,
  Math,
  player: {
    inventory: [],
    storage: [],
    trash: [],
    equipment: [],
    maxInventorySize: 3,
    maxStorageSize: 3,
  },
};
const initialPlayer = context.player;
context.window = context;
vm.createContext(context);
vm.runInContext(read("src/state/game-state.js"), context);
context.player = initialPlayer;
vm.runInContext(read("src/systems/item-system.js"), context);

const stackableItem = {
  name: "샤이닝 인텔리전스",
  type: "normal",
  level: 0,
  count: 1,
  stackable: true,
  templateKey: "shining-intelligence",
  equipGroup: "skill_all",
  tier: 1,
};

let first = context.addStackableItemToInventory(stackableItem);
let second = context.addStackableItemToInventory({ ...stackableItem, id: 2 });
if (!first.ok || !second.ok || !second.stacked) throw new Error("stackable DB item did not stack on second add");
if (context.player.inventory.length !== 1) throw new Error(`expected one inventory slot, got ${context.player.inventory.length}`);
if (context.player.inventory[0].count !== 2) throw new Error(`expected count 2, got ${context.player.inventory[0].count}`);

context.player.inventory = [{ name: "샤이닝 인텔리전스", type: "normal", level: 0, count: 1, equipGroup: "skill_all", tier: 1 }];
let third = context.addStackableItemToInventory({ ...stackableItem, id: 3 });
if (!third.ok || !third.stacked) throw new Error("new stackable DB item did not merge into legacy saved item");
if (context.player.inventory[0].count !== 2) throw new Error("legacy saved item was not counted after merge");
if (context.player.inventory[0].stackable !== true) throw new Error("legacy saved item did not inherit stackable=true after merge");

context.player.inventory = [];
const nonStackable = { name: "시간 여행자의 은시계", type: "normal", level: 0, count: 1, stackable: false, equipGroup: "atk_inc", tier: 1 };
context.addStackableItemToInventory(nonStackable);
context.addStackableItemToInventory({ ...nonStackable, id: 4 });
if (context.player.inventory.length !== 2) throw new Error("non-stackable equipment should still occupy separate slots");

console.log("runtime stackable items smoke test passed");

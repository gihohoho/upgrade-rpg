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

assertContains("src/systems/item-system.js", [
  "getStackedEnhanceSpaceBlockReason",
  "getStackedEnhanceSpaceMessage",
  "getStackedEnhanceSpaceBlockReason(currentItem, sourceArr, sourceMaxSize)",
  "stoppedReason = splitBlockReason === \"space_required\" ? \"분리 공간 부족\" : \"분리 실패\"",
  "겹쳐진 장비를 강화하려면 먼저 1칸의 빈 공간이 필요합니다.",
]);

assertContains("docs/archive/history/GAME_UI_RUNTIME_HISTORY.md", [
  "탈리스만",
  "빛나는 휘장",
  "DB reset/seed 불필요",
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
  selectedSlot: { type: "inv", index: 0 },
};
const initialPlayer = context.player;
const initialSelectedSlot = context.selectedSlot;
context.window = context;
vm.createContext(context);
vm.runInContext(read("src/state/game-state.js"), context);
context.player = initialPlayer;
context.selectedSlot = initialSelectedSlot;
vm.runInContext(read("src/systems/item-system.js"), context);

const stacked = { name: "찬란한 힘의 탈리스만", type: "special_equip", level: 0, count: 2 };
const fullInventory = [stacked, { name: "dummy 1" }, { name: "dummy 2" }];
const roomyInventory = [stacked, { name: "dummy 1" }];

if (context.getStackedEnhanceSpaceBlockReason(stacked, fullInventory, 3) !== "space_required") {
  throw new Error("stacked item in full container should require empty split space");
}

if (context.getStackedEnhanceSpaceBlockReason(stacked, roomyInventory, 3) !== "") {
  throw new Error("stacked item with free space should not be blocked");
}

if (context.getStackedEnhanceSpaceBlockReason({ ...stacked, count: 1 }, fullInventory, 3) !== "") {
  throw new Error("single-count item should not require split space");
}

console.log("runtime stacked enhance space guard smoke test passed");

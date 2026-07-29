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
  "function compactPlayerItemContainer(type)",
  "clearItemSlot(sourceArr, selectedSlot.index)",
  "placeItemInFirstEmptySlot(targetArr, moved, targetMaxSize)",
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
  "처치 시 ${rewardProbability * 100}% 확률",
  "성공: +${field.farm.gain} (표시 상승량 100% 적용)",
  "실패: 상승 없음",
]);
assertContains("index.html", [
  'id="btn-ap-dismantle-zero"',
  'onclick="actionDismantleSpecialToZero()"',
  'id="special-reset-modal"',
  'onclick="confirmSpecialReset()"',
  'onclick="closeSpecialResetModal()"',
  "compactPlayerItemContainer('inv')",
  "compactPlayerItemContainer('storage')",
  "compactPlayerItemContainer('trash')",
  "↑ 위로 정렬",
  "몬스터 처치 시 50% 확률",
  "표시된 상승량을 100% 적용",
]);
assertContains("src/styles/style.css", [
  "#item-action-panel.is-stack-special-action .action-btns",
  ".special-reset-summary",
  ".special-reset-confirm",
  ".field-reward-policy",
  ".field-reward-summary",
  ".item-frame-basic",
  ".item-frame-transcendent",
  ".item-frame-liberated",
  ".item-frame-radiant",
  ".item-frame-dark",
  ".item-frame-luminous",
  ".inventory-compact-btn",
]);
assertContains("src/systems/combat-system.js", [
  "const isSkillCrit = Math.random() <= t.skillCritChance / 100;",
]);
assert(!read("src/systems/combat-system.js").includes("gain *= 0.5;"), "field reward amount must not be halved");

const logs = [];
const initialPlayer = {
  inventory: [],
  storage: [],
  trash: [],
  equipment: new Array(15).fill(null),
  maxInventorySize: 60,
  maxStorageSize: 60,
};
const initialSelectedSlot = { type: "inv", index: 0 };
const context = {
  console,
  Date,
  Math,
  player: initialPlayer,
  selectedSlot: initialSelectedSlot,
  addLog: (message) => logs.push(message),
  updateFullUI: () => {},
  refreshActionPanelStats: () => {},
  closeActionPanel: () => {},
  currentZoneType: "town",
};
context.window = context;
vm.createContext(context);
vm.runInContext(read("src/state/game-state.js"), context, { filename: "src/state/game-state.js" });
context.player = initialPlayer;
context.selectedSlot = initialSelectedSlot;
context.currentZoneType = "town";
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

const invFirst = { name: "첫 번째 아이템", type: "normal", level: 0 };
const invMiddle = { name: "가운데 아이템", type: "normal", level: 0 };
const invLast = { name: "마지막 아이템", type: "normal", level: 0 };
context.player.inventory = [invFirst, invMiddle, invLast];
context.player.storage = [];
context.player.trash = [];
context.selectedSlot = { type: "inv", index: 1 };
vm.runInContext("actionMoveStorage()", context);
assert(context.player.inventory[0] === invFirst, "moving a middle inventory item must preserve the first slot");
assert(context.player.inventory[1] === null, "moving a middle inventory item must leave its original slot empty");
assert(context.player.inventory[2] === invLast, "moving a middle inventory item must not pull the next item forward");
assert(context.player.storage[0] === invMiddle, "moved inventory item must use the first empty storage slot");

vm.runInContext("compactPlayerItemContainer('inv')", context);
assert(context.player.inventory.length === 2, "manual inventory compact must remove empty positions");
assert(context.player.inventory[0] === invFirst && context.player.inventory[1] === invLast, "manual inventory compact must preserve relative item order");

const storageFirst = { name: "보관함 첫 번째", type: "normal", level: 0 };
const storageMiddle = { name: "보관함 가운데", type: "normal", level: 0 };
const storageLast = { name: "보관함 마지막", type: "normal", level: 0 };
context.player.storage = [storageFirst, storageMiddle, storageLast];
context.selectedSlot = { type: "storage", index: 1 };
vm.runInContext("actionMoveStorage()", context);
assert(context.player.storage[1] === null && context.player.storage[2] === storageLast, "storage removal must preserve its empty middle slot");

context.player.inventory = [invFirst, invMiddle, invLast];
context.player.trash = [{ name: "휴지통 첫 번째", type: "normal", level: 0 }];
context.selectedSlot = { type: "inv", index: 1 };
vm.runInContext("actionSell()", context);
assert(context.player.inventory[1] === null && context.player.inventory[2] === invLast, "moving to trash must preserve the inventory hole");
assert(context.player.trash[1] === invMiddle, "trash must receive the item in its first empty slot");
vm.runInContext("compactPlayerItemContainer('trash')", context);
assert(context.player.trash[0].name === "휴지통 첫 번째" && context.player.trash[1] === invMiddle, "trash compact must preserve relative item order");

const zoneContext = { Math };
vm.createContext(zoneContext);
vm.runInContext(`${read("src/data/zones.js")};this.__zones = customZones;`, zoneContext, {
  filename: "src/data/zones.js",
});
const sourceZones = Array.from(zoneContext.__zones);
assert(
  vm.runInContext("getFieldFarmRewardProbability({ prob: 1 })", zoneContext) === 0.5,
  "runtime must enforce 50% even when previously stored master-data still says 100%"
);
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
  if (sourceFarm) {
    farmZoneCount += 1;
    assert(sourceFarm.prob === 0.5, `field ${index + 1} pure-attack reward probability must be 50%`);
  }
}
assert(farmZoneCount === 33, "fields 8 through 40 must all have a pure-attack reward rule");

const combatSource = read("src/systems/combat-system.js");
assert(
  combatSource.includes('getFieldFarmRewardProbability(f)'),
  "combat must use the common 50% field reward probability"
);
assert(
  /if \(f\.specialThreshold[\s\S]*?gain \*= 1 \+[\s\S]*?gain = Math\.floor\(gain\);[\s\S]*?player\.farmAtkBonus \+= gain;/.test(combatSource),
  "every successful zoneData.farm reward must grant the full calculated amount after threshold, bonus, and floor"
);
assertContains("src/api/master-data-adapter.js", [
  "farm: farmRules && Object.keys(farmRules).length ? cloneJson(farmRules) : null",
]);

const iconContext = {};
vm.createContext(iconContext);
vm.runInContext(read("src/utils/icon-utils.js"), iconContext, { filename: "src/utils/icon-utils.js" });
const iconCases = [
  [{ name: "심연의 편린 스태프", specialSlotIdx: 6 }, "weapon-basic.png"],
  [{ name: "-초월- 심연의 편린 스태프", specialSlotIdx: 6 }, "weapon-transcendent.png"],
  [{ name: "-해방- 심연의 편린 목걸이", specialSlotIdx: 7 }, "necklace-liberated.png"],
  [{ name: "짙은 심연의 편린 반지", specialSlotIdx: 8 }, "ring-dark.png"],
  [{ name: "무기 아바타", specialSlotIdx: 9 }, "weapon-avatar-basic.png"],
  [{ name: "찬란한 오라 아바타", specialSlotIdx: 10 }, "aura-avatar-radiant.png"],
  [{ name: "찬란한 클론 레어 아바타", specialSlotIdx: 11 }, "clone-rare-avatar-radiant.png"],
  [{ name: "탈리스만 +0", isTalisman: true }, "talisman-basic.png"],
  [{ name: "-초월- 탈리스만 +0", isTalisman: true }, "talisman-transcendent.png"],
  [{ name: "찬란한 탈리스만 +0", isTalisman: true }, "talisman-radiant.png"],
  [{ name: "영롱한 탈리스만 +0", isTalisman: true }, "talisman-luminous.png"],
  [{ name: "빛나는 휘장 +0", isEmblem: true }, "emblem.png"],
];
for (const [item, expectedFile] of iconCases) {
  const actual = vm.runInContext(`getSpecialEquipIconUrl(${JSON.stringify(item)})`, iconContext);
  assert(actual.endsWith(`/${expectedFile}?v=361`), `${item.name}: expected ${expectedFile}?v=361, got ${actual}`);
}
const frameCases = [
  [{ name: "심연의 편린 반지" }, "basic"],
  [{ name: "-초월- 심연의 편린 반지" }, "transcendent"],
  [{ name: "-해방- 심연의 편린 반지" }, "liberated"],
  [{ name: "찬란한 오라 아바타" }, "radiant"],
  [{ name: "짙은 심연의 편린 반지" }, "dark"],
  [{ name: "영롱한 탈리스만" }, "luminous"],
];
for (const [item, expectedGrade] of frameCases) {
  const actual = vm.runInContext(`getItemFrameGrade(${JSON.stringify(item)})`, iconContext);
  assert(actual === expectedGrade, `${item.name}: expected frame ${expectedGrade}, got ${actual}`);
}

const assetDir = path.join(root, "src", "assets", "special-equipment");
const expectedAssets = [
  ...["weapon", "necklace", "ring"].flatMap((type) =>
    ["basic", "transcendent", "liberated", "dark"].map((tier) => `${type}-${tier}.png`)
  ),
  ...["weapon-avatar", "aura-avatar", "clone-rare-avatar"].flatMap((type) =>
    ["basic", "radiant"].map((tier) => `${type}-${tier}.png`)
  ),
  ...["basic", "transcendent", "radiant", "luminous"].map((tier) => `talisman-${tier}.png`),
  "emblem.png",
].flat();
assert(expectedAssets.length === 23, "special-equipment asset inventory must contain 23 icons");
for (const file of expectedAssets) {
  const buffer = fs.readFileSync(path.join(assetDir, file));
  assert(buffer.toString("ascii", 1, 4) === "PNG", `${file}: expected PNG signature`);
  assert(buffer.readUInt32BE(16) === 256 && buffer.readUInt32BE(20) === 256, `${file}: expected 256x256 dimensions`);
}
assertContains("src/rules/boss-display-rules.js", [
  'if (drop.type === "special_equip")',
  "drop.img = getSpecialEquipIconUrl(drop);",
]);
assertContains("AGENTS.md", [
  "이미지 파일 자체에는 테두리, 프레임, 카드판, inset panel, margin band",
  "기본 등급은 효과 없는 흰색 테두리",
  "등급별 CSS 테두리",
  "여백 없이 채우며",
  "일부가 잘리는 close-up 구도",
  "던전앤파이터풍",
  "실제 브라우저 슬롯 크기",
]);

console.log(
  `runtime item quality-of-life smoke test passed (stable inventory/storage/trash slots; manual compact; grade frames; reset refunds 2^level; ${farmZoneCount} field rewards use 50% chance/full gain; ${expectedAssets.length} generated icons mapped)`
);

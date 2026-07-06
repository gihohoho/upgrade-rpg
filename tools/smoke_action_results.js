const fs = require('fs');
const vm = require('vm');
const path = require('path');
const root = path.resolve(__dirname, '..');
function makeEl(id) {
  return {
    id,
    style: {},
    classList: { add(){}, remove(){}, toggle(){} },
    appendChild(){}, remove(){},
    setAttribute(){},
    addEventListener(){},
    querySelector(){ return makeEl(id + '-q'); },
    querySelectorAll(){ return []; },
    getBoundingClientRect(){ return { left: 100, top: 100, width: 100, height: 100 }; },
    innerHTML: '', innerText: '', textContent: '', value: '', disabled: false,
  };
}
const context = {
  console,
  setTimeout(fn){ return 0; },
  clearTimeout(){},
  setInterval(){ return 1; },
  clearInterval(){},
  Math,
  Date,
  localStorage: { getItem(){return null;}, setItem(){}, removeItem(){} },
  document: {
    getElementById(id){ return makeEl(id); },
    createElement(tag){ return makeEl(tag); },
    querySelector(){ return makeEl('query'); },
    querySelectorAll(){ return []; },
    addEventListener(){},
  },
};
context.window = context;
vm.createContext(context);
const files = [
  'src/state/game-state.js',
  'src/utils/icon-utils.js',
  'src/data/skills.js',
  'src/data/boss-factories.js',
  'src/data/bosses.js',
  'src/rules/abyss-fragment-rules.js',
  'src/rules/boss-display-rules.js',
  'src/rules/boss-drop-rules.js',
  'src/data/boss-bootstrap.js',
  'src/data/zones.js',
  'src/systems/stat-system.js',
  'src/ui/render-ui.js',
  'src/systems/action-result-system.js',
  'src/systems/item-system.js',
  'src/systems/combat-system.js',
];
for (const file of files) {
  const code = fs.readFileSync(path.join(root, file), 'utf8');
  vm.runInContext(code, context, { filename: file });
}
const noop = () => {};
['closeActionPanel','renderSkills','updateFullUI','updateCombatUI','updateGoldUI','renderUI','refreshActionPanelStats','startAutoAttack','toggleBossPanel','toggleSpecialBossPanel','closeAllGameplayModals'].forEach((name) => { context[name] = noop; });
context.addLog = function(message, important) { context.__logs = context.__logs || []; context.__logs.push({ message, important }); };
context.player.inventory = [];
context.player.equipment = new Array(15).fill(null);
context.player.maxInventorySize = 100;
context.currentZoneType = 'town';
context.selectedSlot = { type: 'inv', index: 0 };
context.player.inventory.push({ name: '테스트 스킬피해 장비', type: 'normal', equipGroup: 'skill_all', equipLimit: 1, level: 0 });
let equipResult = context.actionEquipDirect(0);
if (!equipResult || equipResult.type !== 'item.equip' || !equipResult.ok) throw new Error('equip result failed');
context.selectedSlot = { type: 'equip', index: 0 };
let unequipResult = context.actionUnequipDirect(0);
if (!unequipResult || unequipResult.type !== 'item.unequip' || !unequipResult.ok) throw new Error('unequip result failed');
context.player.inventory = [{ name: '스킬강화권', type: 'skill_book', count: 1 }];
context.selectedSlot = { type: 'inv', index: 0 };
let skillResult = context.actionEquipDirect(0);
if (!skillResult || skillResult.type !== 'skill_book.use' || !skillResult.ok || skillResult.data.afterLevel < 2) throw new Error('skill book result failed');
context.currentZoneType = 'boss_empty';
context.currentBoss = null;
let summonResult = vm.runInContext("summonBoss(bossList[0])", context);
if (!summonResult || summonResult.type !== 'boss.summon' || !summonResult.ok || context.currentZoneType !== 'boss_fight') throw new Error('summon result failed');
console.log(JSON.stringify({ ok: true, results: [equipResult.type, unequipResult.type, skillResult.type, summonResult.type] }));

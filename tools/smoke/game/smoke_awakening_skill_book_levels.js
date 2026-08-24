const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..", "..", "..");

function makeElement(id = "") {
	const element = {
		id,
		style: {},
		className: "",
		classList: { add() {}, remove() {}, toggle() {} },
		children: [],
		appendChild(child) {
			this.children.push(child);
			return child;
		},
		remove() {},
		setAttribute() {},
		addEventListener() {},
		querySelector() { return makeElement(`${id}-query`); },
		querySelectorAll() { return []; },
		getBoundingClientRect() { return { left: 0, top: 0, width: 100, height: 100 }; },
		innerText: "",
		textContent: "",
		value: "",
		disabled: false,
	};
	let html = "";
	Object.defineProperty(element, "innerHTML", {
		get() { return html; },
		set(value) {
			html = value;
			if (value === "") this.children = [];
		},
	});
	return element;
}

const elements = new Map();
const skillGrid = makeElement("skill-grid");
const deterministicMath = Object.create(Math);
deterministicMath.random = () => 0;
const context = {
	console,
	Math: deterministicMath,
	Date,
	setTimeout() { return 0; },
	clearTimeout() {},
	setInterval() { return 1; },
	clearInterval() {},
	localStorage: { getItem() { return null; }, setItem() {}, removeItem() {} },
	document: {
		getElementById(id) {
			if (!elements.has(id)) elements.set(id, makeElement(id));
			return elements.get(id);
		},
		createElement(tag) { return makeElement(tag); },
		querySelector(selector) {
			if (selector === ".skill-slots-grid") return skillGrid;
			return makeElement(selector);
		},
		querySelectorAll() { return []; },
		addEventListener() {},
	},
};
context.window = context;
vm.createContext(context);

for (const relative of [
	"src/data/skills.js",
	"src/state/game-state.js",
	"src/systems/action-result-system.js",
	"src/ui/render-ui.js",
	"src/systems/item-system.js",
	"src/systems/combat-system.js",
]) {
	vm.runInContext(fs.readFileSync(path.join(root, relative), "utf8"), context, { filename: relative });
}

const renderSource = fs.readFileSync(path.join(root, "src/ui/render-ui.js"), "utf8");
const generatedSkills = JSON.parse(fs.readFileSync(path.join(root, "backend/seeds/generated/skills.json"), "utf8"));
assert.doesNotMatch(renderSource, /SQ 스킬 레벨 증가/, "talisman A tooltip must not promise an SQ level bonus");
assert.doesNotMatch(renderSource, /SW 스킬 레벨 증가/, "talisman B tooltip must not promise an SW level bonus");
assert.equal(vm.runInContext("skillMasterData.lightsabre.awakening.bonusGroup", context), null, "SQ source metadata must not inherit talisman A");
assert.equal(vm.runInContext("skillMasterData.ironStrike.awakening.bonusGroup", context), null, "SW source metadata must not inherit talisman B");
assert.equal(generatedSkills.find((skill) => skill.id === "lightsabre").awakening.bonusGroup, null, "SQ generated seed must match source");
assert.equal(generatedSkills.find((skill) => skill.id === "ironStrike").awakening.bonusGroup, null, "SW generated seed must match source");

const noop = () => {};
for (const name of [
	"addLog",
	"closeActionPanel",
	"formatNumber",
	"refreshActionPanelStats",
	"showConsumedSkillBookPanel",
	"showDamageText",
	"startAutoAttack",
	"updateCombatUI",
	"updateFullUI",
]) {
	context[name] = name === "formatNumber" ? (value) => String(value) : noop;
}

context.normalizePlayerCharacterState(context.player);
const skills = context.getCurrentCharacterSkills(context.player);
context.player.skills = skills;
context.player.equipment = new Array(15).fill(null);
context.player.equipment[12] = { name: "A 탈리스만", type: "special_equip", isTalisman: true, level: 2 };
context.player.equipment[13] = { name: "B 탈리스만", type: "special_equip", isTalisman: true, level: 3 };
skills.lightsabre = { level: 3, isUpgraded: false };
skills.ironStrike = { level: 4, isUpgraded: false };
skills.baldo = { level: 1 };
skills.deepSword = { level: 1 };

function useBook(name) {
	context.player.inventory = [{ name, type: "skill_book", count: 1 }];
	return context.actionEquipDirect(0);
}

const sqFirst = useBook("심연의 스킬강화권");
assert.equal(sqFirst.ok, true, "SQ first awakening book should succeed");
assert.equal(sqFirst.data.beforeLevel, 3, "SQ should report its previous Q level");
assert.equal(sqFirst.data.afterLevel, 1, "SQ first awakening book should start at level 1");
assert.equal(skills.lightsabre.level, 1, "SQ stored level should be 1 after first awakening book");
assert.equal(skills.lightsabre.isUpgraded, true, "SQ should be awakened after its first book");

const swFirst = useBook("-초월- 심연의 스킬강화권");
assert.equal(swFirst.ok, true, "SW first awakening book should succeed");
assert.equal(swFirst.data.beforeLevel, 4, "SW should report its previous W level");
assert.equal(swFirst.data.afterLevel, 1, "SW first awakening book should start at level 1");
assert.equal(skills.ironStrike.level, 1, "SW stored level should be 1 after first awakening book");
assert.equal(skills.ironStrike.isUpgraded, true, "SW should be awakened after its first book");

context.renderSkills();
assert.equal(skillGrid.children.length, 8, "all eight skills should render");
assert.match(skillGrid.children[0].innerHTML, /Lv\.1<\/div>/, "SQ display should stay at level 1 with talisman A equipped");
assert.doesNotMatch(skillGrid.children[0].innerHTML, /Lv\.4<\/div>/, "SQ display must not inherit talisman A levels");
assert.match(skillGrid.children[1].innerHTML, /Lv\.1<\/div>/, "SW display should stay at level 1 with talisman B equipped");
assert.doesNotMatch(skillGrid.children[1].innerHTML, /Lv\.5<\/div>/, "SW display must not inherit talisman B levels");
assert.match(skillGrid.children[3].innerHTML, /Lv\.4<\/div>/, "R should keep talisman A's +3 level bonus");
assert.match(skillGrid.children[5].innerHTML, /Lv\.5<\/div>/, "F should keep talisman B's +4 level bonus");

skills.baldo.level = 0;
skills.deepSword.level = 0;
context.getTotals = () => ({
	attack: 1,
	aspdMs: 1000,
	basicCritChance: 0,
	basicCritDmg: 0,
	basicAtkDmgInc: 0,
	allDmgInc: 0,
	skillCritChance: 0,
	skillCritDmg: 0,
	skillDmgInc: 0,
	skillProcChanceInc: 0,
	addSkillAtkChance: 0,
	addSkillAtkMult: 0,
});
context.currentZoneType = "boss_fight";
context.currentZoneIndex = 0;
context.currentBoss = { id: 999, name: "test boss" };
context.currentBossHp = 10000000000;
const attack = context.playerAttack();
const hitByLabel = Object.fromEntries(attack.data.skillHits.map((hit) => [hit.label, hit.damage]));
assert.equal(hitByLabel["SQ스킬"], 200000, "SQ combat damage should use its own level 1");
assert.equal(hitByLabel["SW스킬"], 320000, "SW combat damage should use its own level 1");

const sqSecond = useBook("심연의 스킬강화권");
const swSecond = useBook("-초월-심연의 스킬강화권");
assert.equal(sqSecond.data.afterLevel, 2, "SQ's own second awakening book should raise it to level 2");
assert.equal(swSecond.data.afterLevel, 2, "SW's own second awakening book should raise it to level 2");

console.log("smoke_awakening_skill_book_levels: PASS");

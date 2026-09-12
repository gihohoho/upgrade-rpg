const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const root = path.resolve(__dirname, "../../..");
const files = ["src/data/skills.js", "src/state/game-state.js", "src/utils/icon-utils.js", "src/data/boss-factories.js", "src/data/bosses.js", "src/rules/abyss-fragment-rules.js", "src/rules/boss-display-rules.js", "src/rules/boss-drop-rules.js", "src/data/boss-bootstrap.js", "src/data/zones.js", "src/systems/stat-system.js", "src/ui/render-ui.js", "src/systems/action-result-system.js", "src/systems/item-system.js", "src/systems/combat-system.js", "src/app/main.js"];
function runtime() {
	let now = 1000000, seed = 12345, timer = 0;
	const pending = new Map(), events = {}, logs = [];
	const context = { console, Math: Object.create(Math), Date: class extends Date { static now() { return now; } },
		document: { hidden: false, getElementById: () => null, querySelector: () => null, querySelectorAll: () => [], addEventListener(name, handler) { (events[name] ||= []).push(handler); } },
		setInterval: () => ++timer, clearInterval() {}, setTimeout(fn) { pending.set(++timer, fn); return timer; }, clearTimeout(id) { pending.delete(id); }, addEventListener() {},
		localStorage: { getItem: () => null, setItem() { throw Error("test must not save"); } }, location: { search: "", hostname: "localhost" }, URLSearchParams,
	};
	context.window = context;
	context.Math.random = () => ((seed = (seed * 16807) % 2147483647) - 1) / 2147483646;
	vm.createContext(context);
	for (const file of files) vm.runInContext(fs.readFileSync(path.join(root, file), "utf8"), context, { filename: file });
	if (process.argv[2]) {
		for (const file of ["src/api/master-data-adapter.js", "src/api/master-data-runtime-switch.js"]) vm.runInContext(fs.readFileSync(path.join(root, file), "utf8"), context, { filename: file });
		const payload = JSON.parse(fs.readFileSync(path.resolve(process.argv[2]), "utf8").replace(/^\uFEFF/, "")).payload;
		context.RpgBackendMasterDataRuntime.applyLegacyMasterData(context.RpgMasterDataAdapter.createLegacyMasterDataFromPayload({ ok: true, payload }), { hydrateStaticAssets: false });
	}
	const evaluate = (code) => vm.runInContext(code, context);
	for (const name of ["updateFullUI", "updateCombatUI", "updateGoldUI", "renderUI", "showDamageText", "showItemDropText", "refreshOnOffButtonVisuals", "closeAllGameplayModals"]) context[name] = () => {};
	context.addLog = (message) => logs.push(message);
	context.player.maxInventorySize = 100;
	context.player.maxStorageSize = 100;
	const totals = context.getTotals();
	context.getTotals = () => ({ ...totals, attack: 1e12, aspdMs: 500, dropInc: 0 });
	function advance(ms, hidden = false, drain = true) {
		now += ms; context.document.hidden = hidden; context.tickGameClock();
		if (drain) { let batches = 0; while (pending.size) { assert(++batches < 10000); const [id, fn] = pending.entries().next().value; pending.delete(id); fn(); } }
	}
	return { c: context, evaluate, advance, logs, events };
}
function snapshot(r) {
	return JSON.parse(r.evaluate(`JSON.stringify({ hp: currentBossHp, fieldHp: currentEnemy.hp, boss: currentBoss && currentBoss.id, zone: currentZoneType, gold: player.gold, records: player.records, items: player.inventory.map(i => i && ({ name: i.name, count: i.count, level: i.level })), buffs: activeBuffs, cooldown: player.specialBossCD, fieldRespawnEndAt })`));
}
for (const mode of ["normal", "field", "special"]) {
	const visible = runtime(), background = runtime();
	for (const r of [visible, background]) {
		r.evaluate(`currentZoneType = "boss_empty"; player.skills.overdrive.level = 2; player.skills.ironStrike.level = 3; player.skills.heavenlyStrike.level = 1;`);
		if (mode === "field") r.evaluate(`currentZoneType = "field"; currentZoneIndex = 0; currentEnemy.hp = zones[0].maxHp; startAutoAttack();`);
		else r.evaluate(`summonBoss(bossList[0]);`);
		if (mode === "special") r.evaluate(`autoSpecialBossEnabled = true; autoSpecialBossId = specialBossList[0].id;`);
	}
	for (let i = 0; i < 1200; i++) visible.advance(100);
	background.advance(120000, true);
	const ownedIds = background.c.player.inventory.filter(Boolean).map(item => String(item.id));
	assert.equal(new Set(ownedIds).size, ownedIds.length, "batched drops must have unique item IDs");
	assert.deepEqual(snapshot(background), snapshot(visible), `${mode}: delayed time must match foreground combat/rewards/buffs/cooldowns`);
	assert(visible.c.player.records.totalBossKills > 0 || visible.c.player.records.totalMonsterKills > 0);
	const before = JSON.stringify(snapshot(background));
	background.advance(0, false);
	assert.equal(JSON.stringify(snapshot(background)), before, "visibility restore must not repeat rewards");
}
const paused = runtime();
paused.evaluate(`currentZoneType = "boss_empty"; summonBoss(bossList[0]);`);
paused.advance(500);
paused.c.stopAutoAttack(); paused.c.stopGameClock();
const stopped = snapshot(paused);
paused.advance(600000, true);
assert.deepEqual(snapshot(paused), stopped, "paused character must not progress");
paused.c.startAutoAttack(); paused.advance(500);
assert.equal(paused.c.player.records.totalBossKills, 2, "resume must not replay paused duration");
const batched = runtime();
batched.evaluate(`currentZoneType = "boss_empty"; summonBoss(bossList[0]);`);
batched.advance(300000, false, false);
assert(batched.evaluate("gameClock.cursor < Date.now()"), "long delays must yield in bounded batches");
let blocked = false;
batched.events.click[0]({ preventDefault() { blocked = true; }, stopImmediatePropagation() {} });
assert(blocked, "input must wait for reconciliation");
batched.advance(0);
assert.equal(batched.c.player.records.totalBossKills, 600);
const ui = runtime();
const bosses = ui.evaluate("[...bossList, ...specialBossList]");
for (const boss of bosses) {
	const html = ui.c.buildBossDropDetailsHtml(boss);
	assert(!html.includes("undefined"));
	for (const drop of boss.drops) assert(html.includes(drop.name), `${boss.name}: drop omitted from grouped view`);
	ui.c.currentBoss = null; ui.c.currentZoneType = "boss_empty"; ui.c.autoBossSummon = false; ui.c.equipDropEnabled = false;
	const result = ui.c.summonBoss(boss);
	assert(result.ok && ui.c.autoBossSummon && ui.c.equipDropEnabled, `${boss.name}: summon defaults`);
	const next = bosses.find(b => b.id !== boss.id);
	assert.equal(ui.c.summonBoss(next).data.reason, "auto_boss_remove_required");
	assert.equal(ui.c.currentBoss.id, boss.id);
	ui.c.autoBossSummon = false; ui.c.equipDropEnabled = false;
	ui.c.summonBoss(boss);
	assert(!ui.c.autoBossSummon && !ui.c.equipDropEnabled, "resuming the same boss must preserve chosen toggles");
}
assert.match(ui.c.buildBossDropDetailsHtml(bosses[0]), /장비 5종 중 1개 · 8.00%/);
const codex = ui.c.getCodexItems();
assert(codex.every(item => item.template), "all codex entries need real stat templates");
const tali = codex.find(item => item.template.isTalisman && item.template.level === 6);
assert(tali && ui.c.getTalismanCategoryInfo(tali.template).statsHtml, "upgraded talisman stats must resolve");
ui.c.player.inventory = [{ id: 123, name: "old" }];
ui.c.player.storage = [{ id: 124, name: "stored" }];
const first = ui.c.addStackableItemToInventory({ id: 123, name: "new-a", type: "normal", stackable: false });
const second = ui.c.addStackableItemToInventory({ id: 123, name: "new-b", type: "normal", stackable: false });
assert.equal(ui.c.player.inventory[0].id, 123);
assert(first.item.id !== 123 && first.item.id !== 124 && first.item.id !== second.item.id, "same timestamp awards must preserve old identity and allocate unique new IDs");
const formula = ui.c.buildSkillDamageFormulaHtml("스킬레벨 x 공격력 x 500", { damageMultiplier: 500 }, 3, { attack: 100, skillDmgInc: 20, allDmgInc: 50 });
assert(formula.includes(ui.c.formatNumber(270000)) && formula.includes("<strong class=\"skill-damage-formula\"") && formula.includes("skill-damage-result"));
console.log("v401 live game fixes passed: foreground/background parity, field respawn, special cooldown, pause/resume, batching/input, 45 boss defaults/drop groups, codex stats, skill damage");

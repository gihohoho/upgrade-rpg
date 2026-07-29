const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..", "..", "..");
const context = { console };
vm.createContext(context);

for (const relative of [
	"src/utils/icon-utils.js",
	"src/data/boss-factories.js",
	"src/data/bosses.js",
]) {
	vm.runInContext(fs.readFileSync(path.join(root, relative), "utf8"), context, { filename: relative });
}

const rows = vm.runInContext(`
	bossList
		.filter((boss) => boss.id >= 1 && boss.id <= 39)
		.flatMap((boss) => boss.drops.filter((drop) => drop.type === "normal"))
		.map((drop) => ({
			tier: drop.tier,
			group: drop.equipGroup,
			name: drop.name,
			img: getNormalEquipmentIconUrl(drop),
			grade: getItemFrameGrade(drop),
		}))
`, context);

const groupAssetKeys = new Map([
	["skill_all", "skill-all"],
	["atk_inc", "atk-inc"],
	["normal_dmg", "normal-dmg"],
	["skill_chance", "skill-chance"],
	["normal_crit", "normal-crit"],
]);

assert.equal(rows.length, 195, "tiers 1-39 must contain 195 normal equipment drops");
assert.equal(new Set(rows.map((row) => row.tier)).size, 39, "all 39 tiers must be covered");
assert.deepEqual(
	[...new Set(rows.map((row) => row.group))].sort(),
	[...groupAssetKeys.keys()].sort(),
	"normal equipment groups differ",
);
assert.equal(new Set(rows.map((row) => row.img)).size, 195, "every normal equipment drop must use a separate icon URL");

for (const row of rows) {
	const assetKey = groupAssetKeys.get(row.group);
	assert(assetKey, `${row.name}: unknown equipment group ${row.group}`);
	const expected = `src/assets/equipment/tier-${String(row.tier).padStart(2, "0")}-${assetKey}.png?v=365`;
	assert.equal(row.img, expected, `${row.name}: tier/group icon mapping differs`);
}

const tier9Rows = rows.filter((row) => row.tier === 9);
assert.equal(tier9Rows.length, 5, "tier 9 must contain five normal equipment drops");
assert(
	tier9Rows.every((row) => row.grade === "transcendent"),
	"tier 9 -transcendent- prefixes must outrank inner words such as sky",
);

const iconDirectory = path.join(root, "src", "assets", "equipment");
const tierIconPattern = /^tier-\d{2}-(?:skill-all|atk-inc|normal-dmg|skill-chance|normal-crit)\.png$/;
const iconFiles = fs.readdirSync(iconDirectory).filter((file) => tierIconPattern.test(file)).sort();
assert.equal(iconFiles.length, 195, "v365 equipment icon batch must contain 195 tier-specific PNG files");

for (const file of iconFiles) {
	const bytes = fs.readFileSync(path.join(iconDirectory, file));
	assert(bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])), `${file}: invalid PNG signature`);
	assert.equal(bytes.readUInt32BE(16), 256, `${file}: width must be 256`);
	assert.equal(bytes.readUInt32BE(20), 256, `${file}: height must be 256`);
}

console.log("equipment icon family smoke passed");
console.log("- covered tiers / items / tier icon files: 1-39 / 195 / 195");
console.log("- mapping: one separate 256x256 PNG per tier and equipment group");
console.log("- cache key: v365");

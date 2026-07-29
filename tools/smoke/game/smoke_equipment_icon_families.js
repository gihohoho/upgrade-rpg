const assert = require("node:assert/strict");
const crypto = require("node:crypto");
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
	const expected = `src/assets/equipment/tier-${String(row.tier).padStart(2, "0")}-${assetKey}.png?v=367`;
	assert.equal(row.img, expected, `${row.name}: tier/group icon mapping differs`);
}

const familyStageGrades = new Map([
	[21, "basic"],
	[22, "rare"],
	[23, "transcendent"],
	[24, "basic"],
	[25, "rare"],
	[26, "transcendent"],
	[30, "basic"],
	[31, "rare"],
	[35, "transcendent"],
	[36, "liberated"],
]);
for (const [tier, expectedGrade] of familyStageGrades) {
	const tierRows = rows.filter((row) => row.tier === tier);
	assert.equal(tierRows.length, 5, `tier ${tier} must contain five normal equipment drops`);
	assert(
		tierRows.every((row) => row.grade === expectedGrade),
		`tier ${tier} family stage must use the ${expectedGrade} frame`,
	);
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

const elementalCrystalHashes = new Map([
	["tier-10-atk-inc.png", "e2b6cc088ce36dd20ed1a636390e447476a88124e6d35d24a182914c7df8fe7f"],
	["tier-11-atk-inc.png", "2c1bce8ed716813b7456322219267173a6828a67be9278ab5ec90f6075de5f6c"],
	["tier-12-atk-inc.png", "236e853ed30ad9a8db3995c9e6443aa163fe363bf28e073ceb9558ec2a018a42"],
	["tier-18-atk-inc.png", "d11de3623817cf61f2ec6a368d81e770a4a244097d358ef37e5939004e26fca0"],
	["tier-19-atk-inc.png", "28c1e74879bf3043707aae966ec98ab8fd9f0fbce6acf1c1e1765ca4b552ff72"],
	["tier-20-atk-inc.png", "9a6003d02121d215e4f087527be3fb44ab3d6cf537f0de06c01e9f7da0ac9640"],
]);
for (const [file, expectedHash] of elementalCrystalHashes) {
	const actualHash = crypto
		.createHash("sha256")
		.update(fs.readFileSync(path.join(iconDirectory, file)))
		.digest("hex");
	assert.equal(actualHash, expectedHash, `${file}: approved four-element crystal artwork differs`);
}
assert.equal(
	new Set(elementalCrystalHashes.values()).size,
	elementalCrystalHashes.size,
	"all six four-element crystal progression images must remain distinct",
);

console.log("equipment icon family smoke passed");
console.log("- covered tiers / items / tier icon files: 1-39 / 195 / 195");
console.log("- mapping: one separate 256x256 PNG per tier and equipment group");
console.log("- elemental crystal: approved four-element progression at T10/T11/T12/T18/T19/T20");
console.log("- family frames: T23/T26=transcendent, T35=transcendent, T36=liberated");
console.log("- cache key: v367");

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
		.filter((boss) => boss.id >= 10 && boss.id <= 20)
		.flatMap((boss) => boss.drops.filter((drop) => drop.type === "normal"))
		.map((drop) => ({
			tier: drop.tier,
			name: drop.name,
			family: getNormalEquipmentFamilyName(drop.name),
			img: getNormalEquipmentIconUrl(drop),
			grade: getItemFrameGrade(drop),
		}))
`, context);

assert.equal(rows.length, 55, "tiers 10-20 must contain 55 normal equipment drops");
assert(rows.every((row) => row.img.startsWith("src/assets/equipment/")), "every tier 10-20 normal item needs a local icon");
assert.equal(new Set(rows.map((row) => row.img)).size, 20, "v364 must contain 6 ring stages plus 14 pending family bases");

const byName = new Map(rows.map((row) => [row.name, row]));
assert.equal(
	vm.runInContext(`getNormalEquipmentFamilyName("끝없는 절망 : 티아매트의 불신")`, context),
	"절망 : 티아매트의 불신",
	"tier 23 must normalize to the tier 21 base family",
);
assert.equal(
	vm.runInContext(`getNormalEquipmentFamilyName("영원한 파멸 : 베리아스의 불신")`, context),
	"파멸 : 베리아스의 불신",
	"tier 26 must normalize to the tier 24 base family",
);
const seaFamilyNames = [
	"마음을 새긴 바다",
	"-진- 마음을 새긴 바다",
	"★심연★ 마음을 새긴 바다",
];
assert.equal(new Set(seaFamilyNames.map((name) => byName.get(name).family)).size, 1, "sea family name normalization differs");
assert.equal(new Set(seaFamilyNames.map((name) => byName.get(name).img)).size, 1, "pending sea family must keep its basic icon fallback");
assert.deepEqual(
	seaFamilyNames.map((name) => byName.get(name).grade),
	["basic", "rare", "dark"],
	"sea family frame progression differs",
);

const purgatoryFamilyNames = [
	"어둠을 지배하는 고리",
	"-진- 어둠을 지배하는 고리",
	"-초월- 어둠을 지배하는 고리",
	"★연옥★ 어둠을 지배하는 고리",
	"★진 연옥★ 어둠을 지배하는 고리",
	"★초월 연옥★ 어둠을 지배하는 고리",
];
assert.equal(new Set(purgatoryFamilyNames.map((name) => byName.get(name).family)).size, 1, "purgatory family normalization differs");
assert.equal(new Set(purgatoryFamilyNames.map((name) => byName.get(name).img)).size, 6, "purgatory family must use one separate icon per stage");
assert.deepEqual(
	purgatoryFamilyNames.map((name) => byName.get(name).img.split("?")[0]),
	[
		"src/assets/equipment/dark-dominion-ring.png",
		"src/assets/equipment/dark-dominion-ring-jin.png",
		"src/assets/equipment/dark-dominion-ring-transcendent.png",
		"src/assets/equipment/dark-dominion-ring-purgatory.png",
		"src/assets/equipment/dark-dominion-ring-true-purgatory.png",
		"src/assets/equipment/dark-dominion-ring-transcendent-purgatory.png",
	],
	"purgatory family stage asset order differs",
);
assert.deepEqual(
	purgatoryFamilyNames.map((name) => byName.get(name).grade),
	["basic", "rare", "transcendent", "radiant", "dark", "luminous"],
	"purgatory family frame progression differs",
);

const iconDirectory = path.join(root, "src", "assets", "equipment");
const iconFiles = fs.readdirSync(iconDirectory).filter((file) => file.endsWith(".png")).sort();
assert.equal(iconFiles.length, 20, "v364 equipment icon batch must contain 20 PNG files");

for (const file of iconFiles) {
	const bytes = fs.readFileSync(path.join(iconDirectory, file));
	assert(bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10])), `${file}: invalid PNG signature`);
	assert.equal(bytes.readUInt32BE(16), 256, `${file}: width must be 256`);
	assert.equal(bytes.readUInt32BE(20), 256, `${file}: height must be 256`);
}

console.log("equipment icon family smoke passed");
console.log("- covered tiers / items / icon files: 10-20 / 55 / 20");
console.log("- separate upgraded icons: dark-dominion ring 6/6");
console.log("- pending family fallback icons: 14");
console.log("- image size: all 256x256 PNG");

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
	const expected = `src/assets/equipment/tier-${String(row.tier).padStart(2, "0")}-${assetKey}.png?v=368`;
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

const replacedV363DescendantHashes = new Map([
	["tier-10-normal-crit.png", "7dfb92e6d9b876f6063f388f04f88624d6c39630aa0f13bc05201c0248e0768b"],
	["tier-10-normal-dmg.png", "024574bf69411a1c69f9e7449a03463de05a6d75cd260ae40e4f809521e9830e"],
	["tier-10-skill-chance.png", "2813ee94e42e3a3fad201931748f56ad3c17259f3ca1e79ab7c41466e5de62fa"],
	["tier-11-normal-crit.png", "a4867c64f2c0e96279b82a829918b388c4ef1631fd47e2532dcd00d558cfe8d7"],
	["tier-11-normal-dmg.png", "ddecf687dc12ae290ffe3d13aa9e067bae62d9351be67d87e65d4a571bfb768b"],
	["tier-11-skill-chance.png", "44f3eaa2b5edd61ab24aef69fb5276605d0a8b73cf4c23e31cd6678267ac0dad"],
	["tier-12-normal-crit.png", "202c0dfa43cb4e2c4c67aad811d9de16e518c4022baf26eb28a520aef9c63f5f"],
	["tier-12-normal-dmg.png", "789868a2651385c97e1722cefe08654461fe07a8b55af87d897bbe02c28be1fd"],
	["tier-12-skill-chance.png", "4499cc00efa921ddf76a39c675ab4e05f1dcaa6d25304e0964f311af0aa37cd4"],
	["tier-13-atk-inc.png", "eaa378e3132b536bdbfbf18b5c7dd098cacb22ce7bda6f152253d8a660034776"],
	["tier-13-normal-crit.png", "9ed7ee12f48070706680a735da6bf78e198ba2ffff9588513dfd04cd1c981636"],
	["tier-13-normal-dmg.png", "a2f961a951bbab55d87778f5aaa0e8d2546ce816a5a9e721f83b601b2da74fce"],
	["tier-13-skill-all.png", "85803072b451207a5f04abe18cc5bd7b3cb0f77c0a8a6ee3faf252efee0e4788"],
	["tier-13-skill-chance.png", "9b7bd30d3e986a006d0a59ea6a7031d9cff62e97795daad2eb85b9905628cf26"],
	["tier-14-atk-inc.png", "7bc1b697b9c5107a2e7849d96ed25858d3e7b2b07cf6b8fca66f38a78d76f0e5"],
	["tier-14-normal-crit.png", "9e1794e8ea91e452a0dc8f64845feaf342765cff0fa5a98e2b7beb8ee67a4ed1"],
	["tier-14-normal-dmg.png", "1a2abed39d95fd9ccddd64474062ca1eaa688d5dbcd6dafcf1e0f6b27d9126e8"],
	["tier-14-skill-all.png", "c636933eb5502efd443494d16d7a5c88ace4b0e1d3fcecd9e9a86b1d151238ea"],
	["tier-14-skill-chance.png", "612e0773280642c63c3aa92755b7d463c44d6cdcbe36c76062cb8f82a6722b4f"],
	["tier-15-atk-inc.png", "8f413570157067dc9936dc274fdea1dd8b6a04f75b1ed4c4bd5581ce5d337d11"],
	["tier-15-normal-crit.png", "21e6cca41c06199bfabd55962fcd55a7d88bda68f9861134c0839b194b5d774e"],
	["tier-15-normal-dmg.png", "84fabbbcc7a622b3e85b7920d108004b2f2fecd33dce1d1e9bd9607eeb4e294f"],
	["tier-15-skill-all.png", "e6319c4c7578df9c9471eea4cac9bb75192b0a73f31c699ccee779b38c7ab47c"],
	["tier-15-skill-chance.png", "0665f2f99baafb948c65e13fc5960668df1f72967ab10ca91602281aeda83ba8"],
	["tier-16-atk-inc.png", "08247fbfe6be98cfc3fb987847637137f143cd97f48cd40d052a3f5687b2dab6"],
	["tier-16-normal-crit.png", "79b649f0abfa7d6cc457425759781bea3a60ac4a7eb88093d8f750a336fe011c"],
	["tier-16-normal-dmg.png", "c0028bbb1d5f7373c4f82538a56664a9bae47befcd986cf352799e53ad6700da"],
	["tier-16-skill-all.png", "fa2a62eca30fec5759cab63a8cb2628c3ef5cd87bc2248256b3f64f8c2f839ee"],
	["tier-16-skill-chance.png", "7923e3d895abd761926ef81c04cbd3ec1bf2aa44ed688f913402774ad2872bb8"],
	["tier-17-atk-inc.png", "93d55e3f230ab2fc89516aaa5c660dfd47cfa549235e461f5e98179c1e0beeb9"],
	["tier-17-normal-crit.png", "a21ee861fcd9a320ec37178dfbba2aa36068efc3a94d64ea04078209baf95541"],
	["tier-17-normal-dmg.png", "eb4d8ea541f1ea05687ba23fe7c59596d564a49d2d4ea68921da1d7c2494a289"],
	["tier-17-skill-all.png", "817fc9b9cbe504640c5544fec60b3841b5b776aa2e54baf097288d1aa641e0e0"],
	["tier-17-skill-chance.png", "843dfdf57ec78dea4fe5126095ea8605c937f1ceccd056227325bc6c384bb3d1"],
	["tier-18-normal-crit.png", "d938f01ef72bd5680511bbc3f4c01e392d0cf3e10bfdb027cfdcb723b87aa77e"],
	["tier-18-normal-dmg.png", "e99031271c46615f45918b64491ff220f9d5625c3b13e65d0f109cfd69d779ce"],
	["tier-18-skill-chance.png", "b17de9ac7248dc4e45f75b57aa3f9bb70dccc008ef4c32b680ac1243fea321e3"],
	["tier-19-normal-crit.png", "dd7d5fe3e85ebd751d93cf9d5bd530c0e5df6d507dc981ec1b9126a074e806d4"],
	["tier-19-normal-dmg.png", "342ba166ab6631dafe9215e5c0216f95dd281f4febf0b5b23a2748e50d13ed2d"],
	["tier-19-skill-chance.png", "37a96128f0d29af19ba1eee7c636c8cf0a76dbd06e32ee62e3fc0881f2e55bd3"],
	["tier-20-normal-crit.png", "82d3751c98731d5f3c45b11bd4856b1628787b7e2cd3df1d12aa06be13f642e1"],
	["tier-20-normal-dmg.png", "5f7800389636e87831c6dd61f96f6beb20a7d9989843c9cf89939d8a37e09bfa"],
	["tier-20-skill-chance.png", "e865e1ed4225306ce2d9b4c7e2920c3bdcee7c0fea49f90c18b93859ef9e7c6f"],
]);
for (const [file, expectedHash] of replacedV363DescendantHashes) {
	const actualHash = crypto
		.createHash("sha256")
		.update(fs.readFileSync(path.join(iconDirectory, file)))
		.digest("hex");
	assert.equal(actualHash, expectedHash, `${file}: approved v368 replacement artwork differs`);
}
assert.equal(replacedV363DescendantHashes.size, 43, "v368 must protect all 43 remaining v363 descendants");
assert.equal(
	new Set(replacedV363DescendantHashes.values()).size,
	replacedV363DescendantHashes.size,
	"all 43 v368 replacement images must remain distinct",
);

console.log("equipment icon family smoke passed");
console.log("- covered tiers / items / tier icon files: 1-39 / 195 / 195");
console.log("- mapping: one separate 256x256 PNG per tier and equipment group");
console.log("- elemental crystal: approved four-element progression at T10/T11/T12/T18/T19/T20");
console.log("- v363 crystal drafts: all remaining 43 descendants replaced with 13 recognizable equipment families");
console.log("- family frames: T23/T26=transcendent, T35=transcendent, T36=liberated");
console.log("- cache key: v368");

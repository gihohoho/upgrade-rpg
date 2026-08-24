const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { spawnSync } = require("node:child_process");

const root = path.resolve(__dirname, "..", "..", "..");
const assetVersion = "369";

const expectedAssets = new Map([
	["src/assets/equipment/liberation-staff.png", "fe80ea7e231fa913c4214eb21507f1204c83b0bc4f1c90e38f68e1045d5d8b0a"],
	["src/assets/skill-books/skill-book-q.png", "a859b8eb1f2b12d230d21a6be90d98f0afcc9965b29db225535287442ea86f09"],
	["src/assets/skill-books/skill-book-w.png", "5e90cb6811fc72099cd50981f85fbb03213fdc274699e36d8501eae4f0c1c542"],
	["src/assets/skill-books/skill-book-e.png", "3876fcc3daa52b6a2e036a78eae195ceb84de908efa39a08499cc4f10aa05231"],
	["src/assets/skill-books/skill-book-r.png", "15bfc53a8d0ea2d36d855886b4159b17424191029d2559b915804f46839305c3"],
	["src/assets/skill-books/skill-book-t.png", "9008b6ce046f8b0d01e94c22486ccdb4c848aac977fa32c32f57ffb647ee6a84"],
	["src/assets/skill-books/skill-book-f.png", "e4aec88c1963db0117f412d93ef381fe5cf7e4b059410237e54f435ae665ef8d"],
	["src/assets/skill-books/skill-book-d.png", "1bb7745e136323d1f02c8c55b3f557e25df2458938ae8017947e91b24201d540"],
	["src/assets/skill-books/skill-book-sq.png", "496a0617d046dd3d816db783c7afc3736a00430ca64d9a49a8adcf90eb498f47"],
	["src/assets/skill-books/skill-book-sw.png", "3f5df0af07dfc2d5116e4b699cb0b7a454f84b4fe0143ef3666fdce081ad8b27"],
	["src/assets/skill-books/skill-book-m.png", "a676599df3305710b7b8620f2b138452658583faf1caf14281667c54f7b41b5b"],
	["src/assets/skills/weapon-master/q-lightsabre-mastery.png", "f2542790e529ef23cd11cf2d5d1b5e8b01a80139bdd224044dc45795e5e1d862"],
	["src/assets/skills/weapon-master/w-iron-cutting.png", "2ad899a1272b5082bb2875d75bb5c510208ccfb05166de2f9e250913a016e263"],
	["src/assets/skills/weapon-master/e-overdrive.png", "efe54c95035f44beeff9f7b6426490b793239373f764446729da9afaf081747f"],
	["src/assets/skills/weapon-master/r-quick-draw.png", "88de0906bd781b90aff318250de477e3753724460d15d25bd119d21c50444762"],
	["src/assets/skills/weapon-master/t-illusion-sword.png", "192b23f84edc532887b66844d19e7877fed07ca746b6df30b2c703ba511a94fd"],
	["src/assets/skills/weapon-master/f-mind-sword.png", "77b49da045014e982fd07586a2b0cf0c320f86778c1a338b32b0160e660004a9"],
	["src/assets/skills/weapon-master/d-tempest.png", "5e0a3fc483f1357f5f65ac4e0b6d1478ce20d1234e60ada647bfc2ef5a4a59fa"],
	["src/assets/skills/weapon-master/sq-meteor-fall.png", "a3e9455209709521b3348ba4cc00371996852027221b3cf1ff675a89c17c5df7"],
	["src/assets/skills/weapon-master/sw-formless-slash.png", "6096b258c60df21a9714e26cdf5c7fd75a595e04a2da92d49b064f307dfa4bf9"],
	["src/assets/skills/weapon-master/m-heavenly-flash.png", "8921fb2a9caf8ca4a6c274a6cb441240427a7f690de9aa9060f5bd2f67c12a21"],
]);

const expectedSkillUrls = new Map([
	["Q", `src/assets/skills/weapon-master/q-lightsabre-mastery.png?v=${assetVersion}`],
	["W", `src/assets/skills/weapon-master/w-iron-cutting.png?v=${assetVersion}`],
	["E", `src/assets/skills/weapon-master/e-overdrive.png?v=${assetVersion}`],
	["R", `src/assets/skills/weapon-master/r-quick-draw.png?v=${assetVersion}`],
	["T", `src/assets/skills/weapon-master/t-illusion-sword.png?v=${assetVersion}`],
	["F", `src/assets/skills/weapon-master/f-mind-sword.png?v=${assetVersion}`],
	["D", `src/assets/skills/weapon-master/d-tempest.png?v=${assetVersion}`],
	["SQ", `src/assets/skills/weapon-master/sq-meteor-fall.png?v=${assetVersion}`],
	["SW", `src/assets/skills/weapon-master/sw-formless-slash.png?v=${assetVersion}`],
	["M", `src/assets/skills/weapon-master/m-heavenly-flash.png?v=${assetVersion}`],
]);

const skillBookCases = [
	["스킬강화권", "q"],
	["강력한 스킬강화권", "w"],
	["빛나는 스킬강화권", "e"],
	["화려한 스킬강화권", "r"],
	["찬란한 스킬강화권", "t"],
	["해방된 스킬강화권", "f"],
	["천공의 스킬강화권", "d"],
	["심연의 스킬강화권", "sq"],
	["-초월- 심연의 스킬강화권", "sw"],
	["-초월-심연의 스킬강화권", "sw"],
	["진 각성 스킬강화권", "m"],
];

function read(relative) {
	return fs.readFileSync(path.join(root, relative), "utf8");
}

function readFunctionBody(source, functionName) {
	const start = source.indexOf(`function ${functionName}(`);
	assert(start >= 0, `${functionName}: function is missing`);
	const openingBrace = source.indexOf("{", start);
	assert(openingBrace >= 0, `${functionName}: opening brace is missing`);
	let depth = 0;
	for (let index = openingBrace; index < source.length; index += 1) {
		if (source[index] === "{") depth += 1;
		if (source[index] === "}") {
			depth -= 1;
			if (depth === 0) return source.slice(openingBrace + 1, index);
		}
	}
	assert.fail(`${functionName}: closing brace is missing`);
}

function inspectPng(relative) {
	const absolute = path.join(root, relative);
	assert(fs.existsSync(absolute), `${relative}: expected generated asset is missing`);
	const bytes = fs.readFileSync(absolute);
	const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
	assert(bytes.length >= 45, `${relative}: PNG file is too short`);
	assert(bytes.subarray(0, 8).equals(signature), `${relative}: invalid PNG signature`);

	let offset = 8;
	let chunkCount = 0;
	let idatCount = 0;
	let sawIend = false;
	let width = null;
	let height = null;
	let bitDepth = null;
	let colorType = null;

	while (offset < bytes.length) {
		assert(offset + 12 <= bytes.length, `${relative}: truncated PNG chunk header`);
		const length = bytes.readUInt32BE(offset);
		const type = bytes.toString("ascii", offset + 4, offset + 8);
		const chunkEnd = offset + 12 + length;
		assert(chunkEnd <= bytes.length, `${relative}: truncated ${type || "unknown"} PNG chunk`);

		if (chunkCount === 0) {
			assert.equal(type, "IHDR", `${relative}: IHDR must be the first PNG chunk`);
			assert.equal(length, 13, `${relative}: IHDR length must be 13`);
			width = bytes.readUInt32BE(offset + 8);
			height = bytes.readUInt32BE(offset + 12);
			bitDepth = bytes[offset + 16];
			colorType = bytes[offset + 17];
			assert.equal(bytes[offset + 18], 0, `${relative}: unsupported PNG compression method`);
			assert.equal(bytes[offset + 19], 0, `${relative}: unsupported PNG filter method`);
			assert.equal(bytes[offset + 20], 0, `${relative}: interlaced PNG is not approved`);
		}

		if (type === "IDAT") idatCount += 1;
		if (type === "IEND") {
			assert.equal(length, 0, `${relative}: IEND length must be zero`);
			assert.equal(chunkEnd, bytes.length, `${relative}: bytes found after IEND`);
			sawIend = true;
		}

		offset = chunkEnd;
		chunkCount += 1;
	}

	assert.equal(offset, bytes.length, `${relative}: PNG chunk walk did not consume the full file`);
	assert(sawIend, `${relative}: IEND chunk is missing`);
	assert(idatCount > 0, `${relative}: IDAT image data is missing`);
	assert.equal(width, 256, `${relative}: width must be 256`);
	assert.equal(height, 256, `${relative}: height must be 256`);
	assert.equal(bitDepth, 8, `${relative}: bit depth must be 8`);
	assert([2, 6].includes(colorType), `${relative}: color type must be RGB or RGBA`);

	return crypto.createHash("sha256").update(bytes).digest("hex");
}

assert.equal(expectedAssets.size, 21, "v369 must protect exactly 21 generated PNG assets");
assert.equal(
	[...expectedAssets.keys()].filter((relative) => relative === "src/assets/equipment/liberation-staff.png").length,
	1,
	"v369 must contain one liberation staff asset",
);
assert.equal(
	[...expectedAssets.keys()].filter((relative) => relative.startsWith("src/assets/skill-books/")).length,
	10,
	"v369 must contain ten skill-book progression assets",
);
assert.equal(
	[...expectedAssets.keys()].filter((relative) => relative.startsWith("src/assets/skills/weapon-master/")).length,
	10,
	"v369 must contain ten weapon-master skill assets",
);

const discoveredHashes = new Map();
for (const relative of expectedAssets.keys()) discoveredHashes.set(relative, inspectPng(relative));
assert.equal(
	new Set(discoveredHashes.values()).size,
	discoveredHashes.size,
	"all 21 generated item and skill images must remain byte-distinct",
);

const pendingHashes = [];
for (const [relative, expectedHash] of expectedAssets) {
	const actualHash = discoveredHashes.get(relative);
	if (!expectedHash) {
		pendingHashes.push(`\t[${JSON.stringify(relative)}, ${JSON.stringify(actualHash)}],`);
		continue;
	}
	assert.match(expectedHash, /^[0-9a-f]{64}$/, `${relative}: approved SHA-256 is malformed`);
	assert.equal(actualHash, expectedHash, `${relative}: approved generated artwork differs`);
}

const skillContext = { console };
vm.createContext(skillContext);
vm.runInContext(read("src/data/skills.js"), skillContext, { filename: "src/data/skills.js" });
const skillRows = vm.runInContext(`
	Object.values(skillMasterData)
		.flatMap((skill) => [skill, skill.awakening].filter(Boolean))
		.map((skill) => ({ key: skill.slotKey, img: skill.img }))
`, skillContext);
assert.equal(skillRows.length, 10, "weapon master must expose ten skill icons including SQ and SW");
assert.deepEqual(
	[...skillRows.map((row) => row.key)].sort(),
	[...expectedSkillUrls.keys()].sort(),
	"weapon-master skill slot set differs",
);
for (const row of skillRows) {
	assert.equal(row.img, expectedSkillUrls.get(row.key), `${row.key}: weapon-master icon URL differs`);
	assert(!String(row.img).includes("placeholder.co"), `${row.key}: placeholder.co must not be used`);
}
assert.equal(new Set(skillRows.map((row) => row.img)).size, 10, "all ten weapon-master skill URLs must be unique");

const iconContext = { console };
vm.createContext(iconContext);
vm.runInContext(read("src/utils/icon-utils.js"), iconContext, { filename: "src/utils/icon-utils.js" });

const normalizedSkillBookUrls = [];
for (const [name, assetKey] of skillBookCases) {
	const item = { name, type: "skill_book", img: "https://placehold.co/stale-skill-book" };
	iconContext.item = item;
	vm.runInContext("normalizeItemIcon(item)", iconContext);
	const expectedUrl = `src/assets/skill-books/skill-book-${assetKey}.png?v=${assetVersion}`;
	assert.equal(item.img, expectedUrl, `${name}: normalized skill-book icon URL differs`);
	normalizedSkillBookUrls.push(item.img);
}
assert.equal(new Set(normalizedSkillBookUrls).size, 10, "SW aliases must share one URL and all other skill books must stay unique");
assert.equal(
	normalizedSkillBookUrls[8],
	normalizedSkillBookUrls[9],
	"spaced and compact SW skill-book names must resolve to the same icon",
);

const beginnerItem = {
	name: "리버레이션 스태프",
	type: "normal",
	equipGroup: "beginner",
	img: "https://placehold.co/stale-beginner",
};
iconContext.item = beginnerItem;
vm.runInContext("normalizeItemIcon(item)", iconContext);
assert.equal(
	beginnerItem.img,
	`src/assets/equipment/liberation-staff.png?v=${assetVersion}`,
	"beginner weapon must normalize to the v369 liberation staff asset",
);

const bossDisplaySource = read("src/rules/boss-display-rules.js");
assert(
	bossDisplaySource.includes("getSkillBookIconUrl(drop.name)"),
	"boss display must use the local skill-book icon resolver",
);

const renderUiSource = read("src/ui/render-ui.js");
const renderSkillsBody = readFunctionBody(renderUiSource, "renderSkills");
assert(!renderSkillsBody.includes("placeholder.co"), "renderSkills SQ/SW fallback must not use placeholder.co");

const mainSource = read("src/app/main.js");
const beginnerGrantBody = readFunctionBody(mainSource, "giveBeginnerItem");
const beginnerNormalizeIndex = beginnerGrantBody.indexOf("normalizeItemIcon(beginnerItem)");
const beginnerPlacementIndex = beginnerGrantBody.indexOf("placeItemInFirstEmptySlot(player.inventory, beginnerItem");
assert(beginnerNormalizeIndex >= 0, "direct beginner grant must normalize the item icon");
assert(
	beginnerPlacementIndex > beginnerNormalizeIndex,
	"direct beginner grant must normalize its icon before placing the item",
);

const runtimeSwitchSource = read("src/api/master-data-runtime-switch.js");
const applyLegacyBody = readFunctionBody(runtimeSwitchSource, "applyLegacyMasterData");
const finalReplacementIndex = Math.max(
	applyLegacyBody.indexOf("replaceObject(skillMasterData"),
	applyLegacyBody.indexOf("replaceArray(bossList"),
	applyLegacyBody.indexOf("replaceArray(specialBossList"),
);
const iconReapplyIndex = applyLegacyBody.indexOf("applyEquipmentIconAssets()");
assert(iconReapplyIndex >= 0, "backend master-data apply must reapply local generated icon assets");
assert(
	iconReapplyIndex > finalReplacementIndex,
	"local generated icon assets must be reapplied after backend master-data replacement",
);

const indexSource = read("index.html");
for (const [script, expectedCacheVersion] of [
	["src/data/skills.js", 378],
	["src/utils/icon-utils.js", assetVersion],
	["src/rules/boss-display-rules.js", assetVersion],
	["src/ui/render-ui.js", 378],
	["src/api/master-data-runtime-switch.js", assetVersion],
]) {
	assert(
		indexSource.includes(`src=\"${script}?v=${expectedCacheVersion}\"`),
		`${script}: index cache key must be v${expectedCacheVersion}`,
	);
}
assert(indexSource.includes('src="src/app/main.js?v=370"'), "src/app/main.js: index cache key must be v370");

const builderSource = read("tools/build_legacy_static_site.mjs");
assert(builderSource.includes('new Set([".js", ".css", ".png"])'), "legacy builder must publish PNG files");
assert(builderSource.includes('path.join(sourceDirectory, "assets")'), "legacy builder must restrict PNG publication to src/assets");
assert(builderSource.includes("await copyRuntimeFiles(sourcePath, destinationPath)"), "legacy builder must recursively copy nested asset directories");

const build = spawnSync(process.execPath, [path.join(root, "tools", "build_legacy_static_site.mjs")], {
	cwd: root,
	encoding: "utf8",
});
assert.equal(build.status, 0, build.stderr || build.stdout);
for (const [relative] of expectedAssets) {
	const published = path.join(root, "frontend", "legacy-dist", relative);
	assert(fs.existsSync(published), `${relative}: legacy static build omitted the generated asset`);
	assert(
		fs.readFileSync(published).equals(fs.readFileSync(path.join(root, relative))),
		`${relative}: legacy static build changed the generated asset bytes`,
	);
}

if (pendingHashes.length) {
	console.error("v369 generated assets passed structural checks, but approved SHA-256 values are not pinned.");
	console.error("Replace the empty values in expectedAssets with these discovered hashes:");
	pendingHashes.forEach((line) => console.error(line));
	assert.fail("v369 generated asset SHA-256 allowlist is incomplete");
}

console.log("v369 item and skill icon smoke passed");
console.log("- generated PNG assets: equipment 1 / skill books 10 / weapon-master skills 10");
console.log("- PNG contract: complete 256x256 RGB/RGBA files / approved SHA-256 allowlist");
console.log("- runtime: local resolvers / SW alias / backend master-data reapply / no skill placeholders");
console.log("- cache/static package: v369 / all 21 assets copied byte-for-byte");

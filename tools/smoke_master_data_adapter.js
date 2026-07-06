const fs = require("fs");
const path = require("path");
const vm = require("vm");

const projectRoot = path.resolve(__dirname, "..");
const adapterPath = path.join(projectRoot, "src", "api", "master-data-adapter.js");
const bridgePath = path.join(projectRoot, "src", "api", "master-data-bridge.js");
const clientPath = path.join(projectRoot, "src", "api", "game-api-client.js");
const indexPath = path.join(projectRoot, "index.html");
const seedDir = path.join(projectRoot, "backend", "seeds", "generated");

function assert(condition, message) {
	if (!condition) {
		console.error(message);
		process.exit(1);
	}
}

function readJson(name, fallback) {
	const filePath = path.join(seedDir, name);
	if (!fs.existsSync(filePath)) return fallback;
	return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function stripAsset(value) {
	if (typeof value === "string" && value.startsWith("data:image/")) return null;
	if (Array.isArray(value)) return value.map(stripAsset);
	if (value && typeof value === "object") {
		return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, stripAsset(item)]));
	}
	return value;
}

function secondsFromMs(value) {
	if (value === null || value === undefined || value === "") return null;
	return Number(value) / 1000;
}

function inferEnhanceGroup(item) {
	if (item.isTalisman || item.isEmblem) return "talisman_emblem";
	if (["normal", "abyss", "special", "avatar"].includes(item.type)) return "normal_equipment";
	return null;
}

function buildApiPayloadFromSeed({ includeAssets = false } = {}) {
	const characters = readJson("characters.json", []);
	const skills = readJson("skills.json", []);
	const items = readJson("item_templates.json", []);
	const bosses = readJson("bosses.json", []);
	const fields = readJson("field_zones.json", []);
	const dropTables = readJson("drop_tables.json", []);
	const dropItems = readJson("drop_table_items.json", []);
	const enhancement = readJson("enhancement_rules.json", {});
	const asset = (value) => (includeAssets ? value : stripAsset(value));

	const characterSkills = [];
	characters.forEach((character) => {
		(character.skillIds || []).forEach((skillCode, index) => {
			characterSkills.push({ characterCode: character.id, skillCode, sortOrder: index, isDefault: !!character.isDefault });
		});
	});

	const skillLevels = [];
	skills.forEach((skill) => {
		for (let level = 0; level <= Number(skill.maxLevel || 0); level += 1) {
			skillLevels.push({
				skillCode: skill.id,
				level,
				damageMultiplier: skill.damageMultiplier,
				procRateBonus: 0,
				options: { source: "seed", level },
			});
		}
	});

	const enhancementGroups = [
		{
			code: "normal_equipment",
			name: "일반 장비 강화",
			description: "일반 장비/심연 장비 강화 규칙",
			maxLevel: enhancement.normalEquipment ? enhancement.normalEquipment.maxLevel : 20,
			rules: { source: "seed", raw: enhancement.normalEquipment || {} },
			isEnabled: true,
		},
		{
			code: "talisman_emblem",
			name: "탈리스만/빛나는 휘장 강화",
			description: "0강 동일 아이템 재료를 사용해 강화하는 규칙",
			maxLevel: enhancement.talismanAndEmblem ? enhancement.talismanAndEmblem.maxLevel : 6,
			rules: { source: "seed", raw: enhancement.talismanAndEmblem || {} },
			isEnabled: true,
		},
	];

	return {
		characters: characters.map((character) => ({
			code: character.id,
			name: character.name,
			description: character.description,
			imageUrl: null,
			hasImage: false,
			isEnabled: true,
			meta: asset({ source: "seed", raw: character }),
		})),
		skills: skills.map((skill) => ({
			code: skill.id,
			name: skill.name,
			slotKey: skill.slotKey,
			description: skill.description,
			iconUrl: includeAssets ? skill.img : null,
			hasIcon: !!skill.img,
			procRate: skill.baseProcRate,
			cooldownSeconds: secondsFromMs(skill.cooldownMs),
			options: asset({
				source: "seed",
				skillType: skill.skillType,
				effectHtml: skill.effectHtml,
				damageMultiplier: skill.damageMultiplier,
				bonusGroup: skill.bonusGroup,
				awakening: skill.awakening,
				raw: skill,
			}),
		})),
		skillLevels,
		characterSkills,
		itemTemplates: items.map((item) => ({
			code: item.templateKey,
			name: item.name,
			itemType: item.type,
			grade: item.tier !== null && item.tier !== undefined ? String(item.tier) : item.grade,
			iconUrl: includeAssets ? item.img : null,
			hasIcon: !!item.img,
			description: item.equipText || item.description || null,
			stackable: ["skillBook", "material", "consumable"].includes(item.type),
			equipSlot: item.equipGroup || item.specialSlotIdx || null,
			enhanceGroupCode: inferEnhanceGroup(item),
			baseStats: item.baseStats || {},
			options: asset({
				source: "seed",
				tier: item.tier,
				equipGroup: item.equipGroup,
				equipLimit: item.equipLimit,
				specialSlotIdx: item.specialSlotIdx,
				specialStats: item.specialStats,
				sellPrice: item.sellPrice,
				baseCost: item.baseCost,
				baseIlv: item.baseIlv,
				raw: item.raw || item,
			}),
		})),
		bosses: bosses.map((boss) => ({
			code: `boss_${boss.id}`,
			name: boss.name,
			tier: boss.id,
			bossType: boss.isSpecial ? "special" : "normal",
			hp: boss.maxHp,
			imageUrl: includeAssets ? boss.img : null,
			hasImage: !!boss.img,
			description: boss.title || boss.desc1,
			summonRules: asset({
				source: "seed",
				title: boss.title,
				desc1: boss.desc1,
				desc2: boss.desc2,
				desc3: boss.desc3,
				reqLvl: boss.reqLvl,
				dropsList: boss.dropsList || [],
				dropRateDoubled: boss.dropRateDoubled,
				raw: boss,
			}),
			cooldownSeconds: secondsFromMs(boss.cooldownMs),
			isEnabled: true,
		})),
		fieldZones: fields.map((zone) => ({
			code: `field_${zone.level}`,
			name: zone.name,
			sortOrder: zone.level,
			enemyHp: zone.maxHp,
			goldReward: zone.goldReward,
			description: zone.enemyName || zone.name,
			entryRules: zone.req || {},
			farmRules: zone.farm || {},
			isEnabled: true,
		})),
		dropTables: dropTables.map((table) => ({
			code: table.id,
			ownerType: "boss",
			ownerCode: `boss_${table.bossId}`,
			description: table.title,
			rules: { source: "seed", raw: table },
			isEnabled: true,
		})),
		dropTableItems: dropItems.map((item, index) => ({
			id: index + 1,
			dropTableCode: item.dropTableId,
			itemTemplateCode: item.itemTemplateKey,
			rate: item.rate,
			minQuantity: item.quantityMin,
			maxQuantity: item.quantityMax,
			conditions: asset({ source: "seed", bossId: item.bossId, sortOrder: item.sortOrder, raw: item.raw || item }),
		})),
		enhancementGroups,
		enhancementLevels: [],
		enhancementRules: { groups: enhancementGroups, levels: [] },
		assetPolicy: { includeAssets, mode: includeAssets ? "inline-data-url" : "metadata-only" },
		counts: {
			characters: characters.length,
			skills: skills.length,
			characterSkills: characterSkills.length,
			skillLevels: skillLevels.length,
			itemTemplates: items.length,
			bosses: bosses.length,
			fieldZones: fields.length,
			dropTables: dropTables.length,
			dropTableItems: dropItems.length,
			enhancementGroups: enhancementGroups.length,
			enhancementLevels: 26,
		},
	};
}

assert(fs.existsSync(adapterPath), "src/api/master-data-adapter.js 파일이 없습니다.");

const indexHtml = fs.readFileSync(indexPath, "utf8");
const clientTagIndex = indexHtml.indexOf('src="src/api/game-api-client.js"');
const bridgeTagIndex = indexHtml.indexOf('src="src/api/master-data-bridge.js"');
const adapterTagIndex = indexHtml.indexOf('src="src/api/master-data-adapter.js"');
const dataTagIndex = indexHtml.indexOf('src="src/data/skills.js"');
assert(clientTagIndex >= 0, "index.html에 game-api-client.js script 태그가 없습니다.");
assert(bridgeTagIndex >= 0, "index.html에 master-data-bridge.js script 태그가 없습니다.");
assert(adapterTagIndex >= 0, "index.html에 master-data-adapter.js script 태그가 없습니다.");
assert(clientTagIndex < bridgeTagIndex, "game-api-client.js는 master-data-bridge.js보다 먼저 로드되어야 합니다.");
assert(bridgeTagIndex < adapterTagIndex, "master-data-bridge.js는 master-data-adapter.js보다 먼저 로드되어야 합니다.");
assert(adapterTagIndex < dataTagIndex, "master-data-adapter.js는 기존 데이터 파일보다 먼저 로드되어도 안전해야 합니다.");

const fakePayload = buildApiPayloadFromSeed({ includeAssets: false });
const fakeResponse = { ok: true, payload: fakePayload };

const sandbox = {
	console,
	URL,
	Date,
	window: {},
	fetch: async (url) => ({
		ok: true,
		status: 200,
		json: async () => ({
			ok: true,
			responseVersion: "game-api-response.v1",
			type: "game.master_data",
			payload: String(url).includes("includeAssets=true") ? buildApiPayloadFromSeed({ includeAssets: true }) : fakePayload,
			error: null,
		}),
	}),
};
sandbox.window = sandbox;
sandbox.localStorage = {
	items: {},
	getItem(key) { return this.items[key] || null; },
	setItem(key, value) { this.items[key] = String(value); },
};

vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(clientPath, "utf8"), sandbox, { filename: clientPath });
vm.runInContext(fs.readFileSync(bridgePath, "utf8"), sandbox, { filename: bridgePath });
vm.runInContext(fs.readFileSync(adapterPath, "utf8"), sandbox, { filename: adapterPath });

assert(sandbox.RpgMasterDataAdapter, "RpgMasterDataAdapter 전역 객체가 생성되지 않았습니다.");
assert(typeof sandbox.checkBackendMasterDataAdapter === "function", "checkBackendMasterDataAdapter 콘솔 함수가 없습니다.");

const legacyData = sandbox.RpgMasterDataAdapter.createLegacyMasterDataFromPayload(fakeResponse);
const validation = sandbox.RpgMasterDataAdapter.validateLegacyMasterData(legacyData);
assert(validation.ok, `adapter validation failed: ${JSON.stringify(validation.failures)}`);
assert(legacyData.defaultCharacterId === "weapon_master", "defaultCharacterId가 weapon_master가 아닙니다.");
assert(legacyData.skillMasterData.lightsabre.baseProcRate === null, "lightsabre.baseProcRate null 보존 실패");
assert(legacyData.bossList.length === 39, "일반 보스 수가 39개가 아닙니다.");
assert(legacyData.specialBossList.length === 6, "특수 보스 수가 6개가 아닙니다.");
assert(legacyData.fieldZones.length === 40, "필드 수가 40개가 아닙니다.");
assert(legacyData.itemTemplateList.length === 245, "아이템 템플릿 수가 245개가 아닙니다.");
assert(validation.hasInlineAsset === false, "기본 adapter 결과에 inline data URL이 남아 있습니다.");

(async () => {
	const result = await sandbox.checkBackendMasterDataAdapter();
	assert(result.ok === true, "브라우저 adapter 체크 함수가 실패했습니다.");
	const resultWithAssets = await sandbox.checkBackendMasterDataAdapter({ includeAssets: true });
	assert(resultWithAssets.ok === true, "includeAssets adapter 체크 함수가 실패했습니다.");
	console.log("master-data adapter smoke test passed");
})();

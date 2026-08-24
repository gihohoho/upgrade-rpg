/**
 * skills.js
 *
 * 백엔드 분리 준비 2차 정리 - 3순위 적용본
 * ------------------------------------------------------------
 * 목적:
 * - 현재 코드에 흩어진 스킬/스킬강화권 정보를 한 곳에 모읍니다.
 * - 앞으로 캐릭터가 추가될 때, 전투/아이템/툴팁 코드를 크게 고치지 않고
 *   캐릭터별 스킬 목록만 바꿀 수 있게 만드는 준비 단계입니다.
 *
 * 현재 원칙:
 * - 장비, 보스, 드랍, 강화, 필드 시스템은 공통입니다.
 * - 캐릭터마다 달라지는 것은 스킬 목록입니다.
 * - 기존 코드 호환을 위해 player.skills 접근은 유지하되,
 *   실제 기준 구조는 player.userCharacters[currentCharacterId].skills 입니다.
 */

const DEFAULT_CHARACTER_ID = "weapon_master";
const WEAPON_MASTER_SKILL_ICON_ASSET_BASE = "src/assets/skills/weapon-master";
const WEAPON_MASTER_SKILL_ICON_ASSET_VERSION = "369";
const WEAPON_MASTER_SKILL_ICON_FILES = Object.freeze({
	lightsabre: "q-lightsabre-mastery.png",
	lightsabre_sq: "sq-meteor-fall.png",
	ironStrike: "w-iron-cutting.png",
	ironStrike_sw: "sw-formless-slash.png",
	overdrive: "e-overdrive.png",
	baldo: "r-quick-draw.png",
	illusionSword: "t-illusion-sword.png",
	deepSword: "f-mind-sword.png",
	tempestStrike: "d-tempest.png",
	heavenlyStrike: "m-heavenly-flash.png",
});

function getWeaponMasterSkillIconUrl(skillId) {
	const assetName = WEAPON_MASTER_SKILL_ICON_FILES[String(skillId || "")];
	return assetName ? `${WEAPON_MASTER_SKILL_ICON_ASSET_BASE}/${assetName}?v=${WEAPON_MASTER_SKILL_ICON_ASSET_VERSION}` : "";
}

const characterMasterData = {
	weapon_master: {
		id: "weapon_master",
		name: "웨펀마스터",
		description: "현재 기본 캐릭터입니다. 기존 Q/W/E/R/T/F/D/M 스킬 구성을 그대로 사용합니다.",
		skillIds: [
			"lightsabre",
			"ironStrike",
			"overdrive",
			"baldo",
			"illusionSword",
			"deepSword",
			"tempestStrike",
			"heavenlyStrike",
		],
	},
};

const skillMasterData = {
	lightsabre: {
		id: "lightsabre",
		slotKey: "Q",
		name: "광검 마스터리",
		img: getWeaponMasterSkillIconUrl("lightsabre"),
		description: "광검을 보다 효율적으로 다룹니다.",
		effectHtml: "-기본 공격 시 단일 적에게 스킬레벨 x 공격력 x 1의 스킬데미지",
		maxLevel: 7,
		skillType: "passive_damage",
		baseProcRate: null,
		damageMultiplier: 1,
		bonusGroup: null,
		awakening: {
			id: "lightsabre_sq",
			slotKey: "SQ",
			name: "극 귀검술 - 유성락",
			img: getWeaponMasterSkillIconUrl("lightsabre_sq"),
			description: "무수한 기의 검을 내려꽂습니다.",
			effectHtml: "-기본 공격 시 0.5% 확률로 발동<br>-단일 적에게 스킬레벨 x 공격력 x 200000의 스킬데미지",
			baseProcRate: 0.5,
			damageMultiplier: 200000,
			bonusGroup: null,
		},
	},
	ironStrike: {
		id: "ironStrike",
		slotKey: "W",
		name: "극 귀검술 - 참철식",
		img: getWeaponMasterSkillIconUrl("ironStrike"),
		description: "검술을 극성으로 익힙니다.",
		effectHtml: "-기본 공격 시 3% 확률로 발동<br>-단일 적에게 스킬레벨 x 공격력 x 500의 스킬데미지<br>-4초간 모든피해 1% 증가 (합산; 재발동 시 지속시간만 갱신)",
		maxLevel: 7,
		skillType: "proc_damage_buff",
		baseProcRate: 3,
		damageMultiplier: 500,
		bonusGroup: null,
		awakening: {
			id: "ironStrike_sw",
			slotKey: "SW",
			name: "극 발검술 - 무형참",
			img: getWeaponMasterSkillIconUrl("ironStrike_sw"),
			description: "무수한 무형의 검으로 적을 난도질합니다.",
			effectHtml: "-기본 공격 시 0.5% 확률로 발동<br>-단일 적에게 스킬레벨 x 공격력 x 320000의 스킬데미지",
			baseProcRate: 0.5,
			damageMultiplier: 320000,
			bonusGroup: null,
		},
	},
	overdrive: {
		id: "overdrive",
		slotKey: "E",
		name: "오버 드라이브",
		img: getWeaponMasterSkillIconUrl("overdrive"),
		description: "일정 시간 동안 무기의 내구도 이상으로 무기를 활용합니다.",
		effectHtml: "-기본 공격 시 2% 확률로 발동<br>-지속시간 4초 (재발동 시 갱신)<br>-지속중 기본 공격 시 단일 적에게 스킬레벨 x 공격력 x 150의 스킬데미지",
		maxLevel: 7,
		skillType: "proc_buff_damage",
		baseProcRate: 2,
		damageMultiplier: 150,
		bonusGroup: null,
	},
	baldo: {
		id: "baldo",
		slotKey: "R",
		name: "발도",
		img: getWeaponMasterSkillIconUrl("baldo"),
		description: "매우 빠른속도로 납도를 하여 즉 베어버립니다.",
		effectHtml: "-기본 공격 시 3% 확률로 발동<br>-단일 적에게 스킬레벨 x 공격력 x 4000의 스킬데미지",
		maxLevel: 7,
		skillType: "proc_damage",
		baseProcRate: 3,
		damageMultiplier: 4000,
		bonusGroup: "talismanA",
	},
	illusionSword: {
		id: "illusionSword",
		slotKey: "T",
		name: "환영검무",
		img: getWeaponMasterSkillIconUrl("illusionSword"),
		description: "환영이 보일정도의 초고속으로 적을 베어버립니다.",
		effectHtml: "-기본 공격 시 2% 확률로 발동<br>-단일 적에게 스킬레벨 x 공격력 x 12000의 스킬데미지",
		maxLevel: 7,
		skillType: "proc_damage",
		baseProcRate: 2,
		damageMultiplier: 12000,
		bonusGroup: "talismanA",
	},
	deepSword: {
		id: "deepSword",
		slotKey: "F",
		name: "극 귀검술 - 심검",
		img: getWeaponMasterSkillIconUrl("deepSword"),
		description: "눈에보이지 않는 속도로 베어버립니다.",
		effectHtml: "-기본 공격 시 2% 확률로 발동<br>-단일 적에게 스킬레벨 x 공격력 x 16000의 스킬데미지",
		maxLevel: 7,
		skillType: "proc_damage",
		baseProcRate: 2,
		damageMultiplier: 16000,
		bonusGroup: "talismanB",
	},
	tempestStrike: {
		id: "tempestStrike",
		slotKey: "D",
		name: "극 귀검술 - 폭풍식",
		img: getWeaponMasterSkillIconUrl("tempestStrike"),
		description: "수많은 기의 검을 소환하여 각검으로 공격합니다.",
		effectHtml: "-기본 공격 시 1.2% 확률로 발동<br>-단일 적에게 스킬레벨 x 공격력 x 42000의 스킬데미지",
		maxLevel: 7,
		skillType: "proc_damage",
		baseProcRate: 1.2,
		damageMultiplier: 42000,
		bonusGroup: "talismanB",
	},
	heavenlyStrike: {
		id: "heavenlyStrike",
		slotKey: "M",
		name: "천제극섬",
		img: getWeaponMasterSkillIconUrl("heavenlyStrike"),
		description: "모든 웨펀의 궁극의 일격을 가합니다.",
		effectHtml: "-쿨타임 300초<br>-기본 공격 시 5% 확률로 발동<br>-단일 적에게 스킬레벨 x 공격력 x 11000000의 스킬데미지",
		maxLevel: 7,
		skillType: "ultimate_proc_damage",
		baseProcRate: 5,
		damageMultiplier: 11000000,
		cooldownMs: 300000,
		bonusGroup: null,
	},
};

function applyWeaponMasterSkillIconAssets(targetSkillMasterData = skillMasterData) {
	if (!targetSkillMasterData || typeof targetSkillMasterData !== "object") return targetSkillMasterData;
	Object.values(targetSkillMasterData).forEach((skill) => {
		if (!skill || typeof skill !== "object") return;
		const baseIconUrl = getWeaponMasterSkillIconUrl(skill.id);
		if (baseIconUrl) skill.img = baseIconUrl;
		if (skill.awakening && typeof skill.awakening === "object") {
			const awakeningIconUrl = getWeaponMasterSkillIconUrl(skill.awakening.id);
			if (awakeningIconUrl) skill.awakening.img = awakeningIconUrl;
		}
	});
	return targetSkillMasterData;
}

applyWeaponMasterSkillIconAssets();

const skillBookMasterData = {
	"스킬강화권": { itemName: "스킬강화권", targetSkillId: "lightsabre", type: "normal" },
	"강력한 스킬강화권": { itemName: "강력한 스킬강화권", targetSkillId: "ironStrike", type: "normal" },
	"빛나는 스킬강화권": { itemName: "빛나는 스킬강화권", targetSkillId: "overdrive", type: "normal" },
	"화려한 스킬강화권": { itemName: "화려한 스킬강화권", targetSkillId: "baldo", type: "normal" },
	"찬란한 스킬강화권": { itemName: "찬란한 스킬강화권", targetSkillId: "illusionSword", type: "normal" },
	"해방된 스킬강화권": { itemName: "해방된 스킬강화권", targetSkillId: "deepSword", type: "normal" },
	"천공의 스킬강화권": { itemName: "천공의 스킬강화권", targetSkillId: "tempestStrike", type: "normal" },
	"심연의 스킬강화권": { itemName: "심연의 스킬강화권", targetSkillId: "lightsabre", type: "awakening", awakeningKey: "SQ", baseKey: "Q" },
	"-초월- 심연의 스킬강화권": { itemName: "-초월- 심연의 스킬강화권", targetSkillId: "ironStrike", type: "awakening", awakeningKey: "SW", baseKey: "W" },
	"-초월-심연의 스킬강화권": { itemName: "-초월-심연의 스킬강화권", targetSkillId: "ironStrike", type: "awakening", awakeningKey: "SW", baseKey: "W" },
	"진 각성 스킬강화권": { itemName: "진 각성 스킬강화권", targetSkillId: "heavenlyStrike", type: "ultimate" },
};

function getDefaultCharacterId() {
	return DEFAULT_CHARACTER_ID;
}

function getCharacterDefinition(characterId = DEFAULT_CHARACTER_ID) {
	return characterMasterData[characterId] || characterMasterData[DEFAULT_CHARACTER_ID];
}

function getSkillDefinition(skillId) {
	return skillMasterData[skillId] || null;
}

function getCharacterSkillIds(characterId = DEFAULT_CHARACTER_ID) {
	const character = getCharacterDefinition(characterId);
	return [...(character.skillIds || [])];
}

function createDefaultCharacterSkillState(characterId = DEFAULT_CHARACTER_ID) {
	const state = {};
	getCharacterSkillIds(characterId).forEach((skillId) => {
		state[skillId] = { level: skillId === "lightsabre" ? 1 : 0 };
		const def = getSkillDefinition(skillId);
		if (def && def.awakening) state[skillId].isUpgraded = false;
		if (skillId === "heavenlyStrike") state[skillId].lastUsed = 0;
	});
	return state;
}

function getDefaultSkillState(characterId = DEFAULT_CHARACTER_ID) {
	return createDefaultCharacterSkillState(characterId);
}

function createSkillBookMapping() {
	const mapping = {};
	Object.keys(skillBookMasterData).forEach((itemName) => {
		mapping[itemName] = skillBookMasterData[itemName].targetSkillId;
	});
	return mapping;
}

function getSkillBookDefinition(itemName) {
	return skillBookMasterData[itemName] || null;
}

function getSkillBookDisplayInfo(itemName) {
	const book = getSkillBookDefinition(itemName);
	if (!book) return { key: "?", skill: "대응 스킬", type: "일반" };
	const skill = getSkillDefinition(book.targetSkillId);
	if (!skill) return { key: "?", skill: "대응 스킬", type: "일반" };
	if (book.type === "awakening") {
		const awakened = skill.awakening || {};
		return {
			key: book.awakeningKey || awakened.slotKey || skill.slotKey,
			skill: awakened.name || skill.name,
			type: "각성",
			base: book.baseKey || skill.slotKey,
			targetSkillId: book.targetSkillId,
		};
	}
	if (book.type === "ultimate") {
		return { key: skill.slotKey, skill: skill.name, type: "진각성", targetSkillId: book.targetSkillId };
	}
	return { key: skill.slotKey, skill: skill.name, type: "일반", targetSkillId: book.targetSkillId };
}

function isAwakeningSkillBook(itemName) {
	const book = getSkillBookDefinition(itemName);
	return !!book && book.type === "awakening";
}

function getSkillMaxLevel(skillId) {
	const skill = getSkillDefinition(skillId);
	return skill && skill.maxLevel ? skill.maxLevel : 7;
}

function cloneSkillState(skillState) {
	return skillState && typeof skillState === "object" ? { ...skillState } : null;
}

function isMeaningfulLegacySkillState(skillState) {
	if (!skillState || typeof skillState !== "object") return false;
	return (parseInt(skillState.level) || 0) > 0 || !!skillState.isUpgraded || (parseInt(skillState.lastUsed) || 0) > 0;
}

function shouldPreferLegacySkillState(currentState, legacyState) {
	if (!isMeaningfulLegacySkillState(legacyState)) return false;
	if (!currentState || typeof currentState !== "object") return true;

	const currentLevel = parseInt(currentState.level) || 0;
	const legacyLevel = parseInt(legacyState.level) || 0;
	if (legacyLevel > currentLevel) return true;
	if (legacyState.isUpgraded && !currentState.isUpgraded) return true;
	if ((parseInt(legacyState.lastUsed) || 0) > (parseInt(currentState.lastUsed) || 0)) return true;
	return false;
}

function mergeLegacySkillsIntoCharacterSkills(characterSkills, legacySkills, characterId = DEFAULT_CHARACTER_ID) {
	const defaults = createDefaultCharacterSkillState(characterId);
	const nextSkills = characterSkills && typeof characterSkills === "object" ? characterSkills : {};
	const legacy = legacySkills && typeof legacySkills === "object" ? legacySkills : {};

	Object.keys(defaults).forEach((skillId) => {
		if (!nextSkills[skillId]) nextSkills[skillId] = { ...defaults[skillId] };
		if (legacy[skillId] && shouldPreferLegacySkillState(nextSkills[skillId], legacy[skillId])) {
			nextSkills[skillId] = { ...nextSkills[skillId], ...cloneSkillState(legacy[skillId]) };
		}
	});

	return nextSkills;
}

function normalizePlayerCharacterState(targetPlayer) {
	if (!targetPlayer || typeof targetPlayer !== "object") return targetPlayer;
	const characterId = targetPlayer.currentCharacterId || DEFAULT_CHARACTER_ID;
	const legacySkills = targetPlayer.skills && typeof targetPlayer.skills === "object" ? targetPlayer.skills : null;
	if (!Array.isArray(targetPlayer.ownedCharacterIds)) targetPlayer.ownedCharacterIds = [characterId];
	if (!targetPlayer.ownedCharacterIds.includes(characterId)) targetPlayer.ownedCharacterIds.push(characterId);
	if (!targetPlayer.userCharacters || typeof targetPlayer.userCharacters !== "object") targetPlayer.userCharacters = {};
	if (!targetPlayer.userCharacters[characterId]) {
		targetPlayer.userCharacters[characterId] = {
			characterId,
			skills: legacySkills || createDefaultCharacterSkillState(characterId),
		};
	}

	// v068에서 캐릭터별 스킬 구조가 추가되었습니다.
	// 기존 저장 파일은 player.skills에만 실제 스킬 레벨이 있고,
	// userCharacters[currentCharacterId].skills는 기본값으로 생성될 수 있습니다.
	// 이 경우 전투는 새 구조를 읽기 때문에 스킬 발동/데미지 텍스트가 사라진 것처럼 보일 수 있어,
	// 여기서 기존 player.skills 값을 현재 캐릭터 스킬 상태로 안전하게 이관합니다.
	targetPlayer.userCharacters[characterId].skills = mergeLegacySkillsIntoCharacterSkills(
		targetPlayer.userCharacters[characterId].skills,
		legacySkills,
		characterId
	);

	// 기존 코드 호환: 아직 combat/render/item 로직 대부분이 player.skills를 읽습니다.
	// 내부 기준은 userCharacters[currentCharacterId].skills로 두고, player.skills는 같은 객체를 바라보게 합니다.
	targetPlayer.skills = targetPlayer.userCharacters[characterId].skills;
	return targetPlayer;
}

function getCurrentCharacterId(targetPlayer = window.player) {
	return targetPlayer && targetPlayer.currentCharacterId ? targetPlayer.currentCharacterId : DEFAULT_CHARACTER_ID;
}

function getCurrentUserCharacter(targetPlayer = window.player) {
	if (!targetPlayer) return null;
	normalizePlayerCharacterState(targetPlayer);
	return targetPlayer.userCharacters[getCurrentCharacterId(targetPlayer)] || null;
}

function getCurrentCharacterSkills(targetPlayer = window.player) {
	const userCharacter = getCurrentUserCharacter(targetPlayer);
	return userCharacter && userCharacter.skills ? userCharacter.skills : createDefaultCharacterSkillState(DEFAULT_CHARACTER_ID);
}

function getSkillState(skillId, targetPlayer = window.player) {
	const skills = getCurrentCharacterSkills(targetPlayer);
	if (!skills[skillId]) skills[skillId] = { level: 0 };
	return skills[skillId];
}

function getRenderableSkillList(targetPlayer = window.player) {
	const characterId = getCurrentCharacterId(targetPlayer);
	const skills = getCurrentCharacterSkills(targetPlayer);
	return getCharacterSkillIds(characterId).map((skillId) => {
		const baseDef = getSkillDefinition(skillId);
		const skillState = skills[skillId] || { level: 0 };
		let viewDef = { ...baseDef };
		if (baseDef && baseDef.awakening && skillState.isUpgraded) {
			viewDef = { ...baseDef, ...baseDef.awakening, id: baseDef.id, originalSkillId: baseDef.id };
		}
		viewDef.key = viewDef.slotKey; // 기존 renderSkills 코드 호환용 별칭
		viewDef.desc = viewDef.description; // 기존 renderSkills 코드 호환용 별칭
		viewDef.eff = viewDef.effectHtml; // 기존 renderSkills 코드 호환용 별칭
		return viewDef;
	}).filter(Boolean);
}

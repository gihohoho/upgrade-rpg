/*
 * logic.js rebuilt
 * - 1~11티어: 기존 확정 데이터/공식 유지
 * - 12티어: 실측 상수 기반 확정 공식 적용
 * - 13티어 이후: 실측값 입력 전까지 예측 공식 유지
 * - 공개 함수명은 기존 코드와 호환: getRandomInt, formatNumber, calcItemStats,
 *   getEnhanceCost, getBaseEnhanceProb, getEnhanceProb, getTotals
 */

const UNIT_B = 10000;
const FIELD_START_ATTACK_SPEED = 150;
const FIELD_MAX_ATTACK_SPEED = 400;
// 150%에서 1250A로 시작하고, 400%에서 5000A가 되도록 1%당 +15A로 환산합니다.
const BASE_ATTACK_AT_START_SPEED = 1250;
const BASE_ATTACK_GAIN_PER_ASPD = 15;

function getClampedFieldAttackSpeed() {
	let aspd = player && player.addAttackSpeed !== undefined ? parseFloat(player.addAttackSpeed) || FIELD_START_ATTACK_SPEED : FIELD_START_ATTACK_SPEED;
	if (aspd < FIELD_START_ATTACK_SPEED) aspd = FIELD_START_ATTACK_SPEED;
	if (aspd > FIELD_MAX_ATTACK_SPEED) aspd = FIELD_MAX_ATTACK_SPEED;
	return aspd;
}

function getBaseAttackByAttackSpeed() {
	let aspd = getClampedFieldAttackSpeed();
	return Math.floor(BASE_ATTACK_AT_START_SPEED + (aspd - FIELD_START_ATTACK_SPEED) * BASE_ATTACK_GAIN_PER_ASPD);
}


function getRandomInt(min, max) {
	return Math.floor(Math.random() * (max - min + 1)) + min;
}

function formatCompactNumber(num, significantDigits = 4) {
	if (isNaN(num) || num === undefined || num === 0) return "0A";
	const units = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"];
	let isNegative = num < 0;
	let value = Math.abs(num);
	let unitIndex = 0;

	while (value >= 10000 && unitIndex < units.length - 1) {
		value /= 10000;
		unitIndex++;
	}

	let integerDigits = value >= 1 ? Math.floor(Math.log10(value)) + 1 : 1;
	let decimals = Math.max(0, significantDigits - integerDigits);
	let rounded = Number(value.toFixed(decimals));

	if (rounded >= 10000 && unitIndex < units.length - 1) {
		rounded /= 10000;
		unitIndex++;
		integerDigits = rounded >= 1 ? Math.floor(Math.log10(rounded)) + 1 : 1;
		decimals = Math.max(0, significantDigits - integerDigits);
	}

	let text = decimals > 0
		? rounded.toFixed(decimals).replace(/\.0+$/, "").replace(/(\.\d*?)0+$/, "$1")
		: String(Math.round(rounded));
	return (isNegative ? "-" : "") + text + units[unitIndex];
}

function formatNumber(num) {
	return formatCompactNumber(num, 4);
}




function getCodexCompletionBonusPercent() {
	if (typeof getCollectionStats !== "function") return 0;
	const stats = getCollectionStats();
	const owned = Number(stats && stats.owned) || 0;
	return owned * 0.1;
}




const SPECIAL_EQUIP_ATTACK_BY_LEVEL = [
	3417, 3531, 3759, 4101, 4557,
	5127, 5811, 6609, 7521, 8547,
	9687, 11900, 15000, 19300, 24500,
	30800, 38100, 46400, 55700, 66100,
	77500,
];

// 심연의 편린 반지/목걸이 증폭 수치. 반지는 스킬피해, 목걸이는 평타피해에 적용된다.
const ABYSS_RING_NECK_AMP_BY_LEVEL = [
	1.0, 1.1, 1.3, 1.6, 2.0,
	2.5, 3.1, 3.8, 4.6, 5.5,
	6.5, 7.7, 9.1, 10.7, 12.5,
	14.5, 16.7, 19.1, 21.7, 24.5,
	27.5,
];

// 심연의 편린 스태프 고유능력 수치.
const ABYSS_STAFF_MAIN_BY_LEVEL = [
	0.1, 0.2, 0.4, 0.7, 1.1,
	1.6, 2.2, 2.9, 3.7, 4.6,
	5.6, 7.0, 8.8, 11.0, 13.6,
	16.6, 20.0, 23.8, 28.0, 32.6,
	37.6,
];
const ABYSS_STAFF_SUB_BY_LEVEL = [
	0.1, 0.2, 0.4, 0.7, 1.1,
	1.6, 2.2, 2.9, 3.7, 4.6,
	5.6, 6.7, 7.9, 9.2, 10.6,
	12.1, 13.7, 15.4, 17.2, 19.1,
	21.1,
];
const ABYSS_STAFF_BUFF_BY_LEVEL = [
	0.1, 0.25, 0.55, 1.0, 1.6,
	2.35, 3.25, 4.3, 5.5, 6.85,
	8.35, 10.0, 11.8, 13.8, 15.9,
	18.1, 20.5, 23.1, 25.8, 28.6,
	31.6,
];
const ABYSS_STAFF_CLONE_COUNT_BY_LEVEL = [
	2, 2, 2, 2, 2,
	2, 2, 2, 2, 2,
	2, 3, 3, 3, 3,
	3, 4, 4, 4, 4,
	4,
];
const ABYSS_STAFF_CLONE_ASPD_BY_LEVEL = [
	0.001, 2, 6, 12, 20,
	30, 42, 56, 72, 90,
	110, 132, 156, 182, 210,
	240, 272, 306, 342, 380,
	420,
];
const ABYSS_STAFF_MAX_ASPD_CAP_BY_LEVEL = [
	1.0, 1.1, 1.3, 1.6, 2.0,
	2.5, 3.1, 3.8, 4.6, 5.5,
	6.5, 7.8, 9.4, 11.3, 13.5,
	16.0, 18.8, 21.9, 25.3, 29.0,
	33.0,
];


function scaleSpecialArrayToLast(baseArray, targetLast, decimals = 1) {
	const currentLast = baseArray[baseArray.length - 1] || 1;
	const ratio = targetLast / currentLast;
	const scale = Math.pow(10, decimals);
	return baseArray.map((v, idx) => {
		if (idx === baseArray.length - 1) return targetLast;
		return Math.round(v * ratio * scale) / scale;
	});
}

function scaleSpecialIntegerArrayToLast(baseArray, targetLast) {
	const currentLast = baseArray[baseArray.length - 1] || 1;
	const ratio = targetLast / currentLast;
	return baseArray.map((v, idx) => idx === baseArray.length - 1 ? targetLast : Math.round(v * ratio));
}

const TRANSCEND_SPECIAL_EQUIP_ATTACK_BY_LEVEL = scaleSpecialIntegerArrayToLast(SPECIAL_EQUIP_ATTACK_BY_LEVEL, 174000); // +20 = 17.4B
const TRANSCEND_RING_NECK_AMP_BY_LEVEL = scaleSpecialArrayToLast(ABYSS_RING_NECK_AMP_BY_LEVEL, 40.8, 1);
const TRANSCEND_STAFF_MAIN_BY_LEVEL = scaleSpecialArrayToLast(ABYSS_STAFF_MAIN_BY_LEVEL, 56.4, 1);
const TRANSCEND_STAFF_SUB_BY_LEVEL = scaleSpecialArrayToLast(ABYSS_STAFF_SUB_BY_LEVEL, 31.6, 1);
const TRANSCEND_STAFF_BUFF_BY_LEVEL = scaleSpecialArrayToLast(ABYSS_STAFF_BUFF_BY_LEVEL, 42.1, 1);
const TRANSCEND_STAFF_CLONE_ASPD_BY_LEVEL = scaleSpecialArrayToLast(ABYSS_STAFF_CLONE_ASPD_BY_LEVEL, 630, 1);
const TRANSCEND_STAFF_MAX_ASPD_CAP_BY_LEVEL = scaleSpecialArrayToLast(ABYSS_STAFF_MAX_ASPD_CAP_BY_LEVEL, 46.3, 1);
const AVATAR_ATTACK_BY_LEVEL = scaleSpecialIntegerArrayToLast(SPECIAL_EQUIP_ATTACK_BY_LEVEL, 882000); // +20 = 88.2B
const AVATAR_AMP_BY_LEVEL = scaleSpecialArrayToLast(ABYSS_RING_NECK_AMP_BY_LEVEL, 33.0, 1);
const AVATAR_SKILL_CRIT_CHANCE_BY_LEVEL = scaleSpecialArrayToLast(ABYSS_RING_NECK_AMP_BY_LEVEL, 10.0, 1);
const AVATAR_SKILL_CRIT_DMG_BY_LEVEL = scaleSpecialArrayToLast(ABYSS_RING_NECK_AMP_BY_LEVEL, 150.0, 1);
const ENHANCEABLE_AVATAR_NAMES = new Set(["무기 아바타", "오라 아바타", "클론 레어 아바타"]);

function clampEnhanceLevel(level) {
	let lvl = parseInt(level) || 0;
	if (lvl < 0) lvl = 0;
	if (lvl > 20) lvl = 20;
	return lvl;
}

function isAbyssFragmentSpecialEquip(itemOrName) {
	let name = typeof itemOrName === "string" ? itemOrName : (itemOrName && itemOrName.name) || "";
	return name.includes("심연의 편린") && (name.includes("반지") || name.includes("목걸이") || name.includes("스태프"));
}

function isTranscendAbyssFragmentSpecialEquip(itemOrName) {
	let name = typeof itemOrName === "string" ? itemOrName : (itemOrName && itemOrName.name) || "";
	return name.includes("-초월-") && isAbyssFragmentSpecialEquip(name);
}

function isEnhanceableAvatarSpecialEquip(itemOrName) {
	let name = typeof itemOrName === "string" ? itemOrName : (itemOrName && itemOrName.name) || "";
	return ENHANCEABLE_AVATAR_NAMES.has(name);
}

function isEnhanceableSpecialEquip(item) {
	return !!(item && item.type === "special_equip" && (isAbyssFragmentSpecialEquip(item) || isEnhanceableAvatarSpecialEquip(item)));
}

function getSpecialEquipEnhanceCost(item) {
	if (!isEnhanceableSpecialEquip(item)) return 0;
	if (window.isTestCostMode) return 1;
	// 사진 기준: 강화비용 120C 골드 고정
	return 120 * Math.pow(10000, 2);
}

function formatNumberDecimal(num, decimals = 2) {
	return formatCompactNumber(num, 4);
}


const SHINING_EMBLEM_ATK_INC_BY_LEVEL = [10, 12, 15.6, 21.84, 32.76, 52.416, 89.1072];
const SHINING_EMBLEM_ALL_DMG_BY_LEVEL = [15, 18, 23.4, 32.76, 49.14, 78.624, 133.6608];

function calcSpecialEquipStats(item) {
	if (!item || item.type !== "special_equip") return null;
	const name = item.name || "";
	const lvl = clampEnhanceLevel(item.level);
	const st = {
		attack: 0,
		atkInc: 0,
		allDmgInc: 0,
		basicAtkDmgAmp: 0,
		basicCritDmgAmp: 0,
		skillDmgAmp: 0,
		skillCritChance: 0,
		skillCritDmg: 0,
		skillProcChanceInc: 0,
		skillCoefficientInc: 0,
		addSkillAtkMultAmp: 0,
		skillCooldownReductionInc: 0,
		allSkillDamageInc: 0,
		allBuffValueInc: 0,
		cloneCountInc: 0,
		cloneAttackSpeedInc: 0,
		maxAttackSpeedCapInc: 0,
	};

	if (isAbyssFragmentSpecialEquip(item)) {
		const isTranscend = isTranscendAbyssFragmentSpecialEquip(item);
		const attackTable = isTranscend ? TRANSCEND_SPECIAL_EQUIP_ATTACK_BY_LEVEL : SPECIAL_EQUIP_ATTACK_BY_LEVEL;
		const ampTable = isTranscend ? TRANSCEND_RING_NECK_AMP_BY_LEVEL : ABYSS_RING_NECK_AMP_BY_LEVEL;
		const staffMainTable = isTranscend ? TRANSCEND_STAFF_MAIN_BY_LEVEL : ABYSS_STAFF_MAIN_BY_LEVEL;
		const staffSubTable = isTranscend ? TRANSCEND_STAFF_SUB_BY_LEVEL : ABYSS_STAFF_SUB_BY_LEVEL;
		const staffBuffTable = isTranscend ? TRANSCEND_STAFF_BUFF_BY_LEVEL : ABYSS_STAFF_BUFF_BY_LEVEL;
		const staffCloneAspdTable = isTranscend ? TRANSCEND_STAFF_CLONE_ASPD_BY_LEVEL : ABYSS_STAFF_CLONE_ASPD_BY_LEVEL;
		const staffMaxAspdTable = isTranscend ? TRANSCEND_STAFF_MAX_ASPD_CAP_BY_LEVEL : ABYSS_STAFF_MAX_ASPD_CAP_BY_LEVEL;

		st.attack = attackTable[lvl];

		if (name.includes("반지")) {
			st.skillDmgAmp = ampTable[lvl];
			return st;
		}

		if (name.includes("목걸이")) {
			st.basicAtkDmgAmp = ampTable[lvl];
			return st;
		}

		if (name.includes("스태프")) {
			st.skillProcChanceInc = staffMainTable[lvl];
			st.skillCoefficientInc = staffMainTable[lvl];
			st.skillCooldownReductionInc = staffSubTable[lvl];
			st.allSkillDamageInc = staffSubTable[lvl];
			st.allBuffValueInc = staffBuffTable[lvl];
			st.cloneCountInc = ABYSS_STAFF_CLONE_COUNT_BY_LEVEL[lvl];
			st.cloneAttackSpeedInc = staffCloneAspdTable[lvl];
			st.maxAttackSpeedCapInc = staffMaxAspdTable[lvl];
			return st;
		}
	}

	if (isEnhanceableAvatarSpecialEquip(item)) {
		st.attack = AVATAR_ATTACK_BY_LEVEL[lvl];
		if (name === "무기 아바타") st.basicCritDmgAmp = AVATAR_AMP_BY_LEVEL[lvl];
		else if (name === "오라 아바타") st.addSkillAtkMultAmp = AVATAR_AMP_BY_LEVEL[lvl];
		else if (name === "클론 레어 아바타") {
			st.skillCritChance = AVATAR_SKILL_CRIT_CHANCE_BY_LEVEL[lvl];
			st.skillCritDmg = AVATAR_SKILL_CRIT_DMG_BY_LEVEL[lvl];
		}
		return st;
	}

	if (item.isEmblem || name.includes("빛나는 휘장")) {
		st.atkInc = SHINING_EMBLEM_ATK_INC_BY_LEVEL[lvl] || 0;
		st.allDmgInc = SHINING_EMBLEM_ALL_DMG_BY_LEVEL[lvl] || 0;
		return st;
	}

	if (item.isTalisman || name.includes("탈리스만")) {
		// 탈리스만 A/B는 스킬 레벨 증가 전용입니다.
		// 실제 효과는 combat-system.js와 render-ui.js에서 A/B 슬롯별로 적용됩니다.
		return st;
	}

	if (item.specialStats) {
		Object.keys(item.specialStats).forEach((key) => {
			st[key] = (st[key] || 0) + (parseFloat(item.specialStats[key]) || 0);
		});
	}

	return st;
}

// 기존 1~11티어 확정 강화 테이블. 12티어 이후도 강화 레벨 진행률로 사용한다.
const enhanceTable = [
	{ atk: 450, sdmg: 10.0, alldmg: 5.0 },
	{ atk: 460, sdmg: 10.1, alldmg: 5.1 },
	{ atk: 480, sdmg: 10.3, alldmg: 5.3 },
	{ atk: 510, sdmg: 10.6, alldmg: 5.6 },
	{ atk: 550, sdmg: 11.0, alldmg: 6.0 },
	{ atk: 600, sdmg: 11.5, alldmg: 6.5 },
	{ atk: 660, sdmg: 12.1, alldmg: 7.1 },
	{ atk: 730, sdmg: 12.8, alldmg: 7.8 },
	{ atk: 810, sdmg: 13.6, alldmg: 8.6 },
	{ atk: 900, sdmg: 14.5, alldmg: 9.5 },
	{ atk: 1000, sdmg: 15.5, alldmg: 10.5 },
	{ atk: 1190, sdmg: 17.1, alldmg: 11.7 },
	{ atk: 1470, sdmg: 19.3, alldmg: 13.1 },
	{ atk: 1840, sdmg: 22.1, alldmg: 14.7 },
	{ atk: 2300, sdmg: 25.5, alldmg: 16.5 },
	{ atk: 2850, sdmg: 29.5, alldmg: 18.5 },
	{ atk: 3490, sdmg: 34.1, alldmg: 20.7 },
	{ atk: 4220, sdmg: 39.3, alldmg: 23.1 },
	{ atk: 5040, sdmg: 45.1, alldmg: 25.7 },
	{ atk: 5950, sdmg: 51.5, alldmg: 28.5 },
	{ atk: 6950, sdmg: 58.5, alldmg: 31.5 },
];

const curveAtkInc = [0, 0.1, 0.2, 0.3, 0.5, 0.8, 1.1, 1.4, 1.8, 2.3, 2.8, 3.4, 4.1, 4.9, 5.8, 6.8, 7.9, 9.1, 10.4, 11.8, 13.25];
const curveSmult = [0, 0.1, 0.3, 0.6, 1.0, 1.5, 2.1, 2.8, 3.6, 4.5, 5.5, 7.0, 9.0, 11.5, 14.5, 18.0, 22.0, 26.5, 31.5, 37.0, 43.0];
const extraSmult = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 6, 10, 15, 21, 28, 36, 45, 55];

const KNOWN_HIGH_TIER_BASE_ATK_B = { 12: 4, 18: 49.4 };
const KNOWN_HIGH_TIER_ATK20_B = { 12: 69.1, 16: 369, 17: 560, 18: 851 };
const KNOWN_HIGH_TIER_ATK11_B = { 18: 141 };
const KNOWN_HIGH_TIER_SDMG20 = { 12: 607, 16: 2121 };
const KNOWN_HIGH_TIER_BASE_SMULT = { 12: 45450, 18: 104540 };
const KNOWN_HIGH_TIER_SMULT20 = { 12: 1057562, 16: 1957654, 17: 2097179 };
const KNOWN_HIGH_TIER_BASE_CRIT = { 12: 5809, 18: 35162 };
const KNOWN_HIGH_TIER_CRIT20 = { 17: 803447 };


// 12티어는 실측으로 확정된 전용 상수.
// 치명계수 공식: base + dSdmg * growth + extraSmult * extra
// dSdmg10은 dSdmg * 10 정수값으로, JS 소수점 오차를 피하기 위해 사용한다.
const EXACT_TIER_OPTION_CONFIG = {
	12: {
		baseAtk: 4 * UNIT_B,
		atk20: 69.1 * UNIT_B,
		baseSdmg: 120,
		baseAllDmg: 60,
		baseAtkInc: 65,
		baseNdmg: 275,
		baseSmult: 45450,
		smult20: 1057562,
		baseCrit: 5809,
		critGrowth: 3570,
		critExtra: 3,
	},
};

const dSdmg10 = [
	0, 1, 3, 6, 10,
	15, 21, 28, 36, 45,
	55, 71, 93, 121, 155,
	195, 241, 293, 351, 415,
	485,
];

function clampLevel(level) {
	let lvl = parseInt(level) || 0;
	if (lvl > 20) lvl = 20;
	if (lvl < 0) lvl = 0;
	return lvl;
}

function roundToRawB(valueB) {
	return Math.round(valueB * UNIT_B);
}

function expBetween(startVal, endVal, startTier, endTier, tier) {
	if (tier === startTier) return startVal;
	if (tier === endTier) return endVal;
	const ratio = Math.pow(endVal / startVal, 1 / (endTier - startTier));
	return startVal * Math.pow(ratio, tier - startTier);
}

function lagrangeInterpolate(points, x) {
	let total = 0;
	for (let i = 0; i < points.length; i++) {
		let [xi, yi] = points[i];
		let term = yi;
		for (let j = 0; j < points.length; j++) {
			if (i === j) continue;
			let [xj] = points[j];
			term *= (x - xj) / (xi - xj);
		}
		total += term;
	}
	return total;
}

function highTierBaseAtk(tier) {
	if (EXACT_TIER_OPTION_CONFIG[tier] && EXACT_TIER_OPTION_CONFIG[tier].baseAtk !== undefined) {
		return Math.round(EXACT_TIER_OPTION_CONFIG[tier].baseAtk);
	}
	if (KNOWN_HIGH_TIER_BASE_ATK_B[tier] !== undefined) return roundToRawB(KNOWN_HIGH_TIER_BASE_ATK_B[tier]);
	return roundToRawB(expBetween(4, 49.4, 12, 18, tier));
}

function highTierAtk20(tier) {
	if (EXACT_TIER_OPTION_CONFIG[tier] && EXACT_TIER_OPTION_CONFIG[tier].atk20 !== undefined) {
		return Math.round(EXACT_TIER_OPTION_CONFIG[tier].atk20);
	}
	if (KNOWN_HIGH_TIER_ATK20_B[tier] !== undefined) return roundToRawB(KNOWN_HIGH_TIER_ATK20_B[tier]);

	// 12→16은 69.1B, 369B를 지나는 기하성장.
	// 18 이후는 17→18 증가율로 외삽한다. 13티어 이상 실측값이 생기면 위 config에 넣어 정확값으로 고정한다.
	if (tier < 16) {
		return roundToRawB(expBetween(69.1, 369, 12, 16, tier));
	}
	if (tier > 18) {
		const r = 851 / 560;
		return roundToRawB(851 * Math.pow(r, tier - 18));
	}
	return roundToRawB(expBetween(369, 851, 16, 18, tier));
}

function highTierAtk11(tier, baseAtk, atk20) {
	if (KNOWN_HIGH_TIER_ATK11_B[tier] !== undefined) return roundToRawB(KNOWN_HIGH_TIER_ATK11_B[tier]);
	return baseAtk + Math.floor((atk20 - baseAtk) * (7.0 / 43.0));
}

function highTierBaseSmult(tier) {
	if (EXACT_TIER_OPTION_CONFIG[tier] && EXACT_TIER_OPTION_CONFIG[tier].baseSmult !== undefined) {
		return EXACT_TIER_OPTION_CONFIG[tier].baseSmult;
	}
	if (KNOWN_HIGH_TIER_BASE_SMULT[tier] !== undefined) return KNOWN_HIGH_TIER_BASE_SMULT[tier];
	return Math.round(expBetween(45450, 104540, 12, 18, tier));
}

function highTierSmult20(tier) {
	if (EXACT_TIER_OPTION_CONFIG[tier] && EXACT_TIER_OPTION_CONFIG[tier].smult20 !== undefined) {
		return EXACT_TIER_OPTION_CONFIG[tier].smult20;
	}
	if (KNOWN_HIGH_TIER_SMULT20[tier] !== undefined) return KNOWN_HIGH_TIER_SMULT20[tier];
	// 확정값 12,16,17을 모두 통과하는 2차 보간/외삽.
	return Math.round(lagrangeInterpolate([
		[12, 1057562],
		[16, 1957654],
		[17, 2097179],
	], tier));
}

function highTierBaseCrit(tier) {
	if (EXACT_TIER_OPTION_CONFIG[tier] && EXACT_TIER_OPTION_CONFIG[tier].baseCrit !== undefined) {
		return EXACT_TIER_OPTION_CONFIG[tier].baseCrit;
	}
	if (KNOWN_HIGH_TIER_BASE_CRIT[tier] !== undefined) return KNOWN_HIGH_TIER_BASE_CRIT[tier];
	// 11티어 0강 치명계수 4303과 18티어 35162를 잇는다.
	return Math.round(expBetween(4303, 35162, 11, 18, tier));
}

function highTierCrit20(tier) {
	if (KNOWN_HIGH_TIER_CRIT20[tier] !== undefined) return KNOWN_HIGH_TIER_CRIT20[tier];
	// 현재 확정된 17티어 20강 치명계수 비율을 유지한다.
	const base17 = highTierBaseCrit(17);
	const ratio = KNOWN_HIGH_TIER_CRIT20[17] / base17;
	return Math.round(highTierBaseCrit(tier) * ratio);
}

function highTierBaseAtkInc(tier) {
	if (EXACT_TIER_OPTION_CONFIG[tier] && EXACT_TIER_OPTION_CONFIG[tier].baseAtkInc !== undefined) {
		return EXACT_TIER_OPTION_CONFIG[tier].baseAtkInc;
	}
	if (tier <= 16) return 5 * tier + 5;
	return parseFloat((85 + (tier - 16) * 4.6).toFixed(1));
}

function highTierBaseNdmg(tier) {
	if (EXACT_TIER_OPTION_CONFIG[tier] && EXACT_TIER_OPTION_CONFIG[tier].baseNdmg !== undefined) {
		return EXACT_TIER_OPTION_CONFIG[tier].baseNdmg;
	}
	return 25 * tier - 25;
}

function highTierBaseSdmg(tier) {
	if (EXACT_TIER_OPTION_CONFIG[tier] && EXACT_TIER_OPTION_CONFIG[tier].baseSdmg !== undefined) {
		return EXACT_TIER_OPTION_CONFIG[tier].baseSdmg;
	}
	return 10 * tier;
}

function highTierSdmg20(tier) {
	if (KNOWN_HIGH_TIER_SDMG20[tier] !== undefined) return KNOWN_HIGH_TIER_SDMG20[tier];
	// 확정 +20 기준 12→16의 단계별 비율을 사이 단계와 이후 단계에도 유지한다.
	return parseFloat(expBetween(
		KNOWN_HIGH_TIER_SDMG20[12],
		KNOWN_HIGH_TIER_SDMG20[16],
		12,
		16,
		tier,
	).toFixed(1));
}

function highTierBaseAllDmg(tier) {
	if (EXACT_TIER_OPTION_CONFIG[tier] && EXACT_TIER_OPTION_CONFIG[tier].baseAllDmg !== undefined) {
		return EXACT_TIER_OPTION_CONFIG[tier].baseAllDmg;
	}
	return 5 * tier;
}

function getEquipGroup(item) {
	if (item.equipGroup) return item.equipGroup;
	if (item.baseSdmg || item.baseAllDmg) return "skill_all";
	if (item.baseAtkInc) return "atk_inc";
	if (item.baseNdmg) return "normal_dmg";
	if (item.baseSmult || item.baseSchance) return "skill_chance";
	if (item.baseNcDmg || item.baseNcRate) return "normal_crit";
	return "unknown";
}

function getHighTierBaseByGroup(tier, group) {
	if (group === "skill_all") return { baseSdmg: highTierBaseSdmg(tier), baseAllDmg: highTierBaseAllDmg(tier) };
	if (group === "atk_inc") return { baseAtkInc: highTierBaseAtkInc(tier) };
	if (group === "normal_dmg") return { baseNdmg: highTierBaseNdmg(tier) };
	if (group === "skill_chance") return { baseSchance: 20, baseSmult: highTierBaseSmult(tier) };
	if (group === "normal_crit") return { baseNcRate: 35, baseNcDmg: highTierBaseCrit(tier) };
	return {};
}

function calcItemStats(item) {
	if (!item || item.type === "skill_book" || item.type === "special_equip") return null;

	let lvl = clampLevel(item.level);
	let st = { ...item };
	let tier = parseInt(item.tier) || 1;
	let group = getEquipGroup(item);

	if (tier >= 12) {
		st = { ...st, ...getHighTierBaseByGroup(tier, group) };
		// 12티어 이상은 bosses.js의 임시 baseAtk가 남아 있어도 공식 기준값으로 강제 보정한다.
		st.baseAtk = highTierBaseAtk(tier);
	}

	let baseEnhanceAtk = enhanceTable[lvl] && enhanceTable[lvl].atk ? enhanceTable[lvl].atk : 450;
	let baseEnhanceSdmg = enhanceTable[lvl] && enhanceTable[lvl].sdmg ? enhanceTable[lvl].sdmg : 10.0;
	let baseEnhanceAlldmg = enhanceTable[lvl] && enhanceTable[lvl].alldmg ? enhanceTable[lvl].alldmg : 5.0;

	let dAtk = baseEnhanceAtk - 450;
	let dSdmg = baseEnhanceSdmg - 10.0;
	let dAlldmg = baseEnhanceAlldmg - 5.0;

	// 18티어 20강 평타피해 7506%를 만족시키는 기존 고강화 보정.
	if (lvl === 20) dSdmg = 48.5;

	// 1. 기본 공격력
	if (item.enhanceStats) {
		st.attack = item.enhanceStats[lvl];
	} else if (tier >= 12) {
		const t0 = st.baseAtk || highTierBaseAtk(tier);
		const t20 = highTierAtk20(tier);
		const t11 = highTierAtk11(tier, t0, t20);

		if (lvl === 0) st.attack = t0;
		else if (lvl <= 11) st.attack = t0 + Math.floor((t11 - t0) * (curveSmult[lvl] / 7.0));
		else st.attack = t11 + Math.floor((t20 - t11) * ((curveSmult[lvl] - 7.0) / 36.0));
	} else {
		let atkMult = Math.pow(1.52, tier - 1);
		st.attack = (item.baseAtk || 0) + Math.floor(dAtk * atkMult);
	}

	// 2. 스킬 피해 증가 & 모든 피해 증가
	if (st.baseSdmg || st.baseAllDmg) {
		let sdmgMult = 1.0 + 0.6 * (tier - 1);
		let alldmgMult = 1.0 + 0.3 * (tier - 1);
		if (st.baseSdmg && tier >= 12) {
			// +0 기본값은 유지하고, 기존 강화표 진행률로 해당 단계의 확정/보간 +20 목표까지 올린다.
			const progress = dSdmg10[lvl] / dSdmg10[20];
			const target20 = highTierSdmg20(tier);
			st.skillDmgInc = parseFloat((st.baseSdmg + (target20 - st.baseSdmg) * progress).toFixed(1));
		} else {
			st.skillDmgInc = st.baseSdmg ? parseFloat((st.baseSdmg + dSdmg * sdmgMult).toFixed(1)) : 0;
		}
		st.allDmgInc = st.baseAllDmg ? parseFloat((st.baseAllDmg + dAlldmg * alldmgMult).toFixed(1)) : 0;
	} else {
		st.skillDmgInc = 0;
		st.allDmgInc = 0;
	}

	// 3. 평타 피해 증가
	if (st.baseNdmg) {
		let ndmgMult = 10 + 8 * (tier - 1);
		st.basicAtkDmgInc = parseFloat((st.baseNdmg + dSdmg * ndmgMult).toFixed(1));
	} else {
		st.basicAtkDmgInc = 0;
	}

	// 4. 공격력 추가증가
	if (st.baseAtkInc) {
		if (tier === 6) {
			const t6AtkInc = [0, 0.4, 0.9, 1.8, 3.0, 4.5, 6.3, 8.4, 10.8, 13.5, 16.5, 20.1, 24.3, 29.1, 34.5, 40.5, 47.1, 54.3, 62.1, 70.0, 79.0];
			st.atkInc = parseFloat((st.baseAtkInc + t6AtkInc[lvl]).toFixed(1));
		} else if (tier === 7) {
			const t7AtkInc = [0, 0.5, 1.1, 2.2, 3.6, 5.4, 7.5, 10.0, 12.8, 15.9, 19.3, 23.5, 28.4, 34.0, 40.3, 47.3, 55.0, 63.4, 72.5, 82.3, 92.8];
			st.atkInc = parseFloat((st.baseAtkInc + t7AtkInc[lvl]).toFixed(1));
		} else if (tier >= 8) {
			let extraScale = tier - 8;
			st.atkInc = parseFloat((st.baseAtkInc + curveAtkInc[lvl] * extraScale + curveSmult[lvl] * 4 - extraSmult[lvl] * 1.2).toFixed(1));
		} else {
			st.atkInc = parseFloat((st.baseAtkInc + curveAtkInc[lvl] * tier).toFixed(1));
		}
	} else {
		st.atkInc = 0;
	}

	// 5. 추가 스킬공격 계수
	st.addSkillAtkChance = st.baseSchance || 0;
	if (st.baseSmult) {
		if (tier === 6) {
			const t6SmultDelta = [0, 517, 1391, 2702, 4450, 6635, 9257, 12316, 15812, 19745, 24115, 30672, 39416, 50347, 63465, 78770, 96262, 115941, 137807, 161860, 188100];
			st.addSkillAtkMult = st.baseSmult + t6SmultDelta[lvl];
		} else if (tier === 7) {
			const t7SmultDelta = [0, 915, 1830, 3600, 5960, 8910, 12450, 16580, 21300, 26610, 32510, 41362, 53166, 67922, 85630, 106290, 129902, 156466, 185982, 218450, 253870];
			st.addSkillAtkMult = st.baseSmult + t7SmultDelta[lvl];
		} else if (tier >= 12) {
			const t20 = highTierSmult20(tier);
			st.addSkillAtkMult = Math.round(st.baseSmult + (t20 - st.baseSmult) * (curveSmult[lvl] / 43.0));
		} else if (tier >= 8) {
			const smultBases = { 8: { m: 7970, extraWeight: 1 }, 9: { m: 10760, extraWeight: 1 }, 10: { m: 14530, extraWeight: -1 }, 11: { m: 19610, extraWeight: 2 } };
			let conf = smultBases[tier];
			st.addSkillAtkMult = Math.round(st.baseSmult + curveSmult[lvl] * conf.m + extraSmult[lvl] * conf.extraWeight);
		} else {
			const smultMults = [0, 1000, 1333.33, 1820, 2400, 3200, 4200, 5400];
			let m = smultMults[tier] || 0;
			let extra = tier <= 3 ? extraSmult[lvl] : 0;
			st.addSkillAtkMult = Math.round(st.baseSmult + curveSmult[lvl] * m + extra);
		}
	} else {
		st.addSkillAtkMult = 0;
	}

	// 6. 평타 치명타 계수
	st.basicCritChance = st.baseNcRate || 0;
	if (st.baseNcDmg) {
		if (tier === 6) {
			const t6CritDelta = [0, 100, 237, 414, 650, 945, 1299, 1712, 2184, 2715, 3305, 4249, 5547, 7199, 9205, 11565, 14279, 17347, 20760, 24545, 28675];
			st.basicCritDmg = st.baseNcDmg + t6CritDelta[lvl];
		} else if (tier === 7) {
			const t7CritDelta = [0, 95, 335, 575, 895, 1295, 1775, 2335, 2975, 3695, 4495, 5773, 7529, 9763, 12475, 15665, 19333, 23479, 28103, 33205, 38785];
			st.basicCritDmg = st.baseNcDmg + t7CritDelta[lvl];
		} else if (tier === 12) {
			const conf = EXACT_TIER_OPTION_CONFIG[12];
			st.basicCritDmg = Math.round(conf.baseCrit + (dSdmg10[lvl] * conf.critGrowth) / 10 + extraSmult[lvl] * conf.critExtra);
		} else if (tier >= 13) {
			const t20 = highTierCrit20(tier);
			st.basicCritDmg = Math.round(st.baseNcDmg + (t20 - st.baseNcDmg) * (curveSmult[lvl] / 43.0));
		} else if (tier >= 8) {
			const critBases = { 8: { m: 1060, curveWeight: 20, extraWeight: 0 }, 9: { m: 1430, curveWeight: 20, extraWeight: 0 }, 10: { m: 1960, curveWeight: 0, extraWeight: 1 }, 11: { m: 2650, curveWeight: 0, extraWeight: -1 } };
			let conf = critBases[tier];
			st.basicCritDmg = Math.round(st.baseNcDmg + dSdmg * conf.m + curveSmult[lvl] * conf.curveWeight + extraSmult[lvl] * conf.extraWeight);
		} else {
			const ncDmgMults = [0, 80, 160, 240, 320, 420, 600, 1000];
			const kVals = [0, 0, 0, 0, 3, 20, 0, 0];
			const offsetVals = [0, 0, 0, 90, 8, 11, 0, 0];
			let m = ncDmgMults[tier] || 0;
			let k = kVals[tier] || 0;
			let offset = offsetVals[tier] || 0;
			st.basicCritDmg = Math.round(st.baseNcDmg + offset + dSdmg * m + curveSmult[lvl] * k);
		}
	} else {
		st.basicCritDmg = 0;
	}

	st.ilv = (st.baseIlv || 1) + lvl;
	if (lvl === 20) st.ilv += 9;

	return st;
}

function getEnhanceCost(item) {
	if (!item || item.type === "skill_book") return 0;
	if (item.type === "special_equip") return getSpecialEquipEnhanceCost(item);
	if (window.isTestCostMode) return 1;
	return item.baseCost || 20000;
}

function getBaseEnhanceProb(level, item = null) {
	let lvl = parseInt(level) || 0;
	// 일반장비와 특수장비 모두 동일한 강화확률을 사용한다.
	if (lvl < 3) return 1.0;
	if (lvl < 6) return 0.3;
	if (lvl < 9) return 0.12;
	if (lvl < 14) return 0.018;
	if (lvl < 20) return 0.005;
	return 0;
}

function getEnhanceProb(level, item = null) {
	let prob = getBaseEnhanceProb(level, item);
	let t = getTotals();
	prob *= 1 + t.enhanceInc / 100;
	return Math.min(prob, 1.0);
}

function addPercentMultiplicative(currentInc, addedInc) {
	return (1 + (currentInc || 0) / 100) * (1 + (addedInc || 0) / 100) * 100 - 100;
}

function getTotals() {
	let t = {
		attack: getBaseAttackByAttackSpeed() + (player.farmAtkBonus || 0),
		atkInc: 0,
		aspd: getClampedFieldAttackSpeed(),
		basicAtkDmgInc: player.basicAtkDmgInc || 0,
		skillDmgInc: player.skillDmgInc || 0,
		allDmgInc: player.allDmgInc || 0,
		addSkillAtkChance: player.addSkillAtkChance || 0,
		addSkillAtkMult: player.addSkillAtkMult || 0,
		basicCritChance: player.basicCritChance || 0,
		basicCritDmg: player.basicCritDmg || 0,
		skillCritChance: player.skillCritChance || 0,
		skillCritDmg: player.skillCritDmg || 0,
		basicAtkDmgAmp: 0,
		basicCritDmgAmp: 0,
		skillDmgAmp: 0,
		skillProcChanceInc: 0,
		skillCoefficientInc: 0,
		addSkillAtkMultAmp: 0,
		skillCooldownReductionInc: 0,
		allSkillDamageInc: 0,
		allBuffValueInc: 0,
		cloneCountInc: 0,
		cloneAttackSpeedInc: 0,
		maxAttackSpeedCapInc: 0,
		goldInc: window.isTestBuffMode ? 400 : 0,
		dropInc: window.isTestBuffMode ? 400 : 0,
		enhanceInc: window.isTestBuffMode ? 400 : 0,
		farmGainInc: window.isTestBuffMode ? 400 : 0,
	};

	const codexBonusInc = getCodexCompletionBonusPercent();
	t.codexBonusInc = codexBonusInc;
	t.goldInc += codexBonusInc;
	t.dropInc += codexBonusInc;
	t.enhanceInc += codexBonusInc;
	t.farmGainInc += codexBonusInc;

	let equipAttackTotal = 0;
	if (player.equipment && Array.isArray(player.equipment)) {
		player.equipment.forEach((item) => {
			if (!item || item.type === "skill_book") return;

			if (item.type === "special_equip") {
				let sp = calcSpecialEquipStats(item);
				if (sp) {
					equipAttackTotal += sp.attack || 0;
					t.atkInc += sp.atkInc || 0;
					t.allDmgInc += sp.allDmgInc || 0;
					t.basicAtkDmgAmp += sp.basicAtkDmgAmp || 0;
					t.basicCritDmgAmp = addPercentMultiplicative(t.basicCritDmgAmp, sp.basicCritDmgAmp || 0);
					t.skillDmgAmp += sp.skillDmgAmp || 0;
					t.skillCritChance += sp.skillCritChance || 0;
					t.skillCritDmg += sp.skillCritDmg || 0;
					t.skillProcChanceInc = addPercentMultiplicative(t.skillProcChanceInc, sp.skillProcChanceInc || 0);
					t.skillCoefficientInc = addPercentMultiplicative(t.skillCoefficientInc, sp.skillCoefficientInc || 0);
					t.addSkillAtkMultAmp = addPercentMultiplicative(t.addSkillAtkMultAmp, sp.addSkillAtkMultAmp || 0);
					t.skillCooldownReductionInc = addPercentMultiplicative(t.skillCooldownReductionInc, sp.skillCooldownReductionInc || 0);
					t.allSkillDamageInc = addPercentMultiplicative(t.allSkillDamageInc, sp.allSkillDamageInc || 0);
					t.allBuffValueInc = addPercentMultiplicative(t.allBuffValueInc, sp.allBuffValueInc || 0);
					t.cloneCountInc += sp.cloneCountInc || 0;
					t.cloneAttackSpeedInc = addPercentMultiplicative(t.cloneAttackSpeedInc, sp.cloneAttackSpeedInc || 0);
					t.maxAttackSpeedCapInc = addPercentMultiplicative(t.maxAttackSpeedCapInc, sp.maxAttackSpeedCapInc || 0);
				}
				return;
			}

			let st = calcItemStats(item);
			if (st) {
				equipAttackTotal += st.attack || 0;
				t.atkInc += st.atkInc || 0;
				t.basicAtkDmgInc += st.basicAtkDmgInc || 0;
				t.skillDmgInc += st.skillDmgInc || 0;
				t.allDmgInc += st.allDmgInc || 0;
				t.addSkillAtkChance += st.addSkillAtkChance || 0;
				t.addSkillAtkMult += st.addSkillAtkMult || 0;
				t.basicCritChance += st.basicCritChance || 0;
				t.basicCritDmg += st.basicCritDmg || 0;
			}
		});
	}

	t.rawBasicAtkDmgInc = t.basicAtkDmgInc;
	t.rawSkillDmgInc = t.skillDmgInc;
	t.basicAtkDmgInc *= 1 + t.basicAtkDmgAmp / 100;
	t.skillDmgInc *= 1 + t.skillDmgAmp / 100;
	t.basicCritDmg *= 1 + t.basicCritDmgAmp / 100;
	t.addSkillAtkMult *= 1 + t.addSkillAtkMultAmp / 100;

	t.equipAttack = equipAttackTotal;
	t.attack += equipAttackTotal;
	t.attack = Math.floor(t.attack * (1 + t.atkInc / 100));

	t.basicCritChance = Math.min(50.0, t.basicCritChance);
	t.skillCritChance = Math.min(50.0, t.skillCritChance);
	t.addSkillAtkChance = Math.min(30.0, t.addSkillAtkChance);

	if (activeBuffs && activeBuffs.ironStrike && activeBuffs.ironStrike.active) t.allDmgInc += 1;

	let speedMultiplier = 1 + t.aspd / 100;
	if (speedMultiplier < 0.1) speedMultiplier = 0.1;
	t.aspdMs = Math.max(560 / speedMultiplier, 100);

	return t;
}

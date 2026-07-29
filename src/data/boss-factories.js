/*
 * boss-factories.js
 *
 * 12티어 이상 고티어 보스와 장비 드랍 원본을 생성하는 팩토리 함수입니다.
 * bosses.js가 너무 커지는 것을 막기 위해 계산형 생성 로직만 분리했습니다.
 *
 * 백엔드/DB 이전 시 참고:
 * - 여기서 계산되는 baseAtk/baseCost/baseIlv 같은 값은 나중에 seed 데이터로 고정 저장할 수 있습니다.
 * - 운영 중 관리자 페이지에서 수정하려면 최종 결과값을 PostgreSQL item_templates/drop_tables로 옮기면 됩니다.
 */

/*
 * bosses.js rebuilt
 * - 1~11티어: 기존 확정 보스/장비 데이터 보존
 * - 12티어 이상(현재 메타 39까지): stat-system.js의 고단계 공식과 같은 +0 기준값을 장비 base로 주입
 * - 1B = 10000 raw
 */

const bossModelUnitB = 10000;

function bossRoundB(valueB) {
	return Math.round(valueB * bossModelUnitB);
}

function bossExpBetween(startVal, endVal, startTier, endTier, tier) {
	if (tier === startTier) return startVal;
	if (tier === endTier) return endVal;
	const ratio = Math.pow(endVal / startVal, 1 / (endTier - startTier));
	return startVal * Math.pow(ratio, tier - startTier);
}

const bossKnownBaseAtkB = { 12: 4, 18: 49.4 };
const bossKnownBaseSmult = { 12: 45450, 18: 104540 };
const bossKnownBaseCrit = { 12: 5809, 18: 35162 };

function bossHighBaseAtk(tier) {
	if (bossKnownBaseAtkB[tier] !== undefined) return bossRoundB(bossKnownBaseAtkB[tier]);
	return bossRoundB(bossExpBetween(4, 49.4, 12, 18, tier));
}

function bossHighBaseSmult(tier) {
	if (bossKnownBaseSmult[tier] !== undefined) return bossKnownBaseSmult[tier];
	return Math.round(bossExpBetween(45450, 104540, 12, 18, tier));
}

function bossHighBaseCrit(tier) {
	if (bossKnownBaseCrit[tier] !== undefined) return bossKnownBaseCrit[tier];
	return Math.round(bossExpBetween(4303, 35162, 11, 18, tier));
}

function bossHighBaseAtkInc(tier) {
	if (tier <= 16) return 5 * tier + 5;
	return parseFloat((85 + (tier - 16) * 4.6).toFixed(1));
}

function bossHighBaseNdmg(tier) {
	return 25 * tier - 25;
}

function bossHighBaseCost(tier) {
	return Math.round(8e7 * Math.pow(3.2, tier - 15));
}

function bossHighBaseIlv(tier) {
	return 331 + (tier - 12) * 30;
}

function makeHighNormalDrop(tier, name, group, imgText) {
	const common = {
		name,
		type: "normal",
		tier,
		img: `https://placehold.co/64x64/333/FFF?text=${imgText}`,
		baseAtk: bossHighBaseAtk(tier),
		equipGroup: group,
		equipLimit: group === "skill_chance" || group === "normal_crit" ? 2 : 1,
		baseCost: bossHighBaseCost(tier),
		baseIlv: bossHighBaseIlv(tier),
	};
	const localIconUrl = typeof getNormalEquipmentIconUrl === "function"
		? getNormalEquipmentIconUrl(common)
		: "";
	if (localIconUrl) common.img = localIconUrl;

	if (group === "skill_all") {
		common.baseSdmg = 10 * tier;
		common.baseAllDmg = 5 * tier;
		common.equipText = "무기(스킬피해 및 모든피해)";
	}
	if (group === "atk_inc") {
		common.baseAtkInc = bossHighBaseAtkInc(tier);
		common.equipText = "무기(공격력 추가)";
	}
	if (group === "normal_dmg") {
		common.baseNdmg = bossHighBaseNdmg(tier);
		common.equipText = "무기(평타피해)";
	}
	if (group === "skill_chance") {
		common.baseSchance = 20;
		common.baseSmult = bossHighBaseSmult(tier);
		common.equipText = "무기(추가스킬피해)";
	}
	if (group === "normal_crit") {
		common.baseNcRate = 35;
		common.baseNcDmg = bossHighBaseCrit(tier);
		common.equipText = "무기(평타 치명타)";
	}
	return common;
}

function makeHighTalisman(tier, name) {
	const cleanName = name.replace(/\s*\+0$/, "");
	const slotIdx = cleanName.includes("영롱") || cleanName.includes("초월") ? 13 : 12;
	return {
		name: cleanName,
		type: "special_equip",
		tier,
		isTalisman: true,
		specialSlotIdx: slotIdx,
		img: getSpecialEquipIconUrl({ name: cleanName, isTalisman: true }),
		sellPrice: 0,
	};
}

function makeHighEmblem(tier, name, dropRate) {
	return {
		name: name.replace(/\s*\+0$/, ""),
		type: "special_equip",
		tier,
		isEmblem: true,
		specialSlotIdx: 14,
		individualDropRate: dropRate,
		img: getSpecialEquipIconUrl({ name, isEmblem: true }),
		sellPrice: 0,
	};
}

function makeHighBoss(meta) {
	const tier = meta.id;
	const groups = ["skill_all", "atk_inc", "normal_dmg", "skill_chance", "normal_crit"];
	const drops = groups.map((group, idx) => makeHighNormalDrop(tier, meta.dropNames[idx], group, `T${tier}-${idx + 1}`));

	if (meta.talismanName) {
		drops.push(makeHighTalisman(tier, meta.talismanName));
	}
	if (meta.emblemName) {
		drops.push(makeHighEmblem(tier, meta.emblemName, meta.emblemDropRate));
	}

	return {
		id: tier,
		isSpecial: false,
		name: meta.name,
		title: meta.title,
		desc1: `보스존에 ${meta.name}가 등장합니다.`,
		desc2: "#이미 소환된 보스가 있으면 소환되지 않습니다.",
		desc3: "#특수보스가 우선 소환됩니다.",
		dropTitle: "",
		dropsList: drops.map((drop) => {
			const isLevelZeroDisplay = drop && drop.type === "special_equip" && (drop.isTalisman || drop.isEmblem || (drop.name && (drop.name.includes("탈리스만") || drop.name.includes("빛나는 휘장"))));
			const displayName = isLevelZeroDisplay && !/\+\d+$/.test(drop.name) ? `${drop.name} +0` : drop.name;
			return `*${displayName}`;
		}),
		reqLvl: meta.reqLvl,
		img: meta.img,
		maxHp: meta.maxHp,
		equipDropRate: meta.equipDropRate !== undefined ? meta.equipDropRate : 0.02,
		skillDropRate: meta.skillDropRate !== undefined ? meta.skillDropRate : 0,
		talismanDropRate: meta.talismanDropRate || 0,
		emblemDropRate: meta.emblemDropRate || 0,
		dropRateDoubled: !!meta.dropRateDoubled,
		drops,
	};
}

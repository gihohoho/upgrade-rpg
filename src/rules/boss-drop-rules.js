/*
 * boss-drop-rules.js
 *
 * 보스 드랍률 보정과 최초 장비 보너스 지급 규칙입니다.
 * 기존 bosses.js에 섞여 있던 게임 규칙을 분리했습니다.
 *
 * 백엔드 이전 시 참고:
 * - 드랍 확률 계산, 최초 보너스 지급, Math.random() 사용 영역은 최종적으로 FastAPI 서버에서 처리해야 합니다.
 * - 현재는 기존 프론트 게임 동작을 유지하기 위해 함수 이름과 동작을 보존합니다.
 */

const BOSS_DROP_RATE_MULTIPLIER = 2;

function getNormalBossSkillDropRate(boss) {
	if (!boss || boss.skillDropRate <= 0) return 0;
	if (boss.isSpecial) return boss.skillDropRate;

	// 기존 일반보스 50% 보정에 더해 T1~T9 구간은 한 번 더 절반으로 낮춥니다.
	const multiplier = boss.id >= 1 && boss.id <= 9 ? 0.25 : 0.5;
	return boss.skillDropRate * multiplier;
}

function isFirstEquipSkillGuaranteeBoss(boss) {
	return !!(boss && !boss.isSpecial && boss.id >= 2 && boss.id <= 7);
}

function shouldGrantFirstEquipSkillBook(boss) {
	if (!isFirstEquipSkillGuaranteeBoss(boss)) return false;
	if (!player.firstEquipSkillDropGiven || typeof player.firstEquipSkillDropGiven !== "object") {
		player.firstEquipSkillDropGiven = {};
	}
	return !player.firstEquipSkillDropGiven[boss.id];
}

function markFirstEquipSkillBookGranted(boss) {
	if (!player.firstEquipSkillDropGiven || typeof player.firstEquipSkillDropGiven !== "object") {
		player.firstEquipSkillDropGiven = {};
	}
	player.firstEquipSkillDropGiven[boss.id] = true;
}

function grantFirstEquipSkillBookIfNeeded(boss, skillDrops, actionResult) {
	if (!shouldGrantFirstEquipSkillBook(boss) || !skillDrops || skillDrops.length === 0) return false;

	let randomSkill = skillDrops[Math.floor(Math.random() * skillDrops.length)];
	let result = typeof addStackableItemToInventory === "function"
		? addStackableItemToInventory(randomSkill)
		: null;

	if (result && result.ok) {
		markFirstEquipSkillBookGranted(boss);
		const message = result.stacked
			? `🎉 [최초 장비 보너스] ${result.item.name} 추가 획득! (현재 겹침: ${result.item.count}개)`
			: `🎉 [최초 장비 보너스] ${result.item.name} 추가 획득!`;
		if (actionResult && typeof addDropAward === "function") addDropAward(actionResult, result.item.name, message, { stacked: result.stacked, dropType: "first_equip_skill_book" });
		else {
			addLog(message, true);
			showItemDropText(result.item.name);
		}
		return true;
	}

	// 장비 획득으로 가방이 꽉 찬 경우에도 보장 드랍이 사라지지 않도록 보관함으로 보냅니다.
	if (player.storage && hasEmptyItemSlot(player.storage, player.maxStorageSize)) {
		const storedSkill = { ...randomSkill, id: Date.now() + 5, count: randomSkill.count || 1 };
		placeItemInFirstEmptySlot(player.storage, storedSkill, player.maxStorageSize);
		if (typeof recordItemAcquired === "function") recordItemAcquired(storedSkill);
		markFirstEquipSkillBookGranted(boss);
		const message = `🎉 [최초 장비 보너스] ${randomSkill.name} 추가 획득! (가방이 꽉 차 보관함으로 이동)`;
		if (actionResult && typeof addDropAward === "function") addDropAward(actionResult, randomSkill.name, message, { stored: true, dropType: "first_equip_skill_book" });
		else {
			addLog(message, true);
			showItemDropText(randomSkill.name);
		}
		return true;
	}

	const message = `[시스템] 가방과 보관함이 모두 꽉 차서 최초 장비 보너스 스킬강화권을 받을 수 없습니다. 다음 장비 드랍 때 다시 지급됩니다.`;
	if (actionResult && typeof addBlockedReward === "function") addBlockedReward(actionResult, message, "inventory_and_storage_full");
	else addLog(message);
	return false;
}

const SPECIAL_BOSS_DROP_RATE_CONFIG = {
	101: { equip: 0.0225, skill: 0.0188 },
	102: { equip: 0.0075, skill: 0.0075 },
	103: { equip: 0.0030, skill: 0 },
	104: { equip: 0.0050, skill: 0.0020 },
	105: { equip: 0.0015, skill: 0 },
	106: { equip: 0.0050, skill: 0 },
};

function applyNormalBossDropRates() {
	bossList.forEach((boss) => {
		if (boss.equipDropRate === undefined) boss.equipDropRate = boss.id <= 2 ? (boss.id === 1 ? 0.04 : 0.03) : 0.02;
		if (boss.skillDropRate === undefined) boss.skillDropRate = boss.id <= 2 ? (boss.id === 1 ? 0.04 : 0.03) : boss.id >= 10 ? 0 : 0.02;

		if (!boss.dropRateDoubled) {
			boss.equipDropRate = Math.min(1, boss.equipDropRate * BOSS_DROP_RATE_MULTIPLIER);
			boss.skillDropRate = Math.min(1, boss.skillDropRate * BOSS_DROP_RATE_MULTIPLIER);
			if (boss.talismanDropRate) boss.talismanDropRate = Math.min(1, boss.talismanDropRate * BOSS_DROP_RATE_MULTIPLIER);
			if (boss.emblemDropRate) boss.emblemDropRate = Math.min(1, boss.emblemDropRate * BOSS_DROP_RATE_MULTIPLIER);
			boss.drops.forEach((drop) => {
				if (drop.individualDropRate) drop.individualDropRate = Math.min(1, drop.individualDropRate * BOSS_DROP_RATE_MULTIPLIER);
			});
			boss.dropRateDoubled = true;
		}

		let equipStr = (boss.equipDropRate * 100).toFixed(2);
		let skillStr = getNormalBossSkillDropRate(boss) > 0 ? (getNormalBossSkillDropRate(boss) * 100).toFixed(2) : "0.00";
		let taliStr = boss.talismanDropRate ? (boss.talismanDropRate * 100).toFixed(2) : "0.00";
		let emblemStr = boss.emblemDropRate ? (boss.emblemDropRate * 100).toFixed(2) : "0.00";

		boss.dropTitle = `[획득 가능 아이템]`;
		boss.dropsList = boss.dropsList.map((item) => {
			if (item.includes("스킬강화권")) return item + ` (${skillStr}%)`;
			if (item.includes("탈리스만")) return item + ` (${taliStr}%)`;
			if (item.includes("빛나는 휘장")) return item + ` (${emblemStr}%)`;
			return item + ` (${equipStr}%)`;
		});

		boss.drops.forEach((drop) => {
			if (!drop.tier) drop.tier = boss.id;
		});
	});
}

function applySpecialBossDropRates() {
	specialBossList.forEach((boss) => {
		const conf = SPECIAL_BOSS_DROP_RATE_CONFIG[boss.id] || { equip: 0.02, skill: 0 };
		boss.equipDropRate = Math.min(1, conf.equip * BOSS_DROP_RATE_MULTIPLIER);
		boss.skillDropRate = Math.min(1, conf.skill * BOSS_DROP_RATE_MULTIPLIER);
		boss.drops.forEach((drop) => {
			if (drop.individualDropRate) drop.individualDropRate = Math.min(1, drop.individualDropRate * BOSS_DROP_RATE_MULTIPLIER);
		});

		let equipStr = (boss.equipDropRate * 100).toFixed(2);
		let skillStr = (boss.skillDropRate * 100).toFixed(2);

		boss.dropTitle = `[획득 가능 아이템]`;
		boss.dropsList = boss.dropsList.map((item) => {
			if (item.includes("스킬강화권")) return item + ` (${skillStr}%)`;
			return item + ` (${equipStr}%)`;
		});
	});
}

function applyBossDropRates() {
	applyNormalBossDropRates();
	applySpecialBossDropRates();
}

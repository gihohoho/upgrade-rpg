/**
 * Action Result System
 * -----------------------------------------------------------------------------
 * 백엔드 분리 준비용 결과 객체 유틸입니다.
 *
 * 기존 프론트 전용 함수들은 계산/상태 변경/화면 갱신을 한 함수 안에서 같이 처리했습니다.
 * FastAPI로 옮기려면 서버가 "결과 객체"를 반환하고, 프론트는 그 결과를 화면에 표시하는
 * 구조가 필요합니다. 이 파일은 그 중간 단계로, 기존 동작은 유지하면서 전투/강화 결과를
 * API 응답에 가까운 형태로 모으기 위해 사용합니다.
 */

function createGameActionResult(type, payload = {}) {
	return {
		ok: true,
		type,
		payload,
		logs: [],
		effects: [],
		ui: {},
		data: {},
		createdAt: Date.now(),
	};
}

function failGameActionResult(type, message, payload = {}) {
	const result = createGameActionResult(type, payload);
	result.ok = false;
	if (message) result.logs.push({ message, important: false });
	return result;
}


function createItemEquipResult(payload = {}) {
	const result = createGameActionResult("item.equip", payload);
	result.data.itemName = payload.itemName || null;
	result.data.slotType = payload.slotType || null;
	result.data.slotIndex = payload.slotIndex;
	return result;
}

function createItemUnequipResult(payload = {}) {
	const result = createGameActionResult("item.unequip", payload);
	result.data.itemName = payload.itemName || null;
	result.data.slotIndex = payload.slotIndex;
	return result;
}

function createSkillBookUseResult(payload = {}) {
	const result = createGameActionResult("skill_book.use", payload);
	result.data.itemName = payload.itemName || null;
	result.data.skillKey = payload.skillKey || null;
	return result;
}

function createBossSummonResult(payload = {}) {
	const result = createGameActionResult("boss.summon", payload);
	result.data.bossId = payload.bossId || null;
	result.data.bossName = payload.bossName || null;
	result.data.isSpecialBoss = !!payload.isSpecialBoss;
	result.data.transition = {};
	return result;
}

function addResultLog(result, message, important = false) {
	if (!result || !message) return result;
	result.logs.push({ message, important: !!important });
	return result;
}

function addResultEffect(result, effect) {
	if (!result || !effect) return result;
	result.effects.push(effect);
	return result;
}

function requestUiRefresh(result, key, value = true) {
	if (!result) return result;
	result.ui[key] = value;
	return result;
}

function setEnhanceResultView(result, title, rows = [], goldSpent = 0) {
	if (!result) return result;
	result.ui.enhanceResult = {
		title,
		rows: Array.isArray(rows) ? rows : [],
		goldSpent: goldSpent || 0,
	};
	return result;
}

function applyActionResultUi(result) {
	if (!result) return result;

	(result.logs || []).forEach((entry) => {
		if (typeof addLog === "function") addLog(entry.message, !!entry.important);
	});

	(result.effects || []).forEach((effect) => {
		if (!effect || !effect.type) return;
		if (effect.type === "damageText" && typeof showDamageText === "function") {
			showDamageText(effect.text, effect.extraClass || "");
		} else if (effect.type === "itemDropText" && typeof showItemDropText === "function") {
			showItemDropText(effect.itemName || "아이템");
		}
	});

	if (result.ui && result.ui.enhanceResult && typeof renderEnhanceResultLog === "function") {
		const view = result.ui.enhanceResult;
		renderEnhanceResultLog(view.title, view.rows, view.goldSpent);
	}

	if (result.ui && result.ui.closeActionPanel && typeof closeActionPanel === "function") closeActionPanel();
	if (result.ui && result.ui.closeBossPanel && typeof toggleBossPanel === "function" && typeof isBossPanelOpen !== "undefined" && isBossPanelOpen) toggleBossPanel();
	if (result.ui && result.ui.closeSpecialBossPanel && typeof toggleSpecialBossPanel === "function" && typeof isSpecialBossPanelOpen !== "undefined" && isSpecialBossPanelOpen) toggleSpecialBossPanel();
	if (result.ui && result.ui.renderSkills && typeof renderSkills === "function") renderSkills();
	if (result.ui && result.ui.updateGoldUI && typeof updateGoldUI === "function") updateGoldUI();
	if (result.ui && result.ui.updateCombatUI && typeof updateCombatUI === "function") updateCombatUI();
	if (result.ui && result.ui.updateFullUI && typeof updateFullUI === "function") updateFullUI();
	if (result.ui && result.ui.renderUI && typeof renderUI === "function") renderUI();
	if (result.ui && result.ui.refreshActionPanelStats && typeof refreshActionPanelStats === "function") refreshActionPanelStats();
	if (result.ui && result.ui.consumedSkillBook && typeof showConsumedSkillBookPanel === "function") showConsumedSkillBookPanel(result.ui.consumedSkillBook);
	if (result.ui && result.ui.startAutoAttack && typeof startAutoAttack === "function") startAutoAttack();

	return result;
}

function createCombatAttackResult(payload = {}) {
	const result = createGameActionResult("combat.attack", payload);
	result.data.skillHits = [];
	result.data.totalDamage = 0;
	result.data.target = null;
	return result;
}

function addCombatSkillHit(result, label, damage) {
	if (!result) return result;
	result.data.skillHits.push({ label, damage });
	return result;
}

function queueDamageText(result, text, extraClass = "") {
	return addResultEffect(result, { type: "damageText", text, extraClass });
}

function createEnemyKillResult(payload = {}) {
	const result = createGameActionResult("combat.kill", payload);
	result.data.drops = [];
	result.data.rewards = {};
	result.data.transition = {};
	return result;
}

function addRewardGold(result, amount) {
	if (!result) return result;
	result.data.rewards.gold = (result.data.rewards.gold || 0) + (Math.floor(Number(amount) || 0));
	return result;
}

function addDropAward(result, itemName, message, options = {}) {
	if (!result) return result;
	result.data.drops.push({
		itemName,
		stacked: !!options.stacked,
		stored: !!options.stored,
		dropType: options.dropType || "item",
	});
	if (message) addResultLog(result, message, options.important !== false);
	if (itemName) addResultEffect(result, { type: "itemDropText", itemName });
	return result;
}

function addBlockedReward(result, message, reason = "blocked") {
	if (!result) return result;
	result.data.blockedRewards = result.data.blockedRewards || [];
	result.data.blockedRewards.push({ reason, message });
	if (message) addResultLog(result, message, false);
	return result;
}

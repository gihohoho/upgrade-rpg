const CURRENT_SAVE_VERSION = 5;

window.isTestCostMode = false;
window.isCodexRevealMode = false;

function toggleTestCostMode() {
	window.isTestCostMode = !window.isTestCostMode;
	const btn = document.getElementById("btn-test-cost");
	if (btn) {
		if (window.isTestCostMode) {
			btn.innerHTML = "비용 1원<br />ON";
			btn.style.color = "#88ff88";
			btn.style.borderColor = "#88ff88";
		} else {
			btn.innerHTML = "비용 1원<br />OFF";
			btn.style.color = "#ff9999";
			btn.style.borderColor = "#ff9999";
		}
	}
	if (typeof applyToggleButtonVisual === "function") applyToggleButtonVisual(btn, window.isTestCostMode);
	if (typeof refreshActionPanelStats === "function") refreshActionPanelStats();
	addLog(`[시스템] 테스트 모드 (강화 1원)가 ${window.isTestCostMode ? "활성화" : "비활성화"} 되었습니다.`);
}


function applyToggleButtonVisual(btn, isOn) {
	if (!btn) return;
	btn.classList.toggle("is-on-toggle", !!isOn);
	btn.classList.toggle("is-off-toggle", !isOn);
	btn.setAttribute("aria-pressed", isOn ? "true" : "false");
}

function refreshOnOffButtonVisuals() {
	applyToggleButtonVisual(document.getElementById("btn-test-cost"), !!window.isTestCostMode);
	applyToggleButtonVisual(document.getElementById("btn-test-buff"), !!window.isTestBuffMode);
	applyToggleButtonVisual(document.getElementById("btn-test-special-cd"), !!window.isSpecialBossNoCooldownMode);
	applyToggleButtonVisual(document.getElementById("btn-test-codex-reveal"), !!window.isCodexRevealMode);
	applyToggleButtonVisual(document.getElementById("btn-auto-boss"), !!autoBossSummon);
	applyToggleButtonVisual(document.getElementById("btn-equip-drop"), !!equipDropEnabled);
	applyToggleButtonVisual(document.getElementById("btn-auto-special-boss"), !!autoSpecialBossEnabled);
}

let recordPlayLastTick = Date.now();
let isUpdatingCodexUi = false;

function ensurePlayerRecords() {
	if (!player.records || typeof player.records !== "object") player.records = {};
	const r = player.records;
	if (!r.playTimeMs) r.playTimeMs = 0;
	if (!r.totalGoldEarned) r.totalGoldEarned = 0;
	if (!r.totalMonsterKills) r.totalMonsterKills = 0;
	if (!r.totalBossKills) r.totalBossKills = 0;
	if (!r.monsterKillsByName || typeof r.monsterKillsByName !== "object") r.monsterKillsByName = {};
	if (!r.bossKillsByName || typeof r.bossKillsByName !== "object") r.bossKillsByName = {};
	if (!r.enhanceFailByItem || typeof r.enhanceFailByItem !== "object") r.enhanceFailByItem = {};
	if (!r.collection || typeof r.collection !== "object") r.collection = {};
	if (!r.itemDropsByName || typeof r.itemDropsByName !== "object") r.itemDropsByName = {};
	if (!r.itemDryStreakByName || typeof r.itemDryStreakByName !== "object") r.itemDryStreakByName = {};
	return r;
}

function cloneRecordObject(obj) {
	return JSON.parse(JSON.stringify(obj || {}));
}

function refreshRecordSnapshot(force = false) {
	const r = ensurePlayerRecords();
	const now = Date.now();
	if (!force && r.recordSnapshot && r.recordSnapshotUpdatedAt) return r.recordSnapshot;
	r.recordSnapshot = {
		playTimeMs: r.playTimeMs || 0,
		totalGoldEarned: r.totalGoldEarned || 0,
		totalMonsterKills: r.totalMonsterKills || 0,
		totalBossKills: r.totalBossKills || 0,
		monsterKillsByName: cloneRecordObject(r.monsterKillsByName),
		bossKillsByName: cloneRecordObject(r.bossKillsByName),
		enhanceFailByItem: cloneRecordObject(r.enhanceFailByItem),
		collection: cloneRecordObject(r.collection),
		itemDropsByName: cloneRecordObject(r.itemDropsByName),
		itemDryStreakByName: cloneRecordObject(r.itemDryStreakByName),
	};
	r.recordSnapshotUpdatedAt = now;
	return r.recordSnapshot;
}

function getRecordSnapshotForView() {
	return refreshRecordSnapshot(false);
}

function forceRefreshRecordSnapshot() {
	return refreshRecordSnapshot(true);
}

function addGold(amount) {
	amount = Math.floor(Number(amount) || 0);
	if (amount <= 0) return;
	ensurePlayerRecords().totalGoldEarned += amount;
	player.gold += amount;
}

function getRecordItemBaseName(item) {
	if (!item) return "";
	let name = item.name || "";
	if (typeof getBaseStackName === "function") name = getBaseStackName(item);
	name = String(name).replace(/\s+\+\d+$/, "").trim();
	return name;
}

function getRecordItemLevel(item) {
	return Math.max(0, parseInt(item && item.level) || 0);
}

function getRecordItemKeys(item) {
	if (!item || !item.name) return [];
	const baseName = getRecordItemBaseName(item);
	const name = item.name || "";
	const isStackSpecial = item.isTalisman || item.isEmblem || name.includes("탈리스만") || name.includes("빛나는 휘장");
	if (isStackSpecial) return [`${baseName} +${Math.min(6, getRecordItemLevel(item))}`];
	return [baseName];
}

function advanceItemDryStreak() {
	const r = ensurePlayerRecords();
	Object.keys(r.collection).forEach((key) => {
		if (r.collection[key]) r.itemDryStreakByName[key] = (r.itemDryStreakByName[key] || 0) + 1;
	});
}

function recordItemAcquired(item) {
	const r = ensurePlayerRecords();
	let collectionChanged = false;
	getRecordItemKeys(item).forEach((key) => {
		if (!key) return;
		if (!r.collection[key]) collectionChanged = true;
		r.collection[key] = true;
		r.itemDropsByName[key] = (r.itemDropsByName[key] || 0) + ((item && item.count) || 1);
		r.itemDryStreakByName[key] = 0;
	});

	if (collectionChanged && typeof updateFullUI === "function" && !isUpdatingCodexUi) {
		isUpdatingCodexUi = true;
		try {
			updateFullUI();
		} finally {
			isUpdatingCodexUi = false;
		}
	}
}

function recordMonsterKill(name) {
	const r = ensurePlayerRecords();
	name = name || "알 수 없는 몬스터";
	r.totalMonsterKills++;
	r.monsterKillsByName[name] = (r.monsterKillsByName[name] || 0) + 1;
}

function recordBossKill(name) {
	const r = ensurePlayerRecords();
	name = name || "알 수 없는 보스";
	r.totalBossKills++;
	r.bossKillsByName[name] = (r.bossKillsByName[name] || 0) + 1;
}

function recordEnhanceFailure(itemName, count = 1) {
	const r = ensurePlayerRecords();
	itemName = itemName || "알 수 없는 아이템";
	r.enhanceFailByItem[itemName] = (r.enhanceFailByItem[itemName] || 0) + (Number(count) || 1);
}

function tickPlayTimeRecord() {
	const now = Date.now();
	const elapsed = Math.max(0, now - recordPlayLastTick);
	recordPlayLastTick = now;
	if (document.hidden) return;
	ensurePlayerRecords().playTimeMs += elapsed;
}

function startPlayTimeRecordTimer() {
	recordPlayLastTick = Date.now();
	document.addEventListener("visibilitychange", () => {
		recordPlayLastTick = Date.now();
	});
	setInterval(tickPlayTimeRecord, 1000);
}

function migrateSaveData(data) {
	if (!data || typeof data !== "object") return data;

	if (data.saveVersion === undefined || data.saveVersion === null) data.saveVersion = 0;
	if (!data.player || typeof data.player !== "object") data.player = {};

	if (data.saveVersion < 1) {
		if (!Array.isArray(data.player.storage)) data.player.storage = [];
		if (!Array.isArray(data.player.trash)) data.player.trash = [];
		if (!Array.isArray(data.player.mailbox)) data.player.mailbox = [];
		if (!data.fieldEnemyHp || typeof data.fieldEnemyHp !== "object") data.fieldEnemyHp = {};
		if (!data.fieldRespawnEndAt || typeof data.fieldRespawnEndAt !== "object") data.fieldRespawnEndAt = {};
		if (!data.player.specialBossCD || typeof data.player.specialBossCD !== "object") data.player.specialBossCD = {};
		if (!data.player.firstEquipSkillDropGiven || typeof data.player.firstEquipSkillDropGiven !== "object") data.player.firstEquipSkillDropGiven = {};
		data.saveVersion = 1;
	}

	if (data.saveVersion < 2) {
		if (!data.player.maxInventorySize || data.player.maxInventorySize < 60) data.player.maxInventorySize = 60;
		if (!data.player.maxStorageSize || data.player.maxStorageSize < 60) data.player.maxStorageSize = 60;
		data.saveVersion = 2;
	}

	if (data.saveVersion < 4) {
		// v4: 탈리스만A/B/휘장 슬롯 정보와 썸네일을 이름 기준으로 재정규화합니다.
		data.saveVersion = 4;
	}

	if (data.saveVersion < 5) {
		if (!data.player.records || typeof data.player.records !== "object") data.player.records = {};
		data.saveVersion = 5;
	}

	return data;
}

let lastManualSaveAt = 0;
let isResettingGame = false;

function saveGame(options = {}) {
	if (isResettingGame) return;
	if (window.shouldSkipSaveGameForBackendRestore && typeof window.shouldSkipSaveGameForBackendRestore === "function" && window.shouldSkipSaveGameForBackendRestore("idleRpgSaveV22")) {
		return;
	}
	if (typeof tickPlayTimeRecord === "function") tickPlayTimeRecord();
	if (typeof refreshRecordSnapshot === "function") refreshRecordSnapshot(!!options.refreshRecordSnapshot);
	const savePayload = typeof getServerSavePayload === "function"
		? getServerSavePayload(CURRENT_SAVE_VERSION)
		: {
			saveVersion: CURRENT_SAVE_VERSION,
			player,
			currentZoneIndex,
			currentZoneType,
			fieldEnemyHp,
			fieldRespawnEndAt,
		};
	localStorage.setItem("idleRpgSaveV22", JSON.stringify(savePayload));
}

function manualSaveGame() {
	if (window.shouldSkipSaveGameForBackendRestore && typeof window.shouldSkipSaveGameForBackendRestore === "function" && window.shouldSkipSaveGameForBackendRestore("idleRpgSaveV22")) {
		addLog("[저장] 세이브 복구가 새로고침 대기 중이라 수동 저장을 잠시 막았습니다. 새로고침 후 다시 저장하세요.", true);
		return;
	}
	const now = Date.now();
	const cooldownMs = 60000;
	const remain = cooldownMs - (now - lastManualSaveAt);
	if (remain > 0) {
		const remainSeconds = Math.ceil(remain / 1000);
		addLog(`[저장] 수동 저장은 ${remainSeconds}초 후 다시 사용할 수 있습니다.`);
		if (window.recordBackendSaveManualSaveCooldown && typeof window.recordBackendSaveManualSaveCooldown === "function") {
			window.recordBackendSaveManualSaveCooldown({
				reason: "manualSaveGame",
				remainSeconds,
			});
		}
		return;
	}
	lastManualSaveAt = now;
	saveGame({ refreshRecordSnapshot: true });
	addLog(`[저장] 현재 게임 데이터를 수동 저장했습니다. 기록관도 현재 저장 시점 기준으로 갱신되었습니다.`, true);

	if (window.requestBackendSaveAfterManualSave && typeof window.requestBackendSaveAfterManualSave === "function") {
		window.requestBackendSaveAfterManualSave({
			reason: "manualSaveGame",
			source: "manual-save-button",
			log: true,
		}).catch((error) => {
			console.warn("[Upgrade RPG] manual save backend sync failed", error);
		});
	}
}

function openSponsorPage() {
	window.open("https://teamsparta.notion.site/IAM-8ad9729b3dfb42e3a25c72c22106a72a", "_blank", "noopener,noreferrer");
}

function ensureMailbox() {
	if (!player.mailbox) player.mailbox = [];
}

function sendMail(mail) {
	ensureMailbox();
	player.mailbox.unshift({
		id: Date.now() + Math.random(),
		createdAt: Date.now(),
		...mail,
	});
	if (typeof normalizePlayerItemIcons === "function") normalizePlayerItemIcons(player);
	addLog(`📮 [우편함] ${mail.title || "새 우편"}이 도착했습니다.`, true);
	updateFullUI();
}

function getOneHourGoldAmount() {
	let t = typeof getTotals === "function" ? getTotals() : { goldInc: 0 };
	let zone = zones && zones[currentZoneIndex] ? zones[currentZoneIndex] : zones[0];
	let reward = zone && zone.goldReward ? zone.goldReward : 0;
	let finalReward = Math.floor(reward * (1 + ((t && t.goldInc) || 0) / 100));
	let attackIntervalMs = t && t.aspdMs ? t.aspdMs : 560;
	let killsPerHour = Math.max(1, Math.floor(3600000 / (attackIntervalMs + 2000)));
	return Math.max(0, Math.floor(finalReward * killsPerHour));
}

function sendOneHourGoldMail() {
	sendMail({
		type: "gold",
		title: "1H 골드 보상",
		body: "테스트용 1시간 골드 우편입니다.",
		amount: getOneHourGoldAmount(),
	});
	if (!isMailboxOpen) toggleMailbox();
}

function createMailTalismanItem() {
	let img = typeof getSpecialEquipIconUrl === "function" ? getSpecialEquipIconUrl({ name: "탈리스만", isTalisman: true }) : (typeof iconTextUrl === "function" ? iconTextUrl("TA1", "552266", "ffffff") : "");
	return {
		name: "탈리스만",
		type: "special_equip",
		isTalisman: true,
		specialSlotIdx: 12,
		level: 0,
		count: 1,
		img,
		sellPrice: 0,
	};
}

function sendTalismanMail() {
	sendMail({
		type: "item",
		title: "탈리스만 지급 우편",
		body: "테스트용 탈리스만 1개가 도착했습니다.",
		item: createMailTalismanItem(),
	});
	if (!isMailboxOpen) toggleMailbox();
}

function claimMail(index) {
	ensureMailbox();
	let mail = player.mailbox[index];
	if (!mail) return;

	if (mail.type === "gold") {
		addGold(mail.amount || 0);
		addLog(`📮 [우편수령] 골드 ${formatNumber(mail.amount || 0)} 획득!`, true);
		player.mailbox.splice(index, 1);
		updateFullUI();
		return;
	}

	if (mail.type === "item" && mail.item) {
		let result = typeof addStackableItemToInventory === "function" ? addStackableItemToInventory(mail.item) : null;
		if (result && result.ok) {
			addLog(`📮 [우편수령] ${getDisplayNameWithLevel(result.item)} 획득!`, true);
			player.mailbox.splice(index, 1);
			updateFullUI();
		} else {
			addLog("[시스템] 가방과 보관함이 꽉 차서 우편 아이템을 받을 수 없습니다.");
		}
		return;
	}

	if (mail.type === "bundle" && Array.isArray(mail.items)) {
		let received = [];
		for (let item of mail.items) {
			let result = typeof addStackableItemToInventory === "function" ? addStackableItemToInventory(item) : null;
			if (result && result.ok) received.push(getDisplayNameWithLevel(result.item));
			else {
				addLog("[시스템] 가방과 보관함이 꽉 차서 일부 우편 아이템을 받을 수 없습니다.");
				updateFullUI();
				return;
			}
		}
		addLog(`📮 [우편수령] ${received.join(", ")} 획득!`, true);
		player.mailbox.splice(index, 1);
		updateFullUI();
	}
}

function claimAllMail() {
	ensureMailbox();
	if (player.mailbox.length === 0) {
		addLog("[시스템] 받을 우편이 없습니다.");
		return;
	}

	let claimed = 0;
	let blocked = 0;

	for (let i = player.mailbox.length - 1; i >= 0; i--) {
		let mail = player.mailbox[i];
		if (!mail) continue;

		if (mail.type === "gold") {
			addGold(mail.amount || 0);
			player.mailbox.splice(i, 1);
			claimed++;
			continue;
		}

		if (mail.type === "item" && mail.item) {
			let result = typeof addStackableItemToInventory === "function" ? addStackableItemToInventory(mail.item) : null;
			if (result && result.ok) {
				player.mailbox.splice(i, 1);
				claimed++;
			} else {
				blocked++;
			}
			continue;
		}

		if (mail.type === "bundle" && Array.isArray(mail.items)) {
			let allOk = true;
			for (let item of mail.items) {
				let result = typeof addStackableItemToInventory === "function" ? addStackableItemToInventory(item) : null;
				if (!(result && result.ok)) {
					allOk = false;
					break;
				}
			}

			if (allOk) {
				player.mailbox.splice(i, 1);
				claimed++;
			} else {
				blocked++;
			}
		}
	}

	if (claimed > 0) addLog(`📮 [우편수령] 우편 ${claimed}건을 모두 받았습니다.`, true);
	if (blocked > 0) addLog(`[시스템] 가방과 보관함 공간 부족으로 ${blocked}건은 받지 못했습니다.`);
	updateFullUI();
}

function loadGame() {
	try {
		const savedStr = localStorage.getItem("idleRpgSaveV22");
		if (savedStr) {
			let data = migrateSaveData(JSON.parse(savedStr));
			if (typeof applyServerSavePayload === "function") {
				applyServerSavePayload(data);
			} else {
				player = { ...player, ...data.player };
				fieldEnemyHp = data.fieldEnemyHp && typeof data.fieldEnemyHp === "object" ? data.fieldEnemyHp : {};
				fieldRespawnEndAt = data.fieldRespawnEndAt && typeof data.fieldRespawnEndAt === "object" ? data.fieldRespawnEndAt : {};
				currentZoneIndex = parseInt(data.currentZoneIndex) || 0;
				currentZoneType = data.currentZoneType || "field";
			}

			if (currentZoneIndex >= zones.length) currentZoneIndex = zones.length - 1;
			if (currentZoneType === "boss_fight" && !currentBoss) currentZoneType = "boss_empty";
			if (typeof ensureGameStateShape === "function") ensureGameStateShape();
			ensurePlayerRecords();
			if (typeof normalizePlayerSpecialStackItems === "function") normalizePlayerSpecialStackItems();
			if (typeof normalizePlayerItemIcons === "function") normalizePlayerItemIcons(player);
			if (data.saveVersion !== CURRENT_SAVE_VERSION) saveGame();
			return true;
		}
	} catch (e) {
		console.error("세이브 로딩 중 에러:", e);
	}
	return false;
}

function resetGame() {
	const modal = document.getElementById("reset-modal");
	if (modal) modal.style.display = "flex";
}

function closeResetModal() {
	const modal = document.getElementById("reset-modal");
	if (modal) modal.style.display = "none";
}

function confirmResetGame() {
	isResettingGame = true;
	try {
		localStorage.removeItem("idleRpgSaveV22");
	} catch (error) {
		console.error("저장 데이터 삭제 실패:", error);
	}

	// beforeunload 자동 저장이 다시 데이터를 살리는 것을 막은 뒤 새로고침합니다.
	if (window.location && typeof window.location.reload === "function") {
		window.location.reload();
	} else if (typeof location !== "undefined" && typeof location.reload === "function") {
		location.reload();
	}
}

window.onload = function () {
	let loaded = false;
	try {
		loaded = loadGame();
		if (!loaded) {
			currentEnemy.hp = getFieldEnemyHp(0);
		} else if (currentZoneType === "field") {
			currentEnemy.hp = getFieldEnemyHp(currentZoneIndex);
		}

		// 접속 시에는 항상 마을에서 시작합니다.
		if (currentZoneType === "field") syncCurrentFieldHp();
		currentZoneType = "town";
		clearInterval(attackInterval);

		// 에러 발생을 대비하여 안전장치 추가
		if (isNaN(currentEnemy.hp)) currentEnemy.hp = getFieldEnemyHp(currentZoneIndex || 0);

		ensurePlayerRecords();
		if (typeof normalizePlayerItemIcons === "function") normalizePlayerItemIcons(player);
		startPlayTimeRecordTimer();
		updateFullUI();
		renderSkills();
		if (typeof refreshOnOffButtonVisuals === "function") refreshOnOffButtonVisuals();
	} catch (error) {
		console.error("초기화 중 치명적 에러 발생, 강제 복구를 시도합니다:", error);
		currentZoneType = "town";
		updateFullUI();
	}
	if (window.completeBackendSaveRestoreReloadApply && typeof window.completeBackendSaveRestoreReloadApply === "function") {
		const restoreApplyResult = window.completeBackendSaveRestoreReloadApply({
			loaded,
			saveKey: "idleRpgSaveV22",
		});
		if (restoreApplyResult && restoreApplyResult.applied && typeof addLog === "function") {
			addLog("[저장] 복구된 세이브를 새로고침 후 게임에 적용했고, 자동저장 잠금을 해제했습니다.", true);
		}
	}
	setInterval(saveGame, 60000);
	setInterval(() => {
		if (typeof tryStartAutoSpecialBoss === "function") tryStartAutoSpecialBoss(false);
		if (typeof refreshOnOffButtonVisuals === "function") refreshOnOffButtonVisuals();
	}, 1000);
};

document.addEventListener("mousemove", (e) => {
	[ui.tooltip, document.getElementById("boss-tooltip")].forEach((tip) => {
		if (tip && tip.style.display === "block") {
			let tw = tip.offsetWidth;
			let th = tip.offsetHeight;
			let px = e.pageX + 15;
			let py = e.pageY + 15;
			if (px + tw > window.innerWidth) px = window.innerWidth - tw - 10;
			if (py + th > window.innerHeight) py = window.innerHeight - th - 10;
			tip.style.left = px + "px";
			tip.style.top = py + "px";
		}
	});
});

function buildStatHtml(title, titleColor, finalVal, unitVal, equipVal, buffVal, bottomText, showAmp = false, ampValue = 0, codexVal = "") {
	let ampText = showAmp ? ` <span style="color:#ffcc00;">(+${formatPercentSmart(ampValue || 0)} 증폭)</span>` : "";
	const codexRow = codexVal !== "" ? `<div style="margin-left: 10px; margin-bottom: 8px;"><span style="color: #88ffcc;">도감:</span> <span style="color:#ffffff;">${codexVal}</span></div>` : "";
	return `
  <div style="font-family: '돋움', Dotum, sans-serif; font-size: 13px; font-weight: bold; line-height: 1.4; background:#474b62; padding:8px; border:1px solid #777; border-radius:2px;">
      <div style="color: ${titleColor}; font-size: 16px; margin-bottom: 5px; text-shadow: 1px 1px 0 #000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000;">${title}</div>
      <div style="color: #ffffff; margin-bottom: 2px;">최종: ${finalVal}</div>
      <div style="margin-left: 10px; margin-bottom: 2px;"><span style="color: #ff9999;">유닛:</span> <span style="color:#ffffff;">${unitVal}</span></div>
      <div style="margin-left: 10px; margin-bottom: 2px;"><span style="color: #99ccff;">장비:</span> <span style="color:#ffffff;">${equipVal}${ampText}</span></div>
      <div style="margin-left: 10px; margin-bottom: ${codexRow ? "2px" : "8px"};"><span style="color: #cc66ff;">버프:</span> <span style="color:#ffffff;">${buffVal}</span></div>
      ${codexRow}
      ${bottomText ? `<div style="margin-top:4px;">${bottomText}</div>` : ""}
  </div>`;
}

function combinePercentIncForTooltip(currentInc, addedInc) {
	return (1 + (currentInc || 0) / 100) * (1 + (addedInc || 0) / 100) * 100 - 100;
}

function getStatTooltipHTML(key) {
	let t = getTotals();
	let eq = {
		atk: 0,
		atkInc: 0,
		basicAtkDmgInc: 0,
		skillDmgInc: 0,
		allDmgInc: 0,
		addSkillAtkChance: 0,
		addSkillAtkMult: 0,
		basicCritChance: 0,
		basicCritDmg: 0,
		basicAtkDmgAmp: 0,
		basicCritDmgAmp: 0,
		skillDmgAmp: 0,
		skillProcChanceInc: 0,
		skillCoefficientInc: 0,
		addSkillAtkMultAmp: 0,
		skillCritChance: 0,
		skillCritDmg: 0,
	};

	if (player.equipment && Array.isArray(player.equipment)) {
		player.equipment.forEach((item) => {
			if (!item || item.type === "skill_book") return;
			if (item.type === "special_equip") {
				let sp = calcSpecialEquipStats(item);
				if (sp) {
					eq.atk += sp.attack || 0;
					eq.atkInc += sp.atkInc || 0;
					eq.allDmgInc += sp.allDmgInc || 0;
					eq.basicAtkDmgAmp += sp.basicAtkDmgAmp || 0;
					eq.basicCritDmgAmp = combinePercentIncForTooltip(eq.basicCritDmgAmp, sp.basicCritDmgAmp || 0);
					eq.skillDmgAmp += sp.skillDmgAmp || 0;
					eq.skillProcChanceInc = combinePercentIncForTooltip(eq.skillProcChanceInc, sp.skillProcChanceInc || 0);
					eq.skillCoefficientInc = combinePercentIncForTooltip(eq.skillCoefficientInc, sp.skillCoefficientInc || 0);
					eq.addSkillAtkMultAmp = combinePercentIncForTooltip(eq.addSkillAtkMultAmp, sp.addSkillAtkMultAmp || 0);
					eq.skillCritChance += sp.skillCritChance || 0;
					eq.skillCritDmg += sp.skillCritDmg || 0;
				}
				return;
			}
			let st = calcItemStats(item);
			if (st) {
				eq.atk += st.attack || 0;
				eq.atkInc += st.atkInc || 0;
				eq.basicAtkDmgInc += st.basicAtkDmgInc || 0;
				eq.skillDmgInc += st.skillDmgInc || 0;
				eq.allDmgInc += st.allDmgInc || 0;
				eq.addSkillAtkChance += st.addSkillAtkChance || 0;
				eq.addSkillAtkMult += st.addSkillAtkMult || 0;
				eq.basicCritChance += st.basicCritChance || 0;
				eq.basicCritDmg += st.basicCritDmg || 0;
			}
		});
	}

	if (key === "atk") {
		let atkBottom = `<span style="color:#ffcc00;">@평타 피해 증가, 모든 피해 증가 스탯이</span><br><span style="color:#ffffff;">별도 적용됩니다.</span><br><br><span style="color:#ffcc00; font-size:13px;">현재 순수공격력 상승치: ${formatNumber(player.farmAtkBonus || 0)}</span>`;
		return buildStatHtml("공격력", "#ff0000", formatNumber(t.attack), formatNumber(getBaseAttackByAttackSpeed() + (player.farmAtkBonus || 0)), formatNumber(eq.atk), "", atkBottom, true, t.atkInc || 0);
	}
	if (key === "aspd") return buildStatHtml("추가 공격속도", "#3399ff", t.aspd + "%", `${t.aspd}%`, "0%", "", `<span style="color:#ffcc00;">최종 공격속도:</span> <span style="color:#ffffff;">${(t.aspdMs / 1000).toFixed(3)}초/공격</span><br><span style="color:#ff3333;">@수치 중첩 제한. (최대 400%)</span><br><span style="color:#ffcc00;">@필드 몬스터 처치 시 공격속도 +1%, 기본 공격력도 함께 성장합니다.</span>`);
	if (key === "ndmg") return buildStatHtml("평타 피해 증가", "#ff0000", formatPercentSmart(t.basicAtkDmgInc), "0%", formatPercentSmart(eq.basicAtkDmgInc), "", "", true, t.basicAtkDmgAmp || 0);
	if (key === "ncdmg") return buildStatHtml("평타 치명타 피해", "#ff9900", formatPercentSmart(t.basicCritDmg), "0%", formatPercentSmart(eq.basicCritDmg), "", "", true, t.basicCritDmgAmp || 0);
	if (key === "ncrate") return buildStatHtml("평타 치명타 확률", "#ffcc00", formatPercentSmart(t.basicCritChance), "0%", formatPercentSmart(eq.basicCritChance), "", `<span style="color:#ff3333;">@수치 중첩 제한. (최대 50.0%)</span>`, false);
	if (key === "sdmg") return buildStatHtml("스킬 피해 증가", "#3399ff", formatPercentSmart(t.skillDmgInc), "0%", formatPercentSmart(eq.skillDmgInc), "", "", true, t.skillDmgAmp || 0);
	if (key === "scrate") return buildStatHtml("스킬 치명타 확률", "#3399ff", formatPercentSmart(t.skillCritChance), "0%", formatPercentSmart(eq.skillCritChance), "", `<span style="color:#ff3333;">@수치 중첩 제한. (최대 50.0%)</span>`, false);
	if (key === "alldmg") return buildStatHtml("모든 피해 증가", "#cc66ff", formatPercentSmart(t.allDmgInc), "0%", formatPercentSmart(eq.allDmgInc), "", "", true, 0);
	if (key === "scdmg") return buildStatHtml("스킬 치명타 피해", "#3399ff", formatPercentSmart(t.skillCritDmg), "0%", formatPercentSmart(eq.skillCritDmg), "", "", false);
	if (key === "schance") return buildStatHtml("추가 스킬피해 확률", "#00ffff", formatPercentSmart(t.addSkillAtkChance), "0%", formatPercentSmart(eq.addSkillAtkChance), "", `<span style="color:#ff3333;">@수치 중첩 제한. (최대 30.0%)</span>`, false);
	if (key === "unique") {
		return getUniqueTooltipHTML();
	}

	if (key === "smult") {
		// 🌟 추가 스킬피해 계수 단위를 퍼센트(%)로 통일
		return buildStatHtml("추가 스킬피해 계수", "#00ffff", t.addSkillAtkMult + "%", "0%", eq.addSkillAtkMult + "%", "", `<span style="color:#ffcc00;">@스킬 피해 증가, 스킬 치명타 피해<br>증가, 모든 피해 증가 스탯이 별도<br>적용됩니다.</span>`, true, t.addSkillAtkMultAmp || 0);
	}

	let buffValStr = window.isTestBuffMode ? "400%" : "0%";

	const codexValStr = formatPercentFixed1(t.codexBonusInc || 0);

	if (key === "farmgaininc") {
		return buildStatHtml("순수공격력 증가량", "#008080", formatPercentFixed1(t.farmGainInc || 0), "0%", "0%", buffValStr, `<span style="color:#ffcc00;">@필드 몬스터 처치 시 획득하는<br>순수공격력 증가량에 적용됩니다.</span>`, false, 0, codexValStr);
	}

	if (key === "goldinc") {
		return buildStatHtml("골드 획득량 증가", "#cc6600", formatPercentFixed1(t.goldInc), "0%", "0%", buffValStr, "", false, 0, codexValStr);
	}
	if (key === "dropinc") {
		return buildStatHtml("아이템 드랍률 증가", "#00aa00", formatPercentFixed1(t.dropInc), "0%", "0%", buffValStr, "", false, 0, codexValStr);
	}
	if (key === "enhanceinc") {
		return buildStatHtml("강화 성공률 증가", "#6600cc", formatPercentFixed1(t.enhanceInc), "0%", "0%", buffValStr, `<span style="color:#ffcc00;">@기본 강화 확률에 곱산 연산으로 적용됩니다.</span><br><span style="color:#ffffff;">(예: 기본 2% x 500% = 10%)</span>`, false, 0, codexValStr);
	}

	return "";
}

document.querySelectorAll(".stat-row[data-stat]").forEach((el) => {
	el.addEventListener("mouseenter", () => {
		let key = el.getAttribute("data-stat");
		let html = getStatTooltipHTML(key);
		if (html) {
			ui.tooltip.innerHTML = html;
			ui.tooltip.style.display = "block";
		}
	});
	el.addEventListener("mouseleave", hideTooltip);
});

setInterval(() => {
	if (isSpecialBossPanelOpen) {
		specialBossList.forEach((boss) => {
			const cdEl = document.getElementById(`cd-text-${boss.id}`);
			if (cdEl) {
				const cdEndMs = player.specialBossCD[boss.id] || 0;
				const now = Date.now();
				if (now < cdEndMs) {
					const remainSec = Math.ceil((cdEndMs - now) / 1000);
					cdEl.innerText = `${remainSec}`;
				} else {
					cdEl.innerHTML = "&nbsp;";
				}
			}
		});
	}
	const mCdEl = document.getElementById("skill-cd-heavenlyStrike");
	const currentSkills = typeof getCurrentCharacterSkills === "function" ? getCurrentCharacterSkills(player) : (player.skills || {});
	if (mCdEl && currentSkills && currentSkills.heavenlyStrike) {
		const hs = currentSkills.heavenlyStrike;
		const now = Date.now();
		const cdEndMs = (hs.lastUsed || 0) + 300000;
		if (hs.level > 0 && now < cdEndMs) {
			mCdEl.innerText = `${Math.ceil((cdEndMs - now) / 1000)}`;
		} else {
			mCdEl.innerHTML = "&nbsp;";
		}
	}
}, 1000);

setInterval(() => {
	if (activeBuffs && activeBuffs.ironStrike && activeBuffs.ironStrike.active) {
		activeBuffs.ironStrike.timer -= 100;
		if (activeBuffs.ironStrike.timer <= 0) {
			activeBuffs.ironStrike.active = false;
			activeBuffs.ironStrike.timer = 0;
			updateFullUI();
		}
	}
	if (activeBuffs && activeBuffs.overdrive && activeBuffs.overdrive.active) {
		activeBuffs.overdrive.timer -= 100;
		if (activeBuffs.overdrive.timer <= 0) {
			activeBuffs.overdrive.active = false;
			activeBuffs.overdrive.timer = 0;
			if (typeof showDamageText === "function") showDamageText("[E] 버프스킬 종료", "damage-skill-e damage-buff-state");
		}
	}
}, 100);

document.addEventListener("keydown", (e) => {
	if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;
	// 사용자 요청에 의해 모든 단축키(소환, 제거, 자동 등) 기능이 삭제되었습니다.
});

function giveBeginnerItem() {
	if (!hasEmptyItemSlot(player.inventory, player.maxInventorySize)) {
		addLog("[시스템] 가방이 꽉 찼습니다.");
		return;
	}

	const beginnerItem = {
		id: Date.now(),
		name: "리버레이션 스태프",
		type: "normal",
		level: 0,
		img: "",
		baseCost: 350,
		equipGroup: "beginner",
		equipLimit: 6,
		equipTextInfo: `<span style="color:#ff66cc;">초보자 아이템</span>은 <span style="color:#ffcc00;">6개</span>까지 장착<br>가능합니다.`,
		enhanceStats: [100, 107, 121, 142, 170, 205, 247, 296, 352, 415, 485, 618, 814, 1073, 1395, 1780, 2228, 2739, 3313, 3950, 4650],
	};

	if (typeof normalizeItemIcon === "function") normalizeItemIcon(beginnerItem);
	placeItemInFirstEmptySlot(player.inventory, beginnerItem, player.maxInventorySize);
	if (typeof recordItemAcquired === "function") recordItemAcquired(beginnerItem);
	addLog(`🎁 [초보자 지원] ${beginnerItem.name}을(를) 받았습니다!`);
	renderUI();
}

window.isTestBuffMode = false;

function updateCodexRevealButton() {
	const btn = document.getElementById("btn-test-codex-reveal");
	if (!btn) return;
	btn.innerHTML = window.isCodexRevealMode ? "도감보이기<br />ON" : "도감보이기<br />OFF";
	btn.style.color = window.isCodexRevealMode ? "#88ff88" : "#ffaaee";
	if (typeof applyToggleButtonVisual === "function") applyToggleButtonVisual(btn, window.isCodexRevealMode);
}

function toggleCodexRevealMode() {
	window.isCodexRevealMode = !window.isCodexRevealMode;
	updateCodexRevealButton();
	addLog(window.isCodexRevealMode ? "[테스트] 도감 ???? 표시 해제 ON" : "[테스트] 도감 ???? 표시 해제 OFF", true);

	if (typeof renderTownCodexModal === "function") {
		renderTownCodexModal();
	}
}

function toggleTestBuffMode() {
	window.isTestBuffMode = !window.isTestBuffMode;
	const btn = document.getElementById("btn-test-buff");
	if (btn) {
		if (window.isTestBuffMode) {
			btn.innerHTML = `버프<br /><span style="color:#88ff88">ON</span>`;
			btn.style.color = "#88ff88";
			btn.style.borderColor = "#88ff88";
		} else {
			btn.innerHTML = `버프<br />OFF`;
			btn.style.color = "#aaa";
			btn.style.borderColor = "#aaa";
		}
	}
	if (typeof applyToggleButtonVisual === "function") applyToggleButtonVisual(btn, window.isTestBuffMode);
	addLog(`[시스템] 테스트 버프(드랍/강화/골드/순수공 증가량 5배)가 ${window.isTestBuffMode ? "활성화" : "비활성화"} 되었습니다.`);
	updateFullUI(); // 🔥 버튼 클릭 즉시 UI(스탯창) 갱신!
}

function moveToRecentField() {
	if (typeof currentZoneIndex !== "undefined" && zones[currentZoneIndex]) {
		if (typeof closeAllGameplayModals === "function") closeAllGameplayModals();
		currentZoneType = "field";
		currentEnemy.hp = getFieldEnemyHp(currentZoneIndex);
		addLog(`[이동] 최근 사냥터(${zones[currentZoneIndex].name})로 이동했습니다.`);
		closeActionPanel();
		updateFullUI();
		if (currentEnemy.hp > 0) startAutoAttack();
		else clearInterval(attackInterval);
	}
}

function addPureAtk(amount) {
	if (!player.farmAtkBonus) player.farmAtkBonus = 0;
	player.farmAtkBonus += amount;
	if (player.farmAtkBonus < 0) player.farmAtkBonus = 0; // 음수 방지 처리

	let sign = amount > 0 ? "+" : "";
	addLog(`[치트] 순수공격력이 ${sign}${formatNumber(amount)} 변동되었습니다! (현재: ${formatNumber(player.farmAtkBonus)})`, true);
	updateFullUI();
}

function setBaseAtkAspdMax() {
	player.baseAttack = 1250;
	player.addAttackSpeed = 400;
	addLog(`[치트] 기본공/공속 MAX 적용! (기본공 ${formatNumber(getBaseAttackByAttackSpeed())}, 공속 400%)`, true);
	updateFullUI();
}

function getLegacyDefaultSkillStateFallback() {
	return {
		lightsabre: { level: 1, isUpgraded: false },
		ironStrike: { level: 0, isUpgraded: false },
		overdrive: { level: 0 },
		baldo: { level: 0 },
		illusionSword: { level: 0 },
		deepSword: { level: 0 },
		tempestStrike: { level: 0 },
		heavenlyStrike: { level: 0, lastUsed: 0 },
	};
}

function resetSkillsOnly() {
	const characterId = typeof getCurrentCharacterId === "function" ? getCurrentCharacterId(player) : "weapon_master";
	const nextSkills = typeof createDefaultCharacterSkillState === "function"
		? createDefaultCharacterSkillState(characterId)
		: getLegacyDefaultSkillStateFallback();

	if (typeof normalizePlayerCharacterState === "function") normalizePlayerCharacterState(player);
	if (player.userCharacters && player.userCharacters[characterId]) {
		player.userCharacters[characterId].skills = nextSkills;
	}
	player.skills = nextSkills;
	activeBuffs.ironStrike = { active: false, timer: 0 };
	activeBuffs.overdrive = { active: false, timer: 0 };
	addLog(`[테스트] 현재 캐릭터 스킬 데이터만 처음 상태로 초기화했습니다.`, true);
	updateFullUI();
}

window.isSpecialBossNoCooldownMode = false;

function updateSpecialBossNoCooldownButton() {
	const btn = document.getElementById("btn-test-special-cd");
	if (!btn) return;
	btn.innerHTML = window.isSpecialBossNoCooldownMode ? "쿨타임제거<br />ON" : "쿨타임제거<br />OFF";
	btn.style.color = window.isSpecialBossNoCooldownMode ? "#88ff88" : "#66ccff";
	if (typeof applyToggleButtonVisual === "function") applyToggleButtonVisual(btn, window.isSpecialBossNoCooldownMode);
}

function applySpecialBossNoCooldownMode() {
	if (!Array.isArray(specialBossList)) return;
	specialBossList.forEach((boss) => {
		if (boss.originalCooldownMs === undefined) boss.originalCooldownMs = boss.cooldownMs || 0;
		boss.cooldownMs = window.isSpecialBossNoCooldownMode ? 0 : boss.originalCooldownMs;
	});
	if (window.isSpecialBossNoCooldownMode) player.specialBossCD = {};
	updateSpecialBossNoCooldownButton();
}

function toggleSpecialBossNoCooldownMode() {
	window.isSpecialBossNoCooldownMode = !window.isSpecialBossNoCooldownMode;
	applySpecialBossNoCooldownMode();
	addLog(window.isSpecialBossNoCooldownMode ? `[테스트] 특수보스 쿨타임 0초 모드 ON` : `[테스트] 특수보스 쿨타임 0초 모드 OFF`, true);
	updateFullUI();
}

function clearSpecialBossCooldowns() {
	// 이전 버튼명과의 호환용: 이제는 ON/OFF 토글로 동작합니다.
	toggleSpecialBossNoCooldownMode();
}

let selectedTestBossId = null;
let testItemMode = "normal_boss"; // normal_boss: 일반보스 드랍 전체, special_boss: 특수보스 드랍 전체

function isTestDropForMode(drop) {
	return !!drop;
}

function getTestBossPool() {
	// 장비 지급: 일반 보스가 드랍하는 모든 아이템
	// 특수보스 장비지급: 특수 보스가 드랍하는 모든 아이템
	const source = testItemMode === "special_boss" ? specialBossList : bossList;
	return source.filter((boss) => boss.drops && boss.drops.length > 0);
}

function isTestItemModalOpened() {
	const modal = document.getElementById("test-item-modal");
	return !!(modal && modal.style.display === "block");
}

function openTestItemModal() {
	if (isTestItemModalOpened() && testItemMode === "normal_boss") {
		closeTestItemModal();
		return;
	}
	testItemMode = "normal_boss";
	selectedTestBossId = null;
	openTestModalBase();
}

function openTestSpecialItemModal() {
	if (isTestItemModalOpened() && testItemMode === "special_boss") {
		closeTestItemModal();
		return;
	}
	testItemMode = "special_boss";
	selectedTestBossId = null;
	openTestModalBase();
}

function openTestModalBase() {
	const modal = document.getElementById("test-item-modal");
	const title = document.getElementById("test-item-modal-title");
	if (title) title.innerText = testItemMode === "special_boss" ? "특수보스 장비 선택" : "일반보스 장비 선택";
	if (modal) modal.style.display = "block";

	const bosses = getTestBossPool();
	if (!bosses.some((boss) => boss.id === selectedTestBossId)) {
		selectedTestBossId = bosses.length > 0 ? bosses[0].id : null;
	}
	renderTestBossList();
}

function closeTestItemModal() {
	const modal = document.getElementById("test-item-modal");
	if (modal) modal.style.display = "none";
	hideTooltip();
}

function renderTestBossList() {
	const bList = document.getElementById("test-boss-list");
	const iList = document.getElementById("test-item-list");
	if (!bList) return;
	bList.innerHTML = "";
	if (iList) iList.innerHTML = "";

	const allBosses = getTestBossPool();

	allBosses.forEach((boss) => {
		let btn = document.createElement("div");
		btn.className = "boss-slot";

		if (boss.id === selectedTestBossId) {
			btn.style.borderColor = "#00ffff";
			btn.style.boxShadow = "0 0 10px #00ffff";
		}

		btn.innerHTML = `<img src="${boss.img}" alt="boss">`;

		btn.onmouseenter = () => {
			const tip = document.getElementById("boss-tooltip") || ui.tooltip;
			if (!tip) return;
			const matchedDrops = boss.drops.filter(isTestDropForMode).map((drop) => `*${drop.name}`).join("<br>");
			tip.innerHTML = `<div style="font-size:13px; font-weight:bold; line-height:1.4;">
				<div style="color:#ffcc00; font-size:15px; margin-bottom:5px;">${boss.title || boss.name}</div>
				<div style="color:#a3e354; margin-bottom:8px;">${boss.name}</div>
				<div style="color:#d86cf5; margin-bottom:5px;">[지급 가능 아이템]</div>
				<div style="color:#ffcc00;">${matchedDrops || "없음"}</div>
			</div>`;
			tip.style.display = "block";
		};
		btn.onmouseleave = () => {
			const tip = document.getElementById("boss-tooltip") || ui.tooltip;
			if (tip) tip.style.display = "none";
		};

		btn.onclick = () => {
			selectedTestBossId = boss.id;
			renderTestBossList();
		};

		bList.appendChild(btn);

		if (boss.id === selectedTestBossId) {
			renderTestItemList(boss);
		}
	});
}

function renderTestItemList(boss) {
	const iList = document.getElementById("test-item-list");
	if (!iList) return;
	iList.innerHTML = "";

	boss.drops.filter(isTestDropForMode).forEach((drop) => {
		let btn = document.createElement("button");
		const previewItem = typeof prepareStackableItem === "function" ? prepareStackableItem(drop) : { ...drop, level: drop.level || 0, count: drop.count || 1 };
		btn.className = "sys-btn";
		btn.style.height = "auto";
		btn.style.padding = "10px";
		btn.innerHTML = `
      <img class="special-drop-item-icon" src="${previewItem.img}" alt="">
      <span style="font-size:12px; color:#fff;">${typeof getDisplayNameWithLevel === "function" ? getDisplayNameWithLevel(typeof prepareStackableItem === "function" ? prepareStackableItem(drop) : drop) : drop.name}</span>
    `;
		if (typeof applyItemFrameClass === "function") applyItemFrameClass(btn.querySelector(".special-drop-item-icon"), previewItem);

		// 지급 모달에서도 인벤토리처럼 장비 정보 툴팁 표시
		btn.onmouseenter = () => {
			showItemTooltip(previewItem);
		};
		btn.onmouseleave = () => hideTooltip();

		btn.onclick = () => {
			const giveCount = 1;
			let giveItem = { ...drop, level: 0, count: giveCount };
			let result = typeof addStackableItemToInventory === "function"
				? addStackableItemToInventory(giveItem)
				: null;

			if (result && result.ok) {
				addLog(result.stacked ? `🎁 [테스트 지급] ${result.item.name} 획득! (현재 겹침: ${result.item.count}개)` : `🎁 [테스트 지급] ${result.item.name} 아이템을 ${giveCount}개 받았습니다.`, true);
				renderUI();
				return;
			}

			if (hasEmptyItemSlot(player.inventory, player.maxInventorySize)) {
				let newItem = { ...giveItem, id: Date.now() };
				if (typeof normalizeItemIcon === "function") normalizeItemIcon(newItem);
				placeItemInFirstEmptySlot(player.inventory, newItem, player.maxInventorySize);
				addLog(`🎁 [테스트 지급] ${newItem.name} 아이템을 ${giveCount}개 받았습니다.`, true);
				renderUI();
			} else {
				addLog(`[시스템] 가방이 꽉 차서 아이템을 받을 수 없습니다.`);
			}
		};
		iList.appendChild(btn);
	});
}

window.addEventListener("beforeunload", () => { tickPlayTimeRecord(); saveGame(); });

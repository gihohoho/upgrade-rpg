const ui = {
	zoneTitle: document.getElementById("zone-title"),
	enemyName: document.getElementById("enemy-name"),
	enemyHpBar: document.getElementById("enemy-hp-bar"),
	enemyHpText: document.getElementById("enemy-hp-text"),
	log: document.getElementById("log-zone"),
	tooltip: document.getElementById("tooltip"),
	infoGold: document.getElementById("info-gold"),
	infoDrop: document.getElementById("info-drop"),
	invPanel: document.getElementById("inv-panel"),
	equipNormal: document.getElementById("equip-normal"),
	equipSpecial: document.getElementById("equip-special"),
	inventoryContainer: document.getElementById("inventory-container"),
	inventoryCount: document.getElementById("inventory-count"),
	sAtk: document.getElementById("stat-atk"),
	sAspd: document.getElementById("stat-aspd"),
	sNcRate: document.getElementById("stat-nc-rate"),
	sNdmg: document.getElementById("stat-n-dmg"),
	sNcDmg: document.getElementById("stat-nc-dmg"),
	sSdmg: document.getElementById("stat-s-dmg"),
	sScRate: document.getElementById("stat-sc-rate"),
	sAllDmg: document.getElementById("stat-all-dmg"),
	sScDmg: document.getElementById("stat-sc-dmg"),
	sSchance: document.getElementById("stat-s-chance"),
	sSmult: document.getElementById("stat-s-mult"),
	sGoldInc: document.getElementById("stat-gold-inc"),
	sDropInc: document.getElementById("stat-drop-inc"),
	sEnhanceInc: document.getElementById("stat-enhance-inc"),
	sFarmGainInc: document.getElementById("stat-farm-gain-inc"),
	playerGold: document.getElementById("player-gold"),
	hAtk: document.getElementById("hud-atk"),
	hSdmg: document.getElementById("hud-sdmg"),
	hAspd: document.getElementById("hud-aspd"),
	hAlldmg: document.getElementById("hud-alldmg"),
	hNdmg: document.getElementById("hud-ndmg"),
	apPanel: document.getElementById("item-action-panel"),
	apImg: document.getElementById("ap-img"),
	apName: document.getElementById("ap-name"),
	apStats: document.getElementById("ap-stats"),
	apEnhanceLog: document.getElementById("ap-enhance-log"),
	btnApReinforce1: document.getElementById("btn-ap-reinforce1"),
	btnApReinforce20: document.getElementById("btn-ap-reinforce20"),
	btnApReinforce50: document.getElementById("btn-ap-reinforce50"),
	btnApReinforce200: document.getElementById("btn-ap-reinforce200"),
	btnApDismantleZero: document.getElementById("btn-ap-dismantle-zero"),
	btnApSell: document.getElementById("btn-ap-sell"),
	btnApUse: document.getElementById("btn-ap-use"),
	storagePanel: document.getElementById("storage-panel"),
	storageContainer: document.getElementById("storage-container"),
	storageCount: document.getElementById("storage-count"),
	trashPanel: document.getElementById("trash-panel"),
	trashContainer: document.getElementById("trash-container"),
	trashCount: document.getElementById("trash-count"),
	mailboxPanel: document.getElementById("mailbox-panel"),
	mailboxContainer: document.getElementById("mailbox-container"),
	mailboxCount: document.getElementById("mailbox-count"),
	sSchance: document.getElementById("stat-s-chance"),
	sSkillProb: document.getElementById("stat-skill-prob"), // 🔥 고유능력 제어용 추가
	sSmult: document.getElementById("stat-s-mult"),
};

let isStorageOpen = false;
let isTrashOpen = false;
let isMailboxOpen = false;
let currentFieldPage = 0;
let currentBossPage = 0;
const BOSS_PAGE_SIZE = 16;
const fieldGroups = [
	[0, 1, 2], // 마그토늄
	[3, 4, 5], // 이계
	[6], // 테라니움
	[7, 8, 9, 10], // 할렘
	[11, 12, 13, 14], // 루크
	[15, 16, 17], // 핀드워
	[18, 19], // 폭풍의 항로 & 심연의 폭풍의 항로
	[20, 21, 22], // 아이올라이트
	[23, 24, 25], // 절망의 광석
	[26, 27, 28, 29], // 골든 베릴
	[30, 31, 32, 33, 34], // 균열의 단편
	[35, 36, 37, 38, 39], // 퀀텀 카지노
];
const maxFieldPage = 2; // 총 3페이지 (0, 1, 2)

const specialSlotNames = ["특수<br>무기", "특수<br>목걸이", "특수<br>반지", "무기<br>아바타", "오라<br>아바타", "클론 레어<br>아바타", "탈리스만<br>A", "탈리스만<br>B", "휘장"];

function getCleanStackName(item) {
	return item && item.name ? item.name.replace(/\s*\+0$/, "") : "";
}

function getSpecialEquipCategoryPresentation(item) {
	let name = String(item && item.name ? item.name : "");
	let avatarCategory = "";
	if (name.includes("클론 레어 아바타")) avatarCategory = "클론 레어 아바타";
	else if (name.includes("무기 아바타")) avatarCategory = "무기 아바타";
	else if (name.includes("오라 아바타")) avatarCategory = "오라 아바타";

	if (avatarCategory) {
		return {
			label: `[${avatarCategory}]`,
			color: "#6eb4ff",
			description: `${avatarCategory} 슬롯 전용 장비입니다.`,
		};
	}
	return {
		label: "[특수 장비]",
		color: "#ff66cc",
		description: "특수 슬롯에 장착 가능한 아이템입니다.",
	};
}

function isEmblemLike(item) {
	return !!(item && (item.isEmblem || (item.name && item.name.includes("빛나는 휘장"))));
}

function isTalismanLike(item) {
	return !!(item && (item.isTalisman || (item.name && item.name.includes("탈리스만"))));
}

function getDisplayNameWithLevel(item) {
	if (!item) return "";
	let lvl = parseInt(item.level) || 0;
	if (isTalismanLike(item) || isEmblemLike(item)) return `${getCleanStackName(item)} +${lvl}`;
	if (item.type !== "skill_book" && lvl > 0) return `${item.name} +${lvl}`;
	return item.name;
}

function isDisplayStackable(item) {
	return item && (item.type === "skill_book" || isTalismanLike(item) || isEmblemLike(item));
}

function isTalismanBLike(item) {
	const name = (item && item.name) || "";
	return !!(item && isTalismanLike(item) && (name.includes("초월") || name.includes("영롱")));
}

function isTalismanALike(item) {
	const name = (item && item.name) || "";
	return !!(item && isTalismanLike(item) && !isTalismanBLike(item) && !name.includes("빛나는 휘장"));
}

function getTalismanCategoryInfo(item) {
	const levelBonus = (parseInt(item && item.level) || 0) + 1;
	if (isEmblemLike(item)) {
		const st = calcSpecialEquipStats(item) || { atkInc: 0, allDmgInc: 0 };
		return {
			typeName: "[휘장]",
			slotName: "휘장",
			statsHtml: `<div style="color:#ff6666; font-size:14px; margin-bottom:2px;">공격력 추가증가 <span style="color:#88ff88;">${formatPercentSmart(st.atkInc || 0, 1)}</span></div>
         <div style="color:#d26cff; font-size:14px; margin-bottom:2px;">모든 피해 증가 <span style="color:#88ff88;">${formatPercentSmart(st.allDmgInc || 0, 1)}</span></div>
         <div style="color:#999; margin-top:6px; line-height:1.35;">※ 실제 내부 데이터는 정밀값으로 적용되고, 표기만 반올림됩니다.</div>`,
		};
	}
	if (isTalismanBLike(item)) {
		return {
			typeName: "[탈리스만 B]",
			slotName: "탈리스만B",
			statsHtml: `<div style="color:#ffcc00; font-size:14px; margin-bottom:2px;">F 스킬 레벨 증가 <span style="color:#88ff88;">${levelBonus}</span></div>
         <div style="color:#ffcc00; font-size:14px; margin-bottom:2px;">D 스킬 레벨 증가 <span style="color:#88ff88;">${levelBonus}</span></div>
         <div style="color:#ffcc00; font-size:14px; margin-bottom:2px;">SW 스킬 레벨 증가 <span style="color:#88ff88;">${levelBonus}</span></div>`,
		};
	}
	return {
		typeName: "[탈리스만 A]",
		slotName: "탈리스만A",
		statsHtml: `<div style="color:#ffcc00; font-size:14px; margin-bottom:2px;">R 스킬 레벨 증가 <span style="color:#88ff88;">${levelBonus}</span></div>
         <div style="color:#ffcc00; font-size:14px; margin-bottom:2px;">T 스킬 레벨 증가 <span style="color:#88ff88;">${levelBonus}</span></div>
         <div style="color:#ffcc00; font-size:14px; margin-bottom:2px;">SQ 스킬 레벨 증가 <span style="color:#88ff88;">${levelBonus}</span></div>`,
	};
}

function getSlotBadgeHtml(item, equipped = false) {
	if (!item) return "";
	let lvl = parseInt(item.level) || 0;
	if (item.type === "skill_book") {
		return item.count && item.count > 1 ? `<div class="level-badge" style="background:rgba(220,0,0,0.9); color:#fff;">x${item.count}</div>` : "";
	}
	if (isTalismanLike(item) || isEmblemLike(item)) {
		let countText = !equipped && item.count && item.count > 1 ? `<span style="color:#ffcccc;">x${item.count}</span>` : "";
		let levelText = lvl > 0 ? `+${lvl} ` : "";
		let combined = (levelText + countText).trim();
		return combined ? `<div class="level-badge">${combined}</div>` : "";
	}
	if (item.type !== "skill_book") {
		let countText = !equipped && item.count && item.count > 1 ? ` x${item.count}` : "";
		let levelText = lvl > 0 ? `+${lvl}` : "";
		let combined = `${levelText}${countText}`.trim();
		return combined ? `<div class="level-badge">${combined}</div>` : "";
	}
	return "";
}


function toggleStorage() {
	isStorageOpen = !isStorageOpen;
	if (isStorageOpen) {
		isTrashOpen = false;
		isMailboxOpen = false;
		if (ui.trashPanel) ui.trashPanel.style.display = "none";
		if (ui.mailboxPanel) ui.mailboxPanel.style.display = "none";
	}
	if (ui.storagePanel) ui.storagePanel.style.display = isStorageOpen ? "block" : "none";
	if (isStorageOpen) renderUI();
}

function toggleTrash() {
	isTrashOpen = !isTrashOpen;
	if (isTrashOpen) {
		isStorageOpen = false;
		isMailboxOpen = false;
		if (ui.storagePanel) ui.storagePanel.style.display = "none";
		if (ui.mailboxPanel) ui.mailboxPanel.style.display = "none";
	}
	if (ui.trashPanel) ui.trashPanel.style.display = isTrashOpen ? "block" : "none";
	if (isTrashOpen) renderUI();
}

function closeAllGameplayModals() {
	isMailboxOpen = false;
	isStorageOpen = false;
	isTrashOpen = false;
	isBossPanelOpen = false;
	isSpecialBossPanelOpen = false;
	isFieldPanelOpen = false;

	[
		"mailbox-panel",
		"storage-panel",
		"trash-panel",
		"boss-panel",
		"special-boss-panel",
		"field-panel",
		"town-record-modal",
		"town-codex-modal",
		"town-ranking-modal",
		"item-action-panel",
		"test-item-modal",
		"auto-special-modal",
	].forEach((id) => {
		const el = document.getElementById(id);
		if (el) el.style.display = "none";
	});
	selectedSlot = { type: null, index: -1 };
}

function toggleMailbox() {
	isMailboxOpen = !isMailboxOpen;
	if (isMailboxOpen) {
		isStorageOpen = false;
		isTrashOpen = false;
		if (ui.storagePanel) ui.storagePanel.style.display = "none";
		if (ui.trashPanel) ui.trashPanel.style.display = "none";
	}
	if (ui.mailboxPanel) ui.mailboxPanel.style.display = isMailboxOpen ? "block" : "none";
	if (isMailboxOpen) renderUI();
}

function toggleInv() {
	isInvOpen = !isInvOpen;
	if (ui.invPanel) ui.invPanel.style.display = isInvOpen ? "block" : "none";
}


function formatPercentFixed1(value) {
	let n = parseFloat(value) || 0;
	return `${n.toFixed(1)}%`;
}

function formatPercentSmart(value, digits = 3) {
	let n = parseFloat(value) || 0;
	if (!isFinite(n) || n === 0) return "0%";
	let sign = n < 0 ? "-" : "";
	let abs = Math.abs(n);
	let exponent = Math.floor(Math.log10(abs));
	let decimals = Math.max(0, 3 - 1 - exponent);
	let rounded = Number(abs.toFixed(decimals));
	if (rounded >= 1000) decimals = 0;
	let text = decimals > 0
		? rounded.toFixed(decimals).replace(/\.0+$/, "").replace(/(\.\d*?)0+$/, "$1")
		: String(Math.round(rounded));
	return sign + text + "%";
}

function buildSpecialEquipStatsHtml(item, compact = false) {
	let st = calcSpecialEquipStats(item);
	if (!st) return `<div style="color:#aaa;">표시할 특수 옵션이 없습니다.</div>`;
	let rows = [];
	const addRow = (label, value, color = "#ffcc00", inactive = false) => {
		const rowColor = inactive ? "#777777" : color;
		const valueColor = inactive ? "#aaaaaa" : "#ffffff";
		rows.push(`<div style="color:${rowColor}; margin-bottom:${compact ? "1px" : "3px"};">${label} <span style="color:${valueColor};">${value}</span></div>`);
	};
	const isAbyssStaff = item && item.name && item.name.includes("심연의 편린") && item.name.includes("스태프");
	if (st.attack) addRow("공격력", formatNumberDecimal ? formatNumberDecimal(st.attack, 2) : formatNumber(st.attack), "#ff3333");
	if (st.atkInc) addRow("공격력 추가증가", formatPercentSmart(st.atkInc, 1), "#ff6666");
	if (st.allDmgInc) addRow("모든 피해 증가", formatPercentSmart(st.allDmgInc, 1), "#d26cff");
	if (st.basicAtkDmgAmp) addRow("평타피해 추가증가", formatPercentSmart(st.basicAtkDmgAmp, 3), "#ff3333");
	if (st.basicCritDmgAmp) addRow("평타 치명타 피해 증폭", formatPercentSmart(st.basicCritDmgAmp, 1), "#ff9900");
	if (st.skillDmgAmp) addRow("스킬피해 추가증가", formatPercentSmart(st.skillDmgAmp, 3), "#3366ff");
	if (st.skillCritChance) addRow("스킬 치명타 확률", formatPercentSmart(st.skillCritChance, 1), "#3399ff");
	if (st.skillCritDmg) addRow("스킬 치명타 피해 배율", formatPercentSmart(st.skillCritDmg, 1), "#3399ff");
	if (isAbyssStaff) {
		if (st.skillProcChanceInc) addRow("스킬발동확률 증가", formatPercentSmart(st.skillProcChanceInc, 3), "#ff00aa", false);
		if (st.skillCoefficientInc) addRow("스킬계수 증가", formatPercentSmart(st.skillCoefficientInc, 3), "#ff00aa", true);
		if (st.skillCooldownReductionInc) addRow("스킬쿨타임 감소", formatPercentSmart(st.skillCooldownReductionInc, 3), "#ff00aa", true);
		if (st.allSkillDamageInc) addRow("모든스킬 데미지 증가", formatPercentSmart(st.allSkillDamageInc, 2), "#ff00aa", true);
		if (st.allBuffValueInc) addRow("모든버프수치 증가", formatPercentSmart(st.allBuffValueInc, 3), "#ff00aa", true);
		if (st.cloneCountInc) addRow("분신갯수 증가", `${st.cloneCountInc}A`, "#ff00aa", true);
		if (st.cloneAttackSpeedInc) addRow("분신 공격속도 증가", formatPercentSmart(st.cloneAttackSpeedInc, st.cloneAttackSpeedInc < 1 ? 5 : 1), "#ff00aa", true);
		if (st.maxAttackSpeedCapInc) addRow("최대 공격속도 증가치 증가", formatPercentSmart(st.maxAttackSpeedCapInc, 1), "#ff00aa", true);
		rows.push(`<div style="color:#999; margin-top:6px;">비활성화 된 스탯은 적용되지 않습니다.</div>`);
	} else {
		if (st.skillProcChanceInc) addRow("스킬발동확률 증가", formatPercentSmart(st.skillProcChanceInc, 3), "#ff00aa");
		if (st.skillCoefficientInc) addRow("스킬계수 증가", formatPercentSmart(st.skillCoefficientInc, 3), "#ff00aa");
		if (st.addSkillAtkMultAmp) addRow("추가 스킬공격 계수 증폭", formatPercentSmart(st.addSkillAtkMultAmp, 1), "#00ffff");
		if (st.skillCooldownReductionInc) addRow("스킬쿨타임 감소", formatPercentSmart(st.skillCooldownReductionInc, 3), "#ff00aa");
		if (st.allSkillDamageInc) addRow("모든스킬 데미지 증가", formatPercentSmart(st.allSkillDamageInc, 2), "#ff00aa");
		if (st.allBuffValueInc) addRow("모든버프수치 증가", formatPercentSmart(st.allBuffValueInc, 3), "#ff00aa");
		if (st.cloneCountInc) addRow("분신갯수 증가", `${st.cloneCountInc}A`, "#ff00aa");
		if (st.cloneAttackSpeedInc) addRow("분신 공격속도 증가", formatPercentSmart(st.cloneAttackSpeedInc, st.cloneAttackSpeedInc < 1 ? 5 : 1), "#ff00aa");
		if (st.maxAttackSpeedCapInc) addRow("최대 공격속도 증가치 증가", formatPercentSmart(st.maxAttackSpeedCapInc, 1), "#ff00aa");
	}
	if (!rows.length) rows.push(`<div style="color:#aaa;">표시할 특수 옵션이 없습니다.</div>`);
	return rows.join("");
}

function getGoldRewardDisplay(baseReward) {
	let t = getTotals();
	let inc = t.goldInc || 0;
	let base = Math.floor(baseReward);
	let finalReward = Math.floor(baseReward * (1 + inc / 100));
	let bonus = Math.max(0, finalReward - base);
	return `<span class="reward-final">${formatNumber(finalReward)}</span> <span class="reward-breakdown">( <span class="reward-base">${formatNumber(base)}</span> + <span class="reward-bonus">${formatNumber(bonus)}</span> )</span>`;
}

function getEnhanceProbDisplay(level, item = null) {
	if (item) {
		const isStackSpecial = isTalismanLike(item) || isEmblemLike(item);
		if ((isStackSpecial && level >= 6) || (!isStackSpecial && level >= 20)) {
			return `<span class="enhance-prob-max">강화 MAX</span>`;
		}
	}
	let baseProb = getBaseEnhanceProb(level, item) * 100;
	let finalProb = getEnhanceProb(level, item) * 100;
	let bonus = Math.max(0, finalProb - baseProb);
	return `<span class="enhance-prob-final">${formatPercentSmart(finalProb)}</span> <span class="enhance-prob-breakdown">( <span class="enhance-prob-base">${formatPercentSmart(baseProb)}</span> + <span class="enhance-prob-bonus">${formatPercentSmart(bonus)}</span> )</span>`;
}

function getUniqueTooltipHTML() {
	let t = getTotals();
	const rows = [
		{ label: "스킬발동확률 증가", value: formatPercentSmart(t.skillProcChanceInc || 0, 1), active: true },
		{ label: "스킬계수 증가", value: formatPercentSmart(t.skillCoefficientInc || 0, 1), active: false },
		{ label: "스킬쿨타임 감소", value: formatPercentSmart(t.skillCooldownReductionInc || 0, 1), active: false },
		{ label: "모든스킬 데미지 증가", value: formatPercentSmart(t.allSkillDamageInc || 0, 1), active: false },
		{ label: "모든버프수치 증가", value: formatPercentSmart(t.allBuffValueInc || 0, 1), active: false },
		{ label: "분신갯수 증가", value: `${t.cloneCountInc || 0}A`, active: false },
		{ label: "분신 공격속도 증가", value: formatPercentSmart(t.cloneAttackSpeedInc || 0, 1), active: false },
		{ label: "최대 공격속도 증가치 증가", value: formatPercentSmart(t.maxAttackSpeedCapInc || 0, 1), active: false },
	];
	return `<div class="unique-tooltip-box"><div class="unique-tooltip-title">고유능력</div>${rows.map(r => `<div class="unique-tooltip-row ${r.active ? "active" : "inactive"}"><span>${r.label}</span><span class="unique-tooltip-value">${r.value}</span></div>`).join("")}<div class="unique-tooltip-note">비활성화 된 스탯은 적용되지 않습니다.</div></div>`;
}

function addLog(text, isSuccess = false) {
	if (!ui.log) return;
	let p = document.createElement("p");
	p.innerHTML = text;
	if (isSuccess) p.style.color = "#88ff88";
	ui.log.appendChild(p);
	ui.log.scrollTop = ui.log.scrollHeight;
}


function getSkillBookInfo(itemName) {
	// 스킬강화권 정보는 src/data/skills.js의 중앙 데이터에서 가져옵니다.
	// 이 함수 이름은 기존 render/item 코드 호환을 위해 유지합니다.
	if (typeof getSkillBookDisplayInfo === "function") return getSkillBookDisplayInfo(itemName);
	return { key: "?", skill: "대응 스킬", type: "일반" };
}

function buildSkillBookTooltipHtml(item) {
	const info = getSkillBookInfo(item.name);
	let detail = "";
	if (info.type === "각성") {
		detail = `기존 ${info.base} 스킬 레벨과 관계없이 <span style="color:#ff99ff;">${info.key} 스킬을 Lv.1</span>로 각성시킵니다.<br>이미 각성된 후에는 같은 강화권으로 ${info.key} 스킬 레벨을 올립니다. (최대 Lv.7)`;
	} else if (info.type === "진각성") {
		detail = `<span style="color:#ff99ff;">M 진각성 스킬</span>을 획득하거나 레벨을 올립니다.<br>진각성 스킬은 300초 쿨타임을 가집니다.`;
	} else {
		detail = `<span style="color:#ff99ff;">${info.key} 스킬</span>을 획득하거나 레벨을 올립니다.<br>스킬 레벨이 1 상승합니다. (최대 Lv.7)`;
	}
	return `<div style="font-size: 13px; font-weight: bold; line-height: 1.45;">
		<div style="color: #ffcc00; font-size: 15px; margin-bottom: 5px;">${item.name}</div>
		<div style="color: #00ffff; margin-bottom: 5px;">[특수 소비 아이템]</div>
		<div style="color: #ffffff; margin-bottom: 8px;">각 직업의 Q, W, E, R, T, F, D, SQ, SW, M 등<br>대응 스킬을 획득하거나 레벨을 올리는 강화권입니다.</div>
		<div style="color: #a3e354; margin-bottom: 4px;">대상: ${info.key} - ${info.skill}</div>
		<div style="color: #ffffff;">${detail}</div>
		<div style="color: #aaaaaa; margin-top: 8px;">클릭하여 관리창을 열고 사용 버튼으로 사용합니다.</div>
	</div>`;
}


function buildSkillBookActionHtml(item) {
	const info = getSkillBookInfo(item.name);
	let line = "";
	if (info.type === "각성") line = `기존 ${info.base} 레벨과 관계없이 ${info.key} 스킬을 Lv.1로 각성하고, 이후 같은 강화권으로 최대 Lv.7까지 올립니다.`;
	else if (info.type === "진각성") line = `${info.key} 진각성 스킬을 획득하거나 레벨을 올립니다. (쿨타임 300초)`;
	else line = `${info.key} 스킬을 획득하거나 레벨을 올립니다. (최대 Lv.7)`;
	return `<div style="color:#00ffff; line-height:1.45; font-weight:bold;">
		각 직업의 Q/W/E/R/T/F/D/SQ/SW/M 등 대응 스킬 강화권입니다.<br>
		<span style="color:#ffcc00;">대상: ${info.key} - ${info.skill}</span><br>
		<span style="color:#ffffff;">${line}</span>
	</div>`;
}

function showItemTooltip(item) {
	if (!ui.tooltip) return;
	if (item.type === "skill_book") {
		ui.tooltip.innerHTML = buildSkillBookTooltipHtml(item);
		ui.tooltip.style.display = "block";
		return;
	}

	if (isTalismanLike(item) || isEmblemLike(item)) {
		let baseName = getCleanStackName(item);
		let info = getTalismanCategoryInfo(item);
		let lvl = parseInt(item.level) || 0;
		let costCount = Math.pow(2, lvl);
		let materialName = `${baseName} +0`;
		let upgradeCostHtml = lvl >= 6 ? `<div style="color:#88ff88; font-weight:bold;">강화 MAX</div>` : `강화재료: ${materialName} <span style="color:#fff;">${costCount}개</span> 필요<br>강화비용: 비용 소모 없음 / 100.0%`;

		let isEquipped = player.equipment.includes(item);
		let isEquipTxt = isEquipped ? "(장착중)" : "";

		ui.tooltip.innerHTML = `
      <div style="font-size: 13px; font-weight: bold; line-height: 1.4;">
        <div style="color: #ffcc00; font-size: 15px; margin-bottom: 5px;">${baseName} +${lvl} ${isEquipTxt}</div>
        <div style="color: #aaa; margin-bottom: 10px;">클릭하여 관리창을 열고 ${isEquipped ? "해제" : "장착"}할 수 있습니다.</div>
        <div style="color: #28a745; margin-bottom: 10px; font-size: 14px;">${info.typeName}</div>
        ${info.statsHtml}
        <div style="color: #ffcc00; margin-top: 15px;">${upgradeCostHtml}</div>
      </div>
    `;
		ui.tooltip.style.display = "block";
		return;
	}

	if (item.type === "special_equip") {
		let statsHtml = buildSpecialEquipStatsHtml(item);
		let ampNote = item.name && (item.name.includes("반지") || item.name.includes("목걸이")) ? `<div style="color:#ffcc00; margin-top:8px;">※ 해당 추가증가는 스탯창의 증폭수치로 적용됩니다.</div>` : "";
		let category = getSpecialEquipCategoryPresentation(item);
		ui.tooltip.innerHTML = `<div style="font-size: 13px; font-weight: bold; line-height: 1.4;"><div style="color: #ffcc00; font-size: 15px; margin-bottom: 5px;">${getDisplayNameWithLevel(item)}</div><div style="color: ${category.color}; margin-bottom: 8px;">${category.label}</div>${statsHtml}${ampNote}<div style="color: #fff; margin-top:10px;">클릭하여 관리창을 열고<br>전용 슬롯에 장착 및 해제할 수 있습니다.</div></div>`;
		ui.tooltip.style.display = "block";
		return;
	}

	let st = calcItemStats(item);
	let cost = getEnhanceCost(item);
	let lvText = item.level > 0 ? `+${item.level}` : "";
	let costText = item.level >= 20 ? "강화 MAX" : `${formatNumber(cost)} 골드 / (${formatPercentSmart(getEnhanceProb(item.level, item) * 100)})`;

	let statsHtml = `<div style="color: #ff3333; margin-bottom: 2px;">공격력 ${formatNumber(st.attack)}</div>`;
	if (st.atkInc) statsHtml += `<div style="color: #ff3333; margin-bottom: 2px;">공격력 추가증가 ${formatPercentSmart(st.atkInc)}</div>`;
	if (st.basicAtkDmgInc) statsHtml += `<div style="color: #ff3333; margin-bottom: 2px;">평타 피해 증가 ${formatPercentSmart(st.basicAtkDmgInc)}</div>`;
	if (st.skillDmgInc) statsHtml += `<div style="color: #3366ff; margin-bottom: 2px;">스킬 피해 증가 ${formatPercentSmart(st.skillDmgInc)}</div>`;
	if (st.allDmgInc) statsHtml += `<div style="color: #cc33ff; margin-bottom: 2px;">모든 피해 증가 ${formatPercentSmart(st.allDmgInc)}</div>`;
	if (st.addSkillAtkChance) statsHtml += `<div style="color: #00ffff; margin-bottom: 2px;">추가 스킬피해 확률 ${formatPercentSmart(st.addSkillAtkChance)} <span style="color:#ff3333">(최대 30%)</span></div><div style="color: #ffffff; margin-bottom: 10px; line-height: 1.3;">기본 공격시에 추가 스킬공격 확률에 따라<br><span style="color:#6666ff;">공격력 x${(st.addSkillAtkMult / 100).toFixed(2)}</span>의 스킬피해를 입힙니다.</div>`;
	if (st.basicCritChance) statsHtml += `<div style="color: #ffcc00; margin-bottom: 2px;">평타 치명타 확률 ${formatPercentSmart(st.basicCritChance)} <span style="color:#ff3333">(최대 50%)</span></div><div style="color: #ffffff; margin-bottom: 10px; line-height: 1.3;">기본 공격시에 평타 치명타 확률에 따라<br><span style="color:#ff6666;">공격력 x${(st.basicCritDmg / 100).toFixed(2)}</span>의 물리피해를 입힙니다.</div>`;

	let customEquipHtml = item.equipTextInfo
		? `<div style="color: #ffffff; margin-bottom: 10px;">${item.equipTextInfo}</div>`
		: `<div style="color: #ff66cc;">${item.equipText || "장비"}은(는)</div>
       <div style="color: #ffffff; margin-bottom: 10px;"><span style="color:#ffcc00;">${item.equipLimit || 1}개</span>까지 장착 가능합니다.</div>`;

	let html = `
    <div style="font-size: 13px; font-weight: bold; line-height: 1.4;">
        <div style="color: #ffcc00; font-size: 15px; margin-bottom: 2px;">${item.name} ${lvText}</div>
        <div style="color: #888888; font-size: 12px; margin-bottom: 10px;">클릭하여 관리창에서 장착/강화/이동할 수 있습니다.</div>
        <div style="color: #ff3333; margin-bottom: 10px;">[일반]</div>
        ${statsHtml}
        <div style="color: #ffcc00; margin-bottom: 10px; margin-top: 10px;">강화비용: ${costText}</div>
        ${customEquipHtml}
        <div style="color: #99ff99;">아이템 레벨: ${st.ilv}</div>
    </div>`;
	ui.tooltip.innerHTML = html;
	ui.tooltip.style.display = "block";
}

function hideTooltip() {
	if (ui.tooltip) ui.tooltip.style.display = "none";
}

function closeActionPanel() {
	selectedSlot = { type: null, index: -1 };
	if (ui.apEnhanceLog) ui.apEnhanceLog.innerHTML = "";
	if (ui.apPanel) ui.apPanel.classList.remove("is-stack-special-action");
	if (ui.apPanel) ui.apPanel.style.display = "none";
	renderUI();
}

function showConsumedSkillBookPanel(item) {
	selectedSlot = { type: null, index: -1 };
	if (ui.apName) ui.apName.innerText = `${item.name} (모두 사용함)`;
	if (ui.apImg && item.img) ui.apImg.src = item.img;
	if (ui.apStats) ui.apStats.innerHTML = `${buildSkillBookActionHtml(item)}<div style="color:#88ff88; margin-top:10px;">보유한 강화권을 모두 사용했습니다.</div>`;
	[ui.btnApReinforce1, ui.btnApReinforce20, ui.btnApReinforce50, ui.btnApReinforce200, ui.btnApSell].forEach((btn) => {
		if (btn) {
			btn.style.display = "block";
			btn.disabled = true;
		}
	});
	if (ui.btnApUse) {
		ui.btnApUse.style.display = "block";
		ui.btnApUse.disabled = true;
		ui.btnApUse.innerText = "모두 사용함";
	}
	if (ui.btnApDismantleZero) ui.btnApDismantleZero.style.display = "none";
	const btnMove = document.getElementById("btn-ap-move");
	if (btnMove) btnMove.style.display = "none";
	if (ui.apPanel) ui.apPanel.style.display = "block";
	renderUI();
}

function refreshActionPanelStats() {
	if (selectedSlot.index === -1 || !ui.apPanel) return;

	let targetArray = player.inventory;
	if (selectedSlot.type === "equip") targetArray = player.equipment;
	else if (selectedSlot.type === "storage") targetArray = player.storage;
	else if (selectedSlot.type === "trash") targetArray = player.trash;

	let item = targetArray[selectedSlot.index];
	if (!item) return;
	ui.apPanel.classList.remove("is-stack-special-action");

	let isTown = true;
	const btn20 = document.getElementById("btn-ap-reinforce20");
	const btn200 = document.getElementById("btn-ap-reinforce200");
	const btnUse = document.getElementById("btn-ap-use");
	const btnDismantleZero = ui.btnApDismantleZero;
	const btnSell = ui.btnApSell;

	// 버튼 표시 초기화
	if (btnSell) {
		btnSell.disabled = selectedSlot.type === "equip" || selectedSlot.type === "storage" || selectedSlot.type === "trash";
		btnSell.innerText =
			selectedSlot.type === "equip" ? "장착중 이동 불가" :
			selectedSlot.type === "storage" ? "보관함 이동불가" :
			selectedSlot.type === "trash" ? "이미 휴지통에 있음" :
			"휴지통으로 이동";
	}
	if (btn20) btn20.style.display = "block";
	if (ui.btnApReinforce50) ui.btnApReinforce50.style.display = "block";
	if (ui.btnApReinforce200) ui.btnApReinforce200.style.display = "block";
	if (ui.btnApReinforce1) ui.btnApReinforce1.style.display = "block";
	if (btnDismantleZero) {
		btnDismantleZero.style.display = "none";
		btnDismantleZero.disabled = true;
	}
	if (btnUse) {
		btnUse.style.display = "block";
		btnUse.disabled = selectedSlot.type === "storage" || selectedSlot.type === "trash";
		btnUse.innerText = selectedSlot.type === "storage" ? "보관함 사용불가" : selectedSlot.type === "trash" ? "휴지통 사용불가" : selectedSlot.type === "equip" ? "장착 해제" : item.type === "skill_book" ? "사용하기" : "장착하기";
	}

	if (ui.apName) {
		ui.apName.innerText = getDisplayNameWithLevel(item);
	}
	if (selectedSlot.type === "trash") {
		if (ui.apStats) {
			ui.apStats.innerHTML = `<div style="color:#ff99cc; margin-bottom:8px;">휴지통에 있는 아이템입니다.</div><div style="color:#aaa;">가방으로 복구하거나, 휴지통 비우기로 완전히 삭제할 수 있습니다.</div>`;
		}
		[ui.btnApReinforce1, btn20, ui.btnApReinforce50, ui.btnApReinforce200].forEach((btn) => {
			if (btn) {
				btn.innerHTML = "강화불가";
				btn.disabled = true;
			}
		});
		if (btnUse) {
			btnUse.style.display = "block";
			btnUse.disabled = true;
			btnUse.innerText = "휴지통 사용불가";
		}
		let btnMove = document.getElementById("btn-ap-move");
		if (btnMove) {
			btnMove.style.display = "block";
			btnMove.disabled = false;
			btnMove.innerText = "가방으로 복구";
		}
		if (btnSell) {
			btnSell.disabled = true;
			btnSell.innerText = "이미 휴지통에 있음";
		}
		return;
	}


	// 🌟 탈리스만/휘장 액션 패널 로직
	if (isTalismanLike(item) || isEmblemLike(item)) {
		let baseName = getCleanStackName(item);
		let info = getTalismanCategoryInfo(item);
		ui.apPanel.classList.add("is-stack-special-action");

		if (ui.apStats) ui.apStats.innerHTML = `<span style="color:#ff66cc;">${info.typeName} / ${info.slotName} 슬롯 전용 장비입니다.</span><br><br>${info.statsHtml}`;

		[btn20, ui.btnApReinforce50, ui.btnApReinforce200].forEach((btn) => {
			if (btn) {
				btn.style.display = "none";
				btn.disabled = true;
			}
		});

		if (item.level >= 6) {
			if (ui.btnApReinforce1) {
				ui.btnApReinforce1.innerHTML = "강화 MAX";
				ui.btnApReinforce1.disabled = true;
			}
		} else {
			let cost = Math.pow(2, item.level);
			let isSelfPlus0 = selectedSlot.type !== "equip" && item.level === 0;
			let needed = cost + (isSelfPlus0 ? 1 : 0);

			if (ui.btnApReinforce1) {
				ui.btnApReinforce1.innerHTML = `강화 1회<br><span style="font-size:11px; color:#ffcc00;">0강 ${baseName} ${needed}개</span>`;
				ui.btnApReinforce1.disabled = false;
			}
		}
		if (btnDismantleZero && item.level > 0 && selectedSlot.type !== "trash") {
			let refundCount = Math.pow(2, parseInt(item.level) || 0);
			btnDismantleZero.style.display = "block";
			btnDismantleZero.disabled = false;
			btnDismantleZero.innerHTML = `강화 초기화<br><span class="special-reset-refund-preview">+0 ${refundCount}개로 복원</span>`;
		}
	} else if (item.type === "skill_book") {
		if (ui.apStats) ui.apStats.innerHTML = buildSkillBookActionHtml(item);
		if (ui.btnApReinforce1) {
			ui.btnApReinforce1.innerHTML = "강화불가";
			ui.btnApReinforce1.disabled = true;
		}
		if (btn20) {
			btn20.innerHTML = "강화불가";
			btn20.disabled = true;
		}
		if (ui.btnApReinforce50) {
			ui.btnApReinforce50.innerHTML = "강화불가";
			ui.btnApReinforce50.disabled = true;
		}
		if (ui.btnApReinforce200) {
			ui.btnApReinforce200.innerHTML = "강화불가";
			ui.btnApReinforce200.disabled = true;
		}
	} else if (item.type === "special_equip") {
		let st = calcSpecialEquipStats(item);
		let nextSt = item.level < 20 ? calcSpecialEquipStats({ ...item, level: item.level + 1 }) : st;
		let cost = getEnhanceCost(item);
		let canEnhance = isEnhanceableSpecialEquip(item);
		let category = getSpecialEquipCategoryPresentation(item);

		if (ui.apStats) {
			let statsHtml = `<div style="color:${category.color}; margin-bottom:8px;">${category.label} ${category.description}</div><div class="ap-stat-list">${buildSpecialEquipStatsHtml(item, true)}</div>`;
			if (canEnhance) {
				statsHtml += item.level >= 20 ? `<div class="ap-enhance-prob">강화 MAX</div>` : `<div class="ap-enhance-prob">강화 성공 확률: ${getEnhanceProbDisplay(item.level, item)}</div>`;
				if (item.level < 20 && nextSt) {
					let diffs = [];
					const addDiff = (label, key, suffix = "%") => {
						let diff = (nextSt[key] || 0) - (st[key] || 0);
						if (!diff) return;
						let text = key === "attack" ? `+${formatNumberDecimal ? formatNumberDecimal(diff, 2) : formatNumber(diff)}` : `+${formatPercentSmart(diff, 3)}`;
						diffs.push(`<span style="color:#aaa; margin-right:10px;">${label} <span style="color:#88ff88;">${text}</span></span>`);
					};
					addDiff("공격력", "attack");
					addDiff("스킬피해", "skillDmgAmp");
					addDiff("평타피해", "basicAtkDmgAmp");
					addDiff("평타치명증폭", "basicCritDmgAmp");
					addDiff("스킬치명확률", "skillCritChance");
					addDiff("스킬치명피해", "skillCritDmg");
					addDiff("추가스킬계수증폭", "addSkillAtkMultAmp");
					addDiff("스킬발동", "skillProcChanceInc");
					if (diffs.length) statsHtml += `<div style="margin-top:7px; line-height:1.45;">${diffs.join("<br>")}</div>`;
				}
			}
			ui.apStats.innerHTML = statsHtml;
		}

		if (!canEnhance) {
			if (ui.btnApReinforce1) {
				ui.btnApReinforce1.innerHTML = "강화불가";
				ui.btnApReinforce1.disabled = true;
			}
			if (btn20) {
				btn20.innerHTML = "강화불가";
				btn20.disabled = true;
			}
			if (ui.btnApReinforce50) {
				ui.btnApReinforce50.innerHTML = "강화불가";
				ui.btnApReinforce50.disabled = true;
			}
			if (ui.btnApReinforce200) {
				ui.btnApReinforce200.innerHTML = "강화불가";
				ui.btnApReinforce200.disabled = true;
			}
		} else if (item.level >= 20) {
			if (ui.btnApReinforce1) {
				ui.btnApReinforce1.innerHTML = "강화 MAX";
				ui.btnApReinforce1.disabled = true;
			}
			if (btn20) {
				btn20.innerHTML = "강화 MAX";
				btn20.disabled = true;
			}
			if (ui.btnApReinforce50) {
				ui.btnApReinforce50.innerHTML = "강화 MAX";
				ui.btnApReinforce50.disabled = true;
			}
			if (ui.btnApReinforce200) {
				ui.btnApReinforce200.innerHTML = "강화 MAX";
				ui.btnApReinforce200.disabled = true;
			}
		} else {
			if (ui.btnApReinforce1) {
				ui.btnApReinforce1.innerHTML = `강화 1회<br><span style="font-size:11px; color:#ffcc00;">${formatNumber(cost)} 골드</span>`;
				ui.btnApReinforce1.disabled = !isTown || player.gold < cost;
			}
			if (btn20) {
				btn20.innerHTML = `강화 20회<br><span style="font-size:11px; color:#ffcc00;">${formatNumber(cost * 20)} 골드</span>`;
				btn20.disabled = !isTown || player.gold < cost;
			}
			if (ui.btnApReinforce50) {
				ui.btnApReinforce50.innerHTML = `강화 50회<br><span style="font-size:11px; color:#ffcc00;">${formatNumber(cost * 50)} 골드</span>`;
				ui.btnApReinforce50.disabled = !isTown || player.gold < cost;
			}
			if (ui.btnApReinforce200) {
				ui.btnApReinforce200.innerHTML = `강화 200회<br><span style="font-size:11px; color:#ffcc00;">${formatNumber(cost * 200)} 골드</span>`;
				ui.btnApReinforce200.disabled = !isTown || player.gold < cost;
			}
		}
	} else {
		let st = calcItemStats(item);
		let nextSt = item.level < 20 ? calcItemStats({ ...item, level: item.level + 1 }) : st;
		let cost = getEnhanceCost(item);

		const statRows = [];
		const addStatRow = (label, value, diff, colorClass) => {
			statRows.push(`<div class="ap-stat-row ${colorClass || ""}"><span class="ap-stat-label">${label}</span><span class="ap-stat-value">${value}</span><span class="ap-stat-diff">${diff}</span></div>`);
		};

		addStatRow("공격력", formatNumber(st.attack), `+${formatNumber(nextSt.attack - st.attack)}`, "stat-red");
		if (st.skillDmgInc) addStatRow("스킬 피해", `${formatPercentSmart(st.skillDmgInc)}`, `+${formatPercentSmart(nextSt.skillDmgInc - st.skillDmgInc)}`, "stat-blue");
		if (st.allDmgInc) addStatRow("모든 피해", `${formatPercentSmart(st.allDmgInc)}`, `+${formatPercentSmart(nextSt.allDmgInc - st.allDmgInc)}`, "stat-purple");
		if (st.basicAtkDmgInc) addStatRow("평타 피해", `${formatPercentSmart(st.basicAtkDmgInc)}`, `+${formatPercentSmart(nextSt.basicAtkDmgInc - st.basicAtkDmgInc)}`, "stat-red");
		if (st.atkInc) addStatRow("공격력 추가", `${formatPercentSmart(st.atkInc)}`, `+${formatPercentSmart(nextSt.atkInc - st.atkInc)}`, "stat-red");
		if (st.addSkillAtkMult) addStatRow("스킬 계수", `x${(st.addSkillAtkMult / 100).toFixed(2)}`, `+x${((nextSt.addSkillAtkMult - st.addSkillAtkMult) / 100).toFixed(2)}`, "stat-teal");
		if (st.basicCritDmg) addStatRow("치명 계수", `x${(st.basicCritDmg / 100).toFixed(2)}`, `+x${((nextSt.basicCritDmg - st.basicCritDmg) / 100).toFixed(2)}`, "stat-yellow");

		let statsHtml = `<div class="ap-stat-list">${statRows.join("")}</div><div class="ap-enhance-prob">${item.level >= 20 ? "강화 MAX" : `강화 성공 확률: ${getEnhanceProbDisplay(item.level, item)}`}</div>`;

		if (ui.apStats) ui.apStats.innerHTML = statsHtml;

		if (item.level >= 20) {
			if (ui.btnApReinforce1) {
				ui.btnApReinforce1.innerHTML = "강화 MAX";
				ui.btnApReinforce1.disabled = true;
			}
			if (btn20) {
				btn20.innerHTML = "강화 MAX";
				btn20.disabled = true;
			}
			if (ui.btnApReinforce50) {
				ui.btnApReinforce50.innerHTML = "강화 MAX";
				ui.btnApReinforce50.disabled = true;
			}
			if (ui.btnApReinforce200) {
				ui.btnApReinforce200.innerHTML = "강화 MAX";
				ui.btnApReinforce200.disabled = true;
			}
		} else {
			if (ui.btnApReinforce1) {
				ui.btnApReinforce1.innerHTML = `강화 1회<br><span style="font-size:11px; color:#ffcc00;">${formatNumber(cost)} 골드</span>`;
				ui.btnApReinforce1.disabled = !isTown || player.gold < cost;
			}
			if (btn20) {
				btn20.innerHTML = `강화 20회<br><span style="font-size:11px; color:#ffcc00;">${formatNumber(cost * 20)} 골드</span>`;
				btn20.disabled = !isTown || player.gold < cost;
			}
			if (ui.btnApReinforce50) {
				ui.btnApReinforce50.innerHTML = `강화 50회<br><span style="font-size:11px; color:#ffcc00;">${formatNumber(cost * 50)} 골드</span>`;
				ui.btnApReinforce50.disabled = !isTown || player.gold < cost;
			}
			if (ui.btnApReinforce200) {
				ui.btnApReinforce200.innerHTML = `강화 200회<br><span style="font-size:11px; color:#ffcc00;">${formatNumber(cost * 200)} 골드</span>`;
				ui.btnApReinforce200.disabled = !isTown || player.gold < cost;
			}
		}
	}

	let btnMove = document.getElementById("btn-ap-move");
	if (selectedSlot.type === "equip") {
		if (btnMove) {
			btnMove.style.display = "block";
			btnMove.disabled = true;
			btnMove.innerText = "장착중 이동불가";
		}
	} else {
		if (btnMove) {
			btnMove.style.display = "block";
			btnMove.disabled = false;
			btnMove.innerText = selectedSlot.type === "storage" ? "가방으로" : selectedSlot.type === "trash" ? "가방으로 복구" : "보관함 넣기";
		}
	}

	if (ui.apStats) {
		ui.apStats.classList.remove("flash-effect");
		void ui.apStats.offsetWidth;
		ui.apStats.classList.add("flash-effect");
	}
}

function selectItem(type, index, isRefresh = false) {
	if (!isRefresh && selectedSlot.type === type && selectedSlot.index === index && ui.apPanel && ui.apPanel.style.display === "block") {
		closeActionPanel();
		return;
	}
	selectedSlot = { type, index };
	if (!isRefresh && ui.apEnhanceLog) ui.apEnhanceLog.innerHTML = `<div class="ap-enhance-log-title">강화 로그</div><div class="ap-enhance-log-empty">강화 결과가 여기에 표시됩니다.</div>`;
	let targetArray = player.inventory;
	if (type === "equip") targetArray = player.equipment;
	else if (type === "storage") targetArray = player.storage;
	else if (type === "trash") targetArray = player.trash;

	let item = targetArray[index];
	if (!item) {
		closeActionPanel();
		return;
	}
	if (ui.apImg) ui.apImg.src = item.img;
	refreshActionPanelStats();
	if (ui.apPanel) ui.apPanel.style.display = "block";
	renderUI();
}


function getMailboxRewardText(mail) {
	if (!mail) return "";
	if (mail.type === "gold") return `골드 ${formatNumber(mail.amount || 0)}`;
	if (mail.type === "item" && mail.item) {
		return `${getDisplayNameWithLevel(mail.item)} ${mail.item.count && mail.item.count > 1 ? `x${mail.item.count}` : ""}`.trim();
	}
	if (mail.type === "bundle" && Array.isArray(mail.items)) {
		return mail.items.map((item) => `${getDisplayNameWithLevel(item)} ${item.count && item.count > 1 ? `x${item.count}` : ""}`.trim()).join(", ");
	}
	return "보상 없음";
}

function renderMailbox() {
	if (!ui.mailboxContainer) return;
	if (!player.mailbox) player.mailbox = [];
	ui.mailboxContainer.innerHTML = "";

	if (ui.mailboxCount) ui.mailboxCount.innerText = player.mailbox.length;

	if (player.mailbox.length === 0) {
		ui.mailboxContainer.innerHTML = `<div class="mail-empty">도착한 우편이 없습니다.</div>`;
		return;
	}

	player.mailbox.forEach((mail, idx) => {
		let card = document.createElement("div");
		card.className = "mail-card";
		card.innerHTML = `
			<div class="mail-title">${mail.title || "우편"}</div>
			<div class="mail-body">${mail.body || "보상이 도착했습니다."}</div>
			<div class="mail-reward">보상: <span>${getMailboxRewardText(mail)}</span></div>
			<button class="mail-claim-btn" onclick="claimMail(${idx})">받기</button>
		`;
		ui.mailboxContainer.appendChild(card);
	});
}


function renderUI() {
	if (ui.equipNormal) ui.equipNormal.innerHTML = "";
	if (ui.equipSpecial) ui.equipSpecial.innerHTML = "";

	for (let i = 0; i < 15; i++) {
		let slot = document.createElement("div");
		let isSpecial = i >= 6;
		slot.className = "item-slot " + (isSpecial ? "empty-special" : "empty-normal");
		if (isSpecial) slot.innerHTML = specialSlotNames[i - 6];

		let item = player.equipment[i];
		if (item) {
			let lvBadge = getSlotBadgeHtml(item, true);

			slot.innerHTML = `<img src="${item.img}" alt="item">${lvBadge}`;
			if (selectedSlot.type === "equip" && selectedSlot.index === i) slot.classList.add("selected");
			slot.onmouseenter = () => showItemTooltip(item);
			slot.onmouseleave = hideTooltip;
			slot.oncontextmenu = (e) => {
				e.preventDefault();
				selectItem("equip", i, true);
			};
		} else {
			slot.oncontextmenu = (e) => e.preventDefault();
		}
		slot.onclick = () => selectItem("equip", i);

		if (isSpecial && ui.equipSpecial) ui.equipSpecial.appendChild(slot);
		else if (ui.equipNormal) ui.equipNormal.appendChild(slot);
	}

	if (ui.inventoryContainer) {
		ui.inventoryContainer.innerHTML = "";
		for (let i = 0; i < player.maxInventorySize; i++) {
			let slot = document.createElement("div");
			slot.className = "item-slot empty-inv";
			if (i < player.inventory.length) {
				let item = player.inventory[i];
				let lvText = getSlotBadgeHtml(item, false);
				slot.innerHTML = `<img src="${item.img}" alt="item">${lvText}`;
				if (selectedSlot.type === "inv" && selectedSlot.index === i) slot.classList.add("selected");
				slot.onmouseenter = () => showItemTooltip(item);
				slot.onmouseleave = hideTooltip;
				slot.oncontextmenu = (e) => {
					e.preventDefault();
					selectItem("inv", i);
				};
			} else {
				slot.oncontextmenu = (e) => e.preventDefault();
			}

			// 클릭: 관리창 열기. 장착/사용은 관리창 버튼으로 처리
			slot.onclick = () => {
				if (i < player.inventory.length) selectItem("inv", i);
			};

			ui.inventoryContainer.appendChild(slot);
		}
	}

	if (ui.inventoryCount) {
		ui.inventoryCount.innerText = player.inventory.length;
		if (player.inventory.length >= player.maxInventorySize) {
			ui.inventoryCount.style.color = "#ff4444";
			ui.inventoryCount.style.fontWeight = "bold";
		} else {
			ui.inventoryCount.style.color = "inherit";
			ui.inventoryCount.style.fontWeight = "normal";
		}
	}

	if (ui.storageContainer) {
		ui.storageContainer.innerHTML = "";
		for (let i = 0; i < player.maxStorageSize; i++) {
			let slot = document.createElement("div");
			slot.className = "item-slot empty-inv";
			if (i < player.storage.length) {
				let item = player.storage[i];
				let lvText = getSlotBadgeHtml(item, false);

				slot.innerHTML = `<img src="${item.img}" alt="item">${lvText}`;
				if (selectedSlot.type === "storage" && selectedSlot.index === i) slot.classList.add("selected");
				slot.onmouseenter = () => showItemTooltip(item);
				slot.onmouseleave = hideTooltip;
				slot.oncontextmenu = (e) => {
					e.preventDefault();
					selectItem("storage", i);
				};
			} else {
				slot.oncontextmenu = (e) => e.preventDefault();
			}
			slot.onclick = () => {
				if (i < player.storage.length) selectItem("storage", i);
			};
			ui.storageContainer.appendChild(slot);
		}
	}

	if (ui.storageCount) ui.storageCount.innerText = player.storage.length;

	if (ui.trashContainer) {
		ui.trashContainer.innerHTML = "";
		for (let i = 0; i < player.maxStorageSize; i++) {
			let slot = document.createElement("div");
			slot.className = "item-slot empty-inv trash-slot";
			if (i < player.trash.length) {
				let item = player.trash[i];
				let lvText = getSlotBadgeHtml(item, false);
				slot.innerHTML = `<img src="${item.img}" alt="item">${lvText}`;
				if (selectedSlot.type === "trash" && selectedSlot.index === i) slot.classList.add("selected");
				slot.onmouseenter = () => showItemTooltip(item);
				slot.onmouseleave = hideTooltip;
				slot.oncontextmenu = (e) => {
					e.preventDefault();
					selectItem("trash", i);
				};
			} else {
				slot.oncontextmenu = (e) => e.preventDefault();
			}
			slot.onclick = () => {
				if (i < player.trash.length) selectItem("trash", i);
			};
			ui.trashContainer.appendChild(slot);
		}
	}

	if (ui.trashCount) ui.trashCount.innerText = player.trash.length;

	renderMailbox();
}

function updateCombatUI() {
	let maxHpVal = 100;
	let curHpVal = 0;
	if (currentZoneType === "boss_fight" && currentBoss) {
		maxHpVal = currentBoss.maxHp;
		curHpVal = currentBossHp;
	} else if (currentZoneType === "field" && zones[currentZoneIndex]) {
		maxHpVal = zones[currentZoneIndex].maxHp;
		curHpVal = currentEnemy.hp;
	}

	if (currentZoneType === "boss_empty" || currentZoneType === "town") {
		maxHpVal = 0;
		curHpVal = 0;
	}
	if (isNaN(curHpVal)) curHpVal = maxHpVal;

	if (ui.enemyHpText) ui.enemyHpText.innerText = `${formatNumber(curHpVal)} / ${formatNumber(maxHpVal)}`;
	if (ui.enemyHpBar) {
		const hpPercent = maxHpVal === 0 ? 0 : (curHpVal / maxHpVal) * 100;
		ui.enemyHpBar.style.width = Math.max(hpPercent, 0) + "%";
	}
}

function updateGoldUI() {
	if (ui.playerGold) ui.playerGold.innerText = formatNumber(player.gold);
}


function formatRecordDuration(ms) {
	ms = Math.max(0, Math.floor(Number(ms) || 0));
	const totalSec = Math.floor(ms / 1000);
	const d = Math.floor(totalSec / 86400);
	const h = Math.floor((totalSec % 86400) / 3600);
	const m = Math.floor((totalSec % 3600) / 60);
	const s = totalSec % 60;
	if (d > 0) return `${d}일 ${h}시간 ${m}분`;
	if (h > 0) return `${h}시간 ${m}분 ${s}초`;
	if (m > 0) return `${m}분 ${s}초`;
	return `${s}초`;
}

function formatRecordDurationNoSeconds(ms) {
	ms = Math.max(0, Math.floor(Number(ms) || 0));
	const totalMin = Math.floor(ms / 60000);
	const d = Math.floor(totalMin / 1440);
	const h = Math.floor((totalMin % 1440) / 60);
	const m = totalMin % 60;
	return `${d}일 ${h}시간 ${m}분`;
}

function formatRecordGoldNumber(value) {
	const text = formatNumber(value || 0);
	return text.endsWith("A") ? text.slice(0, -1) : text;
}

function formatRecordCountNumber(value) {
	return String(Math.floor(Number(value) || 0));
}

function formatRecordSnapshotTime(ts) {
	if (!ts) return "아직 저장된 기록 없음";
	const d = new Date(ts);
	const pad = (n) => String(n).padStart(2, "0");
	return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function getRecordTopEntry(map) {
	if (!map || typeof map !== "object") return null;
	let bestKey = "";
	let bestVal = 0;
	Object.entries(map).forEach(([key, val]) => {
		val = Number(val) || 0;
		if (val > bestVal) {
			bestKey = key;
			bestVal = val;
		}
	});
	return bestKey ? { key: bestKey, value: bestVal } : null;
}

function getCodexBaseName(drop) {
	if (!drop) return "";
	let name = drop.name || "";
	if (typeof getBaseStackName === "function") name = getBaseStackName(drop);
	return String(name).replace(/\s+\+\d+$/, "").trim();
}

function getCodexCategory(drop) {
	const name = (drop && drop.name) || "";
	if (drop && (drop.isTalisman || drop.isEmblem || name.includes("탈리스만") || name.includes("빛나는 휘장"))) return "탈리스만/휘장";
	if (name.includes("아바타")) return "아바타류";
	if (drop && drop.type === "special_equip") return "특수장비류";
	if (drop && drop.type === "skill_book") return "스킬강화권";
	return "보스 장비";
}

function getCodexItems() {
	const map = new Map();
	const categoryOrder = {
		"보스 장비": 1,
		"탈리스만/휘장": 2,
		"아바타류": 3,
		"특수장비류": 4,
		"스킬강화권": 5,
	};
	const addItem = (key, category, source, order, sourceVisible = true) => {
		if (!key) return;
		if (!map.has(key)) map.set(key, { key, category, sources: new Set(), order: order ?? 999999 });
		const target = map.get(key);
		target.order = Math.min(target.order, order ?? 999999);
		if (source && sourceVisible) target.sources.add(source);
	};

	// 초보자 장비는 항상 도감 첫 번째입니다.
	addItem("리버레이션 스태프", "보스 장비", "초보자 지원", 0, true);

	[...(bossList || []), ...(specialBossList || [])].forEach((boss) => {
		const bossOrder = boss && boss.isSpecial ? 50000 + (boss.id || 0) * 100 : (boss && boss.id ? boss.id * 100 : 99900);
		(boss.drops || []).forEach((drop, dropIdx) => {
			const base = getCodexBaseName(drop);
			const category = getCodexCategory(drop);
			const name = drop.name || "";
			const isStackSpecial = drop.isTalisman || drop.isEmblem || name.includes("탈리스만") || name.includes("빛나는 휘장");
			const sourceVisible = category !== "탈리스만/휘장";
			const order = bossOrder + dropIdx;
			if (isStackSpecial) {
				for (let lvl = 0; lvl <= 6; lvl++) addItem(`${base} +${lvl}`, category, boss.name, order + lvl / 100, sourceVisible);
			} else {
				addItem(base, category, boss.name, order, sourceVisible);
			}
		});
	});

	return Array.from(map.values()).map((it) => ({
		...it,
		sources: Array.from(it.sources),
		categorySort: categoryOrder[it.category] || 99,
	})).sort((a, b) => {
		if (a.categorySort !== b.categorySort) return a.categorySort - b.categorySort;
		if (a.order !== b.order) return a.order - b.order;
		return a.key.localeCompare(b.key, "ko");
	});
}

function getCollectionStats() {
	const records = typeof ensurePlayerRecords === "function" ? ensurePlayerRecords() : (player.records || {});
	const codex = getCodexItems();
	const owned = codex.filter((it) => records.collection && records.collection[it.key]).length;
	const total = codex.length;
	const percent = total ? ((owned / total) * 100).toFixed(1) : "0.0";
	return { codex, owned, total, percent };
}

let codexViewFilter = "all";

function renderTownRecordModal() {
	if (typeof tickPlayTimeRecord === "function") tickPlayTimeRecord();
	const liveRecords = typeof ensurePlayerRecords === "function" ? ensurePlayerRecords() : (player.records || {});
	const records = typeof getRecordSnapshotForView === "function" ? getRecordSnapshotForView() : liveRecords;
	const snapshotAt = liveRecords.recordSnapshotUpdatedAt || 0;
	const content = document.getElementById("town-record-content");
	if (!content) return;

	const mostFail = getRecordTopEntry(records.enhanceFailByItem);
	const mostMonster = getRecordTopEntry(records.monsterKillsByName);
	const mostBoss = getRecordTopEntry(records.bossKillsByName);
	const dry = getRecordTopEntry(records.itemDryStreakByName);

	const row = (label, value) => `
		<div class="record-row">
			<div class="record-label">${label}</div>
			<div class="record-value">${value}</div>
		</div>`;

	content.innerHTML = `
		<div class="record-summary codex-summary">
			<div>현재 표시 기준 (저장 시점)</div>
			<strong>${formatRecordSnapshotTime(snapshotAt)}</strong>
		</div>
		<div class="record-grid">
			${row("총 플레이 시간", formatRecordDuration(records.playTimeMs || 0))}
			${row("총 획득 골드", formatRecordGoldNumber(records.totalGoldEarned || 0))}
			${row("가장 많이 강화 실패한 아이템", mostFail ? `${mostFail.key} <span>(${formatRecordCountNumber(mostFail.value)}회)</span>` : "-")}
			${row("총 처치 몬스터 수", formatRecordCountNumber(records.totalMonsterKills || 0))}
			${row("가장 많이 처치한 몬스터", mostMonster ? `${mostMonster.key} <span>(${formatRecordCountNumber(mostMonster.value)}회)</span>` : "-")}
			${row("총 보스 처치 수", formatRecordCountNumber(records.totalBossKills || 0))}
			${row("가장 많이 처치한 보스", mostBoss ? `${mostBoss.key} <span>(${formatRecordCountNumber(mostBoss.value)}회)</span>` : "-")}
			${row("가장 오래 안나온 아이템", dry ? `${dry.key} <span>(${formatRecordCountNumber(dry.value)}회)</span>` : "-")}
		</div>
	`;
}

function renderTownCodexModal() {
	const records = typeof ensurePlayerRecords === "function" ? ensurePlayerRecords() : (player.records || {});
	const content = document.getElementById("town-codex-content");
	if (!content) return;
	const { codex, owned, total, percent } = getCollectionStats();
	const groups = {};
	codex.forEach((item) => {
		const has = records.collection && records.collection[item.key];
		if (codexViewFilter === "owned" && !has) return;
		if (codexViewFilter === "missing" && has) return;
		if (!groups[item.category]) groups[item.category] = [];
		groups[item.category].push(item);
	});

	const groupHtml = Object.entries(groups).map(([category, items]) => {
		const allInCategory = codex.filter((it) => it.category === category);
		const ownedCount = allInCategory.filter((it) => records.collection && records.collection[it.key]).length;
		return `
			<div class="codex-group">
				<div class="codex-group-title">${category} <span>${ownedCount}/${allInCategory.length}</span></div>
				<div class="codex-list">
					${items.map((it) => {
						const has = records.collection && records.collection[it.key];
						const reveal = !!window.isCodexRevealMode;
						const sourceRaw = it.sources && it.sources.length ? it.sources.slice(0, 2).join(", ") : "";
						const source = sourceRaw ? ((has || reveal) ? sourceRaw : "????") : "";
						return `<div class="codex-item ${has ? "owned" : reveal ? "revealed" : "locked"}">
							<span class="codex-state">${has ? "획득" : reveal ? "공개" : "미획득"}</span>
							<span class="codex-name">${(has || reveal) ? it.key : "????"}</span>
							<span class="codex-source">${source}</span>
						</div>`;
					}).join("")}
				</div>
			</div>`;
	}).join("");

	const bonus = (owned * 0.1).toFixed(2).replace(/\.00$/, "").replace(/(\.\d)0$/, "$1");
	const filterBtn = (filter, label) => `<button class="codex-filter-btn ${codexViewFilter === filter ? "is-on" : "is-off"}" onclick="setCodexViewFilter('${filter}')">${label}</button>`;

	content.innerHTML = `
		<div class="codex-sticky-summary">
			<div class="codex-summary-row">
				<div class="codex-summary">
					<div>획득한 아이템 수집률</div>
					<strong>${owned} / ${total} (${percent}%)</strong>
				</div>
				<div class="codex-summary codex-bonus-summary">
					<div>현재 도감 보너스</div>
					<strong>+${bonus}%</strong>
				</div>
			</div>
			<div class="codex-toolbar codex-filter-toolbar">
				${filterBtn("owned", "획득한 도감만 보기")}
				${filterBtn("missing", "미획득 도감만 보기")}
				${filterBtn("all", "전체 도감 보기")}
			</div>
		</div>
		${groupHtml || `<div class="codex-empty-view">조건에 맞는 도감 항목이 없습니다.</div>`}
	`;
}

function setCodexViewFilter(filter) {
	codexViewFilter = filter || "all";
	renderTownCodexModal();
}

function getEquippedItemLevelTotal() {
	return (player.equipment || []).reduce((sum, item) => {
		// 아이템 레벨 랭킹은 일반 장비(type: normal)만 계산합니다.
		// 탈리스만/휘장/특수장비/아바타/스킬북은 강화 수치와 관계없이 0으로 봅니다.
		if (!item || item.type !== "normal") return sum;
		const lvl = parseInt(item.level) || 0;
		const ilv = (item.baseIlv || 0) + lvl + (lvl >= 20 ? 9 : 0);
		return sum + ilv;
	}, 0);
}

function getCurrentRankingHourKey() {
	const d = new Date();
	const half = d.getMinutes() < 30 ? 0 : 30;
	return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}-${d.getHours()}-${half}`;
}

function refreshRankingSnapshot(force = false) {
	const records = typeof ensurePlayerRecords === "function" ? ensurePlayerRecords() : (player.records || {});
	const hourKey = getCurrentRankingHourKey();
	if (!records.rankingSnapshot || force || records.rankingSnapshotHourKey !== hourKey) {
		if (typeof tickPlayTimeRecord === "function") tickPlayTimeRecord();
		records.rankingSnapshot = {
			itemLevelTotal: getEquippedItemLevelTotal(),
			playTimeMs: records.playTimeMs || 0,
			updatedAt: Date.now(),
		};
		records.rankingSnapshotHourKey = hourKey;
	}
	return records.rankingSnapshot;
}

function formatRankingRefreshTime(ts) {
	const d = ts ? new Date(ts) : new Date();
	const pad = (n) => String(n).padStart(2, "0");
	const minute = d.getMinutes() < 30 ? "00" : "30";
	return `${pad(d.getHours())}:${minute}`;
}

function renderTownRankingModal() {
	const content = document.getElementById("town-ranking-content");
	if (!content) return;
	const nickname = player.nickname || "플레이어";
	const snapshot = refreshRankingSnapshot(false);

	content.innerHTML = `
		<div class="ranking-note">현재는 로컬 환경이라 내 기록만 표시됩니다. 서버 연결 후 전체 유저 랭킹으로 확장하면 됩니다.<br><span>랭킹 갱신시간: 매시 정각/30분 · 현재 표시 기준 ${formatRankingRefreshTime(snapshot.updatedAt)}</span></div>
		<div class="ranking-section">
			<div class="ranking-title">아이템 레벨 랭킹 <span>(장착된 아이템레벨 총합)</span></div>
			<div class="ranking-row ranking-total-row self">
				<span class="rank-no">1</span>
				<span class="rank-name"><span class="ranking-nickname">${nickname}</span></span>
				<span class="rank-score">${formatRecordCountNumber(snapshot.itemLevelTotal || 0)}</span>
			</div>
		</div>
		<div class="ranking-section">
			<div class="ranking-title">총 플레이 시간 랭킹</div>
			<div class="ranking-row ranking-total-row self">
				<span class="rank-no">1</span>
				<span class="rank-name"><span class="ranking-nickname">${nickname}</span></span>
				<span class="rank-score">${formatRecordDurationNoSeconds(snapshot.playTimeMs || 0)}</span>
			</div>
		</div>
	`;
}

function openTownRecordModal() {
	renderTownRecordModal();
	const modal = document.getElementById("town-record-modal");
	if (modal) modal.style.display = "flex";
}

function openTownCodexModal() {
	renderTownCodexModal();
	const modal = document.getElementById("town-codex-modal");
	if (modal) modal.style.display = "flex";
}

function openTownRankingModal() {
	renderTownRankingModal();
	const modal = document.getElementById("town-ranking-modal");
	if (modal) modal.style.display = "flex";
}

function closeTownModal(id) {
	const modal = document.getElementById(id);
	if (modal) modal.style.display = "none";
}

function renderTownHub() {
	const hub = document.getElementById("town-hub-panel");
	if (!hub) return;
	hub.style.display = currentZoneType === "town" ? "block" : "none";

	const mailCount = document.getElementById("town-mail-count");
	if (mailCount) {
		const count = player.mailbox ? player.mailbox.length : 0;
		mailCount.innerText = count;
		mailCount.style.display = count > 0 ? "inline-flex" : "none";
	}
}

function updateFullUI() {
	if (typeof updateAutoSpecialBossButton === "function") updateAutoSpecialBossButton();
	if (typeof refreshOnOffButtonVisuals === "function") refreshOnOffButtonVisuals();
	let zoneData = zones[currentZoneIndex];
	let t = getTotals();
	const nav = document.querySelector(".zone-nav");
	const fieldInfo = document.getElementById("field-info-panel");
	const bossInfo = document.getElementById("boss-info-panel");
	const bossCtrlBtns = document.getElementById("boss-control-btns");
	const imgBox = document.getElementById("enemy-image-placeholder");
	const hpContainer = document.querySelector(".hp-bar-container");

	if (currentZoneType === "boss_fight" && currentBoss) {
		if (nav) nav.style.display = "none";
		if (fieldInfo) fieldInfo.style.display = "none";
		if (bossInfo) bossInfo.style.display = "block";
		if (bossCtrlBtns) bossCtrlBtns.style.display = "flex";
		if (hpContainer) hpContainer.style.display = "block";
		if (ui.zoneTitle) ui.zoneTitle.innerText = currentBoss.isSpecial ? `[특수 보스존]` : `[보스존]`;
		if (ui.enemyName) {
			ui.enemyName.style.display = "block";
			ui.enemyName.innerText = currentBoss.name;
		}
		if (imgBox) {
			imgBox.style.display = "block";
			imgBox.style.background = `url('${currentBoss.img}') center/cover`;
		}
		if (bossInfo) bossInfo.innerHTML = `<div style="color: #ffcc00; font-size: 16px; font-weight: bold; margin-bottom: 5px;">${currentBoss.title}</div><div style="color: #a3e354; margin-bottom: 2px;">${currentBoss.desc1}</div><div style="color: #ffcc00; margin-left: 10px; margin-bottom: 2px;">${currentBoss.desc2}</div><div style="color: #ffcc00; margin-left: 10px; margin-bottom: 15px;">${currentBoss.desc3}</div><div style="color: #d86cf5; margin-bottom: 5px;">${currentBoss.dropTitle}</div><div style="color: #ffcc00; margin-bottom: 15px; line-height: 1.3;">${currentBoss.dropsList.join("<br>")}</div>`;
	} else if (currentZoneType === "boss_empty") {
		if (nav) nav.style.display = "none";
		if (fieldInfo) fieldInfo.style.display = "none";
		if (bossInfo) bossInfo.style.display = "none";
		if (bossCtrlBtns) bossCtrlBtns.style.display = "flex";
		if (hpContainer) hpContainer.style.display = "none";
		if (ui.zoneTitle) ui.zoneTitle.innerText = `[빈 보스존]`;
		if (ui.enemyName) {
			ui.enemyName.style.display = "block";
			ui.enemyName.innerText = `보스 대기중`;
		}
		if (imgBox) {
			imgBox.style.display = "block";
			imgBox.style.background = `#111`;
		}
	} else if (currentZoneType === "town") {
		if (nav) nav.style.display = "none";
		if (fieldInfo) fieldInfo.style.display = "none";
		if (bossInfo) bossInfo.style.display = "none";
		if (bossCtrlBtns) bossCtrlBtns.style.display = "none";
		if (hpContainer) hpContainer.style.display = "none";
		if (ui.zoneTitle) ui.zoneTitle.innerText = `마을`;
		if (ui.enemyName) ui.enemyName.style.display = "none";
		if (imgBox) imgBox.style.display = "none";
	} else {
		if (nav) nav.style.display = "flex";
		if (fieldInfo) fieldInfo.style.display = "block";
		if (bossInfo) bossInfo.style.display = "none";
		if (bossCtrlBtns) bossCtrlBtns.style.display = "none";
		if (hpContainer) hpContainer.style.display = "block";
		if (ui.zoneTitle) ui.zoneTitle.innerText = zoneData.name;
		if (ui.enemyName) ui.enemyName.style.display = "none";
		if (ui.infoGold) ui.infoGold.innerHTML = getGoldRewardDisplay(zoneData.goldReward);
		if (imgBox) {
			imgBox.style.display = "block";
			imgBox.style.background = `#222`;
		}
	}

	renderTownHub();
	updateGoldUI();
	updateCombatUI();

	if (ui.sAtk) ui.sAtk.innerText = formatNumber(t.attack);
	if (ui.sAspd) ui.sAspd.innerText = t.aspd + "%";
	if (ui.sNcRate) ui.sNcRate.innerText = formatPercentSmart(t.basicCritChance);
	if (ui.sNdmg) ui.sNdmg.innerText = formatPercentSmart(t.basicAtkDmgInc);
	if (ui.sNcDmg) ui.sNcDmg.innerText = formatPercentSmart(t.basicCritDmg);
	if (ui.sSdmg) ui.sSdmg.innerText = formatPercentSmart(t.skillDmgInc);
	if (ui.sScRate) ui.sScRate.innerText = formatPercentSmart(t.skillCritChance);
	if (ui.sAllDmg) ui.sAllDmg.innerText = formatPercentSmart(t.allDmgInc);
	if (ui.sScDmg) ui.sScDmg.innerText = formatPercentSmart(t.skillCritDmg);
	if (ui.sSchance) ui.sSchance.innerText = formatPercentSmart(t.addSkillAtkChance);
	if (ui.sSmult) ui.sSmult.innerText = formatPercentSmart(t.addSkillAtkMult);
	if (ui.sGoldInc) ui.sGoldInc.innerText = formatPercentFixed1(t.goldInc);
	if (ui.sDropInc) ui.sDropInc.innerText = formatPercentFixed1(t.dropInc);
	if (ui.sEnhanceInc) ui.sEnhanceInc.innerText = formatPercentFixed1(t.enhanceInc);
	if (ui.sFarmGainInc) ui.sFarmGainInc.innerText = formatPercentFixed1(t.farmGainInc || 0);
	if (ui.sSkillProb) ui.sSkillProb.innerText = formatPercentSmart(t.skillProcChanceInc || 0);

	if (ui.hAtk) ui.hAtk.innerText = formatNumber(t.attack);
	if (ui.hSdmg) ui.hSdmg.innerText = formatPercentSmart(t.skillDmgInc);
	if (ui.hAspd) ui.hAspd.innerText = t.aspd + "%";
	if (ui.hAlldmg) ui.hAlldmg.innerText = formatPercentSmart(t.allDmgInc);
	if (ui.hNdmg) ui.hNdmg.innerText = formatPercentSmart(t.basicAtkDmgInc);

	renderUI();
	renderSkills(); // 🌟 장비 장착/해제/강화 시 스킬창의 탈리스만 보너스 즉각 동기화
}

function getBossByIdForReturn(id, isSpecial = false) {
	const pool = isSpecial ? specialBossList : bossList;
	return (pool || []).find((boss) => boss.id === id) || null;
}

function captureSpecialBossReturnState() {
	if (currentZoneType === "field" && typeof syncCurrentFieldHp === "function") syncCurrentFieldHp();

	return {
		zoneType: currentZoneType,
		zoneIndex: currentZoneIndex,
		fieldHp: currentEnemy ? currentEnemy.hp : 0,
		bossId: currentBoss ? currentBoss.id : null,
		bossIsSpecial: currentBoss ? !!currentBoss.isSpecial : false,
		bossHp: currentBossHp || 0,
		lastBossId: lastSummonedBoss ? lastSummonedBoss.id : null,
		lastBossIsSpecial: lastSummonedBoss ? !!lastSummonedBoss.isSpecial : false,
	};
}

function restoreSpecialBossReturnState(reason = "복귀") {
	const snap = specialBossReturnState;
	specialBossReturnState = null;
	autoSpecialBossInProgress = false;

	if (!snap) {
		currentBoss = null;
		currentBossHp = 0;
		currentZoneType = "boss_empty";
		clearInterval(attackInterval);
		updateFullUI();
		return;
	}

	currentZoneIndex = snap.zoneIndex !== undefined ? snap.zoneIndex : currentZoneIndex;

	if (snap.zoneType === "boss_fight" && snap.bossId && !snap.bossIsSpecial) {
		const boss = getBossByIdForReturn(snap.bossId, false);
		if (boss) {
			currentBoss = boss;
			currentBossHp = Math.max(1, Math.min(snap.bossHp || boss.maxHp, boss.maxHp));
			lastSummonedBoss = boss;
			currentZoneType = "boss_fight";
			addLog(`↩️ [특수보스 ${reason}] 직전 일반보스 ${boss.name} 전투로 복귀합니다.`, true);
			updateFullUI();
			startAutoAttack();
			return;
		}
	}

	if (snap.zoneType === "field") {
		currentBoss = null;
		currentBossHp = 0;
		currentZoneType = "field";
		currentEnemy.hp = getFieldEnemyHp(currentZoneIndex);
		addLog(`↩️ [특수보스 ${reason}] 직전 필드존으로 복귀합니다.`, true);
		updateFullUI();
		if (currentEnemy.hp > 0) startAutoAttack();
		else clearInterval(attackInterval);
		return;
	}

	if (snap.zoneType === "town") {
		currentBoss = null;
		currentBossHp = 0;
		currentZoneType = "town";
		clearInterval(attackInterval);
		addLog(`↩️ [특수보스 ${reason}] 마을로 복귀합니다.`, true);
		updateFullUI();
		return;
	}

	if (snap.zoneType === "boss_empty") {
		currentBoss = null;
		currentBossHp = 0;
		currentZoneType = "boss_empty";
		clearInterval(attackInterval);
		addLog(`↩️ [특수보스 ${reason}] 보스존으로 복귀합니다.`, true);
		updateFullUI();
		return;
	}

	currentBoss = null;
	currentBossHp = 0;
	currentZoneType = "boss_empty";
	clearInterval(attackInterval);
	updateFullUI();
}

function updateAutoSpecialBossButton() {
	const btn = document.getElementById("btn-auto-special-boss");
	if (!btn) return;
	btn.innerHTML = autoSpecialBossEnabled ? `특보 자동<br />ON` : `특보 자동<br />OFF`;
	btn.style.color = autoSpecialBossEnabled ? "#88ff88" : "#e0a8ff";
	if (typeof applyToggleButtonVisual === "function") applyToggleButtonVisual(btn, autoSpecialBossEnabled);
}

function openAutoSpecialBossModal() {
	const modal = document.getElementById("auto-special-modal");
	if (!modal) return;
	renderAutoSpecialBossList();
	modal.style.display = "flex";
}

function closeAutoSpecialBossModal() {
	const modal = document.getElementById("auto-special-modal");
	if (modal) modal.style.display = "none";
}

function toggleAutoSpecialBoss() {
	if (autoSpecialBossEnabled) {
		autoSpecialBossEnabled = false;
		autoSpecialBossId = null;
		updateAutoSpecialBossButton();
		addLog(`[특수보스 자동사냥] OFF`);
		return;
	}
	openAutoSpecialBossModal();
}

function renderAutoSpecialBossList() {
	const list = document.getElementById("auto-special-list");
	if (!list) return;
	list.innerHTML = "";
	(specialBossList || []).forEach((boss) => {
		const btn = document.createElement("button");
		btn.className = "auto-special-choice";
		const cdEnd = player.specialBossCD[boss.id] || 0;
		const remain = Math.max(0, Math.ceil((cdEnd - Date.now()) / 1000));
		btn.innerHTML = `
			<span class="auto-special-name">${boss.name}</span>
			<span class="auto-special-cd">${remain > 0 ? `쿨타임 ${remain}초` : "소환 가능"}</span>
		`;
		btn.onclick = () => startAutoSpecialBoss(boss.id);
		list.appendChild(btn);
	});
}

function startAutoSpecialBoss(bossId) {
	const boss = getBossByIdForReturn(bossId, true);
	if (!boss) {
		addLog(`[특수보스 자동사냥] 선택한 특수보스를 찾을 수 없습니다.`);
		return;
	}
	autoSpecialBossEnabled = true;
	autoSpecialBossId = boss.id;
	closeAutoSpecialBossModal();
	updateAutoSpecialBossButton();
	addLog(`[특수보스 자동사냥] ${boss.name} 자동사냥 ON`, true);
	tryStartAutoSpecialBoss(true);
}

function tryStartAutoSpecialBoss(forceLog = false) {
	if (!autoSpecialBossEnabled || !autoSpecialBossId) return false;
	if (currentBoss && currentBoss.isSpecial) return false;

	const boss = getBossByIdForReturn(autoSpecialBossId, true);
	if (!boss) {
		autoSpecialBossEnabled = false;
		autoSpecialBossId = null;
		updateAutoSpecialBossButton();
		return false;
	}

	const cdEnd = player.specialBossCD[boss.id] || 0;
	if (Date.now() < cdEnd) {
		if (forceLog) addLog(`[특수보스 자동사냥] ${boss.name} 쿨타임이 끝나면 자동으로 이동합니다.`);
		return false;
	}

	specialBossReturnState = captureSpecialBossReturnState();
	if (typeof closeAllGameplayModals === "function") closeAllGameplayModals();
	autoSpecialBossInProgress = true;
	currentBoss = boss;
	currentBossHp = boss.maxHp;
	lastSummonedBoss = boss;
	currentZoneType = "boss_fight";

	if (isBossPanelOpen) toggleBossPanel();
	if (isSpecialBossPanelOpen) toggleSpecialBossPanel();
	closeAutoSpecialBossModal();
	updateAutoSpecialBossButton();
	addLog(`👿 [특수보스 자동사냥] ${boss.name}에게 이동했습니다. 처치 후 직전 위치로 복귀합니다.`, true);
	updateFullUI();
	startAutoAttack();
	return true;
}

function toggleAutoBoss() {
	autoBossSummon = !autoBossSummon;
	const btn = document.getElementById("btn-auto-boss");
	if (autoBossSummon) {
		if (btn) btn.innerHTML = `자동소환<br /><span style="color:#88ff88">ON</span>`;
		addLog(`[시스템] 보스 자동 소환 활성화 (특수보스는 미적용)`);
	} else {
		if (btn) btn.innerHTML = `자동소환<br /><span style="color:#777">OFF</span>`;
		addLog(`[시스템] 보스 자동 소환 비활성화`);
	}
	if (typeof applyToggleButtonVisual === "function") applyToggleButtonVisual(btn, autoBossSummon);
}

function removeBoss() {
	if (currentBoss && currentZoneType === "boss_fight") {
		const removedBoss = currentBoss;
		if (removedBoss.isSpecial) {
			addLog(`[시스템] 특수보스(${removedBoss.name})를 제거했습니다. 직전 위치로 복귀합니다.`);
			currentBoss = null;
			currentBossHp = 0;
			restoreSpecialBossReturnState("제거");
			return;
		}

		addLog(`[시스템] 소환된 보스(${removedBoss.name})를 영구 제거했습니다.`);
		currentBoss = null;
		currentBossHp = 0;
		currentZoneType = "boss_empty";
		clearInterval(attackInterval);
		updateFullUI();
	} else {
		addLog(`[시스템] 제거할 보스가 없습니다.`);
	}
}

function toggleEquipDrop() {
	equipDropEnabled = !equipDropEnabled;
	const btn = document.getElementById("btn-equip-drop");
	if (equipDropEnabled) {
		if (btn) btn.innerHTML = `장비드랍<br /><span style="color:#88ff88">ON</span>`;
		addLog(`[명령어] 일반 보스를 잡으면 다시 장비를 <span style="color:#88ff88;">드랍</span>합니다.`);
	} else {
		if (btn) btn.innerHTML = `장비드랍<br /><span style="color:#ff4444">OFF</span>`;
		addLog(`<span style="color:#ccc;">[명령어] 일반 보스를 잡아도 장비를 <span style="color:#ff4444;">드랍</span>하지 않습니다. (특수보스는 항상 드랍)</span>`);
	}
	if (typeof applyToggleButtonVisual === "function") applyToggleButtonVisual(btn, equipDropEnabled);
}

function getCanonicalBossForSummon(boss) {
	if (!boss) return boss;
	const pool = boss.isSpecial ? specialBossList : bossList;
	return (pool || []).find((b) => b.id === boss.id) || boss;
}

function summonBoss(boss) {
	boss = getCanonicalBossForSummon(boss);
	let summonResult = typeof createBossSummonResult === "function"
		? createBossSummonResult({
			bossId: boss && boss.id,
			bossName: boss && boss.name,
			isSpecialBoss: !!(boss && boss.isSpecial),
			zoneType: currentZoneType,
		})
		: null;

	function failSummon(message, reason) {
		if (summonResult) {
			summonResult.ok = false;
			summonResult.data.reason = reason || "blocked";
			addResultLog(summonResult, message);
			return applyActionResultUi(summonResult);
		}
		addLog(message);
	}

	function applySummonSuccess(message, important = false) {
		if (summonResult) {
			addResultLog(summonResult, message, important);
			summonResult.data.bossId = currentBoss && currentBoss.id;
			summonResult.data.bossName = currentBoss && currentBoss.name;
			summonResult.data.currentBossHp = currentBossHp;
			summonResult.data.currentBossMaxHp = currentBoss && currentBoss.maxHp;
			summonResult.data.zoneType = currentZoneType;
			summonResult.data.lastSummonedBossId = lastSummonedBoss && lastSummonedBoss.id;
			requestUiRefresh(summonResult, "closeBossPanel");
			requestUiRefresh(summonResult, "closeSpecialBossPanel");
			requestUiRefresh(summonResult, "updateFullUI");
			requestUiRefresh(summonResult, "startAutoAttack");
			return applyActionResultUi(summonResult);
		}
		addLog(message, important);
		if (isBossPanelOpen) toggleBossPanel();
		if (isSpecialBossPanelOpen) toggleSpecialBossPanel();
		updateFullUI();
		startAutoAttack();
	}

	if (!boss) {
		return failSummon(`[시스템] 소환할 보스를 찾을 수 없습니다.`, "missing_boss");
	}

	if (boss && boss.isSpecial) {
		if (autoSpecialBossEnabled && autoSpecialBossId && autoSpecialBossId !== boss.id) {
			return failSummon(`[시스템] 특수보스 자동사냥 ON 상태에서는 선택된 특수보스만 소환할 수 있습니다.`, "auto_special_boss_locked");
		}

		if (currentZoneType !== "boss_empty" && currentZoneType !== "boss_fight") {
			return failSummon(`[시스템] 보스존에 입장한 후 소환해주세요.`, "not_in_boss_zone");
		}

		if (currentBoss && currentBoss.isSpecial && currentBoss.id !== boss.id) {
			return failSummon("[시스템] 이미 다른 특수보스가 소환되어 있습니다.", "another_special_boss_active");
		}

		const cdMs = player.specialBossCD[boss.id] || 0;
		if (Date.now() < cdMs) {
			if (summonResult) {
				summonResult.data.cooldownUntil = cdMs;
				summonResult.data.cooldownRemainMs = cdMs - Date.now();
			}
			return failSummon(`[시스템] 쿨타임이 진행 중입니다. 잠시 후 소환해주세요.`, "cooldown_active");
		}

		if (!currentBoss || !currentBoss.isSpecial) {
			specialBossReturnState = captureSpecialBossReturnState();
			if (summonResult) summonResult.data.returnStateCaptured = true;
		}

		currentBoss = boss;
		currentBossHp = boss.maxHp;
		lastSummonedBoss = boss;
		currentZoneType = "boss_fight";
		if (summonResult) summonResult.data.transition = { type: "special_boss_summoned", returnAfterEnd: true };
		return applySummonSuccess(`👿 [특수보스등장] ${boss.name}이(가) 소환되었습니다! 처치/제거 후 직전 위치로 복귀합니다.`);
	}

	if (currentZoneType !== "boss_empty" && currentZoneType !== "boss_fight") {
		return failSummon(`[시스템] 보스존에 입장한 후 소환해주세요.`, "not_in_boss_zone");
	}
	if (currentBoss && currentBoss.id !== boss.id) {
		return failSummon("[시스템] 이미 다른 보스가 소환되어 있습니다. 제거 후 소환하세요.", "another_boss_active");
	}
	if (!currentBoss) {
		currentBoss = boss;
		currentBossHp = boss.maxHp;
		if (summonResult) summonResult.data.transition = { type: "normal_boss_summoned" };
		lastSummonedBoss = boss;
		currentZoneType = "boss_fight";
		return applySummonSuccess(`👿 [보스등장] ${boss.name}이(가) 소환되었습니다!`);
	} else {
		const prevMaxHp = currentBoss.maxHp;
		currentBoss = boss;

		// 보스 maxHp 데이터가 바뀐 상태에서 같은 보스 전투를 재개하면,
		// 예전 currentBoss/currentBossHp가 남아 실제 체력이 boss.js와 다르게 보일 수 있어서 보정합니다.
		if (!currentBossHp || isNaN(currentBossHp) || currentBossHp <= 0 || currentBossHp > boss.maxHp || currentBossHp === prevMaxHp) {
			currentBossHp = boss.maxHp;
		}

		if (summonResult) summonResult.data.transition = { type: "normal_boss_resume", previousMaxHp: prevMaxHp };
		lastSummonedBoss = boss;
		currentZoneType = "boss_fight";
		return applySummonSuccess(`👿 [전투재개] ${boss.name} 전투를 이어서 진행합니다.`);
	}
}

function toggleBossPanel() {
	isBossPanelOpen = !isBossPanelOpen;
	let p = document.getElementById("boss-panel");
	if (p) p.style.display = isBossPanelOpen ? "block" : "none";
	if (isBossPanelOpen) {
		isFieldPanelOpen = false;
		isSpecialBossPanelOpen = false;
		let f = document.getElementById("field-panel");
		if (f) f.style.display = "none";
		let s = document.getElementById("special-boss-panel");
		if (s) s.style.display = "none";
		renderBossZone();
	}
}

function toggleSpecialBossPanel() {
	isSpecialBossPanelOpen = !isSpecialBossPanelOpen;
	let s = document.getElementById("special-boss-panel");
	if (s) s.style.display = isSpecialBossPanelOpen ? "block" : "none";
	if (isSpecialBossPanelOpen) {
		isFieldPanelOpen = false;
		isBossPanelOpen = false;
		let f = document.getElementById("field-panel");
		if (f) f.style.display = "none";
		let b = document.getElementById("boss-panel");
		if (b) b.style.display = "none";
		renderSpecialBossZone();
	}
}

function toggleFieldZone() {
	isFieldPanelOpen = !isFieldPanelOpen;
	let f = document.getElementById("field-panel");
	if (f) f.style.display = isFieldPanelOpen ? "block" : "none";
	if (isFieldPanelOpen) {
		isBossPanelOpen = false;
		isSpecialBossPanelOpen = false;
		let b = document.getElementById("boss-panel");
		if (b) b.style.display = "none";
		let s = document.getElementById("special-boss-panel");
		if (s) s.style.display = "none";
		renderFieldZone();
	}
}

function renderBossZone() {
	const grid = document.getElementById("boss-grid");
	if (!grid) return;
	grid.innerHTML = "";

	const totalPages = Math.max(1, Math.ceil(bossList.length / BOSS_PAGE_SIZE));
	currentBossPage = Math.max(0, Math.min(currentBossPage, totalPages - 1));

	const start = currentBossPage * BOSS_PAGE_SIZE;
	const pageBosses = bossList.slice(start, start + BOSS_PAGE_SIZE);
	const displayBosses = [...pageBosses, ...new Array(Math.max(0, BOSS_PAGE_SIZE - pageBosses.length)).fill(null)];

	displayBosses.forEach((boss) => {
		let slot = document.createElement("div");
		slot.className = "boss-slot";
		if (boss) {
			slot.innerHTML = `<img src="${boss.img}" alt="boss">`;
			slot.onclick = () => summonBoss(boss);
			slot.onmouseenter = (e) => {
				const tip = document.getElementById("boss-tooltip");
				tip.innerHTML = `<div style="color: #ffcc00; font-size: 16px; font-weight: bold; margin-bottom: 5px;">${boss.title}</div><div style="color: #a3e354; margin-bottom: 2px;">${boss.desc1}</div><div style="color: #ffcc00; margin-left: 10px; margin-bottom: 2px;">${boss.desc2}</div><div style="color: #ffcc00; margin-left: 10px; margin-bottom: 15px;">${boss.desc3}</div><div style="color: #fff; margin-bottom: 5px;">보스 체력: ${formatNumber(boss.maxHp)}</div><div style="color: #d86cf5; margin-bottom: 5px;">${boss.dropTitle}</div><div style="color: #ffcc00; margin-bottom: 15px; line-height: 1.3;">${boss.dropsList.join("<br>")}</div>`;
				tip.style.display = "block";
			};
			slot.onmouseleave = () => {
				document.getElementById("boss-tooltip").style.display = "none";
			};
		} else {
			slot.style.background = "#111";
		}
		grid.appendChild(slot);
	});

	const pageInfo = document.getElementById("boss-page-info");
	if (pageInfo) pageInfo.innerText = `${currentBossPage + 1} / ${totalPages}`;
}

window.changeBossPage = function (delta) {
	const totalPages = Math.max(1, Math.ceil(bossList.length / BOSS_PAGE_SIZE));
	const nextPage = currentBossPage + delta;
	if (nextPage < 0 || nextPage >= totalPages) return;
	currentBossPage = nextPage;
	renderBossZone();
};

function renderSpecialBossZone() {
	const grid = document.getElementById("special-boss-grid");
	if (!grid) return;
	grid.innerHTML = "";
	const displayBosses = [...specialBossList, ...new Array(12 - specialBossList.length).fill(null)];
	displayBosses.forEach((boss) => {
		let wrap = document.createElement("div");
		wrap.className = "boss-slot-wrapper";
		let slot = document.createElement("div");
		slot.className = "boss-slot";
		if (boss) {
			slot.innerHTML = `<img src="${boss.img}" alt="boss">`;
			if (autoSpecialBossEnabled && autoSpecialBossId && autoSpecialBossId !== boss.id) {
				slot.classList.add("disabled-special-slot");
				slot.onclick = () => addLog(`[시스템] 특수보스 자동사냥 ON 상태에서는 다른 특수보스를 소환할 수 없습니다.`);
			} else {
				slot.onclick = () => summonBoss(boss);
			}
			let cdText = document.createElement("div");
			cdText.className = "cooldown-text";
			cdText.id = `cd-text-${boss.id}`;
			slot.onmouseenter = (e) => {
				const tip = document.getElementById("boss-tooltip");
				tip.innerHTML = `<div style="color: #ffcc00; font-size: 16px; font-weight: bold; margin-bottom: 5px;">${boss.title}</div><div style="color: #a3e354; margin-bottom: 2px;">${boss.desc1}</div><div style="color: #ffcc00; margin-left: 10px; margin-bottom: 2px;">${boss.desc2}</div><div style="color: #ffcc00; margin-left: 10px; margin-bottom: 15px;">${boss.desc3}</div><div style="color: #fff; margin-bottom: 5px;">보스 체력: ${formatNumber(boss.maxHp)}</div><div style="color: #d86cf5; margin-bottom: 5px;">${boss.dropTitle}</div><div style="color: #ffcc00; margin-bottom: 15px; line-height: 1.3;">${boss.dropsList.join("<br>")}</div>`;
				tip.style.display = "block";
			};
			slot.onmouseleave = () => {
				document.getElementById("boss-tooltip").style.display = "none";
			};
			wrap.appendChild(slot);
			wrap.appendChild(cdText);
		} else {
			slot.style.background = "#111";
			wrap.appendChild(slot);
		}
		grid.appendChild(wrap);
	});
}

window.changeFieldPage = function (dir) {
	currentFieldPage += dir;
	if (currentFieldPage < 0) currentFieldPage = 0;
	if (currentFieldPage > maxFieldPage) currentFieldPage = maxFieldPage;
	renderFieldZone();
};

function renderFieldZone() {
	const container = document.getElementById("field-list-container");
	if (!container) return;
	container.innerHTML = "";

	const list = document.createElement("div");
	list.style.display = "flex";
	list.style.flexDirection = "column";

	let startGrp = currentFieldPage * 4;
	let endGrp = startGrp + 4;

	for (let i = startGrp; i < endGrp && i < fieldGroups.length; i++) {
		let row = document.createElement("div");
		row.className = "field-row";

		fieldGroups[i].forEach((zoneIdx) => {
			let field = zones[zoneIdx];
			if (!field) return;
			let btn = document.createElement("div");
			btn.className = "boss-slot";
			const fieldImg = field.img && field.img !== "undefined" ? field.img : `https://placehold.co/64x64/222/fff?text=Zone${field.level || zoneIdx + 1}`;
			btn.innerHTML = `<img src="${fieldImg}" alt="field">`;

			btn.onmouseenter = (e) => {
				const tip = document.getElementById("boss-tooltip");
				let html = `<div style="font-size: 14px; font-weight: bold; line-height: 1.4;">
          <div style="color: #fff; font-size: 16px; margin-bottom: 5px;">${field.name}</div>`;

				if (field.req) {
					html += `<div style="color: #a3e354; margin-bottom: 10px;">${field.name}를 시작합니다.</div>
            <div style="color: #ff3333; margin-bottom: 2px;">입장조건</div>
            <div style="color: #ff3333; margin-left: 10px; margin-bottom: 10px;">${field.req.text}</div>`;
				}

				if (field.farm) {
					let specHtml = field.farm.specialText ? `<div style="color: #ff99ff; margin-left: 10px;">${field.farm.specialText}</div>` : "";
					html += `<div style="color: #00ffff; margin-bottom: 2px;">공격력 상승량</div>
            <div style="color: #00ffff; margin-left: 10px;">${field.farm.prob * 100}% 확률로 ${field.farm.gain} 증가 (최대 ${field.farm.capText})</div>
            ${specHtml}`;
				}

				if (field.req || field.farm) {
					html += `<div style="margin-top: 10px; border-top: 1px dashed #555; padding-top: 8px;"></div>`;
				}

				html += `<div style="color: #fff; margin-bottom: 5px;">적 HP: ${formatNumber(field.maxHp)}</div>
          <div style="color: #ffcc00;">💰 획득 골드: ${getGoldRewardDisplay(field.goldReward)}</div>
        </div>`;

				tip.innerHTML = html;
				tip.style.display = "block";
			};

			btn.onmouseleave = () => {
				document.getElementById("boss-tooltip").style.display = "none";
			};

			btn.onclick = () => {
				if (field.req) {
					let pureAtk = player.farmAtkBonus || 0;
					if (pureAtk < field.req.minAtk || pureAtk > field.req.maxAtk) {
						addLog(`[시스템] 입장 조건(${field.req.text})을 만족하지 않아 입장할 수 없습니다.`);
						return;
					}
				}
				if (currentZoneType === "field") syncCurrentFieldHp();
				currentZoneType = "field";
				currentZoneIndex = zoneIdx;
				currentEnemy.hp = getFieldEnemyHp(currentZoneIndex);
				toggleFieldZone();
				updateFullUI();
				if (currentEnemy.hp > 0) startAutoAttack();
				else clearInterval(attackInterval);
				addLog(`[이동] ${field.name} 진입`);
			};
			row.appendChild(btn);
		});
		list.appendChild(row);
	}

	container.appendChild(list);

	let pageCtrl = document.createElement("div");
	pageCtrl.className = "field-pagination";
	pageCtrl.innerHTML = `
    <button class="sys-btn field-page-btn" onclick="changeFieldPage(-1)" ${currentFieldPage === 0 ? "disabled" : ""}>◀ 이전</button>
    <span style="font-weight:bold; color:#ffcc00;">${currentFieldPage + 1} / ${maxFieldPage + 1} 페이지</span>
    <button class="sys-btn field-page-btn" onclick="changeFieldPage(1)" ${currentFieldPage === maxFieldPage ? "disabled" : ""}>다음 ▶</button>
  `;
	container.appendChild(pageCtrl);
}

function formatSkillProcRateText(value) {
	let n = parseFloat(value) || 0;
	return `${n.toFixed(2).replace(/\.00$/, "").replace(/(\.\d)0$/, "$1")}%`;
}

function buildSkillProcChanceHtml(baseRate, totalInc) {
	const base = parseFloat(baseRate) || 0;
	const inc = parseFloat(totalInc) || 0;
	const finalRate = base * (1 + inc / 100);
	const added = Math.max(0, finalRate - base);
	return `<span class="skill-proc-final">${formatSkillProcRateText(finalRate)}</span> <span class="skill-proc-detail">(<span class="skill-proc-base">${formatSkillProcRateText(base)}</span>+<span class="skill-proc-added">${formatSkillProcRateText(added)}</span>)</span>`;
}

function renderSkills() {
	const grid = document.querySelector(".skill-slots-grid");
	if (!grid) return;
	grid.innerHTML = "";

	const getEquippedTalismanBonus = (slotIdx) => {
		let eq = player.equipment[slotIdx];
		return eq && isTalismanLike(eq) ? (parseInt(eq.level) || 0) + 1 : 0;
	};
	let tBonusA = getEquippedTalismanBonus(12);
	let tBonusB = getEquippedTalismanBonus(13);

	const skillData = typeof getRenderableSkillList === "function" ? getRenderableSkillList(player) : [];
	const currentSkills = typeof getCurrentCharacterSkills === "function" ? getCurrentCharacterSkills(player) : (player.skills || {});

	for (let i = 0; i < skillData.length; i++) {
		let div = document.createElement("div");
		div.className = "skill-slot-wrapper";
		let sk = { ...skillData[i] };
		let pSk = currentSkills && currentSkills[sk.id] ? currentSkills[sk.id] : { level: 0 };

		if (sk.id === "lightsabre" && pSk.isUpgraded) {
			sk.name = "극 귀검술 - 유성락";
			sk.key = "SQ";
			sk.img = "https://placehold.co/70x70/2ecc71/fff?text=SQ"; // 🌟 깨진 이미지 복구
			sk.description = "무수한 기의 검을 내려꽂습니다.";
			sk.effectHtml = "-기본 공격 시 0.5% 확률로 발동<br>-단일 적에게 스킬레벨 x 공격력 x 200000의 스킬데미지";
			sk.baseProcRate = 0.5;
		}
		if (sk.id === "ironStrike" && pSk.isUpgraded) {
			sk.name = "극 발검술 - 무형참";
			sk.key = "SW";
			sk.img = "https://placehold.co/70x70/27ae60/fff?text=SW"; // 🌟 깨진 이미지 복구
			sk.description = "무수한 무형의 검으로 적을 난도질합니다.";
			sk.effectHtml = "-기본 공격 시 0.5% 확률로 발동<br>-단일 적에게 스킬레벨 x 공격력 x 320000의 스킬데미지";
			sk.baseProcRate = 0.5;
		}

		// 🌟 레벨 합산 로직
		let baseLevel = pSk.level;
		let bonusLevel = 0;

		if (baseLevel > 0) {
			if (sk.id === "baldo" || sk.id === "illusionSword" || (sk.id === "lightsabre" && pSk.isUpgraded)) {
				bonusLevel = tBonusA;
			}
			if (sk.id === "deepSword" || sk.id === "tempestStrike" || (sk.id === "ironStrike" && pSk.isUpgraded)) {
				bonusLevel = tBonusB;
			}
		}

		let totalLevel = baseLevel + bonusLevel;

		// 썸네일은 합산 레벨(Lv.2) 유지, 툴팁 제목은 기본+탈리스만 보너스(1+1)로 분리 표기합니다.
		let badgeText = `${totalLevel}`;
		let tooltipLevelText = bonusLevel > 0
			? `${baseLevel}<span class="skill-tooltip-bonus-level">+${bonusLevel}</span>`
			: `${baseLevel}`;
		let filterStyle = pSk.level === 0 ? "filter: grayscale(100%) brightness(50%);" : "";

		// 🌟 썸네일에서 [단축키] 제거, Lv. 만 남김
		const mCdId = sk.id === "heavenlyStrike" ? "skill-cd-heavenlyStrike" : "";
		div.innerHTML = `<div class="skill-slot-icon"><img src="${sk.img}" style="width:100%; height:100%; ${filterStyle}"><div class="level-badge" style="z-index:2; font-size:11px; padding:2px 4px; background:rgba(0,0,0,0.85); border:1px solid #777;">Lv.${badgeText}</div></div><div class="skill-cooldown-text" ${mCdId ? `id="${mCdId}"` : ""}>&nbsp;</div>`;

		div.style.cursor = "help";
		div.style.position = "relative";

		div.onmouseenter = () => {
			const tip = document.getElementById("tooltip");
			let effHtml = sk.effectHtml || sk.eff || "";
			if (sk.baseProcRate !== undefined && sk.baseProcRate !== null) {
				const procHtml = buildSkillProcChanceHtml(sk.baseProcRate, getTotals().skillProcChanceInc || 0);
				effHtml = effHtml.replace(/기본 공격 시 [0-9.]+% 확률로 발동/, `기본 공격 시 ${procHtml} 확률로 발동`);
			}
			tip.innerHTML = `<div style="color:#3399ff; font-weight:bold; font-size:15px; margin-bottom:5px;">[${sk.key}] ${sk.name} 레벨 ${tooltipLevelText}</div><div style="color:#a3e354; margin-bottom:10px;">${sk.description || sk.desc || ""}</div><div style="color:#cc33ff; margin-bottom:5px;">[패시브]</div><div style="color:#00ffff;">${effHtml}</div>${pSk.level === 0 ? `<div style="color:#ff4444; margin-top:5px; font-weight:bold;">[미습득 상태] 스킬이 발동하지 않습니다.</div>` : ""}`;
			tip.style.display = "block";
		};
		div.onmouseleave = hideTooltip;

		grid.appendChild(div);
	}
}

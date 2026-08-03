/*
 * icon-utils.js
 *
 * 화면에 표시할 아이콘 URL과 저장 아이템의 아이콘을 이름 기준으로 정규화합니다.
 * - 실제 PNG가 준비되지 않은 항목에만 텍스트 아이콘을 fallback으로 사용합니다.
 * - 게임 밸런스/드랍/강화 계산에는 관여하지 않습니다.
 */

function iconTextUrl(text, bg = "333", fg = "FFF") {
	const safeText = String(text || "");
	const bgColor = String(bg).startsWith("#") ? String(bg) : `#${bg}`;
	const fgColor = String(fg).startsWith("#") ? String(fg) : `#${fg}`;
	const fontSize = safeText.length <= 3 ? 24 : safeText.length <= 5 ? 19 : 15;
	const escaped = safeText
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;");
	const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect width="64" height="64" fill="${bgColor}"/><rect x="1.5" y="1.5" width="61" height="61" fill="none" stroke="rgba(255,255,255,0.35)" stroke-width="2"/><text x="32" y="33" text-anchor="middle" dominant-baseline="middle" font-family="Arial, Helvetica, sans-serif" font-size="${fontSize}" font-weight="700" fill="${fgColor}">${escaped}</text></svg>`;
	return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

const SPECIAL_EQUIP_ASSET_BASE = "src/assets/special-equipment";
const SPECIAL_EQUIP_ASSET_VERSION = "361";
const NORMAL_EQUIP_ASSET_BASE = "src/assets/equipment";
const NORMAL_EQUIP_ASSET_VERSION = "368";
const BEGINNER_EQUIP_ASSET_VERSION = "369";
const SKILL_BOOK_ASSET_BASE = "src/assets/skill-books";
const SKILL_BOOK_ASSET_VERSION = "369";
const SKILL_BOOK_ICON_ASSET_BY_NAME = Object.freeze({
	"스킬강화권": "skill-book-q.png",
	"강력한 스킬강화권": "skill-book-w.png",
	"빛나는 스킬강화권": "skill-book-e.png",
	"화려한 스킬강화권": "skill-book-r.png",
	"찬란한 스킬강화권": "skill-book-t.png",
	"해방된 스킬강화권": "skill-book-f.png",
	"천공의 스킬강화권": "skill-book-d.png",
	"심연의 스킬강화권": "skill-book-sq.png",
	"-초월- 심연의 스킬강화권": "skill-book-sw.png",
	"-초월-심연의 스킬강화권": "skill-book-sw.png",
	"진 각성 스킬강화권": "skill-book-m.png",
});
const NORMAL_EQUIP_GROUP_ASSET_KEYS = Object.freeze({
	skill_all: "skill-all",
	atk_inc: "atk-inc",
	normal_dmg: "normal-dmg",
	skill_chance: "skill-chance",
	normal_crit: "normal-crit",
});
const NORMAL_EQUIPMENT_FAMILY_STAGE_GRADES = Object.freeze({
	21: "basic",
	22: "rare",
	23: "transcendent",
	24: "basic",
	25: "rare",
	26: "transcendent",
	30: "basic",
	31: "rare",
	35: "transcendent",
	36: "liberated",
});
const ITEM_FRAME_GRADE_CLASSES = [
	"item-frame-basic",
	"item-frame-uncommon",
	"item-frame-rare",
	"item-frame-transcendent",
	"item-frame-liberated",
	"item-frame-radiant",
	"item-frame-dark",
	"item-frame-luminous",
];

function getItemFrameGrade(item) {
	const name = String((item && item.name) || "");
	const tier = Number(item && item.tier);
	if (item && item.type === "normal" && Number.isInteger(tier)) {
		const familyStageGrade = NORMAL_EQUIPMENT_FAMILY_STAGE_GRADES[tier];
		if (familyStageGrade) return familyStageGrade;
	}
	if (name.startsWith("★초월 연옥★")) return "luminous";
	if (name.startsWith("★진 연옥★") || name.startsWith("★심연★")) return "dark";
	if (name.startsWith("★연옥★")) return "radiant";
	if (name.startsWith("-초월-")) return "transcendent";
	if (name.startsWith("-진-")) return "rare";
	if (name.startsWith("-현-")) return "uncommon";
	if (name.startsWith("[기본]")) return "basic";
	if (name.includes("영롱") || name.includes("천공") || name.includes("진 각성")) return "luminous";
	if (name.includes("짙은") || name === "심연의 스킬강화권") return "dark";
	if (name.includes("찬란") || name.includes("화려")) return "radiant";
	if (name.includes("해방")) return "liberated";
	if (name.includes("초월")) return "transcendent";
	if (name.includes("빛나는")) return "rare";
	if (name.includes("강력한")) return "uncommon";
	return "basic";
}

function getNormalEquipmentIconAssetName(item) {
	if (!item) return "";
	const name = String(item.name || "");
	if (name === "리버레이션 스태프" || String(item.equipGroup || "") === "beginner") {
		return "liberation-staff.png";
	}
	if (item.type !== "normal") return "";
	const tier = Number(item.tier);
	const groupKey = NORMAL_EQUIP_GROUP_ASSET_KEYS[String(item.equipGroup || "")];
	if (!Number.isInteger(tier) || tier < 1 || tier > 39 || !groupKey) return "";
	return `tier-${String(tier).padStart(2, "0")}-${groupKey}.png`;
}

function getNormalEquipmentIconUrl(item) {
	const assetName = getNormalEquipmentIconAssetName(item);
	if (!assetName) return "";
	const assetVersion = assetName === "liberation-staff.png" ? BEGINNER_EQUIP_ASSET_VERSION : NORMAL_EQUIP_ASSET_VERSION;
	return `${NORMAL_EQUIP_ASSET_BASE}/${assetName}?v=${assetVersion}`;
}

function getSkillBookIconUrl(name) {
	const assetName = SKILL_BOOK_ICON_ASSET_BY_NAME[String(name || "")];
	return assetName ? `${SKILL_BOOK_ASSET_BASE}/${assetName}?v=${SKILL_BOOK_ASSET_VERSION}` : "";
}

function normalizeItemIcon(item) {
	if (!item) return item;
	const skillBookIconUrl = getSkillBookIconUrl(item.name);
	if (skillBookIconUrl) {
		item.img = skillBookIconUrl;
		return item;
	}
	if (item.type === "special_equip" && typeof getSpecialEquipIconUrl === "function") {
		item.img = getSpecialEquipIconUrl(item);
		return item;
	}
	const normalIconUrl = getNormalEquipmentIconUrl(item);
	if (normalIconUrl) item.img = normalIconUrl;
	return item;
}

function normalizePlayerItemIcons(targetPlayer) {
	if (!targetPlayer || typeof targetPlayer !== "object") return targetPlayer;

	["inventory", "storage", "trash", "equipment"].forEach((containerName) => {
		const items = targetPlayer[containerName];
		if (!Array.isArray(items)) return;
		items.forEach((item) => {
			if (item) normalizeItemIcon(item);
		});
	});

	if (Array.isArray(targetPlayer.mailbox)) {
		targetPlayer.mailbox.forEach((mail) => {
			if (!mail || typeof mail !== "object") return;
			if (mail.item) normalizeItemIcon(mail.item);
			if (Array.isArray(mail.items)) {
				mail.items.forEach((item) => {
					if (item) normalizeItemIcon(item);
				});
			}
		});
	}

	return targetPlayer;
}

function applyEquipmentIconAssets() {
	const bossCollections = [];
	if (typeof bossList !== "undefined" && Array.isArray(bossList)) bossCollections.push(bossList);
	if (typeof specialBossList !== "undefined" && Array.isArray(specialBossList)) bossCollections.push(specialBossList);
	bossCollections.forEach((bossList) => {
		bossList.forEach((boss) => {
			if (!boss || !Array.isArray(boss.drops)) return;
			boss.drops.forEach((drop) => {
				normalizeItemIcon(drop);
				if (drop && drop.raw) normalizeItemIcon(drop.raw);
			});
		});
	});
}

function applyItemFrameClass(element, item) {
	if (!element || !element.classList) return "";
	element.classList.remove("item-grade-frame", ...ITEM_FRAME_GRADE_CLASSES);
	if (!item) return "";
	const grade = getItemFrameGrade(item);
	element.classList.add("item-grade-frame", `item-frame-${grade}`);
	element.dataset.itemFrameGrade = grade;
	return grade;
}

function getSpecialEquipIconInfo(item) {
	const name = (item && item.name) || "";
	if (item && (item.isEmblem || name.includes("빛나는 휘장"))) return { text: "EMB", bg: "8a6a00", fg: "ffffff" };
	if (name.includes("영롱")) return { text: "TB2", bg: "663388", fg: "ffffff" };
	if (name.includes("초월")) return { text: "TB1", bg: "663388", fg: "ffffff" };
	if (name.includes("찬란한")) return { text: "TA2", bg: "552266", fg: "ffffff" };
	if (name.includes("탈리스만") || (item && item.isTalisman)) return { text: "TA1", bg: "552266", fg: "ffffff" };
	return { text: "SP", bg: "552266", fg: "ffffff" };
}

function getSpecialEquipIconAssetName(item) {
	const name = String((item && item.name) || "");
	const slot = parseInt(item && item.specialSlotIdx);

	if ((item && item.isEmblem) || name.includes("빛나는 휘장")) return "emblem.png";

	if (name.includes("탈리스만") || (item && item.isTalisman)) {
		if (name.includes("영롱")) return "talisman-luminous.png";
		if (name.includes("찬란한")) return "talisman-radiant.png";
		if (name.includes("초월")) return "talisman-transcendent.png";
		return "talisman-basic.png";
	}

	const isRadiantAvatar = name.includes("찬란한");
	if (name.includes("클론 레어 아바타") || slot === 11) {
		return `clone-rare-avatar-${isRadiantAvatar ? "radiant" : "basic"}.png`;
	}
	if (name.includes("무기 아바타") || slot === 9) {
		return `weapon-avatar-${isRadiantAvatar ? "radiant" : "basic"}.png`;
	}
	if (name.includes("오라 아바타") || slot === 10) {
		return `aura-avatar-${isRadiantAvatar ? "radiant" : "basic"}.png`;
	}

	let equipmentType = "";
	if (name.includes("스태프") || slot === 6) equipmentType = "weapon";
	else if (name.includes("목걸이") || slot === 7) equipmentType = "necklace";
	else if (name.includes("반지") || slot === 8) equipmentType = "ring";
	if (!equipmentType) return "";

	let tier = "basic";
	if (name.includes("짙은")) tier = "dark";
	else if (name.includes("해방")) tier = "liberated";
	else if (name.includes("초월")) tier = "transcendent";
	return `${equipmentType}-${tier}.png`;
}

function getSpecialEquipIconUrl(item) {
	const assetName = getSpecialEquipIconAssetName(item);
	if (assetName) return `${SPECIAL_EQUIP_ASSET_BASE}/${assetName}?v=${SPECIAL_EQUIP_ASSET_VERSION}`;
	const icon = getSpecialEquipIconInfo(item);
	return iconTextUrl(icon.text, icon.bg, icon.fg);
}


function getSkillBookIconText(name) {
	if (name === "스킬강화권") return "Q";
	if (name === "강력한 스킬강화권") return "W";
	if (name === "빛나는 스킬강화권") return "E";
	if (name === "화려한 스킬강화권") return "R";
	if (name === "찬란한 스킬강화권") return "T";
	if (name === "해방된 스킬강화권") return "F";
	if (name === "천공의 스킬강화권") return "D";
	if (name === "심연의 스킬강화권") return "SQ";
	if (name === "-초월- 심연의 스킬강화권" || name === "-초월-심연의 스킬강화권") return "SW";
	if (name === "진 각성 스킬강화권") return "M";
	return "SK";
}

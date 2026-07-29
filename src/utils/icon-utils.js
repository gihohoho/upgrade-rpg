/*
 * icon-utils.js
 *
 * 화면에 표시할 임시 아이콘 URL을 만드는 유틸 모음입니다.
 * - 게임 밸런스/드랍/강화 계산에는 관여하지 않습니다.
 * - 나중에 실제 이미지 리소스 서버나 CDN을 붙일 때 이 파일부터 교체하면 됩니다.
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
const NORMAL_EQUIP_ASSET_VERSION = "364";
const NORMAL_EQUIP_ICON_ASSETS = Object.freeze({
	"어둠을 지배하는 고리": Object.freeze({
		basic: "dark-dominion-ring.png",
		jin: "dark-dominion-ring-jin.png",
		transcendent: "dark-dominion-ring-transcendent.png",
		purgatory: "dark-dominion-ring-purgatory.png",
		"true-purgatory": "dark-dominion-ring-true-purgatory.png",
		"transcendent-purgatory": "dark-dominion-ring-transcendent-purgatory.png",
	}),
	"올 엘리멘탈 크리스탈": "all-elemental-crystal.png",
	"군신의 가호가 담긴 보석": "war-god-blessing-jewel.png",
	"루나 베네딕티오": "luna-benedictio.png",
	"영창 : 불멸의 혼": "immortal-soul-chant.png",
	"마음을 새긴 바다": "engraved-sea-heart.png",
	"종말의 시간": "time-of-end.png",
	"광란을 품은 자": "embracing-frenzy.png",
	"세계수의 뿌리": "world-tree-root.png",
	"어나이얼레이터": "annihilator.png",
	"무의식 : 넥스의 몽환의 어둠": "nex-dream-darkness.png",
	"환영 : 넥스의 검은 기운": "nex-black-energy.png",
	"환영 : 넥스의 잠식된 의복": "nex-corrupted-garment.png",
	"원초의 꿈 : 스태프": "primal-dream-staff.png",
	"원초의 꿈 : 창": "primal-dream-spear.png",
});
const NORMAL_EQUIP_RANK_PREFIXES = [
	/^★초월 연옥★\s*/,
	/^★진 연옥★\s*/,
	/^★연옥★\s*/,
	/^★심연★\s*/,
	/^-초월-\s*/,
	/^-진-\s*/,
	/^-현-\s*/,
	/^\[기본\]\s*/,
	/^끝없는\s+/,
	/^영원한\s+/,
	/^선\s*:\s*/,
];
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
	if (name.startsWith("★초월 연옥★")) return "luminous";
	if (name.startsWith("★진 연옥★") || name.startsWith("★심연★")) return "dark";
	if (name.startsWith("★연옥★")) return "radiant";
	if (name.startsWith("-진-")) return "rare";
	if (name.startsWith("-현-")) return "uncommon";
	if (name.includes("영롱") || name.includes("천공") || name.includes("진 각성")) return "luminous";
	if (name.includes("짙은") || name === "심연의 스킬강화권") return "dark";
	if (name.includes("찬란") || name.includes("화려")) return "radiant";
	if (name.includes("해방")) return "liberated";
	if (name.includes("초월")) return "transcendent";
	if (name.includes("빛나는")) return "rare";
	if (name.includes("강력한")) return "uncommon";
	return "basic";
}

function getNormalEquipmentFamilyName(name) {
	let familyName = String(name || "").trim();
	let changed = true;
	while (changed && familyName) {
		changed = false;
		for (const prefix of NORMAL_EQUIP_RANK_PREFIXES) {
			const nextName = familyName.replace(prefix, "").trim();
			if (nextName !== familyName) {
				familyName = nextName;
				changed = true;
				break;
			}
		}
	}
	const knownFamily = Object.keys(NORMAL_EQUIP_ICON_ASSETS)
		.filter((baseName) => familyName.includes(baseName))
		.sort((left, right) => right.length - left.length)[0];
	return knownFamily || familyName;
}

function getNormalEquipmentRankKey(name) {
	const itemName = String(name || "").trim();
	if (itemName.startsWith("★초월 연옥★")) return "transcendent-purgatory";
	if (itemName.startsWith("★진 연옥★")) return "true-purgatory";
	if (itemName.startsWith("★연옥★")) return "purgatory";
	if (itemName.startsWith("★심연★")) return "abyss";
	if (itemName.startsWith("-초월-")) return "transcendent";
	if (itemName.startsWith("-진-")) return "jin";
	if (itemName.startsWith("-현-")) return "hyun";
	if (itemName.startsWith("끝없는 ")) return "endless";
	if (itemName.startsWith("영원한 ")) return "eternal";
	if (itemName.startsWith("선 : ")) return "sun";
	return "basic";
}

function getNormalEquipmentIconAssetName(item) {
	if (!item || item.type !== "normal") return "";
	const familyName = getNormalEquipmentFamilyName(item.name);
	const familyAssets = NORMAL_EQUIP_ICON_ASSETS[familyName];
	if (!familyAssets) return "";
	if (typeof familyAssets === "string") return familyAssets;
	const rankKey = getNormalEquipmentRankKey(item.name);
	return familyAssets[rankKey] || familyAssets.basic || "";
}

function getNormalEquipmentIconUrl(item) {
	const assetName = getNormalEquipmentIconAssetName(item);
	return assetName ? `${NORMAL_EQUIP_ASSET_BASE}/${assetName}?v=${NORMAL_EQUIP_ASSET_VERSION}` : "";
}

function normalizeItemIcon(item) {
	if (!item) return item;
	if (item.type === "special_equip" && typeof getSpecialEquipIconUrl === "function") {
		item.img = getSpecialEquipIconUrl(item);
		return item;
	}
	if (item.type === "normal") {
		const normalIconUrl = getNormalEquipmentIconUrl(item);
		if (normalIconUrl) item.img = normalIconUrl;
	}
	return item;
}

function applyEquipmentIconAssets() {
	const bossCollections = [];
	if (typeof bossList !== "undefined" && Array.isArray(bossList)) bossCollections.push(bossList);
	if (typeof specialBossList !== "undefined" && Array.isArray(specialBossList)) bossCollections.push(specialBossList);
	bossCollections.forEach((bossList) => {
		bossList.forEach((boss) => {
			if (!boss || !Array.isArray(boss.drops)) return;
			boss.drops.forEach((drop) => normalizeItemIcon(drop));
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
	if (name === "-초월-심연의 스킬강화권") return "SW";
	if (name === "진 각성 스킬강화권") return "M";
	return "SK";
}

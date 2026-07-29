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
	if (assetName) return `${SPECIAL_EQUIP_ASSET_BASE}/${assetName}`;
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

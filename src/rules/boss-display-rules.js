/*
 * boss-display-rules.js
 *
 * 보스/드랍 데이터의 화면 표시용 후처리입니다.
 * - 썸네일 생성
 * - 보스 타이틀 단축키 제거
 *
 * 게임 결과에 영향을 주는 계산은 넣지 않습니다.
 */

function applyGeneratedThumbnails() {
	bossList.forEach((boss) => {
		boss.img = iconTextUrl(`T${boss.id}`, "1b2f44", "ffffff");

		let normalEquipNo = 1;
		let specialEquipNo = 6;
		boss.drops.forEach((drop) => {
			if (drop.type === "skill_book") {
				drop.img = iconTextUrl(getSkillBookIconText(drop.name), "ffd700", "000000");
				return;
			}

			if (drop.type === "normal") {
				drop.img = iconTextUrl(`T${boss.id}-${normalEquipNo}`, "333333", "ffffff");
				normalEquipNo++;
				return;
			}

			if (drop.type === "special_equip") {
				if (drop.isTalisman || drop.isEmblem || (drop.name && (drop.name.includes("탈리스만") || drop.name.includes("빛나는 휘장")))) {
					drop.img = getSpecialEquipIconUrl(drop);
				} else {
					drop.img = iconTextUrl(`T${boss.id}-${specialEquipNo}`, "552266", "ffffff");
					specialEquipNo++;
				}
			}
		});
	});

	specialBossList.forEach((boss, idx) => {
		const stNo = idx + 1;
		boss.img = iconTextUrl(`ST${stNo}`, "402255", "ffffff");

		let specialDropNo = 1;
		boss.drops.forEach((drop) => {
			if (drop.type === "skill_book") {
				drop.img = iconTextUrl(getSkillBookIconText(drop.name), "ffd700", "000000");
				return;
			}

			if (drop.isTalisman || drop.isEmblem || (drop.name && (drop.name.includes("탈리스만") || drop.name.includes("빛나는 휘장")))) {
				drop.img = getSpecialEquipIconUrl(drop);
			} else {
				drop.img = iconTextUrl(`ST${stNo}-${specialDropNo}`, "555555", "ffffff");
				specialDropNo++;
			}
		});
	});
}

function stripBossTitleShortcuts() {
	[...bossList, ...specialBossList].forEach((boss) => {
		if (boss.title) boss.title = boss.title.replace(/\s*\([A-Z]+\)$/g, "");
	});
}

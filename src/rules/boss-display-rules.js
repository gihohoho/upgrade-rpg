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
		boss.drops.forEach((drop) => {
			if (drop.type === "skill_book") {
				drop.img = getSkillBookIconUrl(drop.name) || iconTextUrl(getSkillBookIconText(drop.name), "ffd700", "000000");
				return;
			}

			if (drop.type === "normal") {
				drop.img = getNormalEquipmentIconUrl(drop) || iconTextUrl(`T${boss.id}-${normalEquipNo}`, "333333", "ffffff");
				normalEquipNo++;
				return;
			}

			if (drop.type === "special_equip") {
				drop.img = getSpecialEquipIconUrl(drop);
			}
		});
	});

	specialBossList.forEach((boss, idx) => {
		const stNo = idx + 1;
		boss.img = iconTextUrl(`ST${stNo}`, "402255", "ffffff");

		boss.drops.forEach((drop) => {
			if (drop.type === "skill_book") {
				drop.img = getSkillBookIconUrl(drop.name) || iconTextUrl(getSkillBookIconText(drop.name), "ffd700", "000000");
				return;
			}

			if (drop.type === "special_equip") {
				drop.img = getSpecialEquipIconUrl(drop);
			}
		});
	});
}

function stripBossTitleShortcuts() {
	[...bossList, ...specialBossList].forEach((boss) => {
		if (boss.title) boss.title = boss.title.replace(/\s*\([A-Z]+\)$/g, "");
	});
}

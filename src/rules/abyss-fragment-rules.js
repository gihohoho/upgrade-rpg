/*
 * abyss-fragment-rules.js
 *
 * 심연의 편린 특수장비 이름별 특수 능력치 부여 규칙입니다.
 * 현재는 특수보스 드랍 데이터에 후처리로 specialStats를 붙입니다.
 *
 * 백엔드/DB 이전 시 참고:
 * - getAbyssFragmentSpecialStats()의 반환값은 item_options 또는 item_template_options 테이블 후보입니다.
 */

function getAbyssFragmentSpecialStats(name) {
	if (!name) return null;
	if (name.includes("심연의 편린 반지")) {
		return {
			attack: 3417,
			skillDmgAmp: 1.0,
		};
	}
	if (name.includes("심연의 편린 목걸이")) {
		return {
			attack: 3417,
			basicAtkDmgAmp: 1.0,
		};
	}
	if (name.includes("심연의 편린 스태프")) {
		return {
			attack: 3417,
			skillProcChanceInc: 0.1,
			skillCoefficientInc: 0.1,
			skillCooldownReductionInc: 0.1,
			allSkillDamageInc: 0.1,
			allBuffValueInc: 0.1,
			cloneCountInc: 2,
			cloneAttackSpeedInc: 0.001,
			maxAttackSpeedCapInc: 1.0,
		};
	}
	return null;
}

function applyAbyssFragmentStats() {
	specialBossList.forEach((boss) => {
		boss.drops.forEach((drop) => {
			if (drop.type !== "special_equip") return;
			const stats = getAbyssFragmentSpecialStats(drop.name);
			if (stats) drop.specialStats = stats;
		});
	});
}

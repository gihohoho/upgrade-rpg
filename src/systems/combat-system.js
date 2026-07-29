
function normalizeFieldState() {
	if (!fieldEnemyHp || typeof fieldEnemyHp !== "object") fieldEnemyHp = {};
	if (!fieldRespawnEndAt || typeof fieldRespawnEndAt !== "object") fieldRespawnEndAt = {};
}

function getFieldEnemyHp(index) {
	normalizeFieldState();
	const key = String(index);
	const zone = zones[index];
	if (!zone) return 0;

	if (fieldRespawnEndAt[key] && Date.now() >= fieldRespawnEndAt[key]) {
		fieldEnemyHp[key] = zone.maxHp;
		delete fieldRespawnEndAt[key];
	}

	if (fieldEnemyHp[key] === undefined || fieldEnemyHp[key] === null || isNaN(fieldEnemyHp[key])) {
		fieldEnemyHp[key] = zone.maxHp;
	}

	return fieldEnemyHp[key];
}

function setFieldEnemyHp(index, hp) {
	normalizeFieldState();
	const key = String(index);
	fieldEnemyHp[key] = Math.max(0, hp || 0);
}

function scheduleFieldRespawn(index, delayMs = 2000) {
	normalizeFieldState();
	const key = String(index);
	fieldRespawnEndAt[key] = Date.now() + delayMs;
	setFieldEnemyHp(index, 0);

	setTimeout(() => {
		if (!zones[index]) return;
		if (!fieldRespawnEndAt[key] || Date.now() < fieldRespawnEndAt[key]) return;

		fieldEnemyHp[key] = zones[index].maxHp;
		delete fieldRespawnEndAt[key];

		if (currentZoneType === "field" && currentZoneIndex === index) {
			currentEnemy.hp = fieldEnemyHp[key];
			updateCombatUI();
			startAutoAttack();
		}
	}, delayMs);
}

function syncCurrentFieldHp() {
	if (currentZoneType === "field") setFieldEnemyHp(currentZoneIndex, currentEnemy.hp);
}


function enterTown() {
	if (currentZoneType === "field") syncCurrentFieldHp();
	if (typeof closeAllGameplayModals === "function") closeAllGameplayModals();
	clearInterval(attackInterval);
	currentZoneType = "town";
	updateFullUI();
	addLog(`[이동] 마을로 귀환했습니다. 기록관과 도감, 랭킹을 확인할 수 있습니다.`);
}

function enterBossZone() {
	if (currentZoneType === "field") syncCurrentFieldHp();
	if (typeof closeAllGameplayModals === "function") closeAllGameplayModals();
	clearInterval(attackInterval);
	if (currentBoss) {
		currentZoneType = "boss_fight";
		addLog(`[이동] 진행 중이던 보스 전투로 복귀합니다.`);
		startAutoAttack();
	} else {
		currentZoneType = "boss_empty";
		addLog(`[이동] 텅 빈 보스존으로 이동했습니다. 보스를 소환해 주세요.`);
	}
	closeActionPanel();
	updateFullUI();
}

function startAutoAttack() {
	clearInterval(attackInterval);
	if (currentZoneType === "field" || currentZoneType === "boss_fight") {
		attackInterval = setInterval(playerAttack, getTotals().aspdMs);
	}
}

function rollSkillProc(baseRate, totals) {
	let inc = totals && totals.skillProcChanceInc ? totals.skillProcChanceInc : 0;
	return Math.random() <= baseRate * (1 + inc / 100);
}

function playerAttack() {
	let t = getTotals();
	let currentSkills = typeof getCurrentCharacterSkills === "function" ? getCurrentCharacterSkills(player) : (player.skills || {});
	let attackResult = typeof createCombatAttackResult === "function"
		? createCombatAttackResult({ zoneType: currentZoneType, zoneIndex: currentZoneIndex })
		: null;
	let baseDamage = Math.max(t.attack, 1);

	let isCrit = Math.random() <= t.basicCritChance / 100;
	let critMult = isCrit ? 1 + t.basicCritDmg / 100 : 1;
	let normalDamage = baseDamage * (1 + t.basicAtkDmgInc / 100) * (1 + t.allDmgInc / 100) * critMult;

	let totalDamage = isNaN(normalDamage) ? 0 : normalDamage;
	let skillDamageToShow = 0;
	let skillDamageLabels = [];

	function addSkillDamage(label, damage, showText = true) {
		if (isNaN(damage) || damage <= 0) return;
		const isSkillCrit = Math.random() <= t.skillCritChance / 100;
		const finalDamage = damage * (isSkillCrit ? 1 + t.skillCritDmg / 100 : 1);
		totalDamage += finalDamage;
		if (!showText) return;
		skillDamageToShow += finalDamage;
		skillDamageLabels.push({ label, damage: finalDamage });
		if (typeof addCombatSkillHit === "function") addCombatSkillHit(attackResult, label, finalDamage);
	}

	function getShortSkillLabel(label) {
		return String(label || "").replace("스킬", "");
	}

	function getSkillDamageClass(label) {
		let shortLabel = getShortSkillLabel(label);
		const classMap = {
			R: "damage-skill-r",
			T: "damage-skill-t",
			F: "damage-skill-f",
			D: "damage-skill-d",
			W: "damage-skill-w",
			SQ: "damage-skill-sq",
			SW: "damage-skill-sw",
			진각성: "damage-skill-ultimate",
		};
		return classMap[shortLabel] || "damage-skill-default";
	}

	function queueCombinedSkillDamageText() {
		if (!skillDamageLabels.length) return;
		let uniqueLabels = [...new Set(skillDamageLabels.map((skill) => getShortSkillLabel(skill.label)))];
		let damageSum = skillDamageLabels.reduce((sum, skill) => sum + (skill.damage || 0), 0);
		let labelHtml = uniqueLabels.map((label) => `<span class="${getSkillDamageClass(label)}">${label}</span>`).join(`<span class="damage-label-sep">,</span>`);
		let text = { html: `[${labelHtml}] <span class="damage-number">${formatNumber(damageSum)}</span>` };
		let extraClass = uniqueLabels.length > 1 ? "damage-skill-combo" : getSkillDamageClass(uniqueLabels[0]);
		if (typeof queueDamageText === "function") queueDamageText(attackResult, text, extraClass);
		else showDamageText(text, extraClass);
	}

	if (t.addSkillAtkChance > 0 && Math.random() <= t.addSkillAtkChance / 100) {
		let eqSkillDmg = t.attack * (t.addSkillAtkMult / 100) * (1 + t.skillDmgInc / 100) * (1 + t.allDmgInc / 100);
		addSkillDamage("장비스킬", eqSkillDmg, false);
	}

	// 🌟 탈리스만 A/B 보너스: 휘장은 스킬레벨 보너스가 아니라 별도 스탯 장비입니다.
	const getEquippedTalismanBonus = (slotIdx) => {
		let eq = player.equipment[slotIdx];
		if (!eq) return 0;
		let name = eq.name || "";
		let isTalisman = eq.isTalisman || name.includes("탈리스만");
		return isTalisman ? (parseInt(eq.level) || 0) + 1 : 0;
	};
	let tBonusA = getEquippedTalismanBonus(12); // R, T, SQ
	let tBonusB = getEquippedTalismanBonus(13); // F, D, SW

	// 🌟 Q스킬 (광검 마스터리 -> 유성락 각성)
	let lsObj = currentSkills && currentSkills.lightsabre ? currentSkills.lightsabre : { level: 0 };
	if (lsObj.level > 0) {
		let actualLevel = lsObj.level + (lsObj.isUpgraded ? tBonusA : 0); // SQ 보너스
		if (lsObj.isUpgraded) {
			if (rollSkillProc(0.005, t)) {
				let lsDamage = actualLevel * t.attack * 200000;
				lsDamage = lsDamage * (1 + t.skillDmgInc / 100) * (1 + t.allDmgInc / 100);
				addSkillDamage("SQ스킬", lsDamage);
			}
		} else {
			let lsDamage = lsObj.level * t.attack * 1;
			lsDamage = lsDamage * (1 + t.skillDmgInc / 100) * (1 + t.allDmgInc / 100);
			if (!isNaN(lsDamage)) totalDamage += lsDamage;
		}
	}

	let odLevel = currentSkills && currentSkills.overdrive ? currentSkills.overdrive.level : 0;
	if (odLevel > 0 && rollSkillProc(0.02, t)) {
		let wasOverdriveActive = activeBuffs.overdrive.active;
		activeBuffs.overdrive.active = true;
		activeBuffs.overdrive.timer = 4000;
		if (!wasOverdriveActive) {
			if (typeof queueDamageText === "function") queueDamageText(attackResult, "[E] 버프스킬 발동", "damage-skill-e damage-buff-state");
			else showDamageText("[E] 버프스킬 발동", "damage-skill-e damage-buff-state");
		}
	}
	if (activeBuffs.overdrive.active && odLevel > 0) {
		let odDamage = odLevel * t.attack * 150;
		odDamage = odDamage * (1 + t.skillDmgInc / 100) * (1 + t.allDmgInc / 100);
		addSkillDamage("버프스킬", odDamage, false);
	}

	// 🌟 W스킬 (참철식 -> 무형참 각성)
	let isObj = currentSkills && currentSkills.ironStrike ? currentSkills.ironStrike : { level: 0 };
	if (isObj.level > 0) {
		let actualLevel = isObj.level + (isObj.isUpgraded ? tBonusB : 0); // SW 보너스
		if (isObj.isUpgraded) {
			if (rollSkillProc(0.005, t)) {
				let isDamage = actualLevel * t.attack * 320000;
				isDamage = isDamage * (1 + t.skillDmgInc / 100) * (1 + t.allDmgInc / 100);
				addSkillDamage("SW스킬", isDamage);
			}
		} else {
			if (rollSkillProc(0.03, t)) {
				let isDamage = isObj.level * t.attack * 500;
				isDamage = isDamage * (1 + t.skillDmgInc / 100) * (1 + t.allDmgInc / 100);
				addSkillDamage("W스킬", isDamage);
				activeBuffs.ironStrike.active = true;
				activeBuffs.ironStrike.timer = 4000;
				updateFullUI();
			}
		}
	}

	// 🌟 R스킬 (발도)
	let bdLevel = currentSkills && currentSkills.baldo ? currentSkills.baldo.level : 0;
	if (bdLevel > 0 && rollSkillProc(0.03, t)) {
		let actualLevel = bdLevel + tBonusA; // R 보너스
		let bdDamage = actualLevel * t.attack * 4000;
		bdDamage = bdDamage * (1 + t.skillDmgInc / 100) * (1 + t.allDmgInc / 100);
		addSkillDamage("R스킬", bdDamage);
	}

	// 🌟 T스킬 (환영검무)
	let isdLevel = currentSkills && currentSkills.illusionSword ? currentSkills.illusionSword.level : 0;
	if (isdLevel > 0 && rollSkillProc(0.02, t)) {
		let actualLevel = isdLevel + tBonusA; // T 보너스
		let isdDamage = actualLevel * t.attack * 12000;
		isdDamage = isdDamage * (1 + t.skillDmgInc / 100) * (1 + t.allDmgInc / 100);
		addSkillDamage("T스킬", isdDamage);
	}

	// 🌟 F스킬 (심검)
	let dsLevel = currentSkills && currentSkills.deepSword ? currentSkills.deepSword.level : 0;
	if (dsLevel > 0 && rollSkillProc(0.02, t)) {
		let actualLevel = dsLevel + tBonusB; // F 보너스
		let dsDamage = actualLevel * t.attack * 16000;
		dsDamage = dsDamage * (1 + t.skillDmgInc / 100) * (1 + t.allDmgInc / 100);
		addSkillDamage("F스킬", dsDamage);
	}

	// 🌟 D스킬 (폭풍식)
	let tsLevel = currentSkills && currentSkills.tempestStrike ? currentSkills.tempestStrike.level : 0;
	if (tsLevel > 0 && rollSkillProc(0.012, t)) {
		let actualLevel = tsLevel + tBonusB; // D 보너스
		let tsDamage = actualLevel * t.attack * 42000;
		tsDamage = tsDamage * (1 + t.skillDmgInc / 100) * (1 + t.allDmgInc / 100);
		addSkillDamage("D스킬", tsDamage);
	}

	// 🌟 진각성 (천제극섬)
	let hsObj = currentSkills && currentSkills.heavenlyStrike ? currentSkills.heavenlyStrike : { level: 0, lastUsed: 0 };
	if (hsObj.level > 0) {
		let now = Date.now();
		if (now - (hsObj.lastUsed || 0) >= 300000) {
			if (rollSkillProc(0.05, t)) {
				let hsDamage = hsObj.level * t.attack * 11000000;
				hsDamage = hsDamage * (1 + t.skillDmgInc / 100) * (1 + t.allDmgInc / 100);
				addSkillDamage("진각성", hsDamage);
				hsObj.lastUsed = now;
			}
		}
	}

	if (attackResult) {
		attackResult.data.totalDamage = totalDamage;
		attackResult.data.normalDamage = normalDamage;
		attackResult.data.skillDamage = skillDamageToShow;
	}

	if (totalDamage <= 0) return attackResult;

	if (currentZoneType === "boss_fight") {
		currentBossHp -= totalDamage;
		queueCombinedSkillDamageText();
		if (attackResult) {
			attackResult.data.target = "boss";
			attackResult.data.remainingHp = currentBossHp;
			attackResult.data.killed = currentBossHp <= 0;
		}
		if (currentBossHp <= 0) killEnemy(currentBoss);
		else updateCombatUI();
	} else if (currentZoneType === "field") {
		if (currentEnemy.hp <= 0) return attackResult;
		currentEnemy.hp -= totalDamage;
		syncCurrentFieldHp();
		queueCombinedSkillDamageText();
		if (attackResult) {
			attackResult.data.target = "field";
			attackResult.data.remainingHp = currentEnemy.hp;
			attackResult.data.killed = currentEnemy.hp <= 0;
		}
		if (currentEnemy.hp <= 0) killEnemy(zones[currentZoneIndex]);
		else updateCombatUI();
	}

	if (typeof applyActionResultUi === "function") applyActionResultUi(attackResult);
	return attackResult;
}

function killEnemy(zoneData) {
	let t = getTotals();
	let killResult = typeof createEnemyKillResult === "function"
		? createEnemyKillResult({ zoneType: currentZoneType, zoneIndex: currentZoneIndex, targetName: zoneData && zoneData.name })
		: null;

	function addKillLog(message, important = false) {
		if (killResult && typeof addResultLog === "function") addResultLog(killResult, message, important);
		else addLog(message, important);
	}

	function addDropLog(itemName, message, options = {}) {
		if (killResult && typeof addDropAward === "function") addDropAward(killResult, itemName, message, options);
		else {
			addLog(message, options.important !== false);
			showItemDropText(itemName);
		}
	}

	function addBlockedLog(message, reason = "blocked") {
		if (killResult && typeof addBlockedReward === "function") addBlockedReward(killResult, message, reason);
		else addLog(message);
	}

	if (currentZoneType === "boss_fight" && currentBoss) {
		const killedBoss = currentBoss;
		const killedBossWasSpecial = !!currentBoss.isSpecial;
		if (killResult) {
			killResult.data.target = "boss";
			killResult.data.bossId = killedBoss.id;
			killResult.data.bossName = killedBoss.name;
			killResult.data.isSpecialBoss = killedBossWasSpecial;
		}

		if (typeof recordBossKill === "function") recordBossKill(currentBoss.name);
		if (typeof advanceItemDryStreak === "function") advanceItemDryStreak();
		let dropped = false;

		// 🔥 1. 특수보스 쿨타임: 보스를 "처치"했을 때만 적용
		if (currentBoss.isSpecial) {
			player.specialBossCD[currentBoss.id] = Date.now() + currentBoss.cooldownMs;
			if (killResult) killResult.data.cooldownApplied = { bossId: currentBoss.id, until: player.specialBossCD[currentBoss.id] };
		}

		// 🌟 일반장비, 스킬강화권, 탈리스만, 개별확률 특수장비 배열 분리
		let equipDrops = currentBoss.drops.filter((d) => (d.type === "normal" || d.type === "special_equip") && !d.isTalisman && !d.individualDropRate);
		let skillDrops = currentBoss.drops.filter((d) => d.type === "skill_book");
		let taliDrops = currentBoss.drops.filter((d) => d.isTalisman);
		let individualDrops = currentBoss.drops.filter((d) => d.individualDropRate && !d.isTalisman);

		// 🔥 2. 특수보스 장비 드랍: 장비드랍 OFF 상태여도 무조건 드랍 판정 진행
		let isEquipDropAllowed = currentBoss.isSpecial ? true : equipDropEnabled;

		if (isEquipDropAllowed && equipDrops.length > 0) {
			if (Math.random() <= currentBoss.equipDropRate * (1 + t.dropInc / 100)) {
				let randomEquip = equipDrops[Math.floor(Math.random() * equipDrops.length)];
				let newItem = { ...randomEquip, id: Date.now(), level: 0, count: randomEquip.count || 1 };
				let result = typeof addStackableItemToInventory === "function"
					? addStackableItemToInventory(newItem)
					: null;

				if (result && result.ok) {
					addDropLog(result.item.name, result.stacked ? `🎉 [득템] ${result.item.name} 획득! (현재 겹침: ${result.item.count}개)` : `🎉 [득템] ${result.item.name} 획득!`, { stacked: result.stacked, dropType: "equipment" });
					dropped = true;
					if (grantFirstEquipSkillBookIfNeeded(currentBoss, skillDrops, killResult)) dropped = true;
				} else {
					addBlockedLog(`[시스템] 가방이 꽉 차서 장비를 획득하지 못했습니다.`, "inventory_full_equipment");
				}
			}
		}

		// 탈리스만 개별 확률 드랍 로직 추가
		if (taliDrops.length > 0 && currentBoss.talismanDropRate) {
			if (Math.random() <= currentBoss.talismanDropRate * (1 + t.dropInc / 100)) {
				let randomTali = taliDrops[Math.floor(Math.random() * taliDrops.length)];
				let tName = randomTali.name.replace(" +0", "");
				let tSlot = (tName.includes("초월") || tName.includes("영롱")) ? 13 : 12; // 인덱스 정상화

				const newTali = {
					...randomTali,
					id: Date.now() + 2,
					name: tName,
					level: 0,
					count: 1,
					specialSlotIdx: tSlot,
				};
				const result = typeof addStackableItemToInventory === "function"
					? addStackableItemToInventory(newTali)
					: null;

				if (result && result.ok) {
					addDropLog(tName, result.stacked ? `🎉 [득템] ${tName} 획득! (현재 겹침: ${result.item.count}개)` : `🎉 [득템] ${tName} 획득!`, { stacked: result.stacked, dropType: "talisman" });
					dropped = true;
				} else {
					addBlockedLog(`[시스템] 가방이 꽉 차서 탈리스만을 획득하지 못했습니다.`, "inventory_full_talisman");
				}
			}
		}

		// 휘장처럼 보스별 별도 확률을 쓰는 특수장비 드랍 로직
		if (individualDrops.length > 0) {
			individualDrops.forEach((dropItem) => {
				const rate = dropItem.individualDropRate || 0;
				if (rate > 0 && Math.random() <= rate * (1 + t.dropInc / 100)) {
					let dropCopy = { ...dropItem, level: 0 };
					delete dropCopy.individualDropRate;
					let result = typeof addStackableItemToInventory === "function"
						? addStackableItemToInventory(dropCopy)
						: null;

					if (result && result.ok) {
						addDropLog(result.item.name, result.stacked ? `🎉 [득템] ${result.item.name} 획득! (현재 겹침: ${result.item.count}개)` : `🎉 [득템] ${result.item.name} 획득!`, { stacked: result.stacked, dropType: "individual_special_equip" });
						dropped = true;
					} else {
						addBlockedLog(`[시스템] 가방이 꽉 차서 특수장비를 획득하지 못했습니다.`, "inventory_full_special_equip");
					}
				}
			});
		}

		if (skillDrops.length > 0) {
			let baseSkillRate = currentBoss.isSpecial
				? currentBoss.skillDropRate
				: (typeof getNormalBossSkillDropRate === "function" ? getNormalBossSkillDropRate(currentBoss) : currentBoss.skillDropRate * 0.5);
			if (Math.random() <= baseSkillRate * (1 + t.dropInc / 100)) {
				let randomSkill = skillDrops[Math.floor(Math.random() * skillDrops.length)];
				let result = typeof addStackableItemToInventory === "function"
					? addStackableItemToInventory(randomSkill)
					: null;

				if (result && result.ok) {
					addDropLog(result.item.name, result.stacked ? `🎉 [득템] ${result.item.name} 획득! (현재 겹침: ${result.item.count}개)` : `🎉 [득템] ${result.item.name} 획득!`, { stacked: result.stacked, dropType: "skill_book" });
					dropped = true;
				} else {
					addBlockedLog(`[시스템] 가방이 꽉 차서 스킬강화권을 획득하지 못했습니다.`, "inventory_full_skill_book");
				}
			}
		}

		// 🔥 3. 특수보스 처치 후에는 이동 직전 위치로 복귀
		if (killedBossWasSpecial && typeof restoreSpecialBossReturnState === "function") {
			currentBoss = null;
			currentBossHp = 0;
			if (killResult) killResult.data.transition = { type: "restore_special_boss_return_state" };
			restoreSpecialBossReturnState("처치");
		} else if (autoBossSummon && lastSummonedBoss && !currentBoss.isSpecial) {
			currentBossHp = currentBoss.maxHp;
			addKillLog(`👿 [재소환] ${currentBoss.name} 연속 소환!`);
			if (killResult) killResult.data.transition = { type: "auto_resummon", bossName: currentBoss.name, hp: currentBossHp };
		} else {
			currentZoneType = "boss_empty";
			currentBoss = null;
			currentBossHp = 0;
			clearInterval(attackInterval);
			if (killResult) killResult.data.transition = { type: "boss_empty" };
		}

		if (killResult) {
			killResult.data.dropped = dropped;
			requestUiRefresh(killResult, "updateCombatUI");
			if (dropped) requestUiRefresh(killResult, "renderUI");
			if (typeof applyActionResultUi === "function") applyActionResultUi(killResult);
		} else {
			updateCombatUI();
			if (dropped) renderUI();
		}
		return killResult;
	} else if (currentZoneType === "field") {
		if (killResult) {
			killResult.data.target = "field";
			killResult.data.zoneName = zoneData.name;
		}
		if (typeof recordMonsterKill === "function") recordMonsterKill(zoneData.name);
		if (typeof advanceItemDryStreak === "function") advanceItemDryStreak();
		let goldReward = zoneData.goldReward * (1 + t.goldInc / 100);
		addGold(goldReward);
		if (killResult && typeof addRewardGold === "function") addRewardGold(killResult, goldReward);

		if (player.addAttackSpeed === undefined) player.addAttackSpeed = 150;
		let didGrowAttackSpeed = false;
		if (player.addAttackSpeed < 400) {
			player.addAttackSpeed = Math.min(400, player.addAttackSpeed + 1);
			didGrowAttackSpeed = true;
			addKillLog(`⚡ [성장] 공격속도가 1% 증가했습니다! (현재: ${player.addAttackSpeed}%)`);
		}

		if (zoneData.farm) {
			let f = zoneData.farm;
			let rewardProbability = typeof getFieldFarmRewardProbability === "function" ? getFieldFarmRewardProbability(f) : f.prob;
			if (Math.random() <= rewardProbability) {
				let pureAtk = player.farmAtkBonus || 0;
				let gain = f.gain;

				if (f.specialThreshold && pureAtk <= f.specialThreshold) gain *= f.specialMult;
				gain *= 1 + ((t && t.farmGainInc) || 0) / 100;
				gain = Math.floor(gain);

				if (!player.farmAtkBonus) player.farmAtkBonus = 0;
				if (player.farmAtkBonus < f.cap) {
					player.farmAtkBonus += gain;
					if (player.farmAtkBonus > f.cap) player.farmAtkBonus = f.cap;
					addKillLog(`💪 [노가다] 순수공격력이 ${gain} 증가했습니다! (현재: ${formatNumber(player.farmAtkBonus)})`);
					if (killResult) {
						killResult.data.rewards.farmAttackGain = gain;
						killResult.data.rewards.farmAttackTotal = player.farmAtkBonus;
					}
				}
			}
		}
		currentEnemy.hp = 0;
		scheduleFieldRespawn(currentZoneIndex, 2000);
		clearInterval(attackInterval);

		if (killResult) {
			killResult.data.attackSpeedGrew = didGrowAttackSpeed;
			killResult.data.nextRespawnAt = fieldRespawnEndAt[String(currentZoneIndex)];
			requestUiRefresh(killResult, "updateGoldUI");
			requestUiRefresh(killResult, "updateCombatUI");
			if (didGrowAttackSpeed || (killResult.data.rewards && killResult.data.rewards.farmAttackGain)) requestUiRefresh(killResult, "updateFullUI");
			if (typeof applyActionResultUi === "function") applyActionResultUi(killResult);
		} else {
			updateGoldUI();
			if (didGrowAttackSpeed) updateFullUI();
			updateCombatUI();
		}
		return killResult;
	}
	return killResult;
}

function changeZone(offset) {
	let nIdx = currentZoneIndex + offset;
	if (nIdx >= 0 && nIdx < zones.length) {
		if (currentZoneType === "field") syncCurrentFieldHp();
		if (typeof closeAllGameplayModals === "function") closeAllGameplayModals();
		currentZoneType = "field";
		currentZoneIndex = nIdx;
		currentEnemy.hp = getFieldEnemyHp(currentZoneIndex);
		addLog(`[이동] ${zones[currentZoneIndex].name} 진입`);
		closeActionPanel();
		updateFullUI();
		if (currentEnemy.hp > 0) startAutoAttack();
		else clearInterval(attackInterval);
	}
}

function getDamageTextAnchorRect() {
	// 데미지 텍스트는 몬스터 이미지 근처에 떠야 합니다.
	// 기존에는 .enemy-display(width: 100%) 전체 폭을 기준으로 삼아서
	// 텍스트가 화면 오른쪽 바깥으로 나갈 수 있었습니다.
	const imageTarget = document.getElementById("enemy-image-placeholder");
	if (imageTarget && typeof imageTarget.getBoundingClientRect === "function") {
		return imageTarget.getBoundingClientRect();
	}

	const enemyTarget = document.querySelector(".enemy-display");
	if (enemyTarget && typeof enemyTarget.getBoundingClientRect === "function") {
		return enemyTarget.getBoundingClientRect();
	}

	return null;
}

function clampDamageTextPosition(value, min, max) {
	if (!isFinite(value)) return min;
	if (!isFinite(max)) return Math.max(min, value);
	if (max < min) return min;
	return Math.max(min, Math.min(value, max));
}

function getBattleZoneSize(bZone, zRect) {
	return {
		width: bZone.clientWidth || (zRect && zRect.width) || window.innerWidth || 0,
		height: bZone.clientHeight || (zRect && zRect.height) || window.innerHeight || 0,
	};
}

function showItemDropText(itemName) {
	const bZone = document.getElementById("battle-zone");
	if (!bZone) return;

	const dEl = document.createElement("div");
	dEl.className = "damage-text";
	dEl.style.color = "#88ff88";
	dEl.style.fontSize = "20px";
	dEl.innerText = `📦 ${itemName}!`;

	const rect = getDamageTextAnchorRect();
	const zRect = bZone.getBoundingClientRect();
	const zoneSize = getBattleZoneSize(bZone, zRect);

	if (rect) {
		const top = rect.top - zRect.top - 20 + getRandomInt(-20, 20);
		const left = rect.left - zRect.left + rect.width / 2 - 20 + getRandomInt(-30, 30);
		dEl.style.top = clampDamageTextPosition(top, 8, zoneSize.height - 60) + "px";
		dEl.style.left = clampDamageTextPosition(left, 8, zoneSize.width - 180) + "px";
	} else {
		dEl.style.top = "40%";
		dEl.style.left = "50%";
	}

	bZone.appendChild(dEl);
	setTimeout(() => dEl.remove(), 1200);
}

function showDamageText(damageText, extraClass = "") {
	const bZone = document.getElementById("battle-zone");
	if (!bZone) return;

	const dEl = document.createElement("div");
	dEl.className = `damage-text${extraClass ? " " + extraClass : ""}`;

	if (damageText && typeof damageText === "object" && damageText.html) {
		dEl.innerHTML = damageText.html;
	} else {
		dEl.innerText = damageText;
	}

	const rect = getDamageTextAnchorRect();
	const zRect = bZone.getBoundingClientRect();
	const zoneSize = getBattleZoneSize(bZone, zRect);

	if (rect) {
		const top = rect.top - zRect.top + rect.height * 0.35 + getRandomInt(-24, 24);
		const left = rect.left - zRect.left + rect.width + 18 + getRandomInt(0, 36);
		dEl.style.top = clampDamageTextPosition(top, 8, zoneSize.height - 80) + "px";
		dEl.style.left = clampDamageTextPosition(left, 8, zoneSize.width - 240) + "px";
	} else {
		dEl.style.top = "40%";
		dEl.style.left = "50%";
	}

	bZone.appendChild(dEl);
	setTimeout(() => dEl.remove(), 1000);
}

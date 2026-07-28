function getBaseStackName(item) {
	return item && item.name ? item.name.replace(/\s*\+0$/, "") : "";
}

function isEmblemStackItem(item) {
	return !!(item && (item.isEmblem || (item.name && item.name.includes("빛나는 휘장"))));
}

function isTalismanStackItem(item) {
	return !!(item && (item.isTalisman || (item.name && item.name.includes("탈리스만"))));
}

function getTalismanSlotIndexByName(name = "") {
	return (String(name).includes("초월") || String(name).includes("영롱")) ? 13 : 12;
}

function getSpecialStackSlotIndex(item) {
	const name = getBaseStackName(item);
	if (isEmblemStackItem(item)) return 14;
	if (isTalismanStackItem(item)) return getTalismanSlotIndexByName(name);
	return item && item.specialSlotIdx !== undefined ? item.specialSlotIdx : -1;
}

function getSpecialStackIconText(item) {
	const name = getBaseStackName(item);
	if (isEmblemStackItem(item)) return "EMB";
	if (name.includes("찬란한")) return "TA2";
	if (name.includes("영롱")) return "TB2";
	if (name.includes("초월")) return "TB1";
	if (name.includes("탈리스만")) return "TA1";
	return "SP";
}

function ensureSpecialStackIdentity(item) {
	if (!item) return item;
	if (isEmblemStackItem(item)) {
		item.isEmblem = true;
		item.isTalisman = false;
		item.specialSlotIdx = 14;
	} else if (isTalismanStackItem(item)) {
		item.isTalisman = true;
		item.isEmblem = false;
		item.specialSlotIdx = getTalismanSlotIndexByName(item.name || "");
	}
	return item;
}

function normalizeSpecialStackItem(item) {
	if (!item || item.type !== "special_equip") return item;
	ensureSpecialStackIdentity(item);
	if (typeof getSpecialEquipIconUrl === "function" && (isTalismanStackItem(item) || isEmblemStackItem(item))) {
		item.img = getSpecialEquipIconUrl(item);
	}
	return item;
}

function normalizeSpecialStackArray(arr) {
	if (!Array.isArray(arr)) return;
	arr.forEach((item) => normalizeSpecialStackItem(item));
}

function normalizePlayerSpecialStackItems() {
	if (!player) return;
	normalizeSpecialStackArray(player.inventory);
	normalizeSpecialStackArray(player.storage);
	normalizeSpecialStackArray(player.trash);
	if (Array.isArray(player.equipment)) normalizeSpecialStackArray(player.equipment);

	if (Array.isArray(player.mailbox)) {
		player.mailbox.forEach((mail) => {
			if (!mail) return;
			if (mail.item) normalizeSpecialStackItem(mail.item);
			if (Array.isArray(mail.items)) normalizeSpecialStackArray(mail.items);
		});
	}
}

function isTruthyStackableFlag(value) {
	return value === true || value === 1 || value === "1" || String(value).toLowerCase() === "true";
}

function isTemplateStackableItem(item) {
	if (!item || !isTruthyStackableFlag(item.stackable)) return false;
	// 관리자 stackable은 "기본 드랍 아이템을 수량으로 겹칠지"를 뜻합니다.
	// 강화된 장비까지 겹치면 옵션/강화 상태가 섞일 수 있으므로 +0만 겹칩니다.
	return (parseInt(item.level) || 0) === 0;
}

function isZeroLevelStackableItem(item) {
	if (!item) return false;
	if (item.type === "skill_book") return true;
	if ((isTalismanStackItem(item) || isEmblemStackItem(item)) && (parseInt(item.level) || 0) === 0) return true;
	if (isTemplateStackableItem(item)) return true;
	return false;
}

function prepareStackableItem(rawItem) {
	let item = { ...rawItem };
	item.name = getBaseStackName(item);
	item.level = parseInt(item.level) || 0;
	item.count = item.count || 1;
	if (item.stackable !== undefined) item.stackable = isTruthyStackableFlag(item.stackable);
	ensureSpecialStackIdentity(item);
	return item;
}

function isSameStackableItem(left, right) {
	if (!left || !right) return false;
	// 신규 획득 아이템이 DB stackable=true이면, 기존 세이브에 stackable 필드가 없던 같은 +0 아이템도
	// 앞으로는 같은 묶음으로 합칠 수 있게 허용합니다. 둘 다 stackable 대상이 아니면 합치지 않습니다.
	if (!isZeroLevelStackableItem(left) && !isZeroLevelStackableItem(right)) return false;
	if (getBaseStackName(left) !== getBaseStackName(right)) return false;
	if ((parseInt(left.level) || 0) !== (parseInt(right.level) || 0)) return false;
	if ((parseInt(left.level) || 0) !== 0) return false;
	if (left.type && right.type && left.type !== right.type) return false;
	if (left.templateKey && right.templateKey && left.templateKey !== right.templateKey) return false;
	if (left.itemTemplateCode && right.itemTemplateCode && left.itemTemplateCode !== right.itemTemplateCode) return false;
	if (left.equipGroup && right.equipGroup && left.equipGroup !== right.equipGroup) return false;
	if (left.specialSlotIdx !== undefined && right.specialSlotIdx !== undefined && left.specialSlotIdx !== right.specialSlotIdx) return false;
	const leftTier = left.tier ?? left.grade;
	const rightTier = right.tier ?? right.grade;
	if (leftTier !== undefined && rightTier !== undefined && String(leftTier) !== String(rightTier)) return false;
	return true;
}

function findStackableItem(item, arrays = [player.inventory, player.storage]) {
	if (!isZeroLevelStackableItem(item)) return null;
	for (let arr of arrays) {
		let found = arr.find((it) => isSameStackableItem(it, item));
		if (found) return found;
	}
	return null;
}

function addStackableItemToInventory(rawItem) {
	let item = prepareStackableItem(rawItem);
	let found = findStackableItem(item);
	if (found) {
		found.count = (found.count || 1) + (item.count || 1);
		// 기존 세이브 아이템에는 stackable/templateKey가 없을 수 있으므로, 새 DB 드랍 정책을 발견한 스택에 보강합니다.
		if (item.stackable === true) found.stackable = true;
		if (!found.templateKey && item.templateKey) found.templateKey = item.templateKey;
		if (!found.itemTemplateCode && item.itemTemplateCode) found.itemTemplateCode = item.itemTemplateCode;
		if (found.grade === undefined && item.grade !== undefined) found.grade = item.grade;
		if (found.tier === undefined && item.tier !== undefined) found.tier = item.tier;
		if (typeof recordItemAcquired === "function") recordItemAcquired(item);
		return { ok: true, item: found, stacked: true };
	}
	if (player.inventory.length >= player.maxInventorySize) return { ok: false, item, stacked: false };
	item.id = item.id || Date.now() + Math.random();
	player.inventory.push(item);
	if (typeof recordItemAcquired === "function") recordItemAcquired(item);
	return { ok: true, item, stacked: false };
}

function mergeStackableIntoArray(item, targetArr) {
	if (!isZeroLevelStackableItem(item) || !Array.isArray(targetArr)) return false;
	let prepared = prepareStackableItem(item);
	let found = targetArr.find((it) => isSameStackableItem(it, prepared));
	if (found) {
		found.count = (found.count || 1) + (prepared.count || 1);
		if (prepared.stackable === true) found.stackable = true;
		if (!found.templateKey && prepared.templateKey) found.templateKey = prepared.templateKey;
		if (!found.itemTemplateCode && prepared.itemTemplateCode) found.itemTemplateCode = prepared.itemTemplateCode;
		return true;
	}
	return false;
}


function isBeginnerLiberationStaff(item) {
	let name = (item && item.name) || "";
	return name.includes("리버레이션 스태프");
}

function getNormalEquipAllowedSlots(item) {
	if (!item || item.type === "skill_book" || item.type === "special_equip") return [];
	if (isBeginnerLiberationStaff(item)) return [0, 1, 2, 3, 4, 5];

	if (item.equipGroup === "skill_all") return [0]; // N-1: 스킬/모든피해증가
	if (item.equipGroup === "atk_inc") return [1]; // N-2: 공격력%
	if (item.equipGroup === "normal_dmg") return [2]; // N-3: 평타피해증가%

	// N-4/N-5 계열은 남은 일반 장비칸에서 기존 equipLimit 규칙을 유지합니다.
	return [3, 4, 5];
}

function getNormalEquipTargetIndex(item) {
	let allowedSlots = getNormalEquipAllowedSlots(item);
	if (!allowedSlots.length) return -1;

	if (isBeginnerLiberationStaff(item)) {
		for (let idx of allowedSlots) {
			if (player.equipment[idx] === null) return idx;
		}
		return -1;
	}

	let groupCount = 0;
	let firstSameGroupIdx = -1;
	if (item.equipGroup) {
		for (let idx of allowedSlots) {
			if (player.equipment[idx] && player.equipment[idx].equipGroup === item.equipGroup) {
				groupCount++;
				if (firstSameGroupIdx === -1) firstSameGroupIdx = idx;
			}
		}

		if (groupCount >= (item.equipLimit || 1)) return firstSameGroupIdx;
	}

	for (let idx of allowedSlots) {
		if (player.equipment[idx] === null) return idx;
	}

	return -1;
}

function actionEquipDirect(invIndex) {
	let item = player.inventory[invIndex];
	let result = null;

	if (item && item.type === "skill_book" && skillBookMapping[item.name]) {
		let skillKey = skillBookMapping[item.name];
		result = typeof createSkillBookUseResult === "function"
			? createSkillBookUseResult({
				itemName: item.name,
				skillKey,
				inventoryIndex: invIndex,
			})
			: null;

		let currentSkills = typeof getCurrentCharacterSkills === "function" ? getCurrentCharacterSkills(player) : player.skills;
		let skData = typeof getSkillState === "function" ? getSkillState(skillKey, player) : currentSkills[skillKey];
		if (!skData) {
			if (result) {
				result.ok = false;
				addResultLog(result, `[시스템] 대상 스킬 정보를 찾을 수 없습니다.`);
				return applyActionResultUi(result);
			}
			addLog(`[시스템] 대상 스킬 정보를 찾을 수 없습니다.`);
			return;
		}

		let info = typeof getSkillBookInfo === "function" ? getSkillBookInfo(item.name) : { key: "?", skill: "대상 스킬" };
		let skillMaxLevel = typeof getSkillMaxLevel === "function" ? getSkillMaxLevel(skillKey) : 7;
		let isAbyssAwakeningBook = typeof isAwakeningSkillBook === "function"
			? isAwakeningSkillBook(item.name)
			: item.name === "심연의 스킬강화권" || item.name === "-초월- 심연의 스킬강화권" || item.name === "-초월-심연의 스킬강화권";
		let beforeLevel = skData.level || 0;
		let wasUpgraded = !!skData.isUpgraded;

		if (isAbyssAwakeningBook) {
			// 심연의 스킬강화권은 기존 Q/W 레벨을 계승하지 않고 SQ/SW를 Lv.1부터 별도로 성장시킵니다.
			if (!skData.isUpgraded) {
				skData.isUpgraded = true;
				skData.level = 1;
			} else {
				if (skData.level >= skillMaxLevel) {
					if (result) {
						result.ok = false;
						result.data.beforeLevel = beforeLevel;
						result.data.afterLevel = skData.level;
						result.data.reason = "max_level";
						addResultLog(result, `[시스템] ${info.key} 스킬은 이미 최대 레벨(${skillMaxLevel}) 입니다. (소모되지 않음)`);
						return applyActionResultUi(result);
					}
					addLog(`[시스템] ${info.key} 스킬은 이미 최대 레벨(${skillMaxLevel}) 입니다. (소모되지 않음)`);
					return;
				}
				skData.level++;
			}
		} else {
			// Q/W가 이미 SQ/SW로 각성된 상태에서는 일반 Q/W 강화권으로 각성 스킬 레벨을 올릴 수 없습니다.
			if ((skillKey === "lightsabre" || skillKey === "ironStrike") && skData.isUpgraded) {
				if (result) {
					result.ok = false;
					result.data.beforeLevel = beforeLevel;
					result.data.afterLevel = skData.level;
					result.data.reason = "awakened_skill_requires_abyss_book";
					addResultLog(result, `[시스템] 각성된 ${info.key} 계열 스킬은 전용 심연의 스킬강화권으로만 성장시킬 수 있습니다.`, true);
					return applyActionResultUi(result);
				}
				addLog(`[시스템] 각성된 ${info.key} 계열 스킬은 전용 심연의 스킬강화권으로만 성장시킬 수 있습니다.`, true);
				return;
			}

			if (skData.level >= skillMaxLevel) {
				if (result) {
					result.ok = false;
					result.data.beforeLevel = beforeLevel;
					result.data.afterLevel = skData.level;
					result.data.reason = "max_level";
					addResultLog(result, `[시스템] 해당 스킬은 이미 최대 레벨(${skillMaxLevel}) 입니다. (소모되지 않음)`);
					return applyActionResultUi(result);
				}
				addLog(`[시스템] 해당 스킬은 이미 최대 레벨(${skillMaxLevel}) 입니다. (소모되지 않음)`);
				return;
			}
			skData.level++;
		}

		// 아이템 차감 로직 (스택 처리)
		let beforeCount = item.count || 1;
		let afterCount = beforeCount > 1 ? beforeCount - 1 : 0;
		if (item.count && item.count > 1) item.count--;
		else player.inventory.splice(invIndex, 1);

		if (result) {
			result.data.beforeLevel = beforeLevel;
			result.data.afterLevel = skData.level;
			result.data.beforeCount = beforeCount;
			result.data.afterCount = afterCount;
			result.data.wasUpgraded = wasUpgraded;
			result.data.isUpgraded = !!skData.isUpgraded;
			result.data.awakeningBook = !!isAbyssAwakeningBook;
			result.data.skillLabel = info.key;
			if (isAbyssAwakeningBook) {
				addResultLog(result, `✨ [특수스킬강화] ${item.name}을 사용하여 ${info.key} 스킬이 Lv.${skData.level}이 되었습니다!`, true);
			} else {
				addResultLog(result, `✨ [스킬강화] ${item.name}을 사용하여 스킬 레벨이 상승했습니다!`, true);
			}
			if (afterCount > 0) requestUiRefresh(result, "refreshActionPanelStats");
			else requestUiRefresh(result, "consumedSkillBook", { name: item.name, img: item.img });
			requestUiRefresh(result, "renderSkills");
			requestUiRefresh(result, "updateFullUI");
			return applyActionResultUi(result);
		}

		if (isAbyssAwakeningBook) {
			addLog(`✨ [특수스킬강화] ${item.name}을 사용하여 ${info.key} 스킬이 Lv.${skData.level}이 되었습니다!`, true);
		} else {
			addLog(`✨ [스킬강화] ${item.name}을 사용하여 스킬 레벨이 상승했습니다!`, true);
		}

		renderSkills();
		updateFullUI();
		if (afterCount > 0) refreshActionPanelStats();
		else if (typeof showConsumedSkillBookPanel === "function") showConsumedSkillBookPanel({ name: item.name, img: item.img });
		return;
	}

	result = typeof createItemEquipResult === "function"
		? createItemEquipResult({
			slotType: "inv",
			slotIndex: invIndex,
			itemName: item && item.name,
			itemType: item && item.type,
		})
		: null;

	let targetIdx = -1;
	if (item && item.type === "special_equip") {
		ensureSpecialStackIdentity(item);
		if (isTalismanStackItem(item) || isEmblemStackItem(item)) {
			targetIdx = getSpecialStackSlotIndex(item); // 탈리스만A/B/휘장 슬롯 강제 고정
			item.specialSlotIdx = targetIdx;
		} else if (item.specialSlotIdx !== undefined) {
			targetIdx = item.specialSlotIdx;
		}
	} else if (item) {
		targetIdx = getNormalEquipTargetIndex(item);
	}

	if (targetIdx !== -1) {
		let oldEquip = player.equipment[targetIdx];

		// 🔥 스택 장비(탈리스만) 장착 시 1개만 분리
		let newEquip;
		let splitFromStack = false;
		if (item.count && item.count > 1) {
			item.count--; // 인벤토리의 개수는 1개 줄임
			newEquip = { ...item, count: 1 }; // 장착창에는 1개만 복사해서 투입
			splitFromStack = true;
		} else {
			newEquip = player.inventory.splice(invIndex, 1)[0];
		}

		// 장착 중이던 장비를 인벤토리로 되돌리기 (겹침 처리 포함)
		let returnedOldEquip = false;
		let mergedOldEquip = false;
		if (oldEquip !== null) {
			if (!mergeStackableIntoArray(oldEquip, player.inventory)) {
				player.inventory.push(oldEquip);
				returnedOldEquip = true;
			} else {
				mergedOldEquip = true;
			}
		}

		player.equipment[targetIdx] = newEquip;
		if (result) {
			result.data.targetSlotIndex = targetIdx;
			result.data.equippedItem = newEquip ? { name: newEquip.name, level: newEquip.level || 0, count: newEquip.count || 1, type: newEquip.type || null } : null;
			result.data.replacedItem = oldEquip ? { name: oldEquip.name, level: oldEquip.level || 0, count: oldEquip.count || 1, type: oldEquip.type || null } : null;
			result.data.splitFromStack = splitFromStack;
			result.data.returnedOldEquip = returnedOldEquip;
			result.data.mergedOldEquip = mergedOldEquip;
			addResultLog(result, `[장착] ${newEquip.name} 장착 완료.`);
			requestUiRefresh(result, "closeActionPanel");
			requestUiRefresh(result, "updateFullUI");
			if (currentZoneType !== "town" && currentZoneType !== "boss_empty") requestUiRefresh(result, "startAutoAttack");
			return applyActionResultUi(result);
		}
		addLog(`[장착] ${newEquip.name} 장착 완료.`);
		closeActionPanel();
		updateFullUI();
		if (currentZoneType !== "town" && currentZoneType !== "boss_empty") startAutoAttack();
	} else {
		if (result) {
			result.ok = false;
			result.data.reason = item ? "no_available_slot" : "missing_item";
			addResultLog(result, `[시스템] 해당 장비를 장착할 수 있는 장비칸이 비어있지 않습니다!`);
			return applyActionResultUi(result);
		}
		addLog(`[시스템] 해당 장비를 장착할 수 있는 장비칸이 비어있지 않습니다!`);
	}
}

function actionUnequipDirect(equipIndex) {
	let item = player.equipment[equipIndex];
	let result = typeof createItemUnequipResult === "function"
		? createItemUnequipResult({ slotIndex: equipIndex, itemName: item && item.name })
		: null;
	if (!item) {
		if (result) {
			result.ok = false;
			result.data.reason = "missing_item";
			return result;
		}
		return;
	}

	if (isZeroLevelStackableItem(item) && mergeStackableIntoArray(item, player.inventory)) {
		player.equipment[equipIndex] = null;
		if (result) {
			result.data.mergedIntoInventory = true;
			result.data.item = { name: item.name, level: item.level || 0, count: item.count || 1, type: item.type || null };
			addResultLog(result, `[해제] ${item.name} 장착 해제. (인벤토리 겹침 완료)`);
			requestUiRefresh(result, "closeActionPanel");
			requestUiRefresh(result, "updateFullUI");
			if (currentZoneType !== "town" && currentZoneType !== "boss_empty") requestUiRefresh(result, "startAutoAttack");
			return applyActionResultUi(result);
		}
		addLog(`[해제] ${item.name} 장착 해제. (인벤토리 겹침 완료)`);
		closeActionPanel();
		updateFullUI();
		if (currentZoneType !== "town" && currentZoneType !== "boss_empty") startAutoAttack();
		return;
	}

	if (player.inventory.length < player.maxInventorySize) {
		player.equipment[equipIndex] = null;
		player.inventory.push(item);
		if (result) {
			result.data.mergedIntoInventory = false;
			result.data.item = { name: item.name, level: item.level || 0, count: item.count || 1, type: item.type || null };
			addResultLog(result, `[해제] ${item.name} 장착 해제.`);
			requestUiRefresh(result, "closeActionPanel");
			requestUiRefresh(result, "updateFullUI");
			if (currentZoneType !== "town" && currentZoneType !== "boss_empty") requestUiRefresh(result, "startAutoAttack");
			return applyActionResultUi(result);
		}
		addLog(`[해제] ${item.name} 장착 해제.`);
		closeActionPanel();
		updateFullUI();
		if (currentZoneType !== "town" && currentZoneType !== "boss_empty") startAutoAttack();
	} else if (player.inventory.length >= player.maxInventorySize) {
		if (result) {
			result.ok = false;
			result.data.reason = "inventory_full";
			addResultLog(result, `[시스템] 가방이 꽉 차서 벗을 수 없습니다.`);
			return applyActionResultUi(result);
		}
		addLog(`[시스템] 가방이 꽉 차서 벗을 수 없습니다.`);
	}
}

function actionEquipToggle() {
	if (selectedSlot.type === "inv") actionEquipDirect(selectedSlot.index);
	else if (selectedSlot.type === "equip") actionUnequipDirect(selectedSlot.index);
}

function actionUseSelected() {
	if (selectedSlot.type === "inv") actionEquipDirect(selectedSlot.index);
	else if (selectedSlot.type === "equip") actionUnequipDirect(selectedSlot.index);
	else if (selectedSlot.type === "storage") addLog(`[시스템] 보관함 아이템은 먼저 가방으로 꺼낸 뒤 사용할 수 있습니다.`);
	else if (selectedSlot.type === "trash") addLog(`[시스템] 휴지통 아이템은 먼저 가방으로 복구한 뒤 사용할 수 있습니다.`);
}

function actionDismantleSpecialToZero() {
	let pack = getSelectedItemPack();
	let item = pack.item;
	let level = parseInt(item && item.level) || 0;
	if (!item || (!isTalismanStackItem(item) && !isEmblemStackItem(item)) || level <= 0) {
		addLog(`[시스템] 강화된 탈리스만/휘장만 +0으로 분해할 수 있습니다.`);
		return;
	}
	if (selectedSlot.type === "trash") {
		addLog(`[시스템] 휴지통 아이템은 먼저 가방으로 복구해 주세요.`);
		return;
	}

	let baseName = getBaseStackName(item);
	if (typeof window !== "undefined" && typeof window.confirm === "function") {
		let accepted = window.confirm(`${baseName} +${level} 1개를 +0 1개로 되돌릴까요?\n강화에 사용한 재료는 환급되지 않습니다.`);
		if (!accepted) return;
	}

	let zeroItem = prepareStackableItem({
		...item,
		id: Date.now() + Math.random(),
		name: baseName,
		level: 0,
		count: 1,
	});
	let destinationArray;
	let destinationType;

	if (selectedSlot.type === "equip") {
		destinationArray = player.inventory;
		destinationType = "inv";
		let found = destinationArray.find((it) => isSameStackableItem(it, zeroItem));
		if (!found && destinationArray.length >= player.maxInventorySize) {
			addLog(`[시스템] 가방이 꽉 차서 장착 중인 ${baseName}을 +0으로 분해할 수 없습니다.`);
			return;
		}
		player.equipment[selectedSlot.index] = null;
		if (found) found.count = (found.count || 1) + 1;
		else destinationArray.push(zeroItem);
		selectedSlot = { type: destinationType, index: destinationArray.indexOf(found || zeroItem) };
	} else {
		destinationArray = selectedSlot.type === "storage" ? player.storage : player.inventory;
		destinationType = selectedSlot.type === "storage" ? "storage" : "inv";
		let maxSize = destinationType === "storage" ? player.maxStorageSize : player.maxInventorySize;
		let sourceIndex = destinationArray.indexOf(item);
		let found = destinationArray.find((it) => it !== item && isSameStackableItem(it, zeroItem));
		let selectedCount = item.count || 1;

		if (selectedCount > 1 && !found && destinationArray.length >= maxSize) {
			addLog(`[시스템] ${baseName} +0을 담을 빈 공간이 필요합니다.`);
			return;
		}

		if (selectedCount > 1) item.count = selectedCount - 1;
		else if (sourceIndex !== -1) destinationArray.splice(sourceIndex, 1);

		if (found) found.count = (found.count || 1) + 1;
		else destinationArray.push(zeroItem);
		selectedSlot = { type: destinationType, index: destinationArray.indexOf(found || zeroItem) };
	}

	addLog(`♻️ [분해] ${baseName} +${level} 1개를 +0 1개로 되돌렸습니다. (강화 재료 환급 없음)`, true);
	updateFullUI();
	refreshActionPanelStats();
}

function getSelectedItemPack() {
	let targetArray = player.inventory;
	if (selectedSlot.type === "equip") targetArray = player.equipment;
	else if (selectedSlot.type === "storage") targetArray = player.storage;
	else if (selectedSlot.type === "trash") targetArray = player.trash;
	return { item: targetArray[selectedSlot.index], array: targetArray };
}

function getZeroLevelMaterialCount(baseName) {
	let pool = 0;
	[player.inventory, player.storage].forEach((arr) => {
		arr.forEach((it) => {
			if (getBaseStackName(it) === baseName && (parseInt(it.level) || 0) === 0) pool += it.count || 1;
		});
	});
	return pool;
}

function consumeZeroLevelMaterials(baseName, amount, protectedItem) {
	let remaining = amount;
	for (let arr of [player.inventory, player.storage]) {
		for (let i = arr.length - 1; i >= 0; i--) {
			let it = arr[i];
			if (it === protectedItem) continue;
			if (getBaseStackName(it) === baseName && (parseInt(it.level) || 0) === 0) {
				let currentCount = it.count || 1;
				let take = Math.min(currentCount, remaining);
				it.count = currentCount - take;
				remaining -= take;
				if (it.count <= 0) arr.splice(i, 1);
				if (remaining <= 0) return 0;
			}
		}
	}
	return remaining;
}

function renderEnhanceResultLog(title, rows, goldSpent = 0) {
	const el = document.getElementById("ap-enhance-log");
	if (!el) return;
	const goldRow = `<div class="ap-enhance-log-gold">사용 골드: <span>${formatNumber(goldSpent || 0)}</span></div>`;
	if (!rows || rows.length === 0) {
		el.innerHTML = `<div class="ap-enhance-log-title">${title}</div>${goldRow}<div class="ap-enhance-log-empty">성공한 강화가 없습니다.</div>`;
		return;
	}
	el.innerHTML = `<div class="ap-enhance-log-title">${title}</div>${goldRow}` + rows.map((row) => `<div class="ap-enhance-log-row">${row}</div>`).join("");
}

function getStackedEnhanceSpaceBlockReason(item, sourceArr, maxSize) {
	if (!item || (item.count || 1) <= 1) return "";
	if (!Array.isArray(sourceArr)) return "source_missing";
	if (sourceArr.length >= maxSize) return "space_required";
	return "";
}

function getStackedEnhanceSpaceMessage(reason) {
	if (reason === "space_required") return `[시스템] 겹쳐진 장비를 강화하려면 먼저 1칸의 빈 공간이 필요합니다.`;
	return `[시스템] 겹쳐진 장비를 강화 대상으로 분리할 수 없습니다.`;
}

function splitGenericStackableForEnhanceIfNeeded(item) {
	if (!item || !isTemplateStackableItem(item) || item.type === "skill_book" || item.type === "special_equip") {
		return { ok: true, item, split: false };
	}
	if ((item.count || 1) <= 1) return { ok: true, item, split: false };

	let sourceArr = selectedSlot.type === "storage" ? player.storage : player.inventory;
	const maxSize = selectedSlot.type === "storage" ? player.maxStorageSize : player.maxInventorySize;
	const blockReason = getStackedEnhanceSpaceBlockReason(item, sourceArr, maxSize);
	if (blockReason) return { ok: false, item, split: false, reason: blockReason };

	item.count = (item.count || 1) - 1;
	const remainingCount = item.count;
	const splitItem = { ...item, id: Date.now() + Math.random(), count: 1, level: parseInt(item.level) || 0 };
	sourceArr.push(splitItem);
	selectedSlot = { type: selectedSlot.type === "storage" ? "storage" : "inv", index: sourceArr.indexOf(splitItem) };
	return { ok: true, item: splitItem, split: true, remainingCount };
}

function actionReinforce(times) {
	times = Math.max(1, parseInt(times) || 1);
	let pack = getSelectedItemPack();
	let item = pack.item;
	let enhanceResult = typeof createGameActionResult === "function"
		? createGameActionResult("item.enhance", {
			times,
			slotType: selectedSlot && selectedSlot.type,
			slotIndex: selectedSlot && selectedSlot.index,
			itemName: item && item.name,
		})
		: null;
	if (item && item.type === "special_equip") normalizeSpecialStackItem(item);
	if (selectedSlot.type === "trash") {
		if (enhanceResult) {
			enhanceResult.ok = false;
			addResultLog(enhanceResult, `[시스템] 휴지통에 있는 아이템은 강화할 수 없습니다. 먼저 가방으로 복구해 주세요.`);
			return applyActionResultUi(enhanceResult);
		}
		addLog(`[시스템] 휴지통에 있는 아이템은 강화할 수 없습니다. 먼저 가방으로 복구해 주세요.`);
		return;
	}
	if (!item || item.type === "skill_book") return enhanceResult;

	let isTalisman = isTalismanStackItem(item);
	let isEmblem = isEmblemStackItem(item);
	let isStackSpecialEnhance = isTalisman || isEmblem;
	if (item.type === "special_equip" && !isStackSpecialEnhance && !isEnhanceableSpecialEquip(item)) return;

	// 탈리스만/휘장: 강화 대상은 보존하고, 별도의 0강 재료를 소모해 강화합니다.
	// 예: +0 → +1은 강화 대상 1개 + 재료 0강 1개, 총 2개가 필요합니다.
	if (isStackSpecialEnhance) {
		let baseName = getBaseStackName(item);
		let attempts = 0;
		let successRows = [];
		let stoppedReason = "";
		let currentItem = item;

		for (let i = 0; i < times; i++) {
			normalizeSpecialStackItem(currentItem);
			if (!currentItem || currentItem.level >= 6) {
				stoppedReason = "MAX";
				break;
			}

			let currentLevel = parseInt(currentItem.level) || 0;
			let cost = Math.pow(2, currentLevel);
			let isEquippedTarget = selectedSlot.type === "equip";
			let isLooseZeroTarget = !isEquippedTarget && currentLevel === 0;
			let sourceArr = selectedSlot.type === "storage" ? player.storage : player.inventory;
			const sourceMaxSize = selectedSlot.type === "storage" ? player.maxStorageSize : player.maxInventorySize;
			const splitBlockReason = !isEquippedTarget
				? getStackedEnhanceSpaceBlockReason(currentItem, sourceArr, sourceMaxSize)
				: "";
			if (splitBlockReason) {
				stoppedReason = splitBlockReason === "space_required" ? "분리 공간 부족" : "분리 실패";
				break;
			}

			// getZeroLevelMaterialCount는 인벤토리/보관함의 0강 전체를 셉니다.
			// 선택한 +0을 직접 강화하는 경우 이 숫자에는 "강화 대상 1개"도 포함되므로,
			// 실제 필요 수량은 재료 cost + 대상 1개입니다.
			let pool = getZeroLevelMaterialCount(baseName);
			let needed = cost + (isLooseZeroTarget ? 1 : 0);
			if (pool < needed) {
				stoppedReason = `0강 재료 부족`;
				break;
			}

			if (isEquippedTarget) {
				// 장착중인 탈리스만/휘장은 대상을 소모하지 않고 0강 재료만 소모합니다.
				let remaining = consumeZeroLevelMaterials(baseName, cost, null);
				if (remaining > 0) {
					stoppedReason = `0강 재료 부족`;
					break;
				}

				let beforeLevel = currentLevel;
				currentItem.level++;
				if (typeof recordItemAcquired === "function") recordItemAcquired({ ...currentItem, count: 1 });
				attempts++;
				successRows.push(`${i + 1}번째 강화 성공: +${beforeLevel} → +${currentItem.level}`);
			} else {
				// 인벤토리/보관함의 아이템은 선택한 1개를 강화 대상으로 빼고,
				// 나머지 0강을 재료로 소모한 뒤 다음 강화 단계 아이템을 1개 생성합니다.
				currentItem.count = (currentItem.count || 1) - 1;
				if (currentItem.count <= 0) {
					let idx = sourceArr.indexOf(currentItem);
					if (idx !== -1) sourceArr.splice(idx, 1);
				}

				let remaining = consumeZeroLevelMaterials(baseName, cost, null);
				if (remaining > 0) {
					stoppedReason = `0강 재료 부족`;
					break;
				}

				let nextLevel = currentLevel + 1;
				let found = sourceArr.find((it) => getBaseStackName(it) === baseName && (parseInt(it.level) || 0) === nextLevel);
				if (found) {
					ensureSpecialStackIdentity(found);
					found.count = (found.count || 1) + 1;
					currentItem = found;
				} else {
					currentItem = ensureSpecialStackIdentity({
						...item,
						id: Date.now() + Math.random(),
						name: baseName,
						level: nextLevel,
						count: 1,
						isTalisman,
						isEmblem,
					});
					sourceArr.push(currentItem);
				}

				if (typeof recordItemAcquired === "function") recordItemAcquired({ ...currentItem, level: nextLevel, count: 1 });
				selectedSlot = { type: selectedSlot.type === "storage" ? "storage" : "inv", index: sourceArr.indexOf(currentItem) };
				attempts++;
				successRows.push(`${i + 1}번째 강화 성공: +${currentLevel} → +${nextLevel}`);
			}
		}

		if (attempts === 0) {
			const specialStackBlockedMessage = stoppedReason === "분리 공간 부족"
				? getStackedEnhanceSpaceMessage("space_required")
				: `[시스템] ${stoppedReason || "강화할 수 없습니다."}`;
			if (enhanceResult) {
				enhanceResult.ok = false;
				enhanceResult.data = { attempts, successRows, stoppedReason, itemName: baseName };
				addResultLog(enhanceResult, specialStackBlockedMessage);
				setEnhanceResultView(enhanceResult, "강화 결과", [], 0);
				requestUiRefresh(enhanceResult, "updateFullUI");
				requestUiRefresh(enhanceResult, "refreshActionPanelStats");
				return applyActionResultUi(enhanceResult);
			}
			addLog(specialStackBlockedMessage);
			renderEnhanceResultLog("강화 결과", [], 0);
			updateFullUI();
			refreshActionPanelStats();
			return;
		}

		let finalLevel = currentItem ? (parseInt(currentItem.level) || 0) : 0;
		if (enhanceResult) {
			enhanceResult.data = { attempts, successRows, stoppedReason, finalLevel, itemName: baseName, specialStack: true };
			addResultLog(enhanceResult, `✨ [연속강화] ${baseName} ${attempts}회 강화 성공! (현재 +${finalLevel}강)`, true);
			setEnhanceResultView(enhanceResult, `${attempts}회 강화 완료${stoppedReason ? ` / ${stoppedReason}` : ""}`, successRows, 0);
			requestUiRefresh(enhanceResult, "updateFullUI");
			requestUiRefresh(enhanceResult, "refreshActionPanelStats");
			return applyActionResultUi(enhanceResult);
		}
		addLog(`✨ [연속강화] ${baseName} ${attempts}회 강화 성공! (현재 +${finalLevel}강)`, true);
		renderEnhanceResultLog(`${attempts}회 강화 완료${stoppedReason ? ` / ${stoppedReason}` : ""}`, successRows, 0);
		updateFullUI();
		refreshActionPanelStats();
		return;
	}

	const genericStackSplit = splitGenericStackableForEnhanceIfNeeded(item);
	if (!genericStackSplit.ok) {
		const message = getStackedEnhanceSpaceMessage(genericStackSplit.reason);
		if (enhanceResult) {
			enhanceResult.ok = false;
			enhanceResult.data = { reason: genericStackSplit.reason, itemName: item.name, stackedCount: item.count || 1 };
			addResultLog(enhanceResult, message);
			return applyActionResultUi(enhanceResult);
		}
		addLog(message);
		return;
	}
	if (genericStackSplit.split) {
		item = genericStackSplit.item;
		if (enhanceResult) {
			enhanceResult.data.splitFromStackForEnhance = true;
			enhanceResult.data.remainingStackCount = genericStackSplit.remainingCount;
		}
	}

	// 일반장비/강화 가능 특수장비: 성공해도 멈추지 않고 요청 횟수만큼 연속 강화합니다.
	let attempts = 0;
	let successCount = 0;
	let failCount = 0;
	let totalGoldSpent = 0;
	let successRows = [];
	let stoppedReason = "";

	for (let i = 0; i < times; i++) {
		if (item.level >= 20) {
			stoppedReason = "MAX";
			break;
		}

		let cost = getEnhanceCost(item);
		if (player.gold < cost) {
			stoppedReason = "골드 부족";
			break;
		}

		let beforeLevel = item.level;
		let prob = getEnhanceProb(item.level, item);
		player.gold -= cost;
		totalGoldSpent += cost;
		attempts++;

		if (Math.random() <= prob) {
			item.level++;
			successCount++;
			successRows.push(`${i + 1}번째 강화 성공: +${beforeLevel} → +${item.level}`);
		} else {
			failCount++;
		}
	}

	if (failCount > 0 && typeof recordEnhanceFailure === "function") {
		recordEnhanceFailure(item.name || "알 수 없는 아이템", failCount);
	}

	if (attempts === 0) {
		if (enhanceResult) {
			enhanceResult.ok = false;
			enhanceResult.data = { attempts, successCount, failCount, totalGoldSpent, stoppedReason, itemName: item.name };
			addResultLog(enhanceResult, `[시스템] ${stoppedReason || "골드가 부족하거나 최대 레벨입니다."}`);
			setEnhanceResultView(enhanceResult, "강화 결과", [], 0);
			return applyActionResultUi(enhanceResult);
		}
		addLog(`[시스템] ${stoppedReason || "골드가 부족하거나 최대 레벨입니다."}`);
		renderEnhanceResultLog("강화 결과", [], 0);
		return;
	}

	if (enhanceResult) {
		enhanceResult.data = {
			attempts,
			successCount,
			failCount,
			totalGoldSpent,
			stoppedReason,
			itemName: item.name,
			finalLevel: item.level,
			specialStack: false,
			successRows,
		};
		if (successCount > 0) {
			addResultLog(enhanceResult, `✨ [연속강화] ${item.name} ${attempts}회 시도 / 성공 ${successCount}회 / 실패 ${failCount}회 / 현재 +${item.level}강 (-${formatNumber(totalGoldSpent)})`, true);
		} else {
			addResultLog(enhanceResult, `💦 [강화실패] ${item.name} ${attempts}회 연속 실패. (-${formatNumber(totalGoldSpent)})`);
		}
		setEnhanceResultView(enhanceResult, `${attempts}회 시도 / 성공 ${successCount}회 / 실패 ${failCount}회${stoppedReason ? ` / ${stoppedReason}` : ""}`, successRows, totalGoldSpent);
		requestUiRefresh(enhanceResult, "updateFullUI");
		requestUiRefresh(enhanceResult, "refreshActionPanelStats");
		return applyActionResultUi(enhanceResult);
	}

	if (successCount > 0) {
		addLog(`✨ [연속강화] ${item.name} ${attempts}회 시도 / 성공 ${successCount}회 / 실패 ${failCount}회 / 현재 +${item.level}강 (-${formatNumber(totalGoldSpent)})`, true);
	} else {
		addLog(`💦 [강화실패] ${item.name} ${attempts}회 연속 실패. (-${formatNumber(totalGoldSpent)})`);
	}

	renderEnhanceResultLog(`${attempts}회 시도 / 성공 ${successCount}회 / 실패 ${failCount}회${stoppedReason ? ` / ${stoppedReason}` : ""}`, successRows, totalGoldSpent);
	updateFullUI();
	refreshActionPanelStats();
}


function actionSell() {
	let item;
	if (selectedSlot.type === "equip") {
		item = player.equipment[selectedSlot.index];
		if (item) addLog(`[시스템] 장착중인 아이템은 휴지통으로 이동할 수 없습니다. 먼저 장착 해제해 주세요.`);
		return;
	}

	if (selectedSlot.type === "storage") {
		addLog(`[시스템] 보관함에 있는 아이템은 휴지통으로 이동할 수 없습니다. 먼저 가방으로 꺼내 주세요.`);
		return;
	}

	if (selectedSlot.type === "trash") {
		addLog(`[시스템] 이미 휴지통에 있는 아이템입니다. 삭제하려면 휴지통 비우기를 사용해 주세요.`);
		return;
	}

	let targetArray = player.inventory;
	item = targetArray[selectedSlot.index];
	if (!item) return;

	if (!player.trash) player.trash = [];
	if (player.trash.length >= player.maxStorageSize && !(isZeroLevelStackableItem(item) && findStackableItem(item, [player.trash]))) {
		addLog("[시스템] 휴지통이 꽉 찼습니다. 휴지통을 비워 주세요.");
		return;
	}

	let movedItem;
	if (isZeroLevelStackableItem(item)) {
		movedItem = targetArray.splice(selectedSlot.index, 1)[0];
		if (mergeStackableIntoArray(movedItem, player.trash)) {
			addLog(`🗑️ [휴지통] ${getBaseStackName(movedItem)} +${parseInt(movedItem.level) || 0} ${movedItem.count || 1}개를 휴지통에 겹쳐 넣었습니다.`);
		} else {
			player.trash.push(movedItem);
			addLog(`🗑️ [휴지통] ${getBaseStackName(movedItem)} +${parseInt(movedItem.level) || 0} ${movedItem.count || 1}개를 휴지통으로 이동했습니다.`);
		}
	} else if (item.count && item.count > 1) {
		item.count--;
		movedItem = { ...item, count: 1, id: Date.now() + Math.random() };
		player.trash.push(movedItem);
		addLog(`🗑️ [휴지통] ${item.name} 1개를 휴지통으로 이동했습니다. (남은 수량: ${item.count}개)`);
	} else {
		movedItem = targetArray.splice(selectedSlot.index, 1)[0];
		player.trash.push(movedItem);
		addLog(`🗑️ [휴지통] ${movedItem.name}을(를) 휴지통으로 이동했습니다.`);
	}

	closeActionPanel();
	updateFullUI();
	if (currentZoneType !== "town" && currentZoneType !== "boss_empty") startAutoAttack();
}
function actionBulkSell() {
	toggleTrash();
}

function bulkMoveInventoryToTrash() {
	if (!player.inventory || player.inventory.length === 0) {
		addLog("[시스템] 가방에 이동할 아이템이 없습니다.");
		return;
	}
	const modal = document.getElementById("bulk-trash-modal");
	if (modal) modal.style.display = "flex";
}

function closeBulkTrashModal() {
	const modal = document.getElementById("bulk-trash-modal");
	if (modal) modal.style.display = "none";
}

function confirmBulkMoveInventoryToTrash() {
	if (!player.trash) player.trash = [];
	if (!player.inventory || player.inventory.length === 0) {
		closeBulkTrashModal();
		addLog("[시스템] 가방에 이동할 아이템이 없습니다.");
		return;
	}

	let movedCount = 0;
	let remainInventory = [];

	for (let invItem of player.inventory) {
		// 보관함 아이템은 이 함수에서 절대 건드리지 않습니다.
		// 인벤토리 안의 모든 아이템만 휴지통으로 이동합니다.
		if (!invItem) continue;

		if (isZeroLevelStackableItem(invItem)) {
			if (mergeStackableIntoArray(invItem, player.trash)) {
				movedCount += invItem.count || 1;
				continue;
			}
		}

		if (player.trash.length >= player.maxStorageSize) {
			remainInventory.push(invItem);
			continue;
		}

		player.trash.push(invItem);
		movedCount += invItem.count || 1;
	}

	player.inventory = remainInventory;
	closeBulkTrashModal();

	if (movedCount > 0) {
		addLog(`🗑️ [휴지통] 가방의 아이템 ${movedCount}개를 휴지통으로 이동했습니다.`, true);
		updateFullUI();
	} else {
		addLog("[시스템] 휴지통으로 이동할 수 있는 공간이 없습니다.");
	}

	if (!isTrashOpen) toggleTrash();
}

function actionMoveStorage() {
	if (selectedSlot.type === "equip") {
		addLog(`[시스템] 장착중인 아이템은 이동할 수 없습니다. 먼저 장착 해제해 주세요.`);
		return;
	}
	let targetArr;
	let sourceArr;
	let item;

	if (selectedSlot.type === "inv") {
		targetArr = player.storage;
		sourceArr = player.inventory;
		item = sourceArr[selectedSlot.index];
		if (!item) return;
		if (player.storage.length >= player.maxStorageSize && !(isZeroLevelStackableItem(item) && findStackableItem(item, [player.storage]))) {
			addLog("[시스템] 보관함이 꽉 찼습니다.");
			return;
		}
	} else if (selectedSlot.type === "storage") {
		targetArr = player.inventory;
		sourceArr = player.storage;
		item = sourceArr[selectedSlot.index];
		if (!item) return;
		if (player.inventory.length >= player.maxInventorySize && !(isZeroLevelStackableItem(item) && findStackableItem(item, [player.inventory]))) {
			addLog("[시스템] 가방이 꽉 찼습니다.");
			return;
		}
	} else if (selectedSlot.type === "trash") {
		targetArr = player.inventory;
		sourceArr = player.trash;
		item = sourceArr[selectedSlot.index];
		if (!item) return;
		if (player.inventory.length >= player.maxInventorySize && !(isZeroLevelStackableItem(item) && findStackableItem(item, [player.inventory]))) {
			addLog("[시스템] 가방이 꽉 찼습니다.");
			return;
		}
	} else {
		return;
	}

	if (isZeroLevelStackableItem(item) && mergeStackableIntoArray(item, targetArr)) {
		sourceArr.splice(selectedSlot.index, 1);
		addLog(`[이동] ${item.name}을(를) 이동하여 겹쳤습니다.`);
		closeActionPanel();
		updateFullUI();
		return;
	}

	let moved = sourceArr.splice(selectedSlot.index, 1)[0];
	targetArr.push(moved);

	if (selectedSlot.type === "inv") addLog(`[보관] ${moved.name}을(를) 보관함에 넣었습니다.`);
	else if (selectedSlot.type === "storage") addLog(`[이동] ${moved.name}을(를) 가방으로 꺼냈습니다.`);
	else if (selectedSlot.type === "trash") addLog(`[복구] ${moved.name}을(를) 휴지통에서 가방으로 복구했습니다.`);

	closeActionPanel();
	updateFullUI();
}

function emptyTrash() {
	if (!player.trash || player.trash.length === 0) {
		addLog("[시스템] 휴지통이 비어 있습니다.");
		return;
	}
	const modal = document.getElementById("trash-empty-modal");
	if (modal) modal.style.display = "flex";
}

function closeTrashEmptyModal() {
	const modal = document.getElementById("trash-empty-modal");
	if (modal) modal.style.display = "none";
}

function confirmEmptyTrash() {
	if (!player.trash || player.trash.length === 0) {
		closeTrashEmptyModal();
		addLog("[시스템] 휴지통이 비어 있습니다.");
		return;
	}
	const removed = player.trash.length;
	player.trash = [];
	if (selectedSlot.type === "trash") closeActionPanel();
	closeTrashEmptyModal();
	addLog(`🗑️ [휴지통] 휴지통의 아이템 ${removed}칸을 완전히 삭제했습니다.`);
	updateFullUI();
}

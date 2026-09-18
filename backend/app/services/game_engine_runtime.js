// The Python host supplies committed state and server time. No client source is evaluated.
function runServerGame(raw) {
	const input = JSON.parse(raw);
	let now = input.runtime.clock ? input.runtime.clock.cursor : input.now;
	Date.now = () => now;
	let randomCount = 0;
	Math.random = () => {
		if (randomCount >= input.randoms.length) throw Error("random_budget_exceeded");
		return input.randoms[randomCount++] / 9007199254740992;
	};
	const logs = [];
	let actionResult = null;
	for (const name of ["updateFullUI", "updateCombatUI", "updateGoldUI", "renderUI", "renderSkills", "showDamageText", "showItemDropText", "refreshActionPanelStats", "refreshOnOffButtonVisuals", "closeAllGameplayModals", "showConsumedSkillBookPanel", "showGameNotice"]) window[name] = () => {};
	addLog = (message, important = false) => { logs.push({ message, important }); if (logs.length > 200) logs.shift(); };
	applyActionResultUi = (result) => {
		if (!result) return result;
		(result.logs || []).forEach(entry => addLog(entry.message, entry.important));
		if (result.ui && result.ui.startAutoAttack) startAutoAttack();
		if (result.ui && result.ui.closeActionPanel) selectedSlot = { type: null, index: -1 };
		return result;
	};
	window.isAccountGameRuntimePaused = () => false;
	if (input.master) RpgBackendMasterDataRuntime.applyLegacyMasterData(RpgMasterDataAdapter.createLegacyMasterDataFromPayload({ok:true,payload:input.master}), {hydrateStaticAssets:false});
	applyServerSavePayload(input.snapshot);
	normalizePlayerSpecialStackItems();
	ensurePlayerRecords();
	if (input.runtime.game) {
		Object.assign(gameState.runtime, input.runtime.game);
		Object.assign(gameClock, input.runtime.clock);
		gameClock.nextAttackAt = input.runtime.clock.nextAttackAt ?? Infinity;
		gameClock.working = false; gameClock.simulatedAt = null; gameClock.continuation = null;
		const resolveBoss = (boss) => boss ? getBossByIdForReturn(boss.id, !!boss.isSpecial) : null;
		currentBoss = resolveBoss(currentBoss); lastSummonedBoss = resolveBoss(lastSummonedBoss);
	} else {
		currentZoneType = "town";
		initializeGameClock();
	}
	const elapsed = Math.max(0, input.now - gameClock.cursor);
	if (elapsed > 180000) throw Error("settlement_window_exceeded");
	now = input.now;
	let batches = 0;
	while (gameClock.running && gameClock.cursor < now) {
		if (++batches > 200) throw Error("combat_budget_exceeded");
		tickGameClock();
	}
	ensurePlayerRecords().playTimeMs += elapsed;
	const command = input.command;
	if (command) {
		const args = command.args || {};
		const validateBatch = (items) => {
			const actual=items.filter(Boolean).map(item=>({id:String(item.id),count:item.count||1,level:item.level||0}));
			if(!Array.isArray(args.items)||actual.length!==args.items.length||!actual.every((item,i)=>["id","count","level"].every(key=>item[key]===args.items[i][key]))) {
				actionResult=failGameActionResult("items.changed","아이템 목록이 변경됐습니다. 최신 목록과 수량을 확인한 뒤 다시 진행해 주세요.");
				return false;
			}
			return true;
		};
		const pickItem = () => {
			const arrays = {inv:player.inventory,storage:player.storage,equip:player.equipment,trash:player.trash};
			const items = arrays[args.slotType];
			if (!items || !Number.isInteger(args.index) || args.index < 0 || !items[args.index] || String(items[args.index].id) !== String(args.itemId)) throw Error("item_selection_stale");
			selectedSlot = {type:args.slotType,index:args.index};
			return items[args.index];
		};
		switch (command.kind) {
			case "start":
				stopAutoAttack(); currentZoneType="town";currentBoss=null;autoSpecialBossEnabled=false;autoBossSummon=false;
				// Old unrestricted slots are repaired without destroying or selling equipment.
				const displaced = [];
				for (let index=0;index<6;index++) {
					const item=player.equipment[index];
					if(item && !getNormalEquipAllowedSlots(item).includes(index)) {displaced.push(item);player.equipment[index]=null;}
				}
				for (const item of displaced) {
					const allowed=getNormalEquipAllowedSlots(item);
					const empty=allowed.find(i=>!player.equipment[i]);
					if(empty!==undefined) player.equipment[empty]=item;
					else if(hasEmptyItemSlot(player.inventory,player.maxInventorySize)) placeItemInFirstEmptySlot(player.inventory,item,player.maxInventorySize);
					else sendMail({type:"item",title:"장비칸 규칙 변경으로 반환된 장비",item});
				}
				initializeGameClock(); break;
			case "stop": stopAutoAttack(); stopGameClock(); break;
			case "save": refreshRecordSnapshot(true); break;
			case "town": enterTown(); break;
			case "boss_zone": enterBossZone(); break;
			case "field":
				if (!Number.isInteger(args.index) || !zones[args.index]) throw Error("invalid_field");
				if (zones[args.index].req) {
					const req=zones[args.index].req, atk=player.farmAtkBonus||0;
					if(atk<req.minAtk||atk>req.maxAtk) {actionResult=failGameActionResult("field.enter",`입장 조건(${req.text})을 만족하지 않아 입장할 수 없습니다.`);break;}
				}
				changeZone(args.index-currentZoneIndex); break;
			case "summon": {
				const boss=getBossByIdForReturn(args.bossId,!!args.special);
				if(!boss) throw Error("invalid_boss");
				actionResult=summonBoss(boss); break;
			}
			case "remove_boss": removeBoss(); break;
			case "auto_boss": toggleAutoBoss(); break;
			case "equip_drop": toggleEquipDrop(); break;
			case "auto_special":
				if(args.bossId===null){autoSpecialBossEnabled=false;autoSpecialBossId=null;}
				else { const boss=getBossByIdForReturn(args.bossId,true);if(!boss)throw Error("invalid_boss");autoSpecialBossEnabled=true;autoSpecialBossId=boss.id;tryStartAutoSpecialBoss(); } break;
			case "equip": pickItem(); if(args.slotType!=="inv")throw Error("invalid_container");actionResult=actionEquipDirect(args.index);break;
			case "unequip": pickItem();if(args.slotType!=="equip")throw Error("invalid_container");actionResult=actionUnequipDirect(args.index);break;
			case "enhance": pickItem();if(![1,20,50,200].includes(args.times))throw Error("invalid_attempts");actionResult=actionReinforce(args.times);break;
			case "move": pickItem();actionMoveStorage();break;
			case "trash": pickItem();actionSell();break;
			case "compact": if(!["inv","storage","trash"].includes(args.slotType))throw Error("invalid_container");compactPlayerItemContainer(args.slotType);break;
			case "trash_all": if(validateBatch(player.inventory))confirmBulkMoveInventoryToTrash();break;
			case "empty_trash": if(validateBatch(player.trash))confirmEmptyTrash();break;
			case "reset_special": {const item=pickItem();if(args.slotType==="trash"||(!isTalismanStackItem(item)&&!isEmblemStackItem(item))||!(item.level>0))throw Error("invalid_reset");applySpecialResetToZero(item,parseInt(item.level)||0,getSpecialResetRefundCount(item.level));break;}
			case "beginner": giveBeginnerItem();break;
			case "mail": if(!Number.isInteger(args.index)||!player.mailbox[args.index]||String(player.mailbox[args.index].id)!==String(args.mailId))throw Error("mail_selection_stale");claimMail(args.index);break;
			case "mail_all": claimAllMail();break;
			default: throw Error("unknown_game_command");
		}
	}
	if (command?.kind === "enhance" && actionResult) {
		const item = getSelectedItemPack().item;
		actionResult.data = {...actionResult.data, selection: item ? {...selectedSlot, itemId:item.id} : null};
	}
	const clock={running:gameClock.running,cursor:gameClock.cursor,nextAttackAt:Number.isFinite(gameClock.nextAttackAt)?gameClock.nextAttackAt:null,nextBuffAt:gameClock.nextBuffAt,nextMaintenanceAt:gameClock.nextMaintenanceAt};
	return JSON.stringify({snapshot:getServerSavePayload(5),runtime:{game:gameState.runtime,clock},randomCount,result:actionResult,logs});
}

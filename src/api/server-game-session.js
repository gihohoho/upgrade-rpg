(function () {
	"use strict";
	let active = false, connected = false, revision = -1, sessionKey = null;
	let socket = null, busy = null, pending = null, committed = null, identity = null;
	let visuals = null, intentionalClose = false, capability = null;
	let reconnectTimer = null, reconnectAttempt = 0, reconnecting = false, replaced = false;
	let lastVisualAt = 0, nextVisualAttack = 0, deferredUpdate = null;
	const originalSave = window.saveGame;
	const originalQueue = window.queueCurrentAccountSave;
	const originalFlush = window.flushAccountGameSave;
	const originalKill = window.killEnemy;
	const originalStartAttack = window.startAutoAttack;
	const originalReset = window.confirmResetGame;
	let returnFocus = null;
	let rootWasInert = false;

	function noticeElements() {
		let modal = document.getElementById("game-server-modal");
		if (modal) return modal;
		modal = document.createElement("div");
		modal.id = "game-server-modal";
		modal.className = "game-server-modal";
		modal.hidden = true;
		modal.innerHTML = '<section role="dialog" aria-modal="true" aria-labelledby="game-server-title" aria-describedby="game-server-description" tabindex="-1"><h2 id="game-server-title"></h2><p id="game-server-description" aria-live="polite"></p><div class="game-server-actions"></div></section>';
		modal.addEventListener("keydown", (event) => {
			if (event.key === "Escape" && modal.dataset.closeable === "true") closeNotice();
			if (event.key === "Tab") {
				const buttons = [...modal.querySelectorAll("button:not(:disabled)")];
				if (!buttons.length) { event.preventDefault(); return; }
				if (event.shiftKey && document.activeElement === buttons[0]) { event.preventDefault(); buttons.at(-1).focus(); }
				if (!event.shiftKey && document.activeElement === buttons.at(-1)) { event.preventDefault(); buttons[0].focus(); }
			}
		});
		document.body.appendChild(modal);
		return modal;
	}
	function closeNotice() {
		const modal = noticeElements(); modal.hidden = true;
		const root=document.getElementById("game-root");if(root)root.inert=rootWasInert;
		if (returnFocus && returnFocus.isConnected) returnFocus.focus();
	}
	function showNotice(title, description, buttons = [{label:"확인", action:closeNotice}], closeable = true) {
		const modal = noticeElements();
		if (modal.hidden) {
			returnFocus = document.activeElement;
			const root=document.getElementById("game-root");rootWasInert=!!root?.inert;if(root)root.inert=true;
		}
		modal.querySelector("h2").textContent = title;
		modal.querySelector("p").textContent = description;
		const actions = modal.querySelector(".game-server-actions"); actions.replaceChildren();
		for (const button of buttons) {
			const element = document.createElement("button"); element.type = "button"; element.textContent = button.label;
			element.addEventListener("click", button.action); actions.appendChild(element);
		}
		modal.dataset.closeable = String(closeable); modal.hidden = false;
		(modal.querySelector("button") || modal.querySelector("section")).focus();
	}
	window.showGameNotice = (title, description) => showNotice(title, description);

	function status(message, error = false) {
		let element = document.getElementById("server-game-status");
		if (!element) {
			element = document.createElement("div"); element.id = "server-game-status";
			element.setAttribute("role", "status");
			(document.getElementById("background-progress-status")?.parentElement || document.body).appendChild(element);
		}
		element.textContent = message; element.classList.toggle("is-error", error);
	}
	function backup() {
		if (!committed) return false;
		try { localStorage.setItem(getActiveLocalSaveKey(), JSON.stringify(committed)); return true; } catch (_) { return false; }
	}
	function pendingKey() { return `server-game-pending:${identity.accountCharacterId}`; }
	function savePending(value) {
		// This is an action receipt lookup, never a player snapshot to upload.
		try { if (value) localStorage.setItem(pendingKey(), JSON.stringify(value)); else localStorage.removeItem(pendingKey()); }
		catch (_) { if(value) throw new Error("이 기기에 요청 복구 정보를 저장하지 못했습니다. 저장 공간을 확보한 뒤 다시 시도해 주세요."); }
	}
	function apply(update, {force = false} = {}) {
		if (!update || update.heartbeat || update.revision < revision) return;
		if (!force && (document.hidden || busy)) {
			if (!deferredUpdate || update.revision >= deferredUpdate.revision) deferredUpdate = update;
			return;
		}
		if (update.revision === revision && committed) return;
		revision = update.revision;
		committed = JSON.parse(JSON.stringify(update.snapshot));
		applyServerSavePayload(JSON.parse(JSON.stringify(committed)));
		Object.assign(gameState.runtime, update.runtime.game);
		if(currentBoss)currentBoss=getBossByIdForReturn(currentBoss.id,!!currentBoss.isSpecial);
		if(lastSummonedBoss)lastSummonedBoss=getBossByIdForReturn(lastSummonedBoss.id,!!lastSummonedBoss.isSpecial);
		// Authoritative state remains in committed. The visible HP/buffs are prediction only.
		stopGameClock(); attackInterval = null;
		if (typeof normalizePlayerItemIcons === "function") normalizePlayerItemIcons(player);
		updateFullUI(); renderSkills(); refreshOnOffButtonVisuals(); updateAutoSpecialBossButton();
		const auto = document.getElementById("btn-auto-boss");
		const drop = document.getElementById("btn-equip-drop");
		if (auto) auto.innerHTML = `자동소환<br />${autoBossSummon ? "ON" : "OFF"}`;
		if (drop) drop.innerHTML = `장비드랍<br />${equipDropEnabled ? "ON" : "OFF"}`;
		if (selectedSlot.type) refreshActionPanelStats();
		(update.logs || []).forEach(entry => addLog(entry.message, entry.important));
		lastVisualAt = Date.now(); nextVisualAttack = Date.now() + Math.max(1, getTotals().aspdMs || 560);
		backup();
		status(connected ? "서버 사냥 연결됨 · 보상은 1분마다 저장됩니다. 전투 화면은 예상 진행을 표시합니다." : "게임 서버에 연결하고 있습니다…");
	}

	async function request(path, body) {
		const result = await RpgGameApi.request(`/game/session/${path}`, {method:body ? "POST":"GET", body, timeoutMs:20000});
		return result.payload;
	}
	async function available() {
		if (capability !== null) return capability;
		const result = await request("capabilities");
		capability = result.serverAuthority === true;
		return capability;
	}
	function connect() {
		return new Promise((resolve, reject) => {
			intentionalClose = false;
			const url = new URL(RpgGameApi.buildUrl("/game/session/live"));
			url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
			const channel = new WebSocket(url); socket = channel;
			let opened = false;
			const timeout = setTimeout(() => { if (!opened) { channel.close(); reject(new Error("게임 서버 연결을 완료하지 못했습니다.")); } }, 20000);
			channel.onopen = () => channel.send(JSON.stringify({token:RpgAuthSession.getAccessToken(), identity, sessionKey}));
			channel.onmessage = (event) => {
				if (socket !== channel) return;
				const update = JSON.parse(event.data);
				if (update.sessionKey !== sessionKey) return;
				if(update.accessToken) RpgAuthSession.storeAccessToken(update.accessToken, RpgAuthSession.getSessionSnapshot().persistence === "local");
				connected = !!update.active;
				if (!opened) { opened = true; clearTimeout(timeout); reconnectAttempt=0;resolve(); }
				apply(update);
			};
			channel.onclose = () => {
				clearTimeout(timeout);
				if (socket !== channel) return;
				connected = false;
				if (!opened) reject(new Error("게임 연결이 종료됐습니다. 다시 접속해 주세요."));
				if (!intentionalClose && active) {
					status("연결이 끊겨 사냥이 중단됩니다. 자동으로 다시 연결하고 있습니다…", true);
					scheduleReconnect();
				}
			};
		});
	}
	function scheduleReconnect() {
		if(intentionalClose || replaced || reconnectTimer || reconnecting || !active || connected)return;
		const delay=Math.min(30000,1000*2**Math.min(reconnectAttempt++,5))+Math.floor(Math.random()*500);
		reconnectTimer=setTimeout(async()=>{
			reconnectTimer=null;reconnecting=true;
			try {
				const update=await request("resume",{...identity,sessionKey});
				apply(update);await connect();
				status("다시 연결됐습니다. 사냥을 이어갑니다. 연결이 끊긴 시간은 제외됩니다.");
			} catch(error) {
				if([401,403].includes(Number(error.status))) {replaced=true;RpgAccountGate.handleGameSessionInvalid(error);}
				else if([404,409].includes(Number(error.status))) {replaced=true;status("다른 탭으로 접속했거나 게임이 종료됐습니다.",true);if(!document.hidden&&!busy)showReconnect();}
			} finally {reconnecting=false;if(!connected)scheduleReconnect();}
		},delay);
	}
	function showReconnect() {
		showNotice("게임 연결 끊김", "연결이 끊긴 시간에는 사냥이 진행되지 않습니다. 다시 접속하면 저장된 결과를 불러옵니다.", [{label:"다시 접속", action:()=>location.reload()}], false);
	}
	async function start() {
		identity = {slotKey:getActiveBackendSlotKey(), accountCharacterId:getActiveAccountCharacterId()};
		let oldPending;
		try { oldPending = JSON.parse(localStorage.getItem(pendingKey()) || "null"); } catch (_) {}
		// Recover an uncertain old command BEFORE replacing its session. A committed
		// receipt is readable even after disconnect; uncommitted work cannot reroll.
		let recovered = null;
		if (oldPending) {
			try { recovered = await request("command", oldPending); }
			catch (error) { if (![404,409,422].includes(Number(error.status))) throw error; }
			savePending(null);
		}
		const update = await request("open", identity);
		const oldLocal = localStorage.getItem(getActiveLocalSaveKey());
		if(oldLocal && oldLocal !== JSON.stringify(update.snapshot)) {
			// Preserve pre-migration and pending local saves; they cannot overwrite server results.
			localStorage.setItem(`${getActiveLocalSaveKey()}.before-server-game.${Date.now()}`,oldLocal);
		}
		active = true; revision = -1; sessionKey = update.sessionKey;
		isAccountGameBooted = true; isAccountGameRuntimePaused = false;
		apply(update, {force:true});
		await connect();
		startVisuals();
		window.dispatchEvent(new CustomEvent("upgrade-rpg:account-game-ready", {detail:identity}));
		RpgAuthSession.clearPendingUnsyncedSave({accountCharacterId:identity.accountCharacterId,slotKey:identity.slotKey});
		if (recovered?.result) showResult(recovered, "enhance");
		status("서버 사냥 연결됨 · 보상은 1분마다 저장됩니다. 전투 화면은 예상 진행을 표시합니다.");
		return {ok:true, loaded:true, source:"server-gameplay"};
	}
	function selected(type = selectedSlot.type, index = selectedSlot.index) {
		const items = {inv:player.inventory,equip:player.equipment,storage:player.storage,trash:player.trash}[type];
		const item = items && items[index];
		if (!item) throw new Error("아이템을 다시 선택해 주세요.");
		return {slotType:type, index, itemId:item.id};
	}
	function showResult(update, kind) {
		if (["town", "boss_zone", "field"].includes(kind)) closeAllGameplayModals();
		if (["equip", "unequip", "move", "trash", "trash_all", "empty_trash", "reset_special"].includes(kind)) closeActionPanel();
		const result = update.result;
		if (result) {
			if (kind === "enhance" && result.data?.selection) {
				const selection = result.data.selection;
				const items = {inv:player.inventory,equip:player.equipment,storage:player.storage}[selection.type];
				if (String(items?.[selection.index]?.id) === String(selection.itemId)) {
					selectedSlot = {type:selection.type,index:selection.index};
					refreshActionPanelStats();
				}
			}
			// Effects and messages are visible only after the transaction committed.
			applyActionResultUi({...result,logs:[],ui:{...result.ui,startAutoAttack:false}});
			if (result.ok === false) showNotice(kind === "summon" ? "보스 소환 안내" : "처리 안내",
				(result.logs || []).map(entry => String(entry.message).replace(/<[^>]*>/g, "").replace(/^\[시스템\]\s*/, "")).join("\n") || "현재 상태에서는 진행할 수 없습니다.");
		}
	}
	function command(kind, args = {}, {silent = false} = {}) {
		if (busy) return busy;
		if (!connected) { showNotice("연결 확인 중", "서버에 다시 연결한 뒤 진행할 수 있습니다.");scheduleReconnect();return Promise.reject(new Error("게임 연결을 확인해 주세요.")); }
		pending = {...identity,sessionKey,requestId:crypto.randomUUID().replaceAll("-", ""),kind,args};
		savePending(pending);
		busy = new Promise((resolve, reject) => {
			let attempting = false;
			const attempt = async () => {
				if(attempting)return;attempting=true;
				if (!silent) showNotice(kind === "enhance" ? "강화 중" : "처리 중", "결과를 저장하고 있습니다. 잠시만 기다려 주세요.", [], false);
				try {
					const update = await request("command", pending);
					pending = null; savePending(null); busy = null;
					if (!silent) closeNotice();
					apply(update, {force:true});
					if (deferredUpdate) { const queued = deferredUpdate; deferredUpdate = null; apply(queued); }
					showResult(update, kind);
					if (kind === "stop") { intentionalClose = true; connected = false; socket?.close(); }
					resolve(update);
				} catch (error) {
					if (Number(error.status) === 429) {
						setTimeout(attempt, 1000);
						return;
					}
					if ([400,401,403,404,409,422].includes(Number(error.status))) {
						pending = null; savePending(null); busy = null;
						if([401,403].includes(Number(error.status))) {closeNotice();RpgAccountGate.handleGameSessionInvalid(error);reject(error);return;}
						showNotice("처리하지 못했습니다", error.message || "다시 접속한 뒤 시도해 주세요.", [{label:"확인",action:closeNotice},{label:"다시 접속",action:()=>location.reload()}]);
						reject(error); return;
					}
					showNotice("저장 결과 확인 필요", "응답을 받지 못했습니다. 다시 확인하면 같은 요청의 결과를 불러옵니다. 새 강화는 진행되지 않습니다.", [{label:"결과 다시 확인",action:attempt}], false);
				} finally { attempting=false;
				}
			};
			attempt();
		});
		return busy;
	}
	function invoke(kind, args, options) {
		try { return command(kind, typeof args === "function" ? args() : args, options).catch(()=>{}); }
		catch (error) { showNotice("처리 안내", error.message); }
	}
	function bind(name, kind, args = () => ({})) {
		const legacy = window[name];
		window[name] = (...values) => active ? invoke(kind, () => args(...values)) : legacy(...values);
	}
	bind("summonBoss", "summon", boss => ({bossId:boss.id,special:!!boss.isSpecial}));
	bind("enterTown", "town"); bind("enterBossZone", "boss_zone");
	bind("changeZone", "field", offset => ({index:currentZoneIndex+offset}));
	bind("moveToRecentField", "field", () => ({index:currentZoneIndex}));
	bind("removeBoss", "remove_boss"); bind("toggleAutoBoss", "auto_boss"); bind("toggleEquipDrop", "equip_drop");
	bind("startAutoSpecialBoss", "auto_special", bossId => {closeAutoSpecialBossModal();return {bossId};});
	const oldAutoSpecial = window.toggleAutoSpecialBoss;
	window.toggleAutoSpecialBoss = () => active && autoSpecialBossEnabled ? invoke("auto_special",{bossId:null}) : oldAutoSpecial();
	bind("actionEquipDirect", "equip", index => selected("inv",index));
	bind("actionUnequipDirect", "unequip", index => selected("equip",index));
	bind("actionReinforce", "enhance", times => ({...selected(),times}));
	bind("actionMoveStorage", "move", () => selected()); bind("actionSell", "trash", () => selected());
	bind("compactPlayerItemContainer", "compact", slotType => ({slotType}));
	const itemManifest = items => items.filter(Boolean).map(item=>({id:String(item.id),count:item.count||1,level:item.level||0}));
	let trashManifest = null, emptyManifest = null;
	const oldBulk = window.bulkMoveInventoryToTrash, oldEmpty = window.emptyTrash;
	window.bulkMoveInventoryToTrash = (...args) => { if(active) trashManifest=itemManifest(player.inventory);return oldBulk(...args); };
	window.emptyTrash = (...args) => { if(active) emptyManifest=itemManifest(player.trash);return oldEmpty(...args); };
	bind("confirmBulkMoveInventoryToTrash", "trash_all", () => {closeBulkTrashModal();return {items:trashManifest||[]};});
	bind("confirmEmptyTrash", "empty_trash", () => {closeTrashEmptyModal();return {items:emptyManifest||[]};});
	bind("confirmSpecialReset", "reset_special", () => {
		const selection=selected();
		if (!pendingSpecialReset || String(pendingSpecialReset.item.id)!==String(selection.itemId)) throw Error("장비를 다시 선택해 주세요.");
		closeSpecialResetModal();return selection;
	});
	bind("giveBeginnerItem", "beginner");
	bind("claimMail", "mail", index => ({index,mailId:player.mailbox[index].id})); bind("claimAllMail", "mail_all");
	bind("manualSaveGame", "save");
	window.confirmResetGame = () => active ? showNotice("초기화 안내", "마을의 캐릭터 변경 화면에서 캐릭터를 삭제한 뒤 새로 만들어 주세요.") : originalReset();
	window.saveGame = (...args) => active ? backup() : originalSave(...args);
	window.queueCurrentAccountSave = (...args) => active ? command("save", {}, {silent:true}) : originalQueue(...args);
	window.flushAccountGameSave = async (options = {}) => {
		if (!active) return originalFlush(options);
		if (busy) await busy;
		return command(["account-logout","character-switch"].includes(options.reason) ? "stop" : "save", {}, {silent:true});
	};
	window.startAutoAttack = () => active ? undefined : originalStartAttack();
	window.killEnemy = (...args) => {
		if (!active) return originalKill(...args);
		if (currentZoneType === "field") scheduleFieldRespawn(currentZoneIndex,2000);
		else if (currentBoss && !currentBoss.isSpecial && autoBossSummon) currentBossHp = currentBoss.maxHp;
		else currentBossHp = 0;
		updateCombatUI();
	};
	function startVisuals() {
		if (visuals) return;
		stopGameClock();
		visuals = setInterval(() => {
			if (document.hidden || !connected || busy || isAccountGameRuntimePaused) return;
			const now = Date.now();
			// Never replay missed browser time. Server messages replace state directly.
			if (now-lastVisualAt > 1000) { nextVisualAttack=now+Math.max(1,getTotals().aspdMs||560); }
			tickActiveBuffs(Math.min(100,now-lastVisualAt));lastVisualAt=now;
			if (now >= nextVisualAttack && ((currentZoneType === "boss_fight" && currentBoss && currentBossHp>0) || currentZoneType === "field")) {
				nextVisualAttack=now+Math.max(1,getTotals().aspdMs||560);
				if(currentZoneType === "field" && currentEnemy.hp <= 0) currentEnemy.hp=getFieldEnemyHp(currentZoneIndex);
				playerAttack();
			}
		},100);
	}
	document.addEventListener("visibilitychange", () => {
		if (!active || document.hidden) return;
		if (deferredUpdate) {const update=deferredUpdate;deferredUpdate=null;apply(update);}
		lastVisualAt=Date.now();nextVisualAttack=Date.now()+Math.max(1,getTotals().aspdMs||560);
		if (!connected && !busy) {if(replaced)showReconnect();else scheduleReconnect();}
	});
	window.addEventListener("pagehide", () => { if (active) { intentionalClose=true;socket?.close(); } });
	window.addEventListener("online",scheduleReconnect);
	window.addEventListener("pageshow", event => { if(event.persisted && active) location.reload(); });
	window.RpgServerGame = {available,start,startVisuals,command,get active(){return active;},get connected(){return connected;}};
})();

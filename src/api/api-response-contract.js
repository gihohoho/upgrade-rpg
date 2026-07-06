/**
 * API Response Contract
 * -----------------------------------------------------------------------------
 * FastAPI 백엔드 전환 전, 프론트와 백엔드가 공유할 응답 형태를 고정하기 위한
 * 계약 파일입니다.
 *
 * 현재 게임은 아직 실제 API를 호출하지 않지만, v071~v073에서 도입한
 * Action Result 구조를 서버 응답으로 확장할 때 이 형태를 기준으로 사용합니다.
 *
 * 주의:
 * - 이 파일은 현재 index.html에서 로드하지 않습니다.
 * - 즉, 현재 게임 동작에는 영향을 주지 않습니다.
 * - FastAPI 구현 / Vue 전환 / 테스트 코드 작성 시 기준 문서 겸 상수 파일로 사용합니다.
 */
(function attachApiResponseContract(global) {
	const RESPONSE_VERSION = "game-api-response.v1";

	const API_ENDPOINTS = Object.freeze({
		GAME_LOAD: "GET /game/load",
		GAME_SAVE: "POST /game/save",
		GAME_MASTER_DATA: "GET /game/master-data",

		BATTLE_ATTACK: "POST /battle/attack",
		BOSS_SUMMON: "POST /boss/summon",
		BOSS_ATTACK: "POST /boss/attack",

		ITEM_EQUIP: "POST /item/equip",
		ITEM_UNEQUIP: "POST /item/unequip",
		ITEM_ENHANCE: "POST /item/enhance",
		ITEM_MOVE_STORAGE: "POST /item/move-storage",
		ITEM_MOVE_TRASH: "POST /item/move-trash",
		ITEM_EMPTY_TRASH: "POST /item/empty-trash",

		SKILL_USE_BOOK: "POST /skill/use-book",

		MAILBOX_LIST: "GET /mailbox",
		MAILBOX_CLAIM: "POST /mailbox/{mailId}/claim",
		MAILBOX_CLAIM_ALL: "POST /mailbox/claim-all",

		ADMIN_ITEMS: "/admin/items",
		ADMIN_BOSSES: "/admin/bosses",
		ADMIN_DROP_TABLES: "/admin/drop-tables",
		ADMIN_FIELD_ZONES: "/admin/field-zones",
		ADMIN_ENHANCEMENT_RULES: "/admin/enhancement-rules",
		ADMIN_CHARACTERS: "/admin/characters",
		ADMIN_SKILLS: "/admin/skills",
	});

	const ACTION_TYPES = Object.freeze({
		GAME_LOAD: "game.load",
		GAME_SAVE: "game.save",
		GAME_MASTER_DATA: "game.master_data",

		COMBAT_ATTACK: "combat.attack",
		COMBAT_KILL: "combat.kill",
		BOSS_SUMMON: "boss.summon",

		ITEM_EQUIP: "item.equip",
		ITEM_UNEQUIP: "item.unequip",
		ITEM_ENHANCE: "item.enhance",
		ITEM_MOVE_STORAGE: "item.move_storage",
		ITEM_MOVE_TRASH: "item.move_trash",
		ITEM_EMPTY_TRASH: "item.empty_trash",

		SKILL_BOOK_USE: "skill_book.use",

		MAILBOX_LIST: "mailbox.list",
		MAILBOX_CLAIM: "mailbox.claim",
		MAILBOX_CLAIM_ALL: "mailbox.claim_all",

		ADMIN_CHANGE: "admin.change",
	});

	const ERROR_CODES = Object.freeze({
		UNKNOWN_ERROR: "UNKNOWN_ERROR",
		UNAUTHORIZED: "UNAUTHORIZED",
		FORBIDDEN: "FORBIDDEN",
		NOT_FOUND: "NOT_FOUND",
		VALIDATION_ERROR: "VALIDATION_ERROR",
		CONFLICT: "CONFLICT",
		NOT_ENOUGH_GOLD: "NOT_ENOUGH_GOLD",
		INVENTORY_FULL: "INVENTORY_FULL",
		COOLDOWN_ACTIVE: "COOLDOWN_ACTIVE",
		INVALID_STATE: "INVALID_STATE",
		MAX_LEVEL_REACHED: "MAX_LEVEL_REACHED",
	});

	function nowIso() {
		return new Date().toISOString();
	}

	function createApiSuccessResponse(options = {}) {
		return {
			ok: true,
			responseVersion: RESPONSE_VERSION,
			type: options.type || "system.ok",
			requestId: options.requestId || null,
			serverTime: options.serverTime || nowIso(),
			createdAt: options.createdAt || Date.now(),
			payload: options.payload || {},
			data: options.data || {},
			logs: Array.isArray(options.logs) ? options.logs : [],
			effects: Array.isArray(options.effects) ? options.effects : [],
			ui: options.ui || {},
			statePatch: options.statePatch || {},
			meta: options.meta || {},
			error: null,
		};
	}

	function createApiErrorResponse(options = {}) {
		return {
			ok: false,
			responseVersion: RESPONSE_VERSION,
			type: options.type || "system.error",
			requestId: options.requestId || null,
			serverTime: options.serverTime || nowIso(),
			createdAt: options.createdAt || Date.now(),
			payload: options.payload || {},
			data: options.data || {},
			logs: Array.isArray(options.logs) ? options.logs : [],
			effects: [],
			ui: {},
			statePatch: {},
			meta: options.meta || {},
			error: {
				code: options.code || ERROR_CODES.UNKNOWN_ERROR,
				message: options.message || "요청을 처리할 수 없습니다.",
				details: options.details || {},
				fieldErrors: options.fieldErrors || {},
			},
		};
	}

	function normalizeActionResultToApiResponse(actionResult, options = {}) {
		if (!actionResult) {
			return createApiErrorResponse({
				type: options.type || "system.error",
				code: ERROR_CODES.INVALID_STATE,
				message: "변환할 Action Result가 없습니다.",
			});
		}

		const base = {
			type: actionResult.type,
			requestId: options.requestId || null,
			createdAt: actionResult.createdAt || Date.now(),
			payload: actionResult.payload || {},
			data: actionResult.data || {},
			logs: Array.isArray(actionResult.logs) ? actionResult.logs : [],
			effects: Array.isArray(actionResult.effects) ? actionResult.effects : [],
			ui: actionResult.ui || {},
			statePatch: options.statePatch || {},
			meta: options.meta || {},
		};

		if (actionResult.ok === false) {
			return createApiErrorResponse({
				...base,
				code: options.code || actionResult.errorCode || ERROR_CODES.INVALID_STATE,
				message: options.message || (base.logs[0] && base.logs[0].message) || "요청을 처리할 수 없습니다.",
				details: options.details || {},
			});
		}

		return createApiSuccessResponse(base);
	}

	const API_RESPONSE_EXAMPLES = Object.freeze({
		combatAttack: createApiSuccessResponse({
			type: ACTION_TYPES.COMBAT_ATTACK,
			data: {
				target: { kind: "field", name: "필드 몬스터", hpBefore: 100000, hpAfter: 0 },
				totalDamage: 123456,
				normalDamage: 100000,
				skillHits: [{ label: "[W]", damage: 23456 }],
				killed: true,
			},
			effects: [{ type: "damageText", text: "[W] 23,456", extraClass: "skill-damage" }],
			ui: { updateCombatUI: true },
		}),
		combatKill: createApiSuccessResponse({
			type: ACTION_TYPES.COMBAT_KILL,
			data: {
				target: "boss",
				drops: [{ itemName: "심연의 편린 스태프", dropType: "equipment", stacked: false, stored: false }],
				rewards: { gold: 0 },
				transition: { bossCleared: true, returnToField: true },
			},
			logs: [{ message: "심연의 편린 스태프 획득!", important: true }],
			effects: [{ type: "itemDropText", itemName: "심연의 편린 스태프" }],
			ui: { renderUI: true },
		}),
		itemEnhance: createApiSuccessResponse({
			type: ACTION_TYPES.ITEM_ENHANCE,
			data: {
				itemInstanceId: "item_123",
				itemName: "초월 탈리스만",
				beforeLevel: 2,
				afterLevel: 3,
				attempts: 1,
				successCount: 1,
				failCount: 0,
				goldSpent: 0,
			},
			ui: { updateFullUI: true, enhanceResult: { title: "강화 결과", rows: [], goldSpent: 0 } },
		}),
		bossSummonError: createApiErrorResponse({
			type: ACTION_TYPES.BOSS_SUMMON,
			code: ERROR_CODES.COOLDOWN_ACTIVE,
			message: "특수보스 쿨타임이 아직 남아 있습니다.",
			details: { remainingSeconds: 120 },
		}),
	});

	global.GAME_API_CONTRACT = Object.freeze({
		RESPONSE_VERSION,
		API_ENDPOINTS,
		ACTION_TYPES,
		ERROR_CODES,
		createApiSuccessResponse,
		createApiErrorResponse,
		normalizeActionResultToApiResponse,
		API_RESPONSE_EXAMPLES,
	});
})(typeof window !== "undefined" ? window : globalThis);

if (typeof module !== "undefined" && module.exports) {
	module.exports = globalThis.GAME_API_CONTRACT;
}

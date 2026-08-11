(function () {
	"use strict";

	const VERSION = "v371.account-email-auth-session";
	const ACCESS_TOKEN_KEY = "upgradeRpgAccountAccessToken";
	const SELECTED_CHARACTER_KEY = "upgradeRpgSelectedAccountCharacter";
	const AUTH_NOTICE_KEY = "upgradeRpgAccountAuthNotice";
	const PENDING_UNSYNCED_SAVES_KEY = "upgradeRpgPendingUnsyncedAccountSaves";
	const LEGACY_LOCAL_SAVE_KEY = "idleRpgSaveV22";
	const DEFAULT_BACKEND_SLOT_KEY = "default";
	const ACCOUNT_CHARACTER_ID_PATTERN = /^[a-f0-9]{32}$/i;

	let accessToken = "";
	let persistence = "session";
	let currentUser = null;
	let currentCharacter = null;
	let transitionInProgress = false;

	function readStorage(storage, key) {
		try {
			return storage ? storage.getItem(key) : null;
		} catch (error) {
			return null;
		}
	}

	function writeStorage(storage, key, value) {
		try {
			if (!storage) return false;
			if (value === null || value === undefined || value === "") storage.removeItem(key);
			else storage.setItem(key, String(value));
			return true;
		} catch (error) {
			return false;
		}
	}

	function readJson(storage, key) {
		const raw = readStorage(storage, key);
		if (!raw) return null;
		try {
			return JSON.parse(raw);
		} catch (error) {
			return null;
		}
	}

	function getAccountCharacterId(character) {
		const source = character || currentCharacter;
		if (!source || typeof source !== "object") return null;
		const value = source.accountCharacterId !== undefined ? source.accountCharacterId : source.id;
		const normalized = String(value || "").trim().toLowerCase();
		return ACCOUNT_CHARACTER_ID_PATTERN.test(normalized) ? normalized : null;
	}

	function getUserId(user) {
		const source = user || currentUser;
		if (!source || typeof source !== "object") return null;
		const value = source.userId !== undefined ? source.userId : source.id;
		const parsed = Number(value);
		return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
	}

	function normalizeUser(payload) {
		const source = payload && payload.user && typeof payload.user === "object" ? payload.user : payload;
		if (!source || typeof source !== "object") return null;
		const id = getUserId(source);
		if (!id) return null;
		return {
			...source,
			id,
			userId: id,
			username: String(source.username || source.loginId || "").trim(),
			email: String(source.email || "").trim().toLowerCase(),
			emailVerified: source.emailVerified === true || source.email_verified === true || !!source.emailVerifiedAt || !!source.email_verified_at,
			isAdmin: source.isAdmin === true || source.is_admin === true,
			isActive: source.isActive !== false && source.is_active !== false,
		};
	}

	function normalizeCharacter(character) {
		if (!character || typeof character !== "object") return null;
		const metadata = character.accountCharacter && typeof character.accountCharacter === "object"
			? character.accountCharacter
			: (character.character && typeof character.character === "object" ? character.character : character);
		const source = { ...character, ...metadata };
		const id = getAccountCharacterId(source);
		const slotIndex = Number(source.slotIndex !== undefined ? source.slotIndex : source.slot_index);
		if (!id || !Number.isInteger(slotIndex) || slotIndex < 1 || slotIndex > 8) return null;
		return {
			...source,
			id,
			accountCharacterId: id,
			slotIndex,
			slotKey: `character-${slotIndex}`,
			name: String(source.name || source.characterName || `캐릭터 ${slotIndex}`).trim(),
			characterCode: String(source.characterCode || source.character_code || "weapon_master").trim() || "weapon_master",
			summary: character.progress && typeof character.progress === "object"
				? { ...character.progress }
				: (source.summary && typeof source.summary === "object" ? { ...source.summary } : {}),
		};
	}

	function extractAccessToken(response) {
		const payload = response && response.payload && typeof response.payload === "object" ? response.payload : {};
		return String(payload.accessToken || payload.access_token || payload.token || "").trim();
	}

	function getAccessToken() {
		return accessToken;
	}

	function restoreTokenFromStorage() {
		const localToken = readStorage(window.localStorage, ACCESS_TOKEN_KEY);
		const sessionToken = readStorage(window.sessionStorage, ACCESS_TOKEN_KEY);
		if (localToken) {
			accessToken = localToken;
			persistence = "local";
		} else if (sessionToken) {
			accessToken = sessionToken;
			persistence = "session";
		} else {
			accessToken = "";
			persistence = "session";
		}
		return accessToken;
	}

	function storeAccessToken(token, keepLogin) {
		accessToken = String(token || "").trim();
		persistence = keepLogin ? "local" : "session";
		writeStorage(window.localStorage, ACCESS_TOKEN_KEY, keepLogin ? accessToken : null);
		writeStorage(window.sessionStorage, ACCESS_TOKEN_KEY, keepLogin ? null : accessToken);
		return accessToken;
	}

	function getSelectedCharacterStorage() {
		return persistence === "local" ? window.localStorage : window.sessionStorage;
	}

	function restoreSelectedCharacter() {
		const preferred = readJson(getSelectedCharacterStorage(), SELECTED_CHARACTER_KEY);
		const fallback = preferred || readJson(window.sessionStorage, SELECTED_CHARACTER_KEY) || readJson(window.localStorage, SELECTED_CHARACTER_KEY);
		currentCharacter = normalizeCharacter(fallback);
		return currentCharacter;
	}

	function storeSelectedCharacter(character) {
		currentCharacter = normalizeCharacter(character);
		writeStorage(window.localStorage, SELECTED_CHARACTER_KEY, null);
		writeStorage(window.sessionStorage, SELECTED_CHARACTER_KEY, null);
		if (currentCharacter) writeStorage(getSelectedCharacterStorage(), SELECTED_CHARACTER_KEY, JSON.stringify(currentCharacter));
		return currentCharacter;
	}

	function clearSelectedCharacter() {
		currentCharacter = null;
		writeStorage(window.localStorage, SELECTED_CHARACTER_KEY, null);
		writeStorage(window.sessionStorage, SELECTED_CHARACTER_KEY, null);
	}

	function clearSession() {
		accessToken = "";
		currentUser = null;
		currentCharacter = null;
		transitionInProgress = false;
		writeStorage(window.localStorage, ACCESS_TOKEN_KEY, null);
		writeStorage(window.sessionStorage, ACCESS_TOKEN_KEY, null);
		writeStorage(window.localStorage, SELECTED_CHARACTER_KEY, null);
		writeStorage(window.sessionStorage, SELECTED_CHARACTER_KEY, null);
	}

	function storeAuthNotice(message) {
		return writeStorage(window.sessionStorage, AUTH_NOTICE_KEY, String(message || "").trim() || null);
	}

	function consumeAuthNotice() {
		const message = readStorage(window.sessionStorage, AUTH_NOTICE_KEY);
		writeStorage(window.sessionStorage, AUTH_NOTICE_KEY, null);
		return message || "";
	}

	function setCurrentUser(user) {
		currentUser = normalizeUser(user);
		return currentUser;
	}

	function getCurrentUser() {
		return currentUser;
	}

	function getCurrentCharacter() {
		return currentCharacter;
	}

	function getCurrentAccountCharacterId() {
		return getAccountCharacterId(currentCharacter);
	}

	function getCurrentAccountLocalSaveKey() {
		const userId = getUserId(currentUser);
		const characterId = getCurrentAccountCharacterId();
		return buildAccountLocalSaveKey(userId, characterId);
	}

	function buildAccountLocalSaveKey(userId, characterId) {
		const normalizedUserId = Number(userId);
		const normalizedCharacterId = String(characterId || "").trim().toLowerCase();
		return Number.isInteger(normalizedUserId) && normalizedUserId > 0 && ACCOUNT_CHARACTER_ID_PATTERN.test(normalizedCharacterId)
			? `${LEGACY_LOCAL_SAVE_KEY}.u${normalizedUserId}.c${normalizedCharacterId}`
			: LEGACY_LOCAL_SAVE_KEY;
	}

	function resolvePendingUnsyncedIdentity(options) {
		const opts = options || {};
		const userId = Number(opts.userId !== undefined ? opts.userId : getUserId(currentUser));
		const accountCharacterId = String(
			opts.accountCharacterId !== undefined ? opts.accountCharacterId : (getCurrentAccountCharacterId() || ""),
		).trim().toLowerCase();
		if (!Number.isInteger(userId) || userId <= 0 || !ACCOUNT_CHARACTER_ID_PATTERN.test(accountCharacterId)) return null;
		return { userId, accountCharacterId, key: `${userId}:${accountCharacterId}` };
	}

	function readPendingUnsyncedSaves() {
		const stored = readJson(window.localStorage, PENDING_UNSYNCED_SAVES_KEY);
		return stored && typeof stored === "object" && !Array.isArray(stored) ? stored : {};
	}

	function writePendingUnsyncedSaves(markers) {
		const value = markers && Object.keys(markers).length ? JSON.stringify(markers) : null;
		return writeStorage(window.localStorage, PENDING_UNSYNCED_SAVES_KEY, value);
	}

	function markPendingUnsyncedSave(options) {
		const opts = options || {};
		const identity = resolvePendingUnsyncedIdentity(opts);
		if (!identity) return null;
		const markers = readPendingUnsyncedSaves();
		const markedAtMs = Date.now();
		const marker = {
			markerId: `${markedAtMs}-${Math.random().toString(36).slice(2, 10)}`,
			userId: identity.userId,
			accountCharacterId: identity.accountCharacterId,
			saveKey: String(opts.saveKey || buildAccountLocalSaveKey(identity.userId, identity.accountCharacterId)),
			slotKey: String(opts.slotKey || getCurrentAccountBackendSlotKey()),
			characterName: String(opts.characterName || (currentCharacter && currentCharacter.name) || ""),
			markedAt: new Date(markedAtMs).toISOString(),
			status: Number(opts.status) || null,
			reason: String(opts.reason || "backend-save-failed"),
		};
		markers[identity.key] = marker;
		writePendingUnsyncedSaves(markers);
		return marker;
	}

	function getPendingUnsyncedSave(options) {
		const identity = resolvePendingUnsyncedIdentity(options);
		if (!identity) return null;
		const marker = readPendingUnsyncedSaves()[identity.key];
		return marker && typeof marker === "object" ? { ...marker } : null;
	}

	function clearPendingUnsyncedSave(options) {
		const identity = resolvePendingUnsyncedIdentity(options);
		if (!identity) return false;
		const markers = readPendingUnsyncedSaves();
		if (!Object.prototype.hasOwnProperty.call(markers, identity.key)) return false;
		delete markers[identity.key];
		writePendingUnsyncedSaves(markers);
		return true;
	}

	function clearDeletedAccountLocalData(userId) {
		const normalizedUserId = Number(userId);
		if (!Number.isInteger(normalizedUserId) || normalizedUserId <= 0) {
			return { ok: false, removedSaveKeys: 0, removedPendingMarkers: 0 };
		}

		const accountSavePrefix = `${LEGACY_LOCAL_SAVE_KEY}.u${normalizedUserId}.c`;
		let removedSaveKeys = 0;
		try {
			const keysToRemove = [];
			for (let index = 0; index < window.localStorage.length; index += 1) {
				const key = window.localStorage.key(index);
				if (key && key.startsWith(accountSavePrefix)) keysToRemove.push(key);
			}
			keysToRemove.forEach((key) => {
				window.localStorage.removeItem(key);
				removedSaveKeys += 1;
			});
		} catch (error) {
			// 저장소 접근이 막힌 환경에서도 서버 계정 삭제 완료와 세션 정리는 계속 진행합니다.
		}

		let removedPendingMarkers = 0;
		try {
			const markers = readPendingUnsyncedSaves();
			Object.keys(markers).forEach((key) => {
				const marker = markers[key];
				const markerUserId = Number(marker && marker.userId);
				if (markerUserId === normalizedUserId || key.startsWith(`${normalizedUserId}:`)) {
					delete markers[key];
					removedPendingMarkers += 1;
				}
			});
			writePendingUnsyncedSaves(markers);
		} catch (error) {
			// marker 정리에 실패해도 다른 계정 데이터나 legacy 단일 저장을 임의 삭제하지 않습니다.
		}

		return { ok: true, removedSaveKeys, removedPendingMarkers };
	}

	function getCurrentAccountBackendSlotKey() {
		const slotIndex = currentCharacter && Number(currentCharacter.slotIndex);
		return Number.isInteger(slotIndex) && slotIndex >= 1 && slotIndex <= 8
			? `character-${slotIndex}`
			: DEFAULT_BACKEND_SLOT_KEY;
	}

	function hasReadyGameContext() {
		return !!(accessToken && currentUser && getCurrentAccountCharacterId() && !transitionInProgress);
	}

	function setTransitionInProgress(value) {
		transitionInProgress = !!value;
		return transitionInProgress;
	}

	function isTransitionInProgress() {
		return transitionInProgress;
	}

	async function acceptAuthResponse(response, keepLogin) {
		const token = extractAccessToken(response);
		if (!token) throw new Error("로그인 응답에 access token이 없습니다.");
		storeAccessToken(token, !!keepLogin);
		const payload = response && response.payload ? response.payload : {};
		const user = setCurrentUser(payload.user || payload.account || payload);
		if (!user && window.RpgGameApi && typeof window.RpgGameApi.fetchCurrentAccount === "function") {
			const meResponse = await window.RpgGameApi.fetchCurrentAccount({ timeoutMs: 5000 });
			setCurrentUser(meResponse && meResponse.payload ? (meResponse.payload.user || meResponse.payload) : null);
		}
		return { token: accessToken, user: currentUser };
	}

	async function restoreSession(options) {
		const opts = options || {};
		restoreTokenFromStorage();
		if (!accessToken) return { ok: false, authenticated: false, reason: "missing-token" };
		if (!window.RpgGameApi || typeof window.RpgGameApi.fetchCurrentAccount !== "function") {
			return { ok: false, authenticated: false, reason: "api-unavailable" };
		}
		try {
			const response = await window.RpgGameApi.fetchCurrentAccount({ timeoutMs: opts.timeoutMs || 5000 });
			const payload = response && response.payload ? response.payload : {};
			const user = setCurrentUser(payload.user || payload.account || payload);
			if (!user || user.isActive === false) throw new Error("사용할 수 없는 계정입니다.");
			restoreSelectedCharacter();
			return { ok: true, authenticated: true, user, character: currentCharacter, response };
		} catch (error) {
			const status = Number(error && error.status);
			if (status === 401 || status === 403) {
				clearSession();
				return { ok: false, authenticated: false, reason: "session-invalid", retryable: false, error };
			}
			currentUser = null;
			currentCharacter = null;
			transitionInProgress = false;
			return { ok: false, authenticated: false, reason: "session-unavailable", retryable: true, tokenPreserved: true, error };
		}
	}

	function getSessionSnapshot() {
		return {
			version: VERSION,
			authenticated: !!(accessToken && currentUser),
			persistence,
			user: currentUser,
			character: currentCharacter,
			localSaveKey: getCurrentAccountLocalSaveKey(),
			backendSlotKey: getCurrentAccountBackendSlotKey(),
			transitionInProgress,
		};
	}

	window.getCurrentAccountLocalSaveKey = getCurrentAccountLocalSaveKey;
	window.getCurrentAccountBackendSlotKey = getCurrentAccountBackendSlotKey;
	window.getCurrentAccountCharacterId = getCurrentAccountCharacterId;
	window.RpgAuthSession = {
		VERSION,
		ACCESS_TOKEN_KEY,
		SELECTED_CHARACTER_KEY,
		AUTH_NOTICE_KEY,
		PENDING_UNSYNCED_SAVES_KEY,
		LEGACY_LOCAL_SAVE_KEY,
		DEFAULT_BACKEND_SLOT_KEY,
		ACCOUNT_CHARACTER_ID_PATTERN,
		normalizeUser,
		normalizeCharacter,
		extractAccessToken,
		getAccessToken,
		restoreTokenFromStorage,
		storeAccessToken,
		acceptAuthResponse,
		restoreSession,
		clearSession,
		storeAuthNotice,
		consumeAuthNotice,
		setCurrentUser,
		getCurrentUser,
		storeSelectedCharacter,
		restoreSelectedCharacter,
		clearSelectedCharacter,
		getCurrentCharacter,
		getCurrentAccountCharacterId,
		buildAccountLocalSaveKey,
		markPendingUnsyncedSave,
		getPendingUnsyncedSave,
		clearPendingUnsyncedSave,
		clearDeletedAccountLocalData,
		getCurrentAccountLocalSaveKey,
		getCurrentAccountBackendSlotKey,
		hasReadyGameContext,
		setTransitionInProgress,
		isTransitionInProgress,
		getSessionSnapshot,
	};
})();

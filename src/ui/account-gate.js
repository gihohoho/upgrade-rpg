(function () {
	"use strict";

	const VERSION = "v377.email-account-gate-security";
	const SLOT_COUNT = 8;
	const DEFAULT_CHARACTER_OPTIONS = [{ code: "weapon_master", name: "검신" }];
	const AUTH_LINK_ACTIONS = new Set(["verify-email", "reset-password", "delete-account"]);
	const EMAIL_ACTION_TOKEN_PATTERN = /^[A-Za-z0-9_-]{32,256}$/;
	const SESSION_INVALID_ERROR_CODES = new Set([
		"bearer_token_required",
		"access_token_invalid",
		"account_not_found",
		"auth_version_stale",
		"account_suspended",
		"email_verification_required",
	]);
	const RATE_LIMIT_ERROR_CODE = "auth_rate_limited";
	const REQUEST_BODY_TOO_LARGE_ERROR_CODE = "request_body_too_large";
	const EMAIL_ACTION_TOKEN_INVALID_ERROR_CODE = "email_action_token_invalid";
	const gate = document.getElementById("account-gate");
	const panel = document.getElementById("account-gate-panel");
	const modalRoot = document.getElementById("account-modal-root");
	const gameRoot = document.getElementById("game-root");
	const accountBar = document.getElementById("game-account-bar");

	let activeAuthTab = "login";
	let characters = [];
	let characterOptions = DEFAULT_CHARACTER_OPTIONS.slice();
	let activeModal = null;
	let gateBusy = false;
	let initialized = false;
	let pendingRuntimeResume = false;
	let pendingVerificationEmail = "";
	let pendingAuthLinkAction = consumeAuthLinkFragment();

	function escapeHtml(value) {
		return String(value ?? "")
			.replace(/&/g, "&amp;")
			.replace(/</g, "&lt;")
			.replace(/>/g, "&gt;")
			.replace(/"/g, "&quot;")
			.replace(/'/g, "&#39;");
	}

	function consumeAuthLinkFragment() {
		if (!window.location || !window.location.hash) return null;
		const rawHash = String(window.location.hash || "").replace(/^#/, "");
		const params = new URLSearchParams(rawHash);
		const action = String(params.get("auth") || "").trim();
		const token = String(params.get("token") || "").trim();
		if (!AUTH_LINK_ACTIONS.has(action)) return null;

		if (window.history && typeof window.history.replaceState === "function") {
			const cleanUrl = `${window.location.pathname || "index.html"}${window.location.search || ""}`;
			window.history.replaceState(null, document.title, cleanUrl);
		}
		if (!EMAIL_ACTION_TOKEN_PATTERN.test(token)) return { action, token: "", invalid: true };
		return { action, token };
	}

	function handleAuthLinkHashChange() {
		if (!window.location || !window.location.hash) return;
		const params = new URLSearchParams(String(window.location.hash || "").replace(/^#/, ""));
		const action = String(params.get("auth") || "").trim();
		if (!AUTH_LINK_ACTIONS.has(action)) return;
		if (typeof window.location.reload === "function") window.location.reload();
	}

	if (typeof window.addEventListener === "function") {
		window.addEventListener("hashchange", handleAuthLinkHashChange);
	}

	function getErrorCode(error) {
		const response = error && error.response && typeof error.response === "object" ? error.response : {};
		const detail = response.detail && typeof response.detail === "object" && !Array.isArray(response.detail)
			? response.detail
			: {};
		return String(
			(error && error.code)
			|| (response.error && response.error.code)
			|| (response.payload && response.payload.code)
			|| detail.code
			|| response.code
			|| (response.payload && response.payload.status)
			|| "",
		).trim().toLowerCase();
	}

	function getRetryAfterSeconds(error) {
		const response = error && error.response && typeof error.response === "object" ? error.response : {};
		const meta = response.meta && typeof response.meta === "object" ? response.meta : {};
		const details = response.error && response.error.details && typeof response.error.details === "object"
			? response.error.details
			: {};
		const candidates = [
			error && error.retryAfterSeconds,
			meta.retryAfterSeconds,
			meta.retry_after_seconds,
			details.retryAfterSeconds,
			details.retry_after_seconds,
		];
		for (const candidate of candidates) {
			const seconds = Math.ceil(Number(candidate));
			if (Number.isFinite(seconds) && seconds > 0) return Math.min(seconds, 86400);
		}
		return null;
	}

	function isRateLimitError(error) {
		return Number(error && error.status) === 429 || getErrorCode(error) === RATE_LIMIT_ERROR_CODE;
	}

	function isRequestBodyTooLargeError(error) {
		return Number(error && error.status) === 413 || getErrorCode(error) === REQUEST_BODY_TOO_LARGE_ERROR_CODE;
	}

	function isEmailActionTokenInvalidError(error) {
		return getErrorCode(error) === EMAIL_ACTION_TOKEN_INVALID_ERROR_CODE;
	}

	function getRateLimitMessage(error) {
		const retryAfterSeconds = getRetryAfterSeconds(error);
		return retryAfterSeconds
			? `요청이 너무 많습니다. ${retryAfterSeconds}초 후 다시 시도해 주세요.`
			: "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.";
	}

	function getRequestBodyTooLargeMessage() {
		return "요청 데이터가 허용 크기를 넘었습니다. 페이지를 새로고침한 뒤 다시 시도해 주세요.";
	}

	function normalizeEmail(value) {
		return String(value || "").trim().toLowerCase();
	}

	function getPayload(response) {
		return response && response.payload && typeof response.payload === "object" ? response.payload : {};
	}

	function isAccountSessionInvalidError(error) {
		if (window.RpgAuthSession && typeof window.RpgAuthSession.isSessionInvalidError === "function") {
			return window.RpgAuthSession.isSessionInvalidError(error);
		}
		return SESSION_INVALID_ERROR_CODES.has(getErrorCode(error));
	}

	function returnToLoginAfterSessionExpiry(message) {
		const notice = message || "로그인 정보가 만료되었습니다. 현재 캐릭터의 최신 진행은 이 기기의 로컬 저장에 보존했습니다. 다시 로그인해 주세요.";
		if (typeof window.pauseAccountGameRuntime === "function") window.pauseAccountGameRuntime();
		window.RpgAuthSession.clearSession();
		window.RpgAuthSession.storeAuthNotice(notice);
		lockGame();
		renderAuth({ message: notice, tone: "error" });
		if (window.location && typeof window.location.reload === "function") window.location.reload();
	}

	function handleGameSessionInvalid(error) {
		if (!isAccountSessionInvalidError(error)) return false;
		pendingRuntimeResume = false;
		const errorCode = getErrorCode(error);
		returnToLoginAfterSessionExpiry(errorCode === "account_suspended"
			? "계정이 비활성화되어 게임을 계속할 수 없습니다. 최신 진행은 이 기기의 미전송 저장으로 보존했습니다. 관리자에게 계정 상태를 확인해 주세요."
			: (errorCode === "email_verification_required"
				? "이메일 인증이 필요해 현재 로그인을 계속할 수 없습니다. 최신 진행은 이 기기의 미전송 저장으로 보존했습니다. 인증을 완료한 뒤 다시 로그인해 주세요."
				: undefined));
		return true;
	}

	function getCharacterId(character) {
		return window.RpgAuthSession ? window.RpgAuthSession.normalizeCharacter(character)?.accountCharacterId || null : null;
	}

	function getCharacterLabel(character) {
		const code = String(character && character.characterCode || "weapon_master");
		const option = characterOptions.find((item) => item.code === code);
		return option ? option.name : (character && (character.characterName || character.className)) || code;
	}

	function normalizeCharacters(payload) {
		const raw = Array.isArray(payload.characters)
			? payload.characters
			: (Array.isArray(payload.slots) ? payload.slots : []);
		return raw.map((item) => window.RpgAuthSession ? window.RpgAuthSession.normalizeCharacter(item) : null).filter(Boolean);
	}

	function normalizeCharacterOptions(payload) {
		const raw = payload.characterOptions || payload.availableCharacterOptions || payload.availableCharacters || payload.options;
		if (!Array.isArray(raw) || !raw.length) return DEFAULT_CHARACTER_OPTIONS.slice();
		const normalized = raw.map((item) => {
			if (!item) return null;
			if (typeof item === "string") return { code: item, name: item === "weapon_master" ? "검신" : item };
			const code = String(item.code || item.characterCode || item.character_code || "").trim();
			if (!code) return null;
			return { ...item, code, name: String(item.name || item.displayName || code).trim() };
		}).filter(Boolean);
		return normalized.length ? normalized : DEFAULT_CHARACTER_OPTIONS.slice();
	}

	function lockGame() {
		document.body.classList.add("account-gate-active");
		if (gate) gate.hidden = false;
		if (gameRoot) {
			gameRoot.dataset.accountLocked = "true";
			gameRoot.setAttribute("aria-hidden", "true");
			gameRoot.setAttribute("inert", "");
			gameRoot.inert = true;
		}
	}

	function unlockGame() {
		if (gate) gate.hidden = true;
		document.body.classList.remove("account-gate-active");
		if (gameRoot) {
			gameRoot.dataset.accountLocked = "false";
			gameRoot.setAttribute("aria-hidden", "false");
			gameRoot.removeAttribute("inert");
			gameRoot.inert = false;
		}
	}

	function renderLoading(title, message) {
		if (!panel) return;
		gate.dataset.view = "loading";
		panel.className = "account-panel";
		panel.innerHTML = `
			<div class="account-loading-mark" aria-hidden="true">UR</div>
			<h1 id="account-gate-title">${escapeHtml(title || "Upgrade RPG")}</h1>
			<p>${escapeHtml(message || "계정 정보를 확인하고 있습니다...")}</p>
		`;
	}

	function renderSessionRetry(error) {
		if (!panel) return;
		gate.dataset.view = "session-retry";
		panel.className = "account-panel";
		const detail = error && error.message ? error.message : "서버가 아직 준비되지 않았거나 네트워크 연결이 불안정합니다.";
		panel.innerHTML = `
			<div class="account-loading-mark" aria-hidden="true">UR</div>
			<h1 id="account-gate-title">서버에 연결하지 못했습니다</h1>
			<p class="account-auth-copy">로그인 정보는 삭제하지 않았습니다. Render 무료 서버가 깨어나는 데 시간이 걸릴 수 있습니다.</p>
			<div class="account-form-status" data-tone="error" role="status" aria-live="polite">${escapeHtml(detail)}</div>
			<div class="account-retry-actions">
				<button type="button" class="account-primary-button" data-account-action="retry-session">다시 연결</button>
				<button type="button" class="account-secondary-button" data-account-action="forget-session">다른 계정으로 로그인</button>
			</div>
		`;
		const retryButton = panel.querySelector("[data-account-action='retry-session']");
		if (retryButton && retryButton.focus) window.setTimeout(() => retryButton.focus(), 0);
	}

	function renderAuth(options) {
		const opts = options || {};
		if (!panel) return;
		gate.dataset.view = "auth";
		panel.className = "account-panel";
		const isLogin = activeAuthTab === "login";
		panel.innerHTML = `
			<div class="account-brand-mark" aria-hidden="true">UR</div>
			<h1 id="account-gate-title">Upgrade RPG</h1>
			<p class="account-auth-copy">계정으로 접속하면 최대 8개의 캐릭터를 각각 안전하게 저장할 수 있습니다.</p>
			<div class="account-tabs" role="tablist" aria-label="계정 메뉴">
				<button type="button" class="account-tab" role="tab" aria-selected="${isLogin}" data-account-action="auth-tab" data-tab="login">로그인</button>
				<button type="button" class="account-tab" role="tab" aria-selected="${!isLogin}" data-account-action="auth-tab" data-tab="register">회원가입</button>
			</div>
			${isLogin ? renderLoginForm() : renderRegisterForm()}
			<div id="account-form-status" class="account-form-status" data-tone="${escapeHtml(opts.tone || "")}" role="status" aria-live="polite">${escapeHtml(opts.message || "")}</div>
			<p class="account-auth-note">회원가입은 실제로 메일을 받을 수 있는 이메일이 필요합니다. 인증을 완료한 계정만 게임에 접속할 수 있습니다.<br />소셜 로그인은 추후 같은 계정 화면에 추가할 수 있습니다.</p>
		`;
		const firstInput = panel.querySelector("input:not([type='checkbox'])");
		if (firstInput && firstInput.focus) window.setTimeout(() => firstInput.focus(), 0);
	}

	function renderLoginForm() {
		return `
			<form class="account-form" data-account-form="login">
				<div class="account-field">
					<label for="account-login-identifier">아이디 또는 이메일</label>
					<input id="account-login-identifier" name="identifier" autocomplete="username" maxlength="254" autocapitalize="none" spellcheck="false" required placeholder="아이디 또는 가입 이메일" />
				</div>
				<div class="account-field">
					<label for="account-login-password">비밀번호</label>
					<input id="account-login-password" name="password" type="password" autocomplete="current-password" maxlength="72" required placeholder="비밀번호를 입력하세요" />
				</div>
				<label class="account-keep-row">
					<input name="keepLogin" type="checkbox" />
					<span>로그인 유지<br />체크하지 않으면 이 브라우저 탭을 모두 닫을 때 로그인이 해제됩니다.</span>
				</label>
				<button class="account-primary-button" type="submit">로그인</button>
				<div class="account-auth-links" aria-label="계정 찾기와 인증 도움">
					<button type="button" class="account-link-button" data-account-action="recover-username">아이디 찾기</button>
					<button type="button" class="account-link-button" data-account-action="request-password-reset">비밀번호 재설정</button>
					<button type="button" class="account-link-button" data-account-action="resend-verification">인증메일 다시 받기</button>
				</div>
			</form>
		`;
	}

	function renderRegisterForm() {
		return `
			<form class="account-form" data-account-form="register">
				<div class="account-field">
					<label for="account-register-username">사용할 아이디</label>
					<input id="account-register-username" name="username" autocomplete="username" minlength="4" maxlength="24" pattern="[a-z0-9][a-z0-9_]{3,23}" autocapitalize="none" spellcheck="false" required placeholder="영문 소문자·숫자·_ 4~24자" />
					<span class="account-field-help">영문 소문자 또는 숫자로 시작하고, 영문 소문자·숫자·_만 사용할 수 있습니다.</span>
				</div>
				<div class="account-field">
					<label for="account-register-email">가입 이메일</label>
					<input id="account-register-email" name="email" type="email" autocomplete="email" maxlength="254" autocapitalize="none" spellcheck="false" required placeholder="example@email.com" />
					<span class="account-field-help">인증, 아이디 찾기, 비밀번호 재설정, 계정 삭제 확인에 사용합니다.</span>
				</div>
				<div class="account-field">
					<label for="account-register-password">비밀번호</label>
					<input id="account-register-password" name="password" type="password" autocomplete="new-password" minlength="8" maxlength="72" required placeholder="문자와 숫자를 포함해 8자 이상" />
				</div>
				<div class="account-field">
					<label for="account-register-password-confirm">비밀번호 확인</label>
					<input id="account-register-password-confirm" name="passwordConfirm" type="password" autocomplete="new-password" minlength="8" maxlength="72" required placeholder="비밀번호를 한 번 더 입력하세요" />
				</div>
				<button class="account-primary-button" type="submit">인증메일 요청하고 가입하기</button>
			</form>
		`;
	}

	function renderVerificationPending(email, options) {
		const opts = options || {};
		pendingVerificationEmail = normalizeEmail(email || pendingVerificationEmail);
		if (!panel) return;
		gate.dataset.view = "verification-pending";
		panel.className = "account-panel";
		panel.innerHTML = `
			<div class="account-email-mark" aria-hidden="true">✉</div>
			<h1 id="account-gate-title">이메일을 확인해 주세요</h1>
			<p class="account-auth-copy">가입을 마치려면 받은 메일의 <strong>이메일 인증 완료</strong> 버튼을 눌러야 합니다.</p>
			<div class="account-email-callout">
				<span>인증 메일 요청 주소</span>
				<strong>${escapeHtml(pendingVerificationEmail || "가입한 이메일")}</strong>
				<p>메일 도착까지 몇 분 걸릴 수 있습니다. 스팸함도 확인하고, 안내된 시간이 지난 뒤 한 번만 다시 요청해 주세요.</p>
			</div>
			<div id="account-form-status" class="account-form-status" data-tone="${escapeHtml(opts.tone || "success")}" role="status" aria-live="polite">${escapeHtml(opts.message || "인증 메일 요청을 접수했습니다.")}</div>
			<div class="account-verification-actions">
				<button type="button" class="account-secondary-button" data-account-action="verification-back-login">로그인 화면으로</button>
				<button type="button" class="account-primary-button" data-account-action="verification-resend">인증메일 다시 받기</button>
			</div>
		`;
	}

	function renderPasswordResetLinkForm() {
		if (!panel || !pendingAuthLinkAction || pendingAuthLinkAction.action !== "reset-password") return;
		gate.dataset.view = "password-reset";
		panel.className = "account-panel";
		panel.innerHTML = `
			<div class="account-email-mark" aria-hidden="true">🔑</div>
			<h1 id="account-gate-title">새 비밀번호 설정</h1>
			<p class="account-auth-copy">메일 링크 확인이 완료되었습니다. 다른 사이트에서 사용하지 않는 새 비밀번호를 입력해 주세요.</p>
			<form class="account-form" data-account-form="reset-password">
				<div class="account-field"><label for="account-reset-password">새 비밀번호</label><input id="account-reset-password" name="password" type="password" autocomplete="new-password" minlength="8" maxlength="72" required placeholder="문자와 숫자를 포함해 8자 이상" /></div>
				<div class="account-field"><label for="account-reset-password-confirm">새 비밀번호 확인</label><input id="account-reset-password-confirm" name="passwordConfirm" type="password" autocomplete="new-password" minlength="8" maxlength="72" required placeholder="새 비밀번호를 한 번 더 입력하세요" /></div>
				<div id="account-form-status" class="account-form-status" role="status" aria-live="polite"></div>
				<div class="account-verification-actions"><button type="button" class="account-secondary-button" data-account-action="cancel-link-action">취소</button><button type="submit" class="account-primary-button">비밀번호 변경</button></div>
			</form>
		`;
		panel.querySelector("input")?.focus();
	}

	function setAuthStatus(message, tone) {
		const target = document.getElementById("account-form-status");
		if (!target) return;
		target.textContent = String(message || "");
		target.dataset.tone = tone || "";
	}

	function setFormBusy(form, busy, label) {
		if (!form) return;
		form.querySelectorAll("input, button, select").forEach((control) => {
			control.disabled = !!busy;
		});
		const submit = form.querySelector("button[type='submit']");
		if (submit) {
			if (!submit.dataset.originalText) submit.dataset.originalText = submit.textContent;
			submit.textContent = busy ? (label || "처리 중...") : submit.dataset.originalText;
		}
	}

	function getSummaryText(character) {
		const summary = character && character.summary && typeof character.summary === "object" ? character.summary : {};
		const parts = [];
		if (summary.stage !== undefined) parts.push(`${summary.stage}단계`);
		else if (summary.currentZoneIndex !== undefined) parts.push(`구역 ${Number(summary.currentZoneIndex) + 1}`);
		if (summary.level !== undefined && summary.level !== null) parts.push(`Lv.${summary.level}`);
		return parts.join(" · ") || "새로운 모험을 이어갑니다";
	}

	function renderCharacterSlots(options) {
		const opts = options || {};
		const user = window.RpgAuthSession && window.RpgAuthSession.getCurrentUser();
		if (!panel || !user) return;
		gate.dataset.view = "slots";
		panel.className = "account-panel account-slot-panel";
		const bySlot = new Map(characters.map((character) => [character.slotIndex, character]));
		const slotsHtml = Array.from({ length: SLOT_COUNT }, (_, offset) => {
			const slotIndex = offset + 1;
			const character = bySlot.get(slotIndex);
			if (!character) {
				return `
					<button type="button" class="account-slot empty" data-account-action="create-character" data-slot-index="${slotIndex}" aria-label="빈 슬롯 ${slotIndex}, 새 캐릭터 만들기">
						<span class="account-slot-index">${slotIndex}</span>
						<span class="account-slot-copy"><strong>빈 슬롯 ${slotIndex}</strong><span>새 캐릭터 만들기</span></span>
						<span aria-hidden="true">＋</span>
					</button>`;
			}
			return `
				<div class="account-slot">
					<button type="button" class="account-slot-select" data-account-action="select-character" data-character-id="${character.accountCharacterId}" aria-label="${escapeHtml(character.name)} 캐릭터로 게임 시작">
						<span class="account-slot-index">${slotIndex}</span>
						<span class="account-slot-copy">
							<strong>${escapeHtml(character.name)}</strong>
							<span>${escapeHtml(getCharacterLabel(character))} · ${escapeHtml(getSummaryText(character))}</span>
						</span>
					</button>
					<button type="button" class="account-slot-delete" data-account-action="delete-character" data-character-id="${character.accountCharacterId}" aria-label="${escapeHtml(character.name)} 캐릭터 삭제">삭제</button>
				</div>`;
		}).join("");

		panel.innerHTML = `
			<div class="account-slot-header">
				<div>
					<h1 id="account-gate-title">캐릭터를 선택하세요</h1>
					<p>캐릭터마다 장비·골드·진행도가 별도로 저장됩니다.</p>
				</div>
				<div class="account-slot-user"><span>로그인 계정</span><strong>${escapeHtml(user.username)}</strong></div>
			</div>
			<div class="account-slots-grid">${slotsHtml}</div>
			<div id="account-slot-status" class="account-form-status" data-tone="${escapeHtml(opts.tone || "")}" role="status" aria-live="polite">${escapeHtml(opts.message || "")}</div>
			<div class="account-slot-footer">
				<span>${characters.length}/${SLOT_COUNT} 슬롯 사용 중 · 캐릭터를 누르면 게임이 시작됩니다.</span>
				<div class="account-slot-footer-actions">
					<button type="button" class="account-secondary-button" data-account-action="account-settings">계정 관리</button>
					<button type="button" class="account-secondary-button" data-account-action="logout-from-slots">로그아웃</button>
				</div>
			</div>
		`;
	}

	function findCharacter(characterId) {
		const id = String(characterId || "").trim().toLowerCase();
		return characters.find((character) => character.accountCharacterId === id) || null;
	}

	async function loadCharacters(options) {
		const opts = options || {};
		renderLoading("캐릭터 슬롯", "캐릭터 정보를 불러오는 중입니다...");
		const response = await window.RpgGameApi.listAccountCharacters({ timeoutMs: 5000 });
		const payload = getPayload(response);
		characters = normalizeCharacters(payload);
		characterOptions = normalizeCharacterOptions(payload);
		const selected = window.RpgAuthSession.getCurrentCharacter();
		const selectedId = selected && selected.accountCharacterId;
		const availableSelected = selectedId ? findCharacter(selectedId) : null;
		if (opts.resumeSelected && availableSelected) {
			await selectCharacter(availableSelected);
			return;
		}
		if (selectedId && !availableSelected) window.RpgAuthSession.clearSelectedCharacter();
		renderCharacterSlots(opts);
	}

	async function restoreSessionAndContinue(authNotice) {
		const restored = await window.RpgAuthSession.restoreSession({ timeoutMs: 7000 });
		if (!restored.authenticated) {
			if (restored.retryable) {
				renderSessionRetry(restored.error);
				return;
			}
			const invalidStatus = Number(restored.error && restored.error.status);
			renderAuth(authNotice
				? { message: authNotice, tone: "error" }
				: (restored.reason === "session-invalid" ? { message: invalidStatus === 403 ? "사용할 수 없는 계정입니다. 관리자에게 계정 상태를 확인해 주세요." : "로그인 정보가 만료되었습니다. 다시 로그인해 주세요.", tone: "error" } : {}));
			return;
		}
		try {
			await loadCharacters({ resumeSelected: true });
		} catch (error) {
			if (handleGameSessionInvalid(error)) return;
			renderSessionRetry(error);
		}
	}

	async function retrySessionConnection() {
		if (gateBusy) return;
		gateBusy = true;
		renderLoading("서버 다시 연결", "로그인 정보를 유지한 채 서버 상태를 다시 확인하고 있습니다...");
		try {
			await restoreSessionAndContinue("");
		} finally {
			gateBusy = false;
		}
	}

	function renderCharacterOptionTags() {
		return characterOptions.map((option) => `<option value="${escapeHtml(option.code)}">${escapeHtml(option.name)}</option>`).join("");
	}

	function openModal(config) {
		const settings = config || {};
		if (!modalRoot) return null;
		closeModal("replaced");
		activeModal = {
			type: settings.type || "notice",
			data: settings.data || null,
			resolve: settings.resolve || null,
			returnFocus: document.activeElement,
			closeable: settings.closeable !== false,
		};
		modalRoot.innerHTML = `
			<div class="account-modal-backdrop" data-account-modal-backdrop>
				<section class="account-modal" data-tone="${escapeHtml(settings.tone || "")}" role="dialog" aria-modal="true" aria-labelledby="account-modal-title" aria-describedby="account-modal-description">
					<div class="account-modal-header">
						<div><h2 id="account-modal-title">${escapeHtml(settings.title || "안내")}</h2><p id="account-modal-description">${escapeHtml(settings.description || "")}</p></div>
						${settings.closeable === false ? "" : '<button type="button" class="account-icon-button" data-account-action="close-modal" aria-label="창 닫기">×</button>'}
					</div>
					<div class="account-modal-body">${settings.body || ""}</div>
				</section>
			</div>`;
		const focusTarget = modalRoot.querySelector(settings.initialFocus || "input, select, button");
		if (focusTarget && focusTarget.focus) window.setTimeout(() => focusTarget.focus(), 0);
		return activeModal;
	}

	function closeModal(reason) {
		if (!activeModal) {
			if (modalRoot) modalRoot.innerHTML = "";
			return;
		}
		const closing = activeModal;
		activeModal = null;
		if (modalRoot) modalRoot.innerHTML = "";
		if (closing.resolve && reason !== "resolved") closing.resolve(reason || "cancel");
		if (closing.returnFocus && closing.returnFocus.focus) closing.returnFocus.focus();
	}

	function canDismissActiveModal() {
		return !!(activeModal && activeModal.closeable && (!gateBusy || activeModal.type === "legacy-import" || activeModal.type === "pending-unsynced"));
	}

	function openCreateModal(slotIndex) {
		openModal({
			type: "create",
			data: { slotIndex },
			title: `슬롯 ${slotIndex} 새 캐릭터`,
			description: "캐릭터 이름과 직업을 정하면 별도의 새 저장 공간이 만들어집니다.",
			initialFocus: "#account-create-name",
			body: `
				<form class="account-form" data-account-form="create-character">
					<div class="account-field"><label for="account-create-name">캐릭터 이름</label><input id="account-create-name" name="name" maxlength="24" pattern="[가-힣A-Za-z0-9_. \-]+" autocomplete="off" required placeholder="한글·영문·숫자 24자 이내" /></div>
					<div class="account-field"><label for="account-create-code">직업</label><select id="account-create-code" name="characterCode">${renderCharacterOptionTags()}</select></div>
					<p class="account-modal-note">현재 플레이 가능한 직업은 검신입니다. 추후 직업이 추가되면 이 목록에서 선택할 수 있습니다.</p>
					<div id="account-modal-status" class="account-form-status" role="status" aria-live="polite"></div>
					<div class="account-modal-actions"><button type="button" class="account-secondary-button" data-account-action="close-modal">취소</button><button type="submit" class="account-primary-button">캐릭터 만들기</button></div>
				</form>`,
		});
	}

	function openDeleteModal(character) {
		openModal({
			type: "delete",
			data: { character },
			tone: "danger",
			title: "캐릭터 삭제",
			description: `${character.name} 캐릭터와 연결된 진행도를 삭제합니다.`,
			initialFocus: "#account-delete-confirm-name",
			body: `
				<p class="account-modal-warning">삭제한 캐릭터의 장비·골드·진행도는 되돌릴 수 없습니다. 아래에 캐릭터 이름을 정확히 입력해야 삭제할 수 있습니다.</p>
				<div class="account-field"><label for="account-delete-confirm-name">확인 입력: ${escapeHtml(character.name)}</label><input id="account-delete-confirm-name" class="account-confirm-input" autocomplete="off" data-account-delete-name placeholder="${escapeHtml(character.name)}" /></div>
				<div id="account-modal-status" class="account-form-status" role="status" aria-live="polite"></div>
				<div class="account-modal-actions"><button type="button" class="account-secondary-button" data-account-action="close-modal">취소</button><button type="button" class="account-danger-button" data-account-action="confirm-delete-character" disabled>영구 삭제</button></div>`,
		});
	}

	function setModalStatus(message, tone) {
		const target = document.getElementById("account-modal-status");
		if (!target) return;
		target.textContent = String(message || "");
		target.dataset.tone = tone || "";
	}

	function openEmailRequestModal(mode) {
		const definitions = {
			"recover-username": {
				title: "아이디 찾기",
				description: "가입한 이메일로 아이디 안내 메일을 요청합니다.",
				action: "recover-username",
				button: "아이디 안내 메일 받기",
			},
			"request-password-reset": {
				title: "비밀번호 재설정",
				description: "가입한 이메일로 새 비밀번호 설정 링크를 요청합니다.",
				action: "request-password-reset",
				button: "재설정 메일 받기",
			},
			"resend-verification": {
				title: "인증메일 다시 받기",
				description: "아직 인증하지 않은 가입 이메일로 새 인증 링크를 요청합니다.",
				action: "resend-verification",
				button: "인증메일 다시 받기",
			},
		};
		const definition = definitions[mode];
		if (!definition) return;
		openModal({
			type: definition.action,
			title: definition.title,
			description: definition.description,
			initialFocus: "#account-recovery-email",
			body: `
				<form class="account-form" data-account-form="${definition.action}">
					<div class="account-field"><label for="account-recovery-email">가입 이메일</label><input id="account-recovery-email" name="email" type="email" autocomplete="email" maxlength="254" autocapitalize="none" spellcheck="false" required placeholder="example@email.com" /></div>
					<p class="account-modal-note">계정 정보 보호를 위해 가입 여부와 관계없이 같은 완료 안내를 표시합니다.</p>
					<div id="account-modal-status" class="account-form-status" role="status" aria-live="polite"></div>
					<div class="account-modal-actions"><button type="button" class="account-secondary-button" data-account-action="close-modal">취소</button><button type="submit" class="account-primary-button">${definition.button}</button></div>
				</form>`,
		});
	}

	function openAccountSettingsModal() {
		const user = window.RpgAuthSession && window.RpgAuthSession.getCurrentUser();
		if (!user) return;
		const email = String(user.email || "").trim();
		openModal({
			type: "account-settings",
			title: "계정 관리",
			description: `${user.username} 계정의 가입 정보와 삭제 요청을 관리합니다.`,
			body: `
				<div class="account-email-callout account-email-callout-compact">
					<span>가입 이메일</span><strong>${escapeHtml(email || "이메일 정보 없음")}</strong>
					<p>${user.emailVerified ? "이메일 인증 완료" : "이메일 인증 확인이 필요합니다."}</p>
				</div>
				<p class="account-modal-warning"><strong>계정 삭제</strong><br />계정과 모든 캐릭터의 서버 저장을 영구 삭제합니다. 삭제 확인 메일을 받은 뒤 한 번 더 확정해야 합니다.</p>
				<div class="account-modal-actions"><button type="button" class="account-secondary-button" data-account-action="close-modal">돌아가기</button><button type="button" class="account-danger-button" data-account-action="open-account-deletion">계정 삭제 시작</button></div>`,
		});
	}

	function openAccountDeletionRequestModal(previewPayload) {
		const user = window.RpgAuthSession && window.RpgAuthSession.getCurrentUser();
		if (!user) return;
		const preview = previewPayload && typeof previewPayload === "object" ? previewPayload : {};
		const characterCount = Number(preview.characterCount !== undefined ? preview.characterCount : preview.charactersCount);
		const saveSnapshotCount = Number(preview.saveSnapshotCount !== undefined ? preview.saveSnapshotCount : preview.snapshotCount);
		const scope = Array.isArray(preview.deletionScope) ? preview.deletionScope.filter((item) => typeof item === "string" && item.trim()).slice(0, 6) : [];
		openModal({
			type: "account-deletion-request",
			tone: "danger",
			title: "계정 삭제 메일 요청",
			description: "현재 비밀번호를 확인한 뒤 가입 이메일로 최종 삭제 링크를 요청합니다.",
			initialFocus: "#account-deletion-password",
			body: `
				<form class="account-form" data-account-form="account-deletion-request">
					<p class="account-modal-warning">모든 캐릭터, 장비, 골드와 진행도가 삭제되며 되돌릴 수 없습니다. 메일 링크를 누르기 전까지는 삭제되지 않습니다.</p>
					<div class="account-deletion-preview">
						<div><span>삭제 대상 캐릭터</span><strong>${Number.isFinite(characterCount) ? `${escapeHtml(characterCount)}개` : "모든 캐릭터"}</strong></div>
						<div><span>삭제 대상 저장</span><strong>${Number.isFinite(saveSnapshotCount) ? `${escapeHtml(saveSnapshotCount)}개` : "연결된 모든 저장"}</strong></div>
						${scope.length ? `<ul>${scope.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>` : ""}
					</div>
					<div class="account-field"><label for="account-deletion-password">현재 비밀번호</label><input id="account-deletion-password" name="password" type="password" autocomplete="current-password" maxlength="72" required placeholder="현재 비밀번호를 입력하세요" /></div>
					<div id="account-modal-status" class="account-form-status" role="status" aria-live="polite"></div>
					<div class="account-modal-actions"><button type="button" class="account-secondary-button" data-account-action="close-modal">취소</button><button type="submit" class="account-danger-button">삭제 확인 메일 받기</button></div>
				</form>`,
		});
	}

	async function previewAndOpenAccountDeletion() {
		if (gateBusy) return;
		gateBusy = true;
		openModal({
			type: "account-deletion-preview-loading",
			tone: "danger",
			closeable: false,
			title: "삭제 범위를 확인합니다",
			description: "캐릭터와 서버 저장 중 삭제될 항목을 안전하게 확인하고 있습니다.",
			body: '<div class="account-form-status" role="status">잠시만 기다려 주세요...</div>',
		});
		try {
			const response = await window.RpgGameApi.previewAccountDeletion({ timeoutMs: 7000 });
			openAccountDeletionRequestModal(getPayload(response));
		} catch (error) {
			if (handleGameSessionInvalid(error)) return;
			const previewErrorMessage = isRateLimitError(error)
				? getRateLimitMessage(error)
				: (isRequestBodyTooLargeError(error)
					? getRequestBodyTooLargeMessage()
					: (error && error.message ? error.message : "서버 연결을 확인한 뒤 다시 시도해 주세요."));
			openModal({
				type: "account-deletion-preview-error",
				tone: "danger",
				title: "삭제 범위를 확인하지 못했습니다",
				description: "안전을 위해 계정 삭제 요청을 시작하지 않았습니다.",
				body: `<div class="account-form-status" data-tone="error" role="status">${escapeHtml(previewErrorMessage)}</div><div class="account-modal-actions"><button type="button" class="account-secondary-button" data-account-action="close-modal">돌아가기</button><button type="button" class="account-danger-button" data-account-action="open-account-deletion">다시 확인</button></div>`,
			});
		} finally {
			gateBusy = false;
		}
	}

	function openAccountDeletionConfirmModal() {
		openModal({
			type: "account-deletion-confirm",
			tone: "danger",
			closeable: false,
			title: "계정을 영구 삭제합니다",
			description: "메일 링크 확인이 완료되었습니다. 마지막 확인 문구를 입력해야 삭제됩니다.",
			initialFocus: "#account-deletion-confirm-text",
			body: `
				<form class="account-form" data-account-form="account-deletion-confirm">
					<p class="account-modal-warning">계정과 모든 캐릭터의 서버 저장은 복구할 수 없습니다. 계속하려면 아래에 <strong>계정 삭제</strong>를 정확히 입력하세요.</p>
					<div class="account-field"><label for="account-deletion-confirm-text">확인 입력: 계정 삭제</label><input id="account-deletion-confirm-text" name="confirmText" autocomplete="off" data-account-deletion-confirm-text placeholder="계정 삭제" /></div>
					<div id="account-modal-status" class="account-form-status" role="status" aria-live="polite"></div>
					<div class="account-modal-actions"><button type="button" class="account-secondary-button" data-account-action="cancel-link-action">삭제하지 않기</button><button type="submit" class="account-danger-button" data-account-action="confirm-delete-account" disabled>계정 영구 삭제</button></div>
				</form>`,
		});
	}

	function renderAuthLinkRetry(message) {
		if (!panel) return;
		gate.dataset.view = "auth-link-retry";
		panel.className = "account-panel";
		panel.innerHTML = `
			<div class="account-email-mark" aria-hidden="true">!</div>
			<h1 id="account-gate-title">메일 링크를 처리하지 못했습니다</h1>
			<p class="account-auth-copy">링크 정보는 주소창에서 안전하게 지웠고 현재 탭의 메모리에만 보관하고 있습니다.</p>
			<div class="account-form-status" data-tone="error" role="status">${escapeHtml(message || "서버 연결을 확인한 뒤 다시 시도해 주세요.")}</div>
			<div class="account-retry-actions"><button type="button" class="account-secondary-button" data-account-action="cancel-link-action">로그인 화면으로</button><button type="button" class="account-primary-button" data-account-action="retry-link-action">다시 시도</button></div>
		`;
	}

	async function processPendingAuthLinkAction() {
		const link = pendingAuthLinkAction;
		if (!link || link.invalid || !link.token) {
			pendingAuthLinkAction = null;
			renderAuth({ message: "메일 링크가 올바르지 않습니다. 새 메일을 요청해 주세요.", tone: "error" });
			return;
		}
		if (link.action === "reset-password") {
			renderPasswordResetLinkForm();
			return;
		}
		if (link.action === "delete-account") {
			renderLoading("계정 삭제 확인", "삭제 링크를 안전하게 확인했습니다.");
			openAccountDeletionConfirmModal();
			return;
		}

		renderLoading("이메일 인증", "인증 링크를 확인하고 있습니다...");
		try {
			await window.RpgGameApi.verifyAccountEmail({ token: link.token }, { timeoutMs: 7000 });
			pendingAuthLinkAction = null;
			activeAuthTab = "login";
			renderAuth({ message: "이메일 인증이 완료되었습니다. 이제 로그인할 수 있습니다.", tone: "success" });
		} catch (error) {
			if (isEmailActionTokenInvalidError(error)) {
				pendingAuthLinkAction = null;
				activeAuthTab = "login";
				renderAuth({ message: "인증 링크가 만료됐거나 이미 사용되었습니다. 필요하면 인증메일을 다시 요청해 주세요.", tone: "error" });
			} else if (isRateLimitError(error)) {
				renderAuthLinkRetry(`${getRateLimitMessage(error)} 인증 링크는 현재 탭의 메모리에 안전하게 보존했습니다.`);
			} else if (isRequestBodyTooLargeError(error)) {
				renderAuthLinkRetry(`${getRequestBodyTooLargeMessage()} 인증 링크는 현재 탭의 메모리에 안전하게 보존했습니다.`);
			} else {
				renderAuthLinkRetry("서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.");
			}
		}
	}

	function readLegacySave() {
		const key = window.RpgAuthSession ? window.RpgAuthSession.LEGACY_LOCAL_SAVE_KEY : "idleRpgSaveV22";
		let raw = null;
		try {
			raw = window.localStorage ? window.localStorage.getItem(key) : null;
		} catch (error) {
			return { exists: false, key, snapshot: null, error: "기존 브라우저 저장소를 읽을 수 없습니다." };
		}
		if (!raw) return { exists: false, key, snapshot: null, error: null };
		try {
			return { exists: true, key, snapshot: JSON.parse(raw), error: null };
		} catch (error) {
			return { exists: true, key, snapshot: null, error: "기존 세이브 JSON이 손상되었습니다." };
		}
	}

	function requestLegacyImportDecision(character) {
		const legacy = readLegacySave();
		if (!legacy.exists || !legacy.snapshot || legacy.error) return Promise.resolve({ decision: "fresh", legacy });
		return new Promise((resolve) => {
			openModal({
				type: "legacy-import",
				data: { character, legacy },
				resolve: (reason) => resolve({ decision: reason === "import" ? "import" : (reason === "fresh" ? "fresh" : "cancel"), legacy }),
				title: "기존 세이브를 발견했습니다",
				description: "회원 시스템 전에 사용하던 브라우저 세이브가 있습니다.",
				body: `
					<p class="account-modal-note"><strong>${escapeHtml(character.name)}</strong> 캐릭터로 기존 진행도를 가져올 수 있습니다. 가져온 뒤에도 원본 <code>${escapeHtml(legacy.key)}</code>는 삭제하지 않고 그대로 보존합니다.</p>
					<p class="account-modal-warning">새 캐릭터로 시작하면 이 캐릭터에는 기본 상태가 저장됩니다. 기존 세이브는 나중에 다른 빈 캐릭터에서 다시 가져올 수 있습니다.</p>
					<div class="account-modal-actions"><button type="button" class="account-secondary-button" data-account-action="legacy-fresh">새 캐릭터로 시작</button><button type="button" class="account-primary-button" data-account-action="legacy-import">기존 세이브 가져오기</button></div>`,
			});
		});
	}

	function requestPendingUnsyncedDecision(character, marker, backendResponse) {
		const pending = marker && typeof marker === "object" ? marker : {};
		const backendPayload = getPayload(backendResponse);
		const localTime = pending.markedAt ? new Date(pending.markedAt).toLocaleString("ko-KR") : "저장 실패 시점";
		const serverTime = backendPayload.updatedAt ? new Date(backendPayload.updatedAt).toLocaleString("ko-KR") : "서버 저장 없음";
		return new Promise((resolve) => {
			openModal({
				type: "pending-unsynced",
				data: { character, marker: pending },
				resolve: (reason) => resolve(reason === "use-local" ? "local" : (reason === "use-server" ? "server" : "cancel")),
				tone: "warning",
				title: "미전송 저장을 발견했습니다",
				description: `${character.name} 캐릭터의 이 기기 저장과 서버 저장 중 사용할 진행도를 선택합니다.`,
				body: `
					<p class="account-modal-warning">이전 DB 저장이 완료되지 않았습니다. 자동으로 덮어쓰지 않고 직접 선택할 때까지 두 저장을 모두 보존합니다.</p>
					<div class="account-save-choice-grid">
						<div class="account-save-choice"><strong>이 기기 미전송 저장</strong><span>${escapeHtml(localTime)}</span><p>이 기기의 최신 진행을 불러온 뒤 서버에 다시 전송합니다.</p></div>
						<div class="account-save-choice"><strong>서버 저장</strong><span>${escapeHtml(serverTime)}</span><p>서버 진행을 사용하고, 다른 이 기기 저장은 복구용 백업으로 남깁니다.</p></div>
					</div>
					<div class="account-modal-actions"><button type="button" class="account-secondary-button" data-account-action="pending-use-server">서버 저장 사용</button><button type="button" class="account-primary-button" data-account-action="pending-use-local">이 기기 저장 사용</button></div>`,
			});
		});
	}

	async function selectCharacter(character) {
		if (gateBusy || !character) return;
		gateBusy = true;
		window.RpgAuthSession.storeSelectedCharacter(character);
		renderLoading(character.name, "캐릭터 진행도를 안전하게 불러오는 중입니다...");
		try {
			if (typeof window.startAccountCharacterGame !== "function") throw new Error("게임 시작 함수를 찾을 수 없습니다.");
			const result = await window.startAccountCharacterGame(character);
			if (result && result.cancelled) {
				window.RpgAuthSession.clearSelectedCharacter();
				renderCharacterSlots();
				return;
			}
			updateAccountBar();
			unlockGame();
		} catch (error) {
			if (handleGameSessionInvalid(error)) return;
			window.RpgAuthSession.clearSelectedCharacter();
			renderCharacterSlots({ message: error && error.message ? error.message : "캐릭터를 불러오지 못했습니다.", tone: "error" });
		} finally {
			gateBusy = false;
		}
	}

	function updateAccountBar() {
		const user = window.RpgAuthSession && window.RpgAuthSession.getCurrentUser();
		const character = window.RpgAuthSession && window.RpgAuthSession.getCurrentCharacter();
		if (!accountBar || !user || !character) {
			syncAccountBarTownVisibility();
			return;
		}
		const characterTarget = document.getElementById("game-account-character");
		const userTarget = document.getElementById("game-account-user");
		if (characterTarget) characterTarget.textContent = `${character.name} · ${getCharacterLabel(character)}`;
		if (userTarget) userTarget.textContent = user.username;
		syncAccountBarTownVisibility();
	}

	function syncAccountBarTownVisibility(zoneType) {
		if (!accountBar) return false;
		const user = window.RpgAuthSession && window.RpgAuthSession.getCurrentUser();
		const character = window.RpgAuthSession && window.RpgAuthSession.getCurrentCharacter();
		const resolvedZoneType = zoneType !== undefined
			? String(zoneType || "")
			: (typeof currentZoneType !== "undefined" ? String(currentZoneType || "") : "");
		const shouldShow = !!(user && character && resolvedZoneType === "town");
		accountBar.hidden = !shouldShow;
		accountBar.setAttribute("aria-hidden", shouldShow ? "false" : "true");
		accountBar.toggleAttribute("inert", !shouldShow);
		accountBar.inert = !shouldShow;
		accountBar.dataset.zoneVisible = shouldShow ? "town" : "hidden";
		return shouldShow;
	}

	async function transitionFromGame(mode) {
		if (gateBusy) return;
		gateBusy = true;
		pendingRuntimeResume = typeof window.pauseAccountGameRuntime === "function" && window.pauseAccountGameRuntime() === true;
		lockGame();
		renderLoading(mode === "logout" ? "로그아웃" : "캐릭터 변경", "현재 캐릭터를 마지막으로 저장하고 있습니다...");
		try {
			if (typeof window.flushAccountGameSave === "function") {
				await window.flushAccountGameSave({ reason: mode === "logout" ? "account-logout" : "character-switch" });
			}
			window.RpgAuthSession.setTransitionInProgress(true);
			if (mode === "logout") {
				try {
					await window.RpgGameApi.logoutAccount({ timeoutMs: 5000 });
				} catch (error) {
					console.warn("[Upgrade RPG] logout API failed; local session will still be cleared", error);
				}
				window.RpgAuthSession.clearSession();
			} else {
				window.RpgAuthSession.clearSelectedCharacter();
			}
			window.location.reload();
		} catch (error) {
			if (handleGameSessionInvalid(error)) return;
			window.RpgAuthSession.setTransitionInProgress(false);
			openModal({
				type: "save-error",
				tone: "danger",
				closeable: false,
				title: "저장하지 못했습니다",
				description: "캐릭터 변경이나 로그아웃을 중단했습니다.",
				body: `<p class="account-modal-warning">${escapeHtml(error && error.message ? error.message : "백엔드 저장에 실패했습니다.")}<br />잠시 후 다시 시도해 주세요.</p><div class="account-modal-actions"><button type="button" class="account-primary-button" data-account-action="return-to-game">게임으로 돌아가기</button></div>`,
			});
			gateBusy = false;
		}
	}

	async function logoutFromSlots() {
		if (gateBusy) return;
		gateBusy = true;
		renderLoading("로그아웃", "계정 연결을 종료하고 있습니다...");
		try {
			try {
				await window.RpgGameApi.logoutAccount({ timeoutMs: 5000 });
			} catch (error) {
				console.warn("[Upgrade RPG] logout API failed; local session will still be cleared", error);
			}
			window.RpgAuthSession.clearSession();
			renderAuth({ message: "로그아웃했습니다.", tone: "success" });
		} finally {
			gateBusy = false;
		}
	}

	async function handleAuthSubmit(form) {
		if (gateBusy) return;
		const formType = form.dataset.accountForm;
		const data = new FormData(form);
		const username = String(data.get("username") || "").trim().toLowerCase();
		const email = normalizeEmail(data.get("email"));
		const identifier = String(data.get("identifier") || "").trim();
		const password = String(data.get("password") || "");
		const passwordConfirm = String(data.get("passwordConfirm") || "");
		const keepLogin = data.get("keepLogin") === "on";
		if ((formType === "register" && (!username || !email || !password)) || (formType === "login" && (!identifier || !password))) {
			setAuthStatus(formType === "register" ? "아이디, 이메일, 비밀번호를 모두 입력해 주세요." : "아이디 또는 이메일과 비밀번호를 모두 입력해 주세요.", "error");
			return;
		}
		if (formType === "register" && password !== passwordConfirm) {
			setAuthStatus("비밀번호 확인이 일치하지 않습니다.", "error");
			form.querySelector("[name='passwordConfirm']")?.focus();
			return;
		}
		gateBusy = true;
		setFormBusy(form, true, formType === "register" ? "가입 중..." : "로그인 중...");
		setAuthStatus("서버에 안전하게 확인하고 있습니다...", "");
		try {
			const response = formType === "register"
				? await window.RpgGameApi.registerAccount({ username, email, password, passwordConfirm }, { timeoutMs: 15000 })
				: await window.RpgGameApi.loginAccount({ identifier, password }, { timeoutMs: 7000 });
			if (formType === "register") {
				window.RpgAuthSession.clearSession();
				renderVerificationPending(email, { message: "가입과 인증 메일 요청을 접수했습니다. 메일 도착까지 몇 분 걸릴 수 있습니다.", tone: "success" });
				return;
			}
			const token = window.RpgAuthSession.extractAccessToken(response);
			if (token) {
				await window.RpgAuthSession.acceptAuthResponse(response, keepLogin);
				await loadCharacters({ resumeSelected: false });
			} else {
				throw new Error("로그인 토큰을 받지 못했습니다.");
			}
		} catch (error) {
			const errorCode = getErrorCode(error);
			const message = isRateLimitError(error)
				? getRateLimitMessage(error)
				: (isRequestBodyTooLargeError(error)
					? getRequestBodyTooLargeMessage()
					: (errorCode.includes("verification") || errorCode.includes("email_unverified")
						? "이메일 인증이 완료되지 않았습니다. 인증메일을 확인하거나 다시 요청해 주세요."
						: (error && error.message ? error.message : "계정 요청을 처리하지 못했습니다.")));
			if (window.RpgAuthSession.getCurrentUser() || window.RpgAuthSession.getAccessToken()) {
				if (isAccountSessionInvalidError(error)) {
					returnToLoginAfterSessionExpiry("로그인 정보가 만료되었거나 사용할 수 없는 계정입니다. 다시 로그인해 주세요.");
				} else {
					renderSessionRetry(error);
				}
			} else {
				setFormBusy(form, false);
				setAuthStatus(message, "error");
			}
		} finally {
			gateBusy = false;
		}
	}

	async function handleEmailRequestSubmit(form) {
		if (gateBusy) return;
		const formType = form.dataset.accountForm;
		const email = normalizeEmail(new FormData(form).get("email"));
		if (!email) {
			setModalStatus("가입 이메일을 입력해 주세요.", "error");
			return;
		}
		const requests = {
			"recover-username": () => window.RpgGameApi.recoverAccountUsername({ email }, { timeoutMs: 15000 }),
			"request-password-reset": () => window.RpgGameApi.requestAccountPasswordReset({ email }, { timeoutMs: 15000 }),
			"resend-verification": () => window.RpgGameApi.resendAccountVerification({ email }, { timeoutMs: 15000 }),
		};
		const request = requests[formType];
		if (!request) return;
		gateBusy = true;
		setFormBusy(form, true, "메일 요청 중...");
		setModalStatus("메일 요청을 접수하고 있습니다...", "");
		try {
			await request();
			const successMessage = formType === "recover-username"
				? "입력한 이메일과 일치하는 계정이 있다면 아이디 안내 메일 요청을 접수했습니다."
				: (formType === "request-password-reset"
					? "입력한 이메일과 일치하는 계정이 있다면 비밀번호 재설정 메일 요청을 접수했습니다."
					: "입력한 이메일과 일치하는 미인증 계정이 있다면 인증 메일 요청을 접수했습니다.");
			setFormBusy(form, false);
			setModalStatus(successMessage, "success");
		} catch (error) {
			setFormBusy(form, false);
			setModalStatus(isRateLimitError(error)
				? getRateLimitMessage(error)
				: (isRequestBodyTooLargeError(error)
					? getRequestBodyTooLargeMessage()
					: "메일 요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요."), "error");
		} finally {
			gateBusy = false;
		}
	}

	async function resendPendingVerification() {
		if (gateBusy) return;
		if (!pendingVerificationEmail) {
			openEmailRequestModal("resend-verification");
			return;
		}
		gateBusy = true;
		setAuthStatus("인증 메일을 다시 요청하고 있습니다...", "");
		try {
			await window.RpgGameApi.resendAccountVerification({ email: pendingVerificationEmail }, { timeoutMs: 15000 });
			setAuthStatus("인증 메일 요청을 접수했습니다. 도착까지 몇 분 걸릴 수 있으니 받은편지함과 스팸함을 확인해 주세요.", "success");
		} catch (error) {
			setAuthStatus(isRateLimitError(error)
				? getRateLimitMessage(error)
				: (isRequestBodyTooLargeError(error)
					? getRequestBodyTooLargeMessage()
					: "인증 메일 요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요."), "error");
		} finally {
			gateBusy = false;
		}
	}

	async function handlePasswordResetSubmit(form) {
		if (gateBusy || !pendingAuthLinkAction || pendingAuthLinkAction.action !== "reset-password") return;
		const data = new FormData(form);
		const password = String(data.get("password") || "");
		const passwordConfirm = String(data.get("passwordConfirm") || "");
		if (password !== passwordConfirm) {
			setAuthStatus("비밀번호 확인이 일치하지 않습니다.", "error");
			form.querySelector("[name='passwordConfirm']")?.focus();
			return;
		}
		gateBusy = true;
		setFormBusy(form, true, "변경 중...");
		setAuthStatus("새 비밀번호를 안전하게 저장하고 있습니다...", "");
		try {
			await window.RpgGameApi.resetAccountPassword({ token: pendingAuthLinkAction.token, password, passwordConfirm }, { timeoutMs: 7000 });
			pendingAuthLinkAction = null;
			window.RpgAuthSession.clearSession();
			activeAuthTab = "login";
			renderAuth({ message: "비밀번호를 변경했습니다. 새 비밀번호로 로그인해 주세요.", tone: "success" });
		} catch (error) {
			setFormBusy(form, false);
			if (isEmailActionTokenInvalidError(error)) {
				pendingAuthLinkAction = null;
				activeAuthTab = "login";
				renderAuth({ message: "재설정 링크가 만료됐거나 이미 사용되었습니다. 새 메일을 요청해 주세요.", tone: "error" });
			} else {
				setAuthStatus(isRateLimitError(error)
					? `${getRateLimitMessage(error)} 재설정 링크는 현재 탭의 메모리에 안전하게 보존했습니다.`
					: (isRequestBodyTooLargeError(error)
						? `${getRequestBodyTooLargeMessage()} 재설정 링크는 현재 탭의 메모리에 안전하게 보존했습니다.`
						: `${error && error.message ? error.message : "비밀번호 재설정 요청을 처리하지 못했습니다."} 재설정 링크는 현재 탭의 메모리에 보존했습니다.`), "error");
			}
		} finally {
			gateBusy = false;
		}
	}

	async function handleAccountDeletionRequestSubmit(form) {
		if (gateBusy) return;
		const password = String(new FormData(form).get("password") || "");
		if (!password) {
			setModalStatus("현재 비밀번호를 입력해 주세요.", "error");
			return;
		}
		gateBusy = true;
		setFormBusy(form, true, "확인 중...");
		setModalStatus("비밀번호를 확인하고 삭제 확인 메일을 요청하고 있습니다...", "");
		try {
			await window.RpgGameApi.requestAccountDeletion({ password }, { timeoutMs: 15000 });
			setFormBusy(form, false);
			form.querySelector("[type='submit']").disabled = true;
			setModalStatus("삭제 확인 메일 요청을 접수했습니다. 메일 도착까지 몇 분 걸릴 수 있으며, 링크를 누르기 전까지 계정은 삭제되지 않습니다.", "success");
		} catch (error) {
			if (handleGameSessionInvalid(error)) return;
			setFormBusy(form, false);
			const errorCode = getErrorCode(error);
			setModalStatus(isRateLimitError(error)
				? getRateLimitMessage(error)
				: (isRequestBodyTooLargeError(error)
					? getRequestBodyTooLargeMessage()
					: (errorCode === "invalid_credentials"
						? "현재 비밀번호가 올바르지 않습니다. 다시 확인해 주세요."
						: (error && error.message ? error.message : "삭제 확인 메일 요청을 처리하지 못했습니다."))), "error");
		} finally {
			gateBusy = false;
		}
	}

	async function handleAccountDeletionConfirmSubmit(form) {
		if (gateBusy || !pendingAuthLinkAction || pendingAuthLinkAction.action !== "delete-account") return;
		const confirmText = String(new FormData(form).get("confirmText") || "").trim();
		if (confirmText !== "계정 삭제") {
			setModalStatus("확인 문구 ‘계정 삭제’를 정확히 입력해 주세요.", "error");
			return;
		}
		gateBusy = true;
		setFormBusy(form, true, "삭제 중...");
		setModalStatus("계정과 서버 저장을 삭제하고 있습니다...", "");
		try {
			const response = await window.RpgGameApi.confirmAccountDeletion({ token: pendingAuthLinkAction.token, confirmText: "계정 삭제" }, { timeoutMs: 7000 });
			const deletedUserId = Number(getPayload(response).deletedUserId);
			window.RpgAuthSession.clearDeletedAccountLocalData(deletedUserId);
			pendingAuthLinkAction = null;
			window.RpgAuthSession.clearSession();
			closeModal("resolved");
			activeAuthTab = "login";
			renderAuth({ message: "계정과 서버 저장을 삭제했습니다.", tone: "success" });
		} catch (error) {
			setFormBusy(form, false);
			const confirmButton = form.querySelector("[data-account-action='confirm-delete-account']");
			if (confirmButton) confirmButton.disabled = confirmText !== "계정 삭제";
			if (isEmailActionTokenInvalidError(error)) {
				pendingAuthLinkAction = null;
				if (confirmButton) confirmButton.disabled = true;
				setModalStatus("삭제 링크가 만료됐거나 이미 사용되었습니다. 계정 관리에서 새 메일을 요청해 주세요.", "error");
			} else {
				setModalStatus(isRateLimitError(error)
					? `${getRateLimitMessage(error)} 삭제 링크는 현재 탭의 메모리에 안전하게 보존했습니다.`
					: (isRequestBodyTooLargeError(error)
						? `${getRequestBodyTooLargeMessage()} 삭제 링크는 현재 탭의 메모리에 안전하게 보존했습니다.`
						: `${error && error.message ? error.message : "계정 삭제 요청을 처리하지 못했습니다."} 삭제 링크는 현재 탭의 메모리에 보존했습니다.`), "error");
			}
		} finally {
			gateBusy = false;
		}
	}

	async function handleCreateSubmit(form) {
		if (!activeModal || activeModal.type !== "create" || gateBusy) return;
		const data = new FormData(form);
		const name = String(data.get("name") || "").trim();
		const characterCode = String(data.get("characterCode") || "weapon_master");
		const slotIndex = activeModal.data.slotIndex;
		if (!name) {
			setModalStatus("캐릭터 이름을 입력해 주세요.", "error");
			return;
		}
		gateBusy = true;
		setFormBusy(form, true, "만드는 중...");
		try {
			const response = await window.RpgGameApi.createAccountCharacter({ slotIndex, name, characterCode }, { timeoutMs: 7000 });
			const payload = getPayload(response);
			const created = window.RpgAuthSession.normalizeCharacter(payload.character || payload.accountCharacter || payload);
			closeModal("resolved");
			await loadCharacters({ resumeSelected: false });
			if (created) {
				const actual = findCharacter(created.accountCharacterId) || created;
				gateBusy = false;
				await selectCharacter(actual);
			}
		} catch (error) {
			const message = error && error.message ? error.message : "캐릭터를 만들지 못했습니다.";
			if (activeModal && activeModal.type === "create") {
				setFormBusy(form, false);
				setModalStatus(message, "error");
			} else {
				renderCharacterSlots({ message: `캐릭터는 생성됐지만 목록을 새로 불러오지 못했습니다: ${message}`, tone: "error" });
			}
		} finally {
			gateBusy = false;
		}
	}

	function cleanupDeletedCharacterLocalData(character) {
		const user = window.RpgAuthSession.getCurrentUser();
		if (!user || !character) return;
		const localKey = window.RpgAuthSession.buildAccountLocalSaveKey(user.userId, character.accountCharacterId);
		try {
			window.localStorage.removeItem(localKey);
			window.localStorage.removeItem(`${localKey}.pre-backend-recovery`);
			window.RpgAuthSession.clearPendingUnsyncedSave({ userId: user.userId, accountCharacterId: character.accountCharacterId });
		} catch (error) {
			console.warn("[Upgrade RPG] deleted character local cache cleanup failed", error);
		}
	}

	async function verifyCharacterDeletionAfterError(accountCharacterId) {
		const response = await window.RpgGameApi.listAccountCharacters({ timeoutMs: 7000 });
		const payload = getPayload(response);
		const refreshedCharacters = normalizeCharacters(payload);
		return {
			deleted: !refreshedCharacters.some((item) => item.accountCharacterId === accountCharacterId),
			characters: refreshedCharacters,
			characterOptions: normalizeCharacterOptions(payload),
		};
	}

	async function confirmDeleteCharacter() {
		if (!activeModal || activeModal.type !== "delete" || gateBusy) return;
		const character = activeModal.data.character;
		const input = modalRoot.querySelector("[data-account-delete-name]");
		if (!input || input.value !== character.name) {
			setModalStatus("캐릭터 이름을 정확히 입력해 주세요.", "error");
			return;
		}
		gateBusy = true;
		modalRoot.querySelectorAll("button, input").forEach((item) => { item.disabled = true; });
		setModalStatus("캐릭터와 진행도를 삭제하고 있습니다...", "");
		try {
			let deleteError = null;
			try {
				await window.RpgGameApi.deleteAccountCharacter(character.accountCharacterId, { timeoutMs: 7000 });
			} catch (error) {
				deleteError = error;
			}
			if (deleteError) {
				if (handleGameSessionInvalid(deleteError)) return;
				let verification = null;
				try {
					verification = await verifyCharacterDeletionAfterError(character.accountCharacterId);
				} catch (verificationError) {
					if (handleGameSessionInvalid(verificationError)) return;
					modalRoot.querySelectorAll("button, input").forEach((item) => { item.disabled = false; });
					const confirmButton = modalRoot.querySelector("[data-account-action='confirm-delete-character']");
					if (confirmButton && input) confirmButton.disabled = input.value !== character.name;
					setModalStatus("삭제 요청의 결과를 서버에서 확인하지 못했습니다. 자동으로 다시 삭제하지 않았습니다. 잠시 후 슬롯 목록을 확인해 주세요.", "error");
					return;
				}
				characters = verification.characters;
				characterOptions = verification.characterOptions;
				if (!verification.deleted) {
					modalRoot.querySelectorAll("button, input").forEach((item) => { item.disabled = false; });
					const confirmButton = modalRoot.querySelector("[data-account-action='confirm-delete-character']");
					if (confirmButton && input) confirmButton.disabled = input.value !== character.name;
					setModalStatus(`서버 목록에 캐릭터가 남아 있어 삭제 완료로 처리하지 않았습니다. 자동으로 다시 삭제하지 않았습니다. ${deleteError.message || ""}`.trim(), "error");
					return;
				}
				cleanupDeletedCharacterLocalData(character);
				closeModal("resolved");
				renderCharacterSlots({ message: `${character.name} 캐릭터가 서버에서 삭제된 것을 확인했습니다.`, tone: "success" });
				return;
			}

			characters = characters.filter((item) => item.accountCharacterId !== character.accountCharacterId);
			cleanupDeletedCharacterLocalData(character);
			closeModal("resolved");
			try {
				await loadCharacters({ resumeSelected: false, message: `${character.name} 캐릭터를 삭제했습니다.`, tone: "success" });
			} catch (listError) {
				if (handleGameSessionInvalid(listError)) return;
				renderCharacterSlots({ message: `${character.name} 캐릭터는 삭제됐지만 최신 슬롯 목록을 불러오지 못했습니다. 다시 연결해 주세요.`, tone: "error" });
			}
		} finally {
			gateBusy = false;
		}
	}

	async function handleGateClick(event) {
		const actionTarget = event.target && event.target.closest ? event.target.closest("[data-account-action]") : null;
		if (!actionTarget) return;
		const action = actionTarget.dataset.accountAction;
		if (action === "auth-tab") {
			if (gateBusy) return;
			activeAuthTab = actionTarget.dataset.tab === "register" ? "register" : "login";
			renderAuth();
		} else if (action === "recover-username" || action === "request-password-reset" || action === "resend-verification") {
			if (!gateBusy) openEmailRequestModal(action);
		} else if (action === "verification-back-login") {
			if (!gateBusy) {
				activeAuthTab = "login";
				renderAuth({ message: "이메일 인증을 완료한 뒤 로그인해 주세요.", tone: "" });
			}
		} else if (action === "verification-resend") {
			await resendPendingVerification();
		} else if (action === "retry-link-action") {
			if (!gateBusy) await processPendingAuthLinkAction();
		} else if (action === "cancel-link-action") {
			if (!gateBusy) {
				pendingAuthLinkAction = null;
				closeModal("resolved");
				activeAuthTab = "login";
				renderAuth();
			}
		} else if (action === "account-settings") {
			if (!gateBusy) openAccountSettingsModal();
		} else if (action === "open-account-deletion") {
			if (!gateBusy) await previewAndOpenAccountDeletion();
		} else if (action === "create-character") {
			openCreateModal(Number(actionTarget.dataset.slotIndex));
		} else if (action === "select-character") {
			await selectCharacter(findCharacter(actionTarget.dataset.characterId));
		} else if (action === "delete-character") {
			event.stopPropagation();
			openDeleteModal(findCharacter(actionTarget.dataset.characterId));
		} else if (action === "logout-from-slots") {
			await logoutFromSlots();
		} else if (action === "retry-session") {
			await retrySessionConnection();
		} else if (action === "forget-session") {
			if (!gateBusy) {
				window.RpgAuthSession.clearSession();
				renderAuth({ message: "저장된 로그인 정보를 지웠습니다. 다른 계정으로 로그인해 주세요.", tone: "success" });
			}
		} else if (action === "close-modal") {
			if (canDismissActiveModal()) closeModal("cancel");
		} else if (action === "return-to-game") {
			if (!gateBusy) {
				if (pendingRuntimeResume && typeof window.resumeAccountGameRuntime === "function") window.resumeAccountGameRuntime();
				pendingRuntimeResume = false;
				closeModal("resolved");
				unlockGame();
			}
		} else if (action === "confirm-delete-character") {
			await confirmDeleteCharacter();
		} else if (action === "legacy-import" || action === "legacy-fresh") {
			if (activeModal && activeModal.resolve) activeModal.resolve(action === "legacy-import" ? "import" : "fresh");
			activeModal.resolve = null;
			closeModal("resolved");
		} else if (action === "pending-use-local" || action === "pending-use-server") {
			if (activeModal && activeModal.type === "pending-unsynced" && activeModal.resolve) {
				activeModal.resolve(action === "pending-use-local" ? "use-local" : "use-server");
				activeModal.resolve = null;
				closeModal("resolved");
			}
		}
	}

	async function handleGateSubmit(event) {
		const form = event.target && event.target.closest ? event.target.closest("[data-account-form]") : null;
		if (!form) return;
		event.preventDefault();
		if (form.dataset.accountForm === "login" || form.dataset.accountForm === "register") await handleAuthSubmit(form);
		if (["recover-username", "request-password-reset", "resend-verification"].includes(form.dataset.accountForm)) await handleEmailRequestSubmit(form);
		if (form.dataset.accountForm === "reset-password") await handlePasswordResetSubmit(form);
		if (form.dataset.accountForm === "account-deletion-request") await handleAccountDeletionRequestSubmit(form);
		if (form.dataset.accountForm === "account-deletion-confirm") await handleAccountDeletionConfirmSubmit(form);
		if (form.dataset.accountForm === "create-character") await handleCreateSubmit(form);
	}

	function handleGateInput(event) {
		if (!activeModal) return;
		if (activeModal.type === "delete" && event.target.matches("[data-account-delete-name]")) {
			const button = modalRoot.querySelector("[data-account-action='confirm-delete-character']");
			if (button) button.disabled = event.target.value !== activeModal.data.character.name;
		}
		if (activeModal.type === "account-deletion-confirm" && event.target.matches("[data-account-deletion-confirm-text]")) {
			const button = modalRoot.querySelector("[data-account-action='confirm-delete-account']");
			if (button) button.disabled = event.target.value.trim() !== "계정 삭제";
		}
	}

	function handleKeyboard(event) {
		if (activeModal) {
			if (event.key === "Escape" && canDismissActiveModal()) {
				event.preventDefault();
				closeModal("cancel");
				return;
			}
			if (event.key === "Tab") {
				const controls = Array.from(modalRoot.querySelectorAll("button:not(:disabled), input:not(:disabled), select:not(:disabled), [tabindex='0']"));
				if (!controls.length) return;
				const first = controls[0];
				const last = controls[controls.length - 1];
				if (event.shiftKey && document.activeElement === first) {
					event.preventDefault();
					last.focus();
				} else if (!event.shiftKey && document.activeElement === last) {
					event.preventDefault();
					first.focus();
				}
			}
			return;
		}
	}

	async function start() {
		if (initialized) return;
		initialized = true;
		lockGame();
		renderLoading();
		if (!window.RpgAuthSession || !window.RpgGameApi) {
			renderAuth({ message: "계정 모듈을 불러오지 못했습니다. 페이지를 새로고침해 주세요.", tone: "error" });
			return;
		}
		if (pendingAuthLinkAction) {
			await processPendingAuthLinkAction();
			return;
		}
		const authNotice = window.RpgAuthSession.consumeAuthNotice();
		await restoreSessionAndContinue(authNotice);
	}

	if (gate) {
		gate.addEventListener("click", handleGateClick);
		gate.addEventListener("submit", handleGateSubmit);
		gate.addEventListener("input", handleGateInput);
	}
	if (modalRoot) {
		modalRoot.addEventListener("click", (event) => {
			if (event.target.matches("[data-account-modal-backdrop]") && canDismissActiveModal()) closeModal("cancel");
		});
	}
	document.addEventListener("keydown", handleKeyboard);
	document.getElementById("game-account-switch")?.addEventListener("click", () => transitionFromGame("switch"));
	document.getElementById("game-account-logout")?.addEventListener("click", () => transitionFromGame("logout"));

	window.RpgAccountGate = {
		VERSION,
		SLOT_COUNT,
		start,
		lockGame,
		unlockGame,
		renderAuth,
		loadCharacters,
		renderCharacterSlots,
		requestLegacyImportDecision,
		requestPendingUnsyncedDecision,
		verifyCharacterDeletionAfterError,
		readLegacySave,
		updateAccountBar,
		syncAccountBarTownVisibility,
		transitionFromGame,
		handleGameSessionInvalid,
		getState: () => ({ initialized, activeAuthTab, gateBusy, characters: characters.slice(), characterOptions: characterOptions.slice(), modalType: activeModal && activeModal.type }),
	};
})();

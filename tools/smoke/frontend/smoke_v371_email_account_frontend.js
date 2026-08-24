const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..", "..", "..");
const read = (relative) => fs.readFileSync(path.join(root, relative), "utf8");

function createStorage(initialValues) {
	const values = new Map(Object.entries(initialValues || {}).map(([key, value]) => [String(key), String(value)]));
	return {
		get length() { return values.size; },
		key(index) { return Array.from(values.keys())[index] || null; },
		getItem(key) { return values.has(String(key)) ? values.get(String(key)) : null; },
		setItem(key, value) { values.set(String(key), String(value)); },
		removeItem(key) { values.delete(String(key)); },
	};
}

function testDeletedAccountLocalCleanup(authSource) {
	const deletedCharacterId = "a".repeat(32);
	const otherCharacterId = "b".repeat(32);
	const deletedSaveKey = `idleRpgSaveV22.u17.c${deletedCharacterId}`;
	const otherSaveKey = `idleRpgSaveV22.u18.c${otherCharacterId}`;
	const markerKey = "upgradeRpgPendingUnsyncedAccountSaves";
	const localStorage = createStorage({
		idleRpgSaveV22: "legacy-preserved",
		[deletedSaveKey]: "deleted-account-save",
		[`${deletedSaveKey}.pre-backend-recovery`]: "deleted-account-backup",
		[otherSaveKey]: "other-account-save",
		[markerKey]: JSON.stringify({
			[`17:${deletedCharacterId}`]: { userId: 17, accountCharacterId: deletedCharacterId },
			[`18:${otherCharacterId}`]: { userId: 18, accountCharacterId: otherCharacterId },
		}),
	});
	const context = { localStorage, sessionStorage: createStorage(), Date, Math };
	context.window = context;
	vm.runInNewContext(authSource, context, { filename: "auth-session.js" });
	const result = context.RpgAuthSession.clearDeletedAccountLocalData(17);

	assert.equal(result.ok, true);
	assert.equal(result.removedSaveKeys, 2);
	assert.equal(result.removedPendingMarkers, 1);
	assert.equal(localStorage.getItem("idleRpgSaveV22"), "legacy-preserved", "legacy single save must be preserved");
	assert.equal(localStorage.getItem(deletedSaveKey), null);
	assert.equal(localStorage.getItem(`${deletedSaveKey}.pre-backend-recovery`), null);
	assert.equal(localStorage.getItem(otherSaveKey), "other-account-save", "another account save was removed");
	const remainingMarkers = JSON.parse(localStorage.getItem(markerKey));
	assert.equal(remainingMarkers[`17:${deletedCharacterId}`], undefined);
	assert.equal(remainingMarkers[`18:${otherCharacterId}`].userId, 18);
}

async function testApiContracts(clientSource) {
	const calls = [];
	const queuedMailPaths = new Set([
		"/api/v1/auth/register",
		"/api/v1/auth/resend-verification",
		"/api/v1/auth/recover-username",
		"/api/v1/auth/request-password-reset",
		"/api/v1/auth/account-deletion/request",
	]);
	const context = {
		URL,
		AbortController,
		setTimeout,
		clearTimeout,
		localStorage: { getItem() { return null; }, setItem() {}, removeItem() {} },
		sessionStorage: { getItem() { return null; }, setItem() {}, removeItem() {} },
		RpgAuthSession: { getAccessToken() { return "safe-bearer"; } },
		async fetch(url, options) {
			const parsedUrl = new URL(String(url));
			const status = queuedMailPaths.has(parsedUrl.pathname) ? 202 : 200;
			calls.push({ url: parsedUrl, options, status });
			return { ok: true, status, async json() { return { ok: true, payload: { status: status === 202 ? "accepted" : "ok" } }; } };
		},
	};
	context.window = context;
	vm.runInNewContext(clientSource, context, { filename: "game-api-client.js" });

	await context.RpgGameApi.registerAccount({ username: "user_1", email: "user@example.com", password: "Password1", passwordConfirm: "Password1" });
	await context.RpgGameApi.loginAccount({ identifier: "user@example.com", password: "Password1" });
	await context.RpgGameApi.verifyAccountEmail({ token: "verification-token" });
	await context.RpgGameApi.resendAccountVerification({ email: "user@example.com" });
	await context.RpgGameApi.recoverAccountUsername({ email: "user@example.com" });
	await context.RpgGameApi.requestAccountPasswordReset({ email: "user@example.com" });
	await context.RpgGameApi.resetAccountPassword({ token: "reset-token", password: "Password2", passwordConfirm: "Password2" });
	await context.RpgGameApi.previewAccountDeletion();
	await context.RpgGameApi.requestAccountDeletion({ password: "Password2" });
	await context.RpgGameApi.confirmAccountDeletion({ token: "delete-token", confirmText: "계정 삭제" });

	const byPath = new Map(calls.map((call) => [call.url.pathname, call]));
	const publicPaths = [
		"/api/v1/auth/register",
		"/api/v1/auth/login",
		"/api/v1/auth/verify-email",
		"/api/v1/auth/resend-verification",
		"/api/v1/auth/recover-username",
		"/api/v1/auth/request-password-reset",
		"/api/v1/auth/reset-password",
		"/api/v1/auth/account-deletion/confirm",
	];
	for (const publicPath of publicPaths) {
		assert.equal(byPath.get(publicPath).options.headers.Authorization, undefined, `${publicPath} leaked an existing bearer token`);
	}
	assert.equal(byPath.get("/api/v1/auth/account-deletion/preview").options.headers.Authorization, "Bearer safe-bearer");
	assert.equal(byPath.get("/api/v1/auth/account-deletion/request").options.headers.Authorization, "Bearer safe-bearer");
	assert.equal(JSON.parse(byPath.get("/api/v1/auth/login").options.body).identifier, "user@example.com");
	assert.equal(JSON.parse(byPath.get("/api/v1/auth/account-deletion/confirm").options.body).confirmText, "계정 삭제");
	for (const queuedMailPath of queuedMailPaths) {
		assert.equal(byPath.get(queuedMailPath).status, 202, `${queuedMailPath} was not exercised as an accepted queued request`);
	}
}

function testSecurityErrorClassification(gateSource) {
	const constantsStart = gateSource.indexOf("const SESSION_INVALID_ERROR_CODES");
	const constantsEnd = gateSource.indexOf("const gate =", constantsStart);
	const helpersStart = gateSource.indexOf("function getErrorCode");
	const helpersEnd = gateSource.indexOf("function returnToLoginAfterSessionExpiry", helpersStart);
	assert(constantsStart >= 0 && constantsEnd > constantsStart, "account security error constants are missing");
	assert(helpersStart >= 0 && helpersEnd > helpersStart, "account security error helpers are missing");
	const source = `${gateSource.slice(constantsStart, constantsEnd)}\n${gateSource.slice(helpersStart, helpersEnd)}`;
	const context = { window: {} };
	vm.runInNewContext(`${source}; window.helpers = { getErrorCode, getRetryAfterSeconds, isRateLimitError, isRequestBodyTooLargeError, isEmailActionTokenInvalidError, getRateLimitMessage, isAccountSessionInvalidError };`, context);
	const helpers = context.window.helpers;
	const envelopeError = (status, code, meta) => ({
		status,
		response: {
			error: { code, message: "safe" },
			meta: meta || {},
		},
	});

	for (const code of [
		"bearer_token_required",
		"access_token_invalid",
		"account_not_found",
		"auth_version_stale",
		"account_suspended",
		"email_verification_required",
	]) {
		assert.equal(helpers.isAccountSessionInvalidError(envelopeError(code === "account_suspended" ? 403 : 401, code)), true, `${code} did not invalidate the session`);
	}
	for (const [status, code] of [[401, "invalid_credentials"], [403, "admin_account_deletion_blocked"], [403, "admin_permission_required"], [429, "auth_rate_limited"], [413, "request_body_too_large"]]) {
		assert.equal(helpers.isAccountSessionInvalidError(envelopeError(status, code)), false, `${code} incorrectly invalidated the session`);
	}
	assert.equal(
		helpers.getErrorCode({ status: 401, response: { payload: { status: "error" }, detail: { code: "auth_version_stale", message: "safe" } } }),
		"auth_version_stale",
		"FastAPI detail error code was masked by a generic payload status",
	);
	const limited = envelopeError(429, "auth_rate_limited", { retryAfterSeconds: 37 });
	assert.equal(helpers.isRateLimitError(limited), true);
	assert.equal(helpers.getRetryAfterSeconds(limited), 37);
	assert.match(helpers.getRateLimitMessage(limited), /37초 후 다시 시도/);
	assert.equal(helpers.isRequestBodyTooLargeError(envelopeError(413, "request_body_too_large")), true);
	assert.equal(helpers.isEmailActionTokenInvalidError(envelopeError(400, "email_action_token_invalid")), true);
}

function testFragmentConsumption(gateSource) {
	const start = gateSource.indexOf("function consumeAuthLinkFragment()");
	const end = gateSource.indexOf("function getErrorCode", start);
	assert(start >= 0 && end > start, "email action fragment consumer is missing");
	const source = gateSource.slice(start, end);
	let replacedUrl = "";
	const context = {
		URLSearchParams,
		document: { title: "Upgrade RPG" },
		window: {
			location: { hash: `#auth=reset-password&token=${"a".repeat(43)}`, pathname: "/index.html", search: "?from=email" },
			history: { replaceState(_state, _title, value) { replacedUrl = value; } },
		},
	};
	vm.runInNewContext(`const AUTH_LINK_ACTIONS = new Set(["verify-email", "reset-password", "delete-account"]); const EMAIL_ACTION_TOKEN_PATTERN = /^[A-Za-z0-9_-]{32,256}$/; ${source}; window.result = consumeAuthLinkFragment();`, context);
	assert.equal(context.window.result.action, "reset-password");
	assert.equal(context.window.result.token, "a".repeat(43));
	assert.equal(replacedUrl, "/index.html?from=email");
	assert(!replacedUrl.includes("a".repeat(43)), "email action token remained in the cleaned browser URL");
	for (const [label, token] of [
		["short", "a".repeat(31)],
		["overlong", "a".repeat(257)],
		["punctuation", `${"a".repeat(31)}!`],
		["non-ascii", `${"a".repeat(31)}한`],
	]) {
		context.window.location.hash = `#auth=verify-email&token=${encodeURIComponent(token)}`;
		vm.runInNewContext("window.invalidResult = consumeAuthLinkFragment();", context);
		assert.equal(context.window.invalidResult.invalid, true, `${label} email action token was sent toward the API`);
		assert.equal(context.window.invalidResult.token, "", `${label} email action token remained in memory`);
	}
}

function testSameDocumentFragmentReload(gateSource) {
	const start = gateSource.indexOf("function handleAuthLinkHashChange()");
	const end = gateSource.indexOf("function getErrorCode", start);
	assert(start >= 0 && end > start, "same-document email action fragment listener is missing");
	const source = gateSource.slice(start, end);
	assert.doesNotMatch(source, /params\.get\(["']token["']\)/, "hashchange listener must not read the action token");

	let hashChangeListener = null;
	let reloadCount = 0;
	const context = {
		URLSearchParams,
		window: {
			location: {
				hash: "",
				reload() { reloadCount += 1; },
			},
			addEventListener(name, listener) {
				if (name === "hashchange") hashChangeListener = listener;
			},
		},
	};
	vm.runInNewContext(`const AUTH_LINK_ACTIONS = new Set(["verify-email", "reset-password", "delete-account"]); ${source}`, context);
	assert.equal(typeof hashChangeListener, "function");
	context.window.location.hash = "#auth=reset-password&token=private-link-token";
	hashChangeListener();
	assert.equal(reloadCount, 1, "whitelisted same-document auth link did not reload immediately");
	context.window.location.hash = "#auth=untrusted-action&token=private-link-token";
	hashChangeListener();
	assert.equal(reloadCount, 1, "unknown fragment action triggered a reload");
}

function testTownOnlyAccountBar(gateSource) {
	const start = gateSource.indexOf("function syncAccountBarTownVisibility");
	const end = gateSource.indexOf("async function transitionFromGame", start);
	assert(start >= 0 && end > start, "town-only account bar synchronizer is missing");
	const source = gateSource.slice(start, end);
	const attributes = new Map();
	const accountBar = {
		hidden: true,
		inert: true,
		dataset: {},
		setAttribute(name, value) { attributes.set(name, String(value)); },
		toggleAttribute(name, enabled) { if (enabled) attributes.set(name, ""); else attributes.delete(name); },
	};
	const context = {
		accountBar,
		window: {
			RpgAuthSession: {
				getCurrentUser() { return { id: 1 }; },
				getCurrentCharacter() { return { accountCharacterId: "a".repeat(32) }; },
			},
		},
	};
	vm.runInNewContext(`${source}; window.sync = syncAccountBarTownVisibility;`, context);
	assert.equal(context.window.sync("field"), false);
	assert.equal(accountBar.hidden, true);
	assert.equal(accountBar.inert, true);
	assert.equal(attributes.get("aria-hidden"), "true");
	assert.equal(context.window.sync("town"), true);
	assert.equal(accountBar.hidden, false);
	assert.equal(accountBar.inert, false);
	assert.equal(attributes.get("aria-hidden"), "false");
}

async function run() {
	const html = read("index.html");
	const adminHtml = read("admin.html");
	const gateSource = read("src/ui/account-gate.js");
	const clientSource = read("src/api/game-api-client.js");
	const authSource = read("src/api/auth-session.js");
	const renderSource = read("src/ui/render-ui.js");
	const accountCss = read("src/styles/account.css");
	const adminSource = read("src/api/admin/admin-account-management.js");

	assert.match(html, /src\/styles\/account\.css\?v=378/);
	assert.match(html, /<meta name="referrer" content="no-referrer" \/>/);
	assert.match(html, /auth-session\.js\?v=377/);
	assert.match(html, /game-api-client\.js\?v=378/);
	assert.match(html, /render-ui\.js\?v=378/);
	assert.match(html, /account-gate\.js\?v=378/);
	assert.match(html, /id="game-account-bar"[^>]+aria-hidden="true"[^>]+hidden[^>]+inert/);
	assert.match(adminHtml, /account-admin\.css\?v=371/);
	assert.match(adminHtml, /admin-account-management\.js\?v=371/);

	assert.match(gateSource, /name="identifier"/);
	assert.match(gateSource, /name="email" type="email"/);
	assert.match(gateSource, /registerAccount\([\s\S]+timeoutMs: 15000/);
	assert.match(gateSource, /recoverAccountUsername\(\{ email \}, \{ timeoutMs: 15000 \}\)/);
	assert.match(gateSource, /requestAccountPasswordReset\(\{ email \}, \{ timeoutMs: 15000 \}\)/);
	assert.match(gateSource, /resendAccountVerification\(\{ email \}, \{ timeoutMs: 15000 \}\)/);
	assert.match(gateSource, /resendAccountVerification\(\{ email: pendingVerificationEmail \}, \{ timeoutMs: 15000 \}\)/);
	assert.match(gateSource, /requestAccountDeletion\(\{ password \}, \{ timeoutMs: 15000 \}\)/);
	assert.match(gateSource, /renderVerificationPending\(email/);
	assert.match(gateSource, /window\.RpgAuthSession\.clearSession\(\);[\s\S]+renderVerificationPending/);
	assert.doesNotMatch(gateSource, /verification_email_delivery_failed/);
	assert.match(gateSource, /가입과 인증 메일 요청을 접수했습니다\. 메일 도착까지 몇 분 걸릴 수 있습니다\./);
	assert.match(gateSource, /아이디 안내 메일 요청을 접수했습니다/);
	assert.match(gateSource, /비밀번호 재설정 메일 요청을 접수했습니다/);
	assert.match(gateSource, /삭제 확인 메일 요청을 접수했습니다/);
	assert.doesNotMatch(gateSource, /인증 메일을 보냈습니다|인증 메일을 다시 보냈습니다|삭제 확인 메일을 보냈습니다/);
	assert.match(gateSource, /const RATE_LIMIT_ERROR_CODE = "auth_rate_limited"/);
	assert.match(gateSource, /const REQUEST_BODY_TOO_LARGE_ERROR_CODE = "request_body_too_large"/);
	assert.match(gateSource, /meta\.retryAfterSeconds/);
	assert.match(gateSource, /요청 데이터가 허용 크기를 넘었습니다/);
	assert(gateSource.includes("const EMAIL_ACTION_TOKEN_PATTERN = /^[A-Za-z0-9_-]{32,256}$/;"));
	assert.match(gateSource, /EMAIL_ACTION_TOKEN_PATTERN\.test\(token\)/);
	assert.doesNotMatch(gateSource, /status >= 400 && status < 500/);
	assert.match(gateSource, /if \(isEmailActionTokenInvalidError\(error\)\)[\s\S]+else if \(isRateLimitError\(error\)\)[\s\S]+인증 링크는 현재 탭의 메모리에 안전하게 보존했습니다/);
	assert.match(gateSource, /재설정 링크는 현재 탭의 메모리에 안전하게 보존했습니다/);
	assert.match(gateSource, /삭제 링크는 현재 탭의 메모리에 안전하게 보존했습니다/);
	const resetHandler = gateSource.slice(gateSource.indexOf("async function handlePasswordResetSubmit"), gateSource.indexOf("async function handleAccountDeletionRequestSubmit"));
	const deletionConfirmHandler = gateSource.slice(gateSource.indexOf("async function handleAccountDeletionConfirmSubmit"), gateSource.indexOf("async function handleCreateSubmit"));
	assert.match(resetHandler, /error && error\.message[\s\S]+재설정 링크는 현재 탭의 메모리에 보존했습니다/);
	assert.match(deletionConfirmHandler, /error && error\.message[\s\S]+삭제 링크는 현재 탭의 메모리에 보존했습니다/);
	assert.match(authSource, /const SESSION_INVALID_ERROR_CODES = new Set/);
	assert.match(authSource, /if \(isSessionInvalidError\(error\)\)/);
	assert.doesNotMatch(authSource, /status === 401 \|\| status === 403/);
	assert.match(gateSource, /replaceState\(null, document\.title, cleanUrl\)/);
	assert.match(gateSource, /"recover-username":\s*\{/);
	assert.match(gateSource, /"request-password-reset":\s*\{/);
	assert.match(gateSource, /"resend-verification":\s*\{/);
	assert.match(gateSource, /data-account-form="\$\{definition\.action\}"/);
	assert.match(gateSource, /data-account-form="account-deletion-request"/);
	assert.match(gateSource, /data-account-form="account-deletion-confirm"/);
	assert.match(gateSource, /data-account-action="confirm-delete-account" disabled/);
	assert.match(gateSource, /getPayload\(response\)\.deletedUserId/);
	assert.match(gateSource, /clearDeletedAccountLocalData\(deletedUserId\)/);
	assert.match(gateSource, /previewAccountDeletion\(\{ timeoutMs: 7000 \}\)/);
	assert(gateSource.indexOf("previewAccountDeletion({ timeoutMs: 7000 })") < gateSource.indexOf("openAccountDeletionRequestModal(getPayload(response))"));
	assert.match(renderSource, /syncAccountBarTownVisibility\(currentZoneType\)/);

	assert.match(accountCss, /width:\s*min\(700px,/);
	assert.match(accountCss, /#game-account-character[\s\S]+font-size:\s*17px/);
	assert.match(accountCss, /\.game-account-actions button[\s\S]+min-height:\s*44px/);
	assert.match(accountCss, /\.account-auth-links/);
	assert.match(accountCss, /\.account-deletion-preview/);
	assert.match(accountCss, /@media \(max-width: 480px\)/);

	assert.match(adminSource, /escapeHtml\(user\.maskedEmail/);
	assert.match(adminSource, /escapeHtml\(formatValue\(user\.email\)\)/);
	assert.match(adminSource, /user\.emailVerified \? "인증 완료" : "인증 대기"/);
	assert.doesNotMatch(`${html}\n${adminHtml}\n${gateSource}\n${clientSource}`, /brevo|sendgrid|smtp/i);

	await testApiContracts(clientSource);
	testSecurityErrorClassification(gateSource);
	testDeletedAccountLocalCleanup(authSource);
	testFragmentConsumption(gateSource);
	testSameDocumentFragmentReload(gateSource);
	testTownOnlyAccountBar(gateSource);

	console.log("v371 email account frontend smoke passed");
	console.log("- queued 202 email acceptance wording and generic recovery UX: ok");
	console.log("- 429 Retry-After / 413 messaging and exact session-invalid code allowlist: ok");
	console.log("- auth-link token memory preservation with exact invalid-token disposal: ok");
	console.log("- fragment token immediate URL cleanup and public/bearer API split: ok");
	console.log("- same-document auth fragment fail-closed reload without token access: ok");
	console.log("- deletion preview + two-step custom confirmation: ok");
	console.log("- deleted-account local cache cleanup with legacy/other-account preservation: ok");
	console.log("- town-only enlarged account bar and safe admin email rendering: ok");
}

run().catch((error) => {
	console.error(error);
	process.exitCode = 1;
});

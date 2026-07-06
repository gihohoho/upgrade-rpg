(function () {
	"use strict";

	const BADGE_ID = "backend-save-data-dev-badge";
	const TOGGLE_ID = "backend-save-data-dev-badge-toggle";
	const WRAPPER_ID = "backend-save-data-dev-badge-wrap";
	const STYLE_ID = "backend-save-data-dev-badge-style";
	const STORAGE_KEY = "upgradeRpgShowBackendSaveDataDevBadge";
	const VERSION = "v104.backend-save-data-dev-badge-hud-top-align";

	let currentAction = null;
	let lastLoadResult = null;

	function isLocalDevelopment() {
		try {
			const protocol = window.location && window.location.protocol;
			const host = window.location && window.location.hostname;
			return protocol === "file:" || host === "localhost" || host === "127.0.0.1";
		} catch (error) {
			return true;
		}
	}

	function readStorage(key) {
		try {
			return window.localStorage ? window.localStorage.getItem(key) : null;
		} catch (error) {
			return null;
		}
	}

	function writeStorage(key, value) {
		try {
			if (window.localStorage) window.localStorage.setItem(key, value);
		} catch (error) {
			// localStorage 사용이 막힌 환경에서는 현재 탭 표시 상태만 사용합니다.
		}
	}

	function shouldCreateControls() {
		const stored = readStorage(STORAGE_KEY);
		return isLocalDevelopment() || stored === "1" || stored === "0";
	}

	function shouldShowBadgeByDefault() {
		const stored = readStorage(STORAGE_KEY);
		if (stored === "1") return true;
		if (stored === "0") return false;
		return isLocalDevelopment();
	}

	function getPolicy() {
		if (typeof window.getBackendSaveSyncPolicy === "function") return window.getBackendSaveSyncPolicy();
		return {
			mode: "unknown",
			manualDualWriteEnabled: false,
			fallbackToLocalStorage: true,
			localSaveKey: window.UPGRADE_RPG_LOCAL_SAVE_KEY || "idleRpgSaveV22",
			status: getStatus(),
		};
	}

	function getStatus() {
		if (typeof window.getBackendSaveSyncStatus === "function") return window.getBackendSaveSyncStatus();
		return {
			ok: null,
			state: "unknown",
			updatedAt: null,
			mode: "unknown",
			error: null,
			summary: null,
		};
	}

	function getStateKind(state, ok) {
		const value = String(state || "");
		if (currentAction) return "loading";
		if (value === "synced") return "ok";
		if (value === "skipped_local_only_mode" || value === "local_only_mode") return "local";
		if (value === "ready_manual_dual" || value === "skipped_manual_save_cooldown") return "idle";
		if (value === "never_synced") return "idle";
		if (value.indexOf("failed") >= 0 || ok === false) return "failed";
		if (value.indexOf("syncing") >= 0 || value.indexOf("loading") >= 0) return "loading";
		return "unknown";
	}

	function formatClockFromIso(value) {
		if (!value) return "-";
		try {
			const date = new Date(value);
			if (Number.isNaN(date.getTime())) return "-";
			return date.toLocaleTimeString("ko-KR", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
		} catch (error) {
			return "-";
		}
	}

	function formatClockNow() {
		try {
			return new Date().toLocaleTimeString("ko-KR", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
		} catch (error) {
			return new Date().toTimeString().slice(0, 8);
		}
	}

	function formatShortNumber(value) {
		if (value === null || value === undefined || value === "") return "-";
		const number = Number(value);
		if (!Number.isFinite(number)) return String(value);
		if (Math.abs(number) >= 1e12) return `${(number / 1e12).toFixed(1)}T`;
		if (Math.abs(number) >= 1e9) return `${(number / 1e9).toFixed(1)}B`;
		if (Math.abs(number) >= 1e6) return `${(number / 1e6).toFixed(1)}M`;
		if (Math.abs(number) >= 1e3) return `${(number / 1e3).toFixed(1)}K`;
		return String(number);
	}

	function summarizeSave(status) {
		const summary = status && status.summary ? status.summary : null;
		if (!summary) return "save: -";
		const parts = [];
		if (summary.level !== null && summary.level !== undefined) parts.push(`Lv:${summary.level}`);
		if (summary.gold !== null && summary.gold !== undefined) parts.push(`G:${formatShortNumber(summary.gold)}`);
		if (summary.inventoryItems !== null && summary.inventoryItems !== undefined) parts.push(`Inv:${summary.inventoryItems}`);
		if (summary.storageItems !== null && summary.storageItems !== undefined) parts.push(`Sto:${summary.storageItems}`);
		return parts.length ? parts.join(" · ") : "save: summary";
	}

	function summarizeLoadResult() {
		if (!lastLoadResult) return "loaded: -";
		const data = lastLoadResult && lastLoadResult.data ? lastLoadResult.data : {};
		const payload = lastLoadResult && lastLoadResult.payload ? lastLoadResult.payload : {};
		if (data.exists === false) return "loaded: empty";
		if (data.status) return `loaded: ${data.status}${payload.saveVersion !== undefined && payload.saveVersion !== null ? ` · v${payload.saveVersion}` : ""}`;
		return "loaded: checked";
	}

	function ensureStyle() {
		if (document.getElementById(STYLE_ID)) return;
		const style = document.createElement("style");
		style.id = STYLE_ID;
		style.textContent = `
#${WRAPPER_ID} {
	position: fixed;
	right: 20px;
	bottom: 170px;
	z-index: 99998;
	width: 226px;
	box-sizing: border-box;
	pointer-events: none;
}
#bottom-hud > #${WRAPPER_ID} {
	position: absolute;
	right: 20px;
	top: auto;
	bottom: calc(100% + 10px);
	transform: none;
	width: 226px;
	z-index: 99998;
}
#${BADGE_ID} {
	position: relative;
	z-index: 1;
	width: 100%;
	box-sizing: border-box;
	padding: 14px 10px 10px;
	border: 1px solid rgba(255, 255, 255, 0.18);
	border-radius: 10px;
	background: rgba(9, 13, 22, 0.90);
	box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
	color: #f8fafc;
	font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
	font-size: 11px;
	line-height: 1.35;
	letter-spacing: -0.01em;
	backdrop-filter: blur(8px);
	user-select: none;
	pointer-events: auto;
}
#${TOGGLE_ID} {
	position: absolute;
	left: 50%;
	top: 0;
	transform: translate(-50%, -50%);
	z-index: 2;
	box-sizing: border-box;
	min-width: 82px;
	border: 1px solid rgba(255, 255, 255, 0.22);
	border-radius: 999px;
	background: rgba(9, 13, 22, 0.96);
	box-shadow: 0 6px 18px rgba(0, 0, 0, 0.28);
	color: #f8fafc;
	font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
	font-size: 10px;
	font-weight: 800;
	line-height: 1;
	padding: 5px 10px;
	cursor: pointer;
	pointer-events: auto;
	text-align: center;
	white-space: nowrap;
}
#${TOGGLE_ID}:hover { background: rgba(30, 41, 59, 0.98); }
#${BADGE_ID}[data-hidden="true"] { display: none; }
#${WRAPPER_ID}[data-badge-visible="false"] { width: 92px; }
#bottom-hud > #${WRAPPER_ID}[data-badge-visible="false"] { right: 20px; width: 92px; }
#${WRAPPER_ID}[data-badge-visible="false"] #${TOGGLE_ID} {
	position: relative;
	left: 50%;
	top: auto;
	transform: translateX(-50%);
}
#${TOGGLE_ID}[data-hidden="true"] { display: none; }
#${BADGE_ID} .sd-badge-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
#${BADGE_ID} .sd-badge-title { font-weight: 800; font-size: 11px; white-space: nowrap; }
#${BADGE_ID} .sd-badge-pill {
	display: inline-flex;
	align-items: center;
	gap: 4px;
	max-width: 98px;
	padding: 2px 7px;
	border-radius: 999px;
	font-size: 10px;
	font-weight: 800;
	background: rgba(148, 163, 184, 0.22);
	color: #e2e8f0;
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}
#${BADGE_ID} .sd-badge-dot { width: 6px; height: 6px; min-width: 6px; border-radius: 999px; background: #94a3b8; }
#${BADGE_ID}[data-kind="ok"] .sd-badge-dot { background: #22c55e; }
#${BADGE_ID}[data-kind="loading"] .sd-badge-dot { background: #38bdf8; }
#${BADGE_ID}[data-kind="local"] .sd-badge-dot { background: #f59e0b; }
#${BADGE_ID}[data-kind="idle"] .sd-badge-dot { background: #94a3b8; }
#${BADGE_ID}[data-kind="failed"] .sd-badge-dot { background: #ef4444; }
#${BADGE_ID} .sd-badge-meta { margin-top: 5px; display: flex; flex-wrap: wrap; gap: 4px 8px; color: #cbd5e1; }
#${BADGE_ID} .sd-badge-summary,
#${BADGE_ID} .sd-badge-load,
#${BADGE_ID} .sd-badge-updated { margin-top: 4px; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
#${BADGE_ID} .sd-badge-updated { color: #64748b; font-size: 10px; }
#${BADGE_ID} .sd-badge-actions {
	margin-top: 6px;
	display: grid;
	grid-template-columns: repeat(4, minmax(0, 1fr));
	gap: 5px;
}
#${BADGE_ID} button {
	border: 1px solid rgba(255, 255, 255, 0.16);
	border-radius: 6px;
	background: rgba(255, 255, 255, 0.08);
	color: #f8fafc;
	font: inherit;
	font-size: 9px;
	padding: 4px 5px;
	cursor: pointer;
	white-space: nowrap;
	text-align: center;
}
#${BADGE_ID} button:hover { background: rgba(255, 255, 255, 0.15); }
#${BADGE_ID} button[data-active="true"] {
	border-color: rgba(34, 197, 94, 0.68);
	background: rgba(34, 197, 94, 0.18);
	color: #bbf7d0;
	box-shadow: inset 0 0 0 1px rgba(34, 197, 94, 0.18);
}
#${BADGE_ID} button[data-busy="true"] { cursor: wait; opacity: 0.72; }
#${BADGE_ID}[data-flash="true"] { box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(56, 189, 248, 0.45); }
@media (max-width: 1280px) {
	#${WRAPPER_ID}, #bottom-hud > #${WRAPPER_ID} { width: 218px; }
	#bottom-hud > #${WRAPPER_ID} { right: 20px; bottom: calc(100% + 8px); }
	#bottom-hud > #${WRAPPER_ID}[data-badge-visible="false"] { right: 20px; width: 92px; }
	#${BADGE_ID} { font-size: 10px; padding: 13px 8px 8px; }
}
@media (max-width: 980px) {
	#${WRAPPER_ID}, #bottom-hud > #${WRAPPER_ID} { width: 206px; }
	#bottom-hud > #${WRAPPER_ID}[data-badge-visible="false"] { right: 20px; width: 88px; }
}
@media (max-width: 640px) {
	#${WRAPPER_ID}, #bottom-hud > #${WRAPPER_ID} { width: 196px; }
	#bottom-hud > #${WRAPPER_ID} { right: 12px; bottom: calc(100% + 6px); }
	#bottom-hud > #${WRAPPER_ID}[data-badge-visible="false"] { right: 12px; width: 88px; }
	#${BADGE_ID} { font-size: 10px; padding: 13px 8px 7px; }
}
`;
		document.head.appendChild(style);
	}

	function getPreferredParent() {
		return document.getElementById("bottom-hud") || document.body;
	}

	function ensureBadgeWrapper() {
		ensureStyle();
		const preferredParent = getPreferredParent();
		let wrapper = document.getElementById(WRAPPER_ID);
		if (!wrapper) {
			wrapper = document.createElement("div");
			wrapper.id = WRAPPER_ID;
		}
		if (preferredParent && wrapper.parentElement !== preferredParent) {
			preferredParent.appendChild(wrapper);
		}
		return wrapper;
	}

	function attachBadgeToPreferredParent(element) {
		const wrapper = ensureBadgeWrapper();
		if (element && wrapper && element.parentElement !== wrapper) {
			wrapper.appendChild(element);
		}
		return element;
	}

	function createToggle() {
		ensureStyle();
		let toggle = document.getElementById(TOGGLE_ID);
		if (toggle) return toggle;
		toggle = document.createElement("button");
		toggle.id = TOGGLE_ID;
		toggle.type = "button";
		toggle.setAttribute("aria-controls", BADGE_ID);
		toggle.addEventListener("click", () => toggleBackendSaveDataDevBadge());
		attachBadgeToPreferredParent(toggle);
		return toggle;
	}

	function createBadge() {
		ensureStyle();
		let badge = document.getElementById(BADGE_ID);
		if (badge) return badge;
		badge = document.createElement("div");
		badge.id = BADGE_ID;
		badge.setAttribute("role", "status");
		badge.setAttribute("aria-live", "polite");
		badge.innerHTML = `
			<div class="sd-badge-row">
				<div class="sd-badge-title">SAVE DATA</div>
				<div class="sd-badge-pill"><span class="sd-badge-dot"></span><span data-sd-state>unknown</span></div>
			</div>
			<div class="sd-badge-meta">
				<span data-sd-mode>mode: unknown</span>
				<span data-sd-slot>slot: default</span>
			</div>
			<div class="sd-badge-summary" data-sd-summary>save: -</div>
			<div class="sd-badge-load" data-sd-load>loaded: -</div>
			<div class="sd-badge-updated" data-sd-updated>updated: -</div>
			<div class="sd-badge-actions">
				<button type="button" data-sd-action="sync" title="현재 localStorage 저장값을 백엔드 DB에 즉시 저장합니다. 게임 저장 버튼이 아니라 DB 전송 확인용입니다.">sync DB</button>
				<button type="button" data-sd-action="load" title="백엔드 DB에 저장된 세이브 스냅샷을 조회만 합니다. 아직 게임에 적용하지 않습니다.">load DB</button>
				<button type="button" data-sd-action="dual" title="수동 저장 시 localStorage와 백엔드 DB에 함께 저장합니다.">dual</button>
				<button type="button" data-sd-action="local" title="수동 저장 시 기존 localStorage에만 저장합니다.">local</button>
			</div>
		`;
		badge.addEventListener("click", handleBadgeClick);
		attachBadgeToPreferredParent(badge);
		return badge;
	}

	async function runBadgeAction(action) {
		if (currentAction) return;
		currentAction = action;
		refreshBackendSaveDataDevBadge({ flash: true });
		try {
			if (action === "sync") {
				if (typeof window.syncLatestLocalSaveToBackend !== "function") throw new Error("syncLatestLocalSaveToBackend 함수를 찾을 수 없습니다.");
				await window.syncLatestLocalSaveToBackend({ reason: "save-data-dev-badge", source: "save-data-dev-badge", log: true });
			} else if (action === "load") {
				if (typeof window.loadBackendSaveSnapshot !== "function") throw new Error("loadBackendSaveSnapshot 함수를 찾을 수 없습니다.");
				lastLoadResult = await window.loadBackendSaveSnapshot({ timeoutMs: 2500 });
			} else if (action === "dual") {
				if (typeof window.enableBackendSaveDualWrite !== "function") throw new Error("enableBackendSaveDualWrite 함수를 찾을 수 없습니다.");
				window.enableBackendSaveDualWrite();
			} else if (action === "local") {
				if (typeof window.disableBackendSaveDualWrite !== "function") throw new Error("disableBackendSaveDualWrite 함수를 찾을 수 없습니다.");
				window.disableBackendSaveDualWrite();
			}
		} catch (error) {
			console.warn("[Upgrade RPG] save-data dev badge action failed", action, error);
		} finally {
			currentAction = null;
			refreshBackendSaveDataDevBadge({ flash: true });
		}
	}

	function handleBadgeClick(event) {
		const button = event.target && event.target.closest ? event.target.closest("button[data-sd-action]") : null;
		if (!button) return;
		runBadgeAction(button.getAttribute("data-sd-action"));
	}

	function updateActionButtonStates(badge, mode) {
		if (!badge) return;
		const dualButton = badge.querySelector('button[data-sd-action="dual"]');
		const localButton = badge.querySelector('button[data-sd-action="local"]');
		const syncButton = badge.querySelector('button[data-sd-action="sync"]');
		const loadButton = badge.querySelector('button[data-sd-action="load"]');
		if (dualButton) dualButton.dataset.active = mode === "manual_dual" ? "true" : "false";
		if (localButton) localButton.dataset.active = mode === "local_only" ? "true" : "false";
		if (syncButton) syncButton.dataset.busy = currentAction === "sync" ? "true" : "false";
		if (loadButton) loadButton.dataset.busy = currentAction === "load" ? "true" : "false";
	}

	function updateToggleState(toggle, visible) {
		if (!toggle) return;
		toggle.dataset.hidden = shouldCreateControls() ? "false" : "true";
		toggle.dataset.badgeVisible = visible ? "true" : "false";
		toggle.textContent = visible ? "hide SAVE" : "show SAVE";
		toggle.title = visible ? "SAVE DATA 배지를 숨깁니다." : "SAVE DATA 배지를 다시 표시합니다.";
		toggle.setAttribute("aria-expanded", visible ? "true" : "false");
	}

	function refreshBackendSaveDataDevBadge(options = {}) {
		if (!shouldCreateControls()) return { ok: true, version: VERSION, visible: false, skipped: true };
		const badge = attachBadgeToPreferredParent(createBadge());
		const toggle = attachBadgeToPreferredParent(createToggle());
		const policy = getPolicy();
		const status = getStatus();
		const state = currentAction ? `${currentAction}ing` : status.state || "unknown";
		const kind = getStateKind(status.state || state, status.ok);
		const visible = shouldShowBadgeByDefault();
		const updatedAt = formatClockNow();
		const statusUpdatedAt = formatClockFromIso(status.updatedAt);
		const mode = policy.mode || status.mode || "unknown";
		const slot = status.slotKey || policy.defaultSlotKey || "default";

		badge.dataset.kind = kind;
		badge.dataset.state = state;
		badge.dataset.mode = mode;
		badge.dataset.hidden = visible ? "false" : "true";
		badge.dataset.flash = options.flash ? "true" : "false";
		badge.title = [
			`state: ${state}`,
			`mode: ${mode}`,
			`slot: ${slot}`,
			`statusUpdated: ${statusUpdatedAt}`,
			status.error ? `error: ${status.error}` : null,
		].filter(Boolean).join("\n");

		const stateEl = badge.querySelector("[data-sd-state]");
		const modeEl = badge.querySelector("[data-sd-mode]");
		const slotEl = badge.querySelector("[data-sd-slot]");
		const summaryEl = badge.querySelector("[data-sd-summary]");
		const loadEl = badge.querySelector("[data-sd-load]");
		const updatedEl = badge.querySelector("[data-sd-updated]");

		if (stateEl) stateEl.textContent = state;
		if (modeEl) modeEl.textContent = `mode: ${mode}`;
		if (slotEl) slotEl.textContent = `slot: ${slot}`;
		if (summaryEl) summaryEl.textContent = summarizeSave(status);
		if (loadEl) loadEl.textContent = summarizeLoadResult();
		if (updatedEl) updatedEl.textContent = `updated: ${updatedAt}${statusUpdatedAt !== "-" ? ` · saved: ${statusUpdatedAt}` : ""}`;

		const wrapper = document.getElementById(WRAPPER_ID);
		if (wrapper) {
			wrapper.dataset.badgeVisible = visible ? "true" : "false";
			wrapper.dataset.mode = mode;
		}
		updateActionButtonStates(badge, mode);
		updateToggleState(toggle, visible);

		if (options.flash) {
			window.setTimeout(() => {
				const current = document.getElementById(BADGE_ID);
				if (current) current.dataset.flash = "false";
			}, 650);
		}

		return { ok: true, version: VERSION, visible, kind, state, policy, status, lastLoadResult, updatedAt };
	}

	function showBackendSaveDataDevBadge() {
		writeStorage(STORAGE_KEY, "1");
		return refreshBackendSaveDataDevBadge({ flash: true });
	}

	function hideBackendSaveDataDevBadge() {
		writeStorage(STORAGE_KEY, "0");
		return refreshBackendSaveDataDevBadge();
	}

	function toggleBackendSaveDataDevBadge() {
		const badge = document.getElementById(BADGE_ID);
		const currentlyVisible = readStorage(STORAGE_KEY) !== "0" && (!badge || badge.dataset.hidden !== "true");
		return currentlyVisible ? hideBackendSaveDataDevBadge() : showBackendSaveDataDevBadge();
	}

	function startBadgeAutoRefresh() {
		if (!shouldCreateControls()) return;
		const refresh = () => {
			try {
				refreshBackendSaveDataDevBadge();
			} catch (error) {
				console.warn("[Upgrade RPG] save-data dev badge refresh failed", error);
			}
		};
		if (document.readyState === "loading") {
			document.addEventListener("DOMContentLoaded", refresh, { once: true });
		} else {
			refresh();
		}
		window.addEventListener("upgrade-rpg:backend-save-sync-status", () => refreshBackendSaveDataDevBadge({ flash: true }));
		window.addEventListener("upgrade-rpg:backend-save-sync-mode", () => refreshBackendSaveDataDevBadge({ flash: true }));
		window.setTimeout(refresh, 500);
		window.setTimeout(refresh, 1500);
		window.setTimeout(refresh, 3000);
		window.setInterval(refresh, 5000);
	}

	window.RpgBackendSaveDataDevBadge = {
		VERSION,
		BADGE_ID,
		TOGGLE_ID,
		WRAPPER_ID,
		STORAGE_KEY,
		refreshBackendSaveDataDevBadge,
		showBackendSaveDataDevBadge,
		hideBackendSaveDataDevBadge,
		toggleBackendSaveDataDevBadge,
	};
	window.refreshBackendSaveDataDevBadge = refreshBackendSaveDataDevBadge;
	window.showBackendSaveDataDevBadge = showBackendSaveDataDevBadge;
	window.hideBackendSaveDataDevBadge = hideBackendSaveDataDevBadge;
	window.toggleBackendSaveDataDevBadge = toggleBackendSaveDataDevBadge;

	startBadgeAutoRefresh();
})();

(function () {
	"use strict";

	const BADGE_ID = "backend-master-data-dev-badge";
	const TOGGLE_ID = "backend-master-data-dev-badge-toggle";
	const WRAPPER_ID = "backend-master-data-dev-badge-wrap";
	const STYLE_ID = "backend-master-data-dev-badge-style";
	const STORAGE_KEY = "upgradeRpgShowBackendMasterDataDevBadge";
	const VERSION = "v104.backend-master-data-dev-badge-hud-top-align";

	function isLocalDevelopment() {
		try {
			const protocol = window.location && window.location.protocol;
			const host = window.location && window.location.hostname;
			return protocol === "file:" || host === "localhost" || host === "127.0.0.1";
		} catch (error) {
			return true;
		}
	}

	function shouldCreateControls() {
		const stored = readStorage(STORAGE_KEY);
		return isLocalDevelopment() || stored === "1" || stored === "0";
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
			// localStorage 사용이 막힌 환경에서는 현재 표시 상태만 사용합니다.
		}
	}

	function shouldShowBadgeByDefault() {
		const stored = readStorage(STORAGE_KEY);
		if (stored === "1") return true;
		if (stored === "0") return false;
		return isLocalDevelopment();
	}

	function getPolicy() {
		if (window.RpgBackendMasterDataBootPolicy && typeof window.RpgBackendMasterDataBootPolicy.getBackendMasterDataBootPolicy === "function") {
			return window.RpgBackendMasterDataBootPolicy.getBackendMasterDataBootPolicy();
		}
		if (typeof window.getBackendMasterDataBootPolicy === "function") return window.getBackendMasterDataBootPolicy();
		return {
			mode: "unknown",
			includeAssets: false,
			timeoutMs: null,
			shouldTryBackend: false,
			required: false,
			fallbackToStaticJs: true,
		};
	}

	function getRuntimeStatus() {
		if (window.RpgBackendMasterDataRuntime && typeof window.RpgBackendMasterDataRuntime.getBackendMasterDataRuntimeStatus === "function") {
			return window.RpgBackendMasterDataRuntime.getBackendMasterDataRuntimeStatus();
		}
		if (typeof window.getBackendMasterDataRuntimeStatus === "function") return window.getBackendMasterDataRuntimeStatus();
		return { state: "unknown" };
	}

	function getStateKind(state) {
		const value = String(state || "");
		if (value === "applied" || value === "applied_with_missing_targets") return "ok";
		if (value === "loading" || value === "backend_auto_waiting_for_page_load") return "loading";
		if (value === "static_js_mode") return "static";
		if (value.indexOf("failed") >= 0) return "fallback";
		return "unknown";
	}

	function summarizeCounts(status) {
		const counts = status && status.counts ? status.counts : {};
		const parts = [];
		if (counts.bossList !== undefined || counts.normalBosses !== undefined) parts.push(`B:${counts.bossList ?? counts.normalBosses}`);
		if (counts.specialBossList !== undefined || counts.specialBosses !== undefined) parts.push(`S:${counts.specialBossList ?? counts.specialBosses}`);
		if (counts.fieldZones !== undefined) parts.push(`F:${counts.fieldZones}`);
		if (counts.itemTemplates !== undefined) parts.push(`I:${counts.itemTemplates}`);
		return parts.join(" · ");
	}

	function formatClock(date) {
		try {
			return date.toLocaleTimeString("ko-KR", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });
		} catch (error) {
			return date.toTimeString().slice(0, 8);
		}
	}

	function ensureStyle() {
		if (document.getElementById(STYLE_ID)) return;
		const style = document.createElement("style");
		style.id = STYLE_ID;
		style.textContent = `
#${WRAPPER_ID} {
	position: fixed;
	right: 238px;
	bottom: 170px;
	z-index: 99999;
	width: 205px;
	box-sizing: border-box;
	pointer-events: none;
}
#bottom-hud > #${WRAPPER_ID} {
	position: absolute;
	left: auto;
	right: 252px;
	top: auto;
	bottom: calc(100% + 10px);
	transform: none;
	width: 205px;
	z-index: 99999;
}
#${BADGE_ID} {
	position: relative;
	z-index: 1;
	width: 100%;
	min-width: 0;
	max-width: 100%;
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
	min-width: 72px;
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
#${WRAPPER_ID}[data-badge-visible="false"] { width: 84px; }
#bottom-hud > #${WRAPPER_ID}[data-badge-visible="false"] { right: 112px; width: 84px; }
#${WRAPPER_ID}[data-badge-visible="false"] #${TOGGLE_ID} {
	position: relative;
	left: 50%;
	top: auto;
	transform: translateX(-50%);
}
#${TOGGLE_ID}[data-hidden="true"] { display: none; }
#${BADGE_ID} .md-badge-row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: 8px;
}
#${BADGE_ID} .md-badge-title { font-weight: 800; font-size: 11px; white-space: nowrap; }
#${BADGE_ID} .md-badge-pill {
	display: inline-flex;
	align-items: center;
	gap: 4px;
	max-width: 92px;
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
#${BADGE_ID} .md-badge-dot { width: 6px; height: 6px; min-width: 6px; border-radius: 999px; background: #94a3b8; }
#${BADGE_ID}[data-kind="ok"] .md-badge-dot { background: #22c55e; }
#${BADGE_ID}[data-kind="loading"] .md-badge-dot { background: #38bdf8; }
#${BADGE_ID}[data-kind="static"] .md-badge-dot { background: #f59e0b; }
#${BADGE_ID}[data-kind="fallback"] .md-badge-dot { background: #ef4444; }
#${BADGE_ID} .md-badge-meta { margin-top: 5px; display: flex; flex-wrap: wrap; gap: 4px 8px; color: #cbd5e1; }
#${BADGE_ID} .md-badge-counts { margin-top: 4px; color: #94a3b8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
#${BADGE_ID} .md-badge-updated { margin-top: 3px; color: #64748b; font-size: 10px; }
#${BADGE_ID} .md-badge-actions {
	margin-top: 6px;
	display: grid;
	grid-template-columns: repeat(3, minmax(0, 1fr));
	gap: 5px;
}
#${BADGE_ID} button {
	border: 1px solid rgba(255, 255, 255, 0.16);
	border-radius: 6px;
	background: rgba(255, 255, 255, 0.08);
	color: #f8fafc;
	font: inherit;
	font-size: 10px;
	padding: 4px 6px;
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
#${BADGE_ID}[data-flash="true"] {
	box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(56, 189, 248, 0.45);
}
@media (max-width: 1280px) {
	#${WRAPPER_ID}, #bottom-hud > #${WRAPPER_ID} { width: 192px; }
	#bottom-hud > #${WRAPPER_ID} { right: 228px; bottom: calc(100% + 8px); }
	#bottom-hud > #${WRAPPER_ID}[data-badge-visible="false"] { right: 108px; width: 84px; }
	#${BADGE_ID} { font-size: 10px; padding: 13px 8px 8px; }
}
@media (max-width: 980px) {
	#${WRAPPER_ID}, #bottom-hud > #${WRAPPER_ID} { width: 176px; }
	#bottom-hud > #${WRAPPER_ID} { right: 186px; bottom: calc(100% + 8px); }
	#bottom-hud > #${WRAPPER_ID}[data-badge-visible="false"] { right: 100px; width: 80px; }
}
@media (max-width: 640px) {
	#${WRAPPER_ID}, #bottom-hud > #${WRAPPER_ID} { width: 168px; }
	#bottom-hud > #${WRAPPER_ID} { right: 176px; bottom: calc(100% + 6px); }
	#bottom-hud > #${WRAPPER_ID}[data-badge-visible="false"] { right: 96px; width: 78px; }
	#${BADGE_ID} { font-size: 10px; padding: 13px 8px 7px; }
}
`;
		document.head.appendChild(style);
	}

	function createToggle() {
		ensureStyle();
		let toggle = document.getElementById(TOGGLE_ID);
		if (toggle) return toggle;
		toggle = document.createElement("button");
		toggle.id = TOGGLE_ID;
		toggle.type = "button";
		toggle.setAttribute("aria-controls", BADGE_ID);
		toggle.addEventListener("click", () => toggleBackendMasterDataDevBadge());
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
			<div class="md-badge-row">
				<div class="md-badge-title">MASTER DATA</div>
				<div class="md-badge-pill"><span class="md-badge-dot"></span><span data-md-state>unknown</span></div>
			</div>
			<div class="md-badge-meta">
				<span data-md-mode>mode: unknown</span>
				<span data-md-assets>assets: off</span>
			</div>
			<div class="md-badge-counts" data-md-counts>counts: -</div>
			<div class="md-badge-updated" data-md-updated>updated: -</div>
			<div class="md-badge-actions">
				<button type="button" data-md-action="refresh" title="현재 런타임 상태와 개수만 다시 읽어서 이 배지 표시를 갱신합니다. 게임 데이터를 다시 받지는 않습니다.">refresh</button>
				<button type="button" data-md-action="auto" title="백엔드 master-data 자동 시도 모드로 바꾸고 새로고침합니다.">auto</button>
				<button type="button" data-md-action="static" title="기존 JS 데이터만 쓰는 모드로 바꾸고 새로고침합니다.">static</button>
			</div>
		`;
		badge.addEventListener("click", handleBadgeClick);
		attachBadgeToPreferredParent(badge);
		return badge;
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

	function handleBadgeClick(event) {
		const button = event.target && event.target.closest ? event.target.closest("button[data-md-action]") : null;
		if (!button) return;
		const action = button.getAttribute("data-md-action");
		if (action === "refresh") {
			refreshBackendMasterDataDevBadge({ flash: true });
		} else if (action === "auto" && typeof window.useAutoBackendMasterDataMode === "function") {
			window.useAutoBackendMasterDataMode();
		} else if (action === "static" && typeof window.useStaticMasterDataMode === "function") {
			window.useStaticMasterDataMode();
		}
	}

	function updateActionButtonStates(badge, mode) {
		if (!badge) return;
		const autoButton = badge.querySelector('button[data-md-action="auto"]');
		const staticButton = badge.querySelector('button[data-md-action="static"]');
		if (autoButton) autoButton.dataset.active = mode === "auto" ? "true" : "false";
		if (staticButton) staticButton.dataset.active = mode === "static" ? "true" : "false";
	}

	function updateToggleState(toggle, visible) {
		if (!toggle) return;
		toggle.dataset.hidden = shouldCreateControls() ? "false" : "true";
		toggle.dataset.badgeVisible = visible ? "true" : "false";
		toggle.textContent = visible ? "hide MD" : "show MD";
		toggle.title = visible ? "MASTER DATA 배지를 숨깁니다." : "MASTER DATA 배지를 다시 표시합니다.";
		toggle.setAttribute("aria-expanded", visible ? "true" : "false");
	}

	function refreshBackendMasterDataDevBadge(options = {}) {
		if (!shouldCreateControls()) return { ok: true, version: VERSION, visible: false, skipped: true };
		const badge = attachBadgeToPreferredParent(createBadge());
		const toggle = attachBadgeToPreferredParent(createToggle());
		const policy = getPolicy();
		const status = getRuntimeStatus();
		const state = status.state || "unknown";
		const kind = getStateKind(state);
		const counts = summarizeCounts(status);
		const visible = shouldShowBadgeByDefault();
		const updatedAt = formatClock(new Date());

		badge.dataset.kind = kind;
		badge.dataset.state = state;
		badge.dataset.mode = policy.mode || "unknown";
		badge.dataset.hidden = visible ? "false" : "true";
		badge.dataset.flash = options.flash ? "true" : "false";
		badge.title = [
			`state: ${state}`,
			`mode: ${policy.mode || "unknown"}`,
			`includeAssets: ${!!policy.includeAssets}`,
			`timeoutMs: ${policy.timeoutMs || "-"}`,
			`updated: ${updatedAt}`,
			status.errorMessage ? `error: ${status.errorMessage}` : null,
		].filter(Boolean).join("\n");

		const stateEl = badge.querySelector("[data-md-state]");
		const modeEl = badge.querySelector("[data-md-mode]");
		const assetsEl = badge.querySelector("[data-md-assets]");
		const countsEl = badge.querySelector("[data-md-counts]");
		const updatedEl = badge.querySelector("[data-md-updated]");
		if (stateEl) stateEl.textContent = state;
		if (modeEl) modeEl.textContent = `mode: ${policy.mode || "unknown"}`;
		if (assetsEl) assetsEl.textContent = `assets: ${policy.includeAssets ? "on" : "off"}`;
		if (countsEl) countsEl.textContent = counts ? `counts: ${counts}` : "counts: -";
		if (updatedEl) updatedEl.textContent = `updated: ${updatedAt}`;
		const wrapper = document.getElementById(WRAPPER_ID);
		if (wrapper) {
			wrapper.dataset.badgeVisible = visible ? "true" : "false";
			wrapper.dataset.mode = policy.mode || "unknown";
		}
		updateActionButtonStates(badge, policy.mode || "unknown");
		updateToggleState(toggle, visible);

		if (options.flash) {
			window.setTimeout(() => {
				const current = document.getElementById(BADGE_ID);
				if (current) current.dataset.flash = "false";
			}, 650);
		}

		return {
			ok: true,
			version: VERSION,
			visible,
			kind,
			state,
			policy,
			status,
			updatedAt,
		};
	}

	function showBackendMasterDataDevBadge() {
		writeStorage(STORAGE_KEY, "1");
		return refreshBackendMasterDataDevBadge({ flash: true });
	}

	function hideBackendMasterDataDevBadge() {
		writeStorage(STORAGE_KEY, "0");
		return refreshBackendMasterDataDevBadge();
	}

	function toggleBackendMasterDataDevBadge() {
		const badge = document.getElementById(BADGE_ID);
		const currentlyVisible = readStorage(STORAGE_KEY) !== "0" && (!badge || badge.dataset.hidden !== "true");
		return currentlyVisible ? hideBackendMasterDataDevBadge() : showBackendMasterDataDevBadge();
	}

	function startBadgeAutoRefresh() {
		if (!shouldCreateControls()) return;
		const refresh = () => {
			try {
				refreshBackendMasterDataDevBadge();
			} catch (error) {
				console.warn("[Upgrade RPG] master-data dev badge refresh failed", error);
			}
		};
		if (document.readyState === "loading") {
			document.addEventListener("DOMContentLoaded", refresh, { once: true });
		} else {
			refresh();
		}
		window.setTimeout(refresh, 500);
		window.setTimeout(refresh, 1500);
		window.setTimeout(refresh, 3000);
		window.setInterval(refresh, 5000);
	}

	window.RpgBackendMasterDataDevBadge = {
		VERSION,
		BADGE_ID,
		TOGGLE_ID,
		WRAPPER_ID,
		STORAGE_KEY,
		isLocalDevelopment,
		refreshBackendMasterDataDevBadge,
		attachBadgeToPreferredParent,
		showBackendMasterDataDevBadge,
		hideBackendMasterDataDevBadge,
		toggleBackendMasterDataDevBadge,
	};

	window.refreshBackendMasterDataDevBadge = refreshBackendMasterDataDevBadge;
	window.showBackendMasterDataDevBadge = showBackendMasterDataDevBadge;
	window.hideBackendMasterDataDevBadge = hideBackendMasterDataDevBadge;
	window.toggleBackendMasterDataDevBadge = toggleBackendMasterDataDevBadge;

	startBadgeAutoRefresh();
})();

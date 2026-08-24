(function () {
	"use strict";

	const VERSION = "v378.game-dev-ui-admin-visibility";
	const DEV_UI_SELECTOR = "[data-admin-dev-ui]";

	function isLocalDevelopment() {
		try {
			const protocol = window.location && window.location.protocol;
			const host = window.location && window.location.hostname;
			return protocol === "file:" || host === "localhost" || host === "127.0.0.1";
		} catch (error) {
			return false;
		}
	}

	function getCurrentUser() {
		try {
			if (!window.RpgAuthSession || typeof window.RpgAuthSession.getCurrentUser !== "function") return null;
			return window.RpgAuthSession.getCurrentUser();
		} catch (error) {
			return null;
		}
	}

	function canUseGameDevUi() {
		if (isLocalDevelopment()) return true;
		const user = getCurrentUser();
		return !!(user && user.isAdmin === true);
	}

	function setDevUiAccess(element, allowed) {
		if (!element) return;
		element.hidden = !allowed;
		element.setAttribute("aria-hidden", allowed ? "false" : "true");
		element.toggleAttribute("inert", !allowed);
		element.inert = !allowed;
		element.dataset.adminDevUiAccess = allowed ? "allowed" : "denied";
		if (!allowed && element.id === "test-item-modal") element.style.display = "none";
	}

	function syncGameDevUiVisibility() {
		const allowed = canUseGameDevUi();
		const elements = Array.from(document.querySelectorAll(DEV_UI_SELECTOR));
		elements.forEach((element) => setDevUiAccess(element, allowed));
		return { ok: true, version: VERSION, allowed, count: elements.length };
	}

	function blockUnauthorizedDevUiClick(event) {
		const target = event.target && event.target.closest ? event.target.closest(DEV_UI_SELECTOR) : null;
		if (!target || canUseGameDevUi()) return;
		event.preventDefault();
		event.stopImmediatePropagation();
		setDevUiAccess(target, false);
	}

	window.RpgGameDevUiAccess = {
		VERSION,
		DEV_UI_SELECTOR,
		isLocalDevelopment,
		canUseGameDevUi,
		syncGameDevUiVisibility,
	};
	window.canUseGameDevUi = canUseGameDevUi;
	window.syncGameDevUiVisibility = syncGameDevUiVisibility;

	document.addEventListener("click", blockUnauthorizedDevUiClick, true);
	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", syncGameDevUiVisibility, { once: true });
	} else {
		syncGameDevUiVisibility();
	}
	window.addEventListener("upgrade-rpg:account-game-ready", syncGameDevUiVisibility);
})();

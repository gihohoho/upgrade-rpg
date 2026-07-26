(function (window) {
	"use strict";

	const VERSION = "v348.frontend-static-runtime-config";
	const PRODUCTION_API_BASE_URL = "https://upgrade-rpg-api.onrender.com/api/v1";
	const LOCAL_HOSTS = new Set(["", "localhost", "127.0.0.1", "::1"]);
	const hostname = String(window.location && window.location.hostname || "").toLowerCase();
	const isLocal = LOCAL_HOSTS.has(hostname);

	if (!isLocal) {
		window.__UPGRADE_RPG_API_BASE_URL__ = PRODUCTION_API_BASE_URL;
	}

	window.RpgRuntimeConfig = Object.freeze({
		version: VERSION,
		isLocal,
		apiBaseUrl: isLocal ? null : PRODUCTION_API_BASE_URL,
	});
})(window);

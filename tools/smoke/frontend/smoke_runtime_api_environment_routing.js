const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..", "..", "..");
const clientSource = fs.readFileSync(path.join(root, "src", "api", "game-api-client.js"), "utf8");
const productionApi = "https://upgrade-rpg-api.onrender.com/api/v1";
const localApi = "http://127.0.0.1:8000/api/v1";

for (const entrypoint of ["index.html", "admin.html"]) {
	const html = fs.readFileSync(path.join(root, entrypoint), "utf8");
	assert.match(html, /src="src\/api\/game-api-client\.js\?v=378"/, `${entrypoint} must reload the environment-aware API client`);
}
assert.match(
	fs.readFileSync(path.join(root, "admin.html"), "utf8"),
	/src="src\/api\/admin\/admin-settings-helpers\.js\?v=378"/,
	"admin.html must reload the environment-aware reset helper",
);

function loadClient({ runtimeConfig, storedApiBaseUrl, windowApiBaseUrl }) {
	const localValues = new Map();
	if (storedApiBaseUrl) localValues.set("upgradeRpgApiBaseUrl", storedApiBaseUrl);
	const window = {
		RpgRuntimeConfig: runtimeConfig,
		__UPGRADE_RPG_API_BASE_URL__: windowApiBaseUrl,
		localStorage: {
			getItem(key) { return localValues.has(key) ? localValues.get(key) : null; },
			setItem(key, value) { localValues.set(key, String(value)); },
		},
		sessionStorage: {
			getItem() { return null; },
			setItem() {},
			removeItem() {},
		},
		setTimeout,
		clearTimeout,
	};
	const context = vm.createContext({ window, URL, fetch: async () => { throw new Error("not used"); }, AbortController });
	vm.runInContext(clientSource, context, { filename: "game-api-client.js" });
	return context.window.RpgGameApi;
}

{
	const api = loadClient({
		runtimeConfig: { isLocal: true, apiBaseUrl: null },
		storedApiBaseUrl: productionApi,
	});
	assert.equal(api.getApiBaseUrl(), localApi, "local page must ignore a stale production URL from localStorage");
	assert.throws(
		() => api.setApiBaseUrl(productionApi),
		/localhost|127\.0\.0\.1/,
		"local page must reject a production API override",
	);
}

for (const staleLocalApi of [
	"http://localhost:8001/api/v1",
	"http://127.0.0.1:8001/api/v1",
	"http://[::1]:8001/api/v1",
]) {
	const api = loadClient({
		runtimeConfig: { isLocal: true, apiBaseUrl: null },
		storedApiBaseUrl: staleLocalApi,
	});
	assert.equal(api.getApiBaseUrl(), localApi, "local page must ignore stale loopback ports and stay on the running API");
	assert.throws(
		() => api.setApiBaseUrl(staleLocalApi),
		/127\.0\.0\.1:8000/,
		"local page must reject a non-default loopback API override",
	);
}

{
	const staleLocalApi = "http://localhost:8000/api/v1";
	const api = loadClient({
		runtimeConfig: { isLocal: false, apiBaseUrl: productionApi },
		storedApiBaseUrl: staleLocalApi,
		windowApiBaseUrl: staleLocalApi,
	});
	assert.equal(api.getApiBaseUrl(), productionApi, "production page must stay pinned to its deployed API");
	assert.equal(api.getEnvironmentDefaultApiBaseUrl(), productionApi, "production reset default must stay on its deployed API");
	assert.equal(api.setApiBaseUrl(api.getEnvironmentDefaultApiBaseUrl()), productionApi, "production default reset must not throw");
	assert.throws(
		() => api.setApiBaseUrl(staleLocalApi),
		/배포 설정값/,
		"production page must reject a local API override",
	);
}

console.log("runtime API environment routing smoke passed");
console.log("- local stale production override ignored: yes");
console.log("- stale local loopback ports ignored: yes");
console.log("- production API remains pinned: yes");

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const projectRoot = path.resolve(__dirname, "..", "..", "..");
const clientPath = path.join(projectRoot, "src", "api", "game-api-client.js");
const bridgePath = path.join(projectRoot, "src", "api", "master-data-bridge.js");
const indexPath = path.join(projectRoot, "index.html");

function assert(condition, message) {
	if (!condition) {
		console.error(message);
		process.exit(1);
	}
}

assert(fs.existsSync(clientPath), "src/api/game-api-client.js 파일이 없습니다.");
assert(fs.existsSync(bridgePath), "src/api/master-data-bridge.js 파일이 없습니다.");

const indexHtml = fs.readFileSync(indexPath, "utf8");
const clientTagIndex = indexHtml.indexOf('src="src/api/game-api-client.js"');
const bridgeTagIndex = indexHtml.indexOf('src="src/api/master-data-bridge.js"');
const mainTagIndex = indexHtml.indexOf('src="src/app/main.js"');

assert(clientTagIndex >= 0, "index.html에 game-api-client.js script 태그가 없습니다.");
assert(bridgeTagIndex >= 0, "index.html에 master-data-bridge.js script 태그가 없습니다.");
assert(clientTagIndex < bridgeTagIndex, "game-api-client.js는 master-data-bridge.js보다 먼저 로드되어야 합니다.");
assert(bridgeTagIndex < mainTagIndex, "master-data-bridge.js는 main.js보다 먼저 로드되어야 합니다.");

const fakePayload = {
	characters: [{}],
	skills: Array.from({ length: 8 }, () => ({})),
	characterSkills: Array.from({ length: 8 }, () => ({})),
	skillLevels: Array.from({ length: 64 }, () => ({})),
	itemTemplates: Array.from({ length: 245 }, () => ({})),
	bosses: Array.from({ length: 45 }, () => ({})),
	fieldZones: Array.from({ length: 40 }, () => ({})),
	dropTables: Array.from({ length: 45 }, () => ({})),
	dropTableItems: Array.from({ length: 245 }, () => ({})),
	enhancementGroups: Array.from({ length: 2 }, () => ({})),
	enhancementLevels: Array.from({ length: 26 }, () => ({})),
	assetPolicy: { mode: "metadata-only" },
	counts: {
		characters: 1,
		skills: 8,
		characterSkills: 8,
		skillLevels: 64,
		itemTemplates: 245,
		bosses: 45,
		fieldZones: 40,
		dropTables: 45,
		dropTableItems: 245,
		enhancementGroups: 2,
		enhancementLevels: 26,
	},
};

const sandbox = {
	console,
	URL,
	Date,
	window: {},
	fetch: async (url) => ({
		ok: true,
		status: 200,
		json: async () => ({
			ok: true,
			responseVersion: "game-api-response.v1",
			type: "game.master_data",
			payload: fakePayload,
			data: { status: "loaded" },
			meta: { includeAssets: String(url).includes("includeAssets=true") },
			error: null,
		}),
	}),
};
sandbox.window = sandbox;
sandbox.localStorage = {
	items: {},
	getItem(key) {
		return this.items[key] || null;
	},
	setItem(key, value) {
		this.items[key] = String(value);
	},
};

vm.createContext(sandbox);
vm.runInContext(fs.readFileSync(clientPath, "utf8"), sandbox, { filename: clientPath });
vm.runInContext(fs.readFileSync(bridgePath, "utf8"), sandbox, { filename: bridgePath });

assert(sandbox.RpgGameApi, "RpgGameApi 전역 객체가 생성되지 않았습니다.");
assert(sandbox.RpgMasterDataBridge, "RpgMasterDataBridge 전역 객체가 생성되지 않았습니다.");
assert(typeof sandbox.checkBackendMasterData === "function", "checkBackendMasterData 콘솔 함수가 없습니다.");
assert(typeof sandbox.loadBackendMasterData === "function", "loadBackendMasterData 콘솔 함수가 없습니다.");

(async () => {
	const result = await sandbox.checkBackendMasterData();
	assert(result.ok === true, "기본 master-data 브릿지 검증에 실패했습니다.");

	const includeAssetResult = await sandbox.checkBackendMasterData({ includeAssets: true });
	assert(includeAssetResult.ok === true, "includeAssets master-data 브릿지 검증에 실패했습니다.");

	console.log("frontend master-data bridge smoke test passed");
})();

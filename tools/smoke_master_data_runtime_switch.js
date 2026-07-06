#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const runtimePath = path.join(root, "src", "api", "master-data-runtime-switch.js");
const indexPath = path.join(root, "index.html");
const adapterPath = path.join(root, "src", "api", "master-data-adapter.js");

function fail(message) {
	console.error(message);
	process.exit(1);
}

if (!fs.existsSync(runtimePath)) fail("src/api/master-data-runtime-switch.js 파일이 없습니다.");
if (!fs.existsSync(adapterPath)) fail("src/api/master-data-adapter.js 파일이 없습니다.");

const runtime = fs.readFileSync(runtimePath, "utf8");
const index = fs.readFileSync(indexPath, "utf8");

[
	"upgradeRpgUseBackendMasterData",
	"enableBackendMasterDataMode",
	"disableBackendMasterDataMode",
	"checkBackendMasterDataRuntimeMode",
	"applyBackendMasterDataBeforeGameStart",
	"replaceObject(characterMasterData",
	"replaceObject(skillMasterData",
	"replaceArray(bossList",
	"replaceArray(specialBossList",
	"replaceArray(zones",
	"failed_fallback_to_static_js",
].forEach((needle) => {
	if (!runtime.includes(needle)) fail(`runtime switch에 필요한 코드가 없습니다: ${needle}`);
});

const requiredOrder = [
	"src/api/game-api-client.js",
	"src/api/master-data-bridge.js",
	"src/api/master-data-adapter.js",
	"src/data/skills.js",
	"src/data/bosses.js",
	"src/data/zones.js",
	"src/app/main.js",
	"src/api/master-data-runtime-switch.js",
];
let previousIndex = -1;
requiredOrder.forEach((needle) => {
	const currentIndex = index.indexOf(needle);
	if (currentIndex === -1) fail(`index.html에 script가 없습니다: ${needle}`);
	if (currentIndex <= previousIndex) fail(`index.html script 로딩 순서가 올바르지 않습니다: ${needle}`);
	previousIndex = currentIndex;
});

console.log("master-data runtime switch smoke test passed");

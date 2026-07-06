const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const checklistPath = path.join(root, "src", "api", "master-data-browser-checklist.js");
const indexPath = path.join(root, "index.html");
const docsPath = path.join(root, "docs", "MASTER_DATA_BROWSER_CHECKLIST.md");

function assert(condition, message) {
	if (!condition) {
		console.error(message);
		process.exit(1);
	}
}

assert(fs.existsSync(checklistPath), "src/api/master-data-browser-checklist.js 파일이 없습니다.");
assert(fs.existsSync(docsPath), "docs/MASTER_DATA_BROWSER_CHECKLIST.md 문서가 없습니다.");

const source = fs.readFileSync(checklistPath, "utf8");
const index = fs.readFileSync(indexPath, "utf8");

[
	"runBackendMasterDataBrowserChecklist",
	"assertBackendMasterDataBrowserChecklist",
	"printBackendMasterDataManualChecklist",
	"RpgBackendMasterDataBrowserChecklist",
	"checkBackendMasterDataRuntimeIntegrity",
	"renderBossZone",
	"renderSpecialBossZone",
	"renderFieldZone",
	"openTestItemModal",
	"openTestSpecialItemModal",
	"lightsabreProcRate",
].forEach((token) => {
	assert(source.includes(token), `browser checklist source에 ${token} 토큰이 없습니다.`);
});

[
	"src/api/master-data-runtime-switch.js",
	"src/api/master-data-runtime-validator.js",
	"src/api/master-data-browser-checklist.js",
].forEach((token) => {
	assert(index.includes(token), `index.html에 ${token} 로딩이 없습니다.`);
});

const switchIndex = index.indexOf("src/api/master-data-runtime-switch.js");
const validatorIndex = index.indexOf("src/api/master-data-runtime-validator.js");
const checklistIndex = index.indexOf("src/api/master-data-browser-checklist.js");
assert(switchIndex < validatorIndex, "runtime switch는 runtime validator보다 먼저 로드되어야 합니다.");
assert(validatorIndex < checklistIndex, "runtime validator는 browser checklist보다 먼저 로드되어야 합니다.");

console.log("master-data browser checklist smoke test passed");

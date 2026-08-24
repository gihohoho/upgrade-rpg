const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");
const badgePath = path.join(root, "src", "api", "master-data-dev-badge.js");
const indexPath = path.join(root, "index.html");

function fail(message) {
	console.error(message);
	process.exit(1);
}

if (!fs.existsSync(badgePath)) fail("src/api/master-data-dev-badge.js 파일이 없습니다.");
if (!fs.existsSync(indexPath)) fail("index.html 파일이 없습니다.");

const badgeSource = fs.readFileSync(badgePath, "utf8");
const indexSource = fs.readFileSync(indexPath, "utf8");

const requiredSnippets = [
	"RpgBackendMasterDataDevBadge",
	"refreshBackendMasterDataDevBadge",
	"showBackendMasterDataDevBadge",
	"hideBackendMasterDataDevBadge",
	"toggleBackendMasterDataDevBadge",
	"backend-master-data-dev-badge",
	"upgradeRpgShowBackendMasterDataDevBadge",
	"getBackendMasterDataRuntimeStatus",
	"getBackendMasterDataBootPolicy",
	"v378.backend-master-data-dev-badge-admin-visibility",
	"RpgGameDevUiAccess",
	"canUseGameDevUi",
	"removeControls",
	"attachBadgeToPreferredParent",
	"bottom-hud",
	"backend-master-data-dev-badge-toggle",
	"backend-master-data-dev-badge-wrap",
	"WRAPPER_ID",
	"TOGGLE_ID",
	"data-active",
	"updated:",
	"hide MD",
	"show MD",
	"shouldCreateControls",
	"bottom: calc(100% + 10px)",
	"right: 238px",
	"position: fixed",
];

requiredSnippets.forEach((snippet) => {
	if (!badgeSource.includes(snippet)) fail(`master-data dev badge 구현에 ${snippet} 항목이 없습니다.`);
});

if (!indexSource.includes('src/api/master-data-dev-badge.js')) {
	fail("index.html에 master-data-dev-badge.js 로딩이 없습니다.");
}

const runtimeSwitchIndex = indexSource.indexOf('src/api/master-data-runtime-switch.js');
const badgeIndex = indexSource.indexOf('src/api/master-data-dev-badge.js');
if (runtimeSwitchIndex < 0 || badgeIndex < 0 || badgeIndex < runtimeSwitchIndex) {
	fail("master-data-dev-badge.js는 master-data-runtime-switch.js 이후에 로드되어야 합니다.");
}

console.log("master-data dev badge smoke test passed");

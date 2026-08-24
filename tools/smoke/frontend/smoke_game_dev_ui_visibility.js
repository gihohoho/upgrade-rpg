const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..", "..", "..");

function read(relativePath) {
	return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function createElement(id) {
	const attributes = new Map();
	return {
		id,
		hidden: false,
		inert: false,
		dataset: {},
		style: { display: id === "test-item-modal" ? "block" : "" },
		setAttribute(name, value) { attributes.set(name, String(value)); },
		toggleAttribute(name, enabled) { if (enabled) attributes.set(name, ""); else attributes.delete(name); },
		getAttribute(name) { return attributes.get(name); },
	};
}

function testAccessPolicy(source) {
	let currentUser = { userId: 1, isAdmin: false };
	const elements = [createElement("test-panel"), createElement("test-item-modal")];
	const windowListeners = new Map();
	const context = {
		Array,
		document: {
			readyState: "complete",
			querySelectorAll(selector) {
				assert.equal(selector, "[data-admin-dev-ui]");
				return elements;
			},
			addEventListener() {},
		},
		window: {
			location: { protocol: "https:", hostname: "gihohoho-upgrade-rpg.onrender.com" },
			RpgAuthSession: { getCurrentUser: () => currentUser },
			addEventListener(name, handler) { windowListeners.set(name, handler); },
		},
	};
	vm.runInNewContext(source, context);

	assert.equal(context.window.RpgGameDevUiAccess.canUseGameDevUi(), false, "배포환경 일반 계정이 개발 UI 권한을 얻었습니다.");
	elements.forEach((element) => {
		assert.equal(element.hidden, true);
		assert.equal(element.inert, true);
		assert.equal(element.getAttribute("aria-hidden"), "true");
		assert.equal(element.dataset.adminDevUiAccess, "denied");
	});
	assert.equal(elements[1].style.display, "none", "권한이 사라진 뒤 테스트 모달이 닫히지 않았습니다.");

	currentUser = { userId: 2, isAdmin: true };
	windowListeners.get("upgrade-rpg:account-game-ready")();
	assert.equal(context.window.RpgGameDevUiAccess.canUseGameDevUi(), true, "배포환경 관리자 권한이 반영되지 않았습니다.");
	elements.forEach((element) => {
		assert.equal(element.hidden, false);
		assert.equal(element.inert, false);
		assert.equal(element.getAttribute("aria-hidden"), "false");
		assert.equal(element.dataset.adminDevUiAccess, "allowed");
	});

	currentUser = { userId: 3, isAdmin: false };
	context.window.location.hostname = "127.0.0.1";
	assert.equal(context.window.RpgGameDevUiAccess.canUseGameDevUi(), true, "로컬 개발환경의 테스트 UI가 차단되었습니다.");
}

function testStaticContracts() {
	const html = read("index.html");
	const css = read("src/styles/account.css");
	const renderSource = read("src/ui/render-ui.js");
	const masterBadge = read("src/api/master-data-dev-badge.js");
	const saveBadge = read("src/api/save-data-dev-badge.js");

	assert.match(html, /id="game-account-bar"[^>]+data-zone-visible="hidden"[^>]+aria-hidden="true"[^>]+hidden[^>]+inert/);
	assert.match(html, /id="test-panel"[^>]+data-admin-dev-ui="test-panel"[^>]+aria-hidden="true"[^>]+hidden[^>]+inert/);
	assert.match(html, /id="test-item-modal"[^>]+data-admin-dev-ui="test-item-modal"[^>]+aria-hidden="true"[^>]+hidden[^>]+inert/);
	assert.match(html, /game-dev-ui-access\.js\?v=378/);
	assert(html.indexOf("game-dev-ui-access.js?v=378") < html.indexOf("main.js?v=370"), "개발 UI access gate는 main.js보다 먼저 로드되어야 합니다.");
	assert.match(css, /\.game-account-bar\[data-zone-visible="hidden"\][\s\S]+display:\s*none\s*!important/);
	assert.match(css, /\[data-admin-dev-ui\]\[hidden\][\s\S]+display:\s*none\s*!important/);
	assert.match(renderSource, /function syncRenderedAccountBarTownVisibility\(\)[\s\S]+syncAccountBarTownVisibility\(currentZoneType\)[\s\S]+dataset\.zoneVisible = "hidden"/);

	[masterBadge, saveBadge].forEach((source) => {
		assert.match(source, /RpgGameDevUiAccess\.canUseGameDevUi\(\)/);
		assert.match(source, /function removeControls\(\)/);
		assert.doesNotMatch(source, /isLocalDevelopment\(\) \|\| stored === "1" \|\| stored === "0"/);
	});
}

const accessSource = read("src/ui/game-dev-ui-access.js");
testAccessPolicy(accessSource);
testStaticContracts();
console.log("game dev UI visibility smoke test passed");

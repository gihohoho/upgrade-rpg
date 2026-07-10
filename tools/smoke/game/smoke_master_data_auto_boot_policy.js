#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");
const requiredFiles = [
  "src/api/game-api-client.js",
  "src/api/master-data-boot-policy.js",
  "src/api/master-data-runtime-switch.js",
  "index.html",
];

for (const file of requiredFiles) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) {
    console.error(`필수 파일이 없습니다: ${file}`);
    process.exit(1);
  }
}

const bootPolicy = fs.readFileSync(path.join(root, "src/api/master-data-boot-policy.js"), "utf8");
const runtimeSwitch = fs.readFileSync(path.join(root, "src/api/master-data-runtime-switch.js"), "utf8");
const apiClient = fs.readFileSync(path.join(root, "src/api/game-api-client.js"), "utf8");
const indexHtml = fs.readFileSync(path.join(root, "index.html"), "utf8");

const requiredBootTokens = [
  "DEFAULT_BOOT_MODE = BOOT_MODES.AUTO",
  "DEFAULT_INCLUDE_ASSETS = false",
  "getBackendMasterDataBootPolicy",
  "useAutoBackendMasterDataMode",
  "useStaticMasterDataMode",
  "requireBackendMasterDataMode",
  "setBackendMasterDataIncludeAssets",
];

for (const token of requiredBootTokens) {
  if (!bootPolicy.includes(token)) {
    console.error(`boot policy에 필요한 토큰이 없습니다: ${token}`);
    process.exit(1);
  }
}

const requiredRuntimeTokens = [
  "getBootPolicy",
  "hydrateMissingAssetsFromStaticData",
  "failed_fallback_to_static_js",
  "backend_auto_waiting_for_page_load",
  "policy.includeAssets",
  "policy.timeoutMs",
];

for (const token of requiredRuntimeTokens) {
  if (!runtimeSwitch.includes(token)) {
    console.error(`runtime switch에 필요한 토큰이 없습니다: ${token}`);
    process.exit(1);
  }
}

const requiredApiTokens = ["AbortController", "timeoutMs", "DEFAULT_REQUEST_TIMEOUT_MS"];
for (const token of requiredApiTokens) {
  if (!apiClient.includes(token)) {
    console.error(`API client에 필요한 토큰이 없습니다: ${token}`);
    process.exit(1);
  }
}

const adapterIndex = indexHtml.indexOf('src/api/master-data-adapter.js');
const bootPolicyIndex = indexHtml.indexOf('src/api/master-data-boot-policy.js');
const skillsIndex = indexHtml.indexOf('src/data/skills.js');
const runtimeIndex = indexHtml.indexOf('src/api/master-data-runtime-switch.js');

if (!(adapterIndex >= 0 && bootPolicyIndex > adapterIndex && skillsIndex > bootPolicyIndex && runtimeIndex > skillsIndex)) {
  console.error("index.html의 master-data boot policy 로딩 순서가 올바르지 않습니다.");
  process.exit(1);
}

console.log("master-data auto boot policy smoke test passed");

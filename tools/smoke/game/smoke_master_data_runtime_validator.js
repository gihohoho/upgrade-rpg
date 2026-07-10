#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, "..", "..", "..");
const validatorPath = path.join(root, 'src', 'api', 'master-data-runtime-validator.js');
const switchPath = path.join(root, 'src', 'api', 'master-data-runtime-switch.js');
const indexPath = path.join(root, 'index.html');
const docsPath = path.join(root, 'docs', 'MASTER_DATA_RUNTIME_VALIDATOR.md');

function fail(message) {
  console.error(message);
  process.exit(1);
}

function read(filePath) {
  if (!fs.existsSync(filePath)) fail(`missing file: ${path.relative(root, filePath)}`);
  return fs.readFileSync(filePath, 'utf8');
}

const validator = read(validatorPath);
const runtimeSwitch = read(switchPath);
const indexHtml = read(indexPath);
read(docsPath);

[
  'RpgBackendMasterDataRuntimeValidator',
  'checkBackendMasterDataRuntimeIntegrity',
  'assertBackendMasterDataRuntimeIntegrity',
  'getBackendMasterDataRuntimeDebugSnapshot',
  'REQUIRED_DOM_IDS',
  'EXPECTED_MINIMUMS',
  'requireBackendMode',
  'backend_mode_not_applied',
  'count_too_low',
  'missing_dom',
].forEach((token) => {
  if (!validator.includes(token)) fail(`validator missing token: ${token}`);
});

[
  'RpgBackendMasterDataRuntime',
  'enableBackendMasterDataMode',
  'applyBackendMasterDataBeforeGameStart',
].forEach((token) => {
  if (!runtimeSwitch.includes(token)) fail(`runtime switch missing token: ${token}`);
});

const scriptOrder = [
  'src/api/game-api-client.js',
  'src/api/master-data-bridge.js',
  'src/api/master-data-adapter.js',
  'src/api/master-data-runtime-switch.js',
  'src/api/master-data-runtime-validator.js',
];
let previous = -1;
for (const script of scriptOrder) {
  const current = indexHtml.indexOf(script);
  if (current === -1) fail(`index.html missing script: ${script}`);
  if (current <= previous) fail(`index.html script order is wrong near: ${script}`);
  previous = current;
}

console.log('master-data runtime validator smoke test passed');

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");

function assertContains(file, patterns) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  const text = fs.readFileSync(fullPath, "utf8");
  for (const pattern of patterns) {
    if (!text.includes(pattern)) throw new Error(`${file}: missing pattern ${pattern}`);
  }
}

assertContains("src/api/game-api-client.js", [
  "saveGameSnapshot",
  "loadGameSnapshot",
  "listGameSaveSlots",
  'request("/game/save"',
  'request("/game/load"',
  'request("/game/save-slots"',
]);

assertContains("src/api/save-data-bridge.js", [
  "readLocalSaveSnapshot",
  "buildBackendSavePayload",
  "pushLocalSaveToBackend",
  "loadBackendSaveSnapshot",
  "checkBackendSaveSnapshotBridge",
  "idleRpgSaveV22",
]);

assertContains("index.html", [
  'src/api/game-api-client.js',
  'src/api/save-data-bridge.js',
  'src/api/save-data-integrity.js',
]);

console.log("save data bridge smoke test passed");

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const root = path.resolve(__dirname, "..", "..", "..");

function mustExist(file) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  return fs.readFileSync(fullPath, "utf8");
}

const docsIndex = mustExist("docs/README.md");
for (const text of ["Docs Index", "current/", "guides/", "contracts/", "archive/stage-notes/", "과거 기록"]) {
  if (!docsIndex.includes(text)) throw new Error(`docs/README.md missing ${text}`);
}

const archiveReadme = mustExist("docs/archive/stage-notes/README.md");
if (!archiveReadme.includes("Stage Notes Archive")) throw new Error("archive README missing title");

for (const required of [
  "docs/current/README.md",
  "docs/current/PROJECT_STRUCTURE.md",
  "docs/current/PRODUCTION_DEPLOYMENT_PLAN.md",
  "docs/guides/README.md",
  "docs/contracts/README.md",
  "docs/archive/README.md",
]) {
  mustExist(required);
}

const rootDocs = fs.readdirSync(path.join(root, "docs"), { withFileTypes: true })
  .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
  .map((entry) => entry.name)
  .sort();
const expectedRootDocs = ["CHANGELOG.md", "README.md"];
if (JSON.stringify(rootDocs) !== JSON.stringify(expectedRootDocs)) {
  throw new Error(`docs root must contain only ${expectedRootDocs.join(", ")}: ${rootDocs.join(", ")}`);
}

const rootSmokeCopies = fs.readdirSync(path.join(root, "tools"), { withFileTypes: true })
  .filter((entry) => entry.isFile() && entry.name.startsWith("smoke_"))
  .map((entry) => entry.name)
  .sort();
if (rootSmokeCopies.length) {
  throw new Error(`obsolete root smoke copies remain: ${rootSmokeCopies.join(", ")}`);
}

for (const removed of [
  "README_BACKEND_READY.md",
  "CHANGELOG.md",
  "tools/smoke_api_response_contract.js",
  "docs/API_RESPONSE_CONTRACT.md",
  "docs/BACKEND_ARCHITECTURE.md",
  "docs/NEXT_STEPS.md",
]) {
  if (fs.existsSync(path.join(root, removed))) throw new Error(`superseded path remains: ${removed}`);
}

for (const archived of [
  "docs/archive/stage-notes/ADMIN_MASTER_DATA_RELATIONS.md",
  "docs/archive/stage-notes/ADMIN_READONLY_PAGE.md",
  "docs/archive/stage-notes/MASTER_DATA_DEV_BADGE.md",
  "docs/archive/stage-notes/UI_RESULT_SEPARATION_STAGE1.md",
]) {
  mustExist(archived);
}

function filesUnder(relative) {
  const base = path.join(root, relative);
  const output = [];
  for (const entry of fs.readdirSync(base, { withFileTypes: true })) {
    const child = path.join(relative, entry.name);
    if (entry.isDirectory()) output.push(...filesUnder(child));
    else if (entry.isFile()) output.push(child);
  }
  return output;
}

const canonical = ["docs/current", "docs/guides", "docs/contracts"].flatMap(filesUnder);
const archived = filesUnder("docs/archive");
const archivedHashes = new Map();
for (const relative of archived) {
  const digest = crypto.createHash("sha256").update(fs.readFileSync(path.join(root, relative))).digest("hex");
  if (!archivedHashes.has(digest)) archivedHashes.set(digest, []);
  archivedHashes.get(digest).push(relative);
}
for (const relative of canonical) {
  const digest = crypto.createHash("sha256").update(fs.readFileSync(path.join(root, relative))).digest("hex");
  if (archivedHashes.has(digest)) {
    throw new Error(`canonical/archive duplicate: ${relative} == ${archivedHashes.get(digest).join(", ")}`);
  }
}

console.log("docs index/archive structure smoke test passed");

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");

function mustExist(file) {
  const fullPath = path.join(root, file);
  if (!fs.existsSync(fullPath)) throw new Error(`missing file: ${file}`);
  return fs.readFileSync(fullPath, "utf8");
}

const docsIndex = mustExist("docs/README.md");
for (const text of ["Docs Index", "docs/archive/stage-notes/", "지금 자주 보는 문서", "보관 문서"]) {
  if (!docsIndex.includes(text)) throw new Error(`docs/README.md missing ${text}`);
}

const archiveReadme = mustExist("docs/archive/stage-notes/README.md");
if (!archiveReadme.includes("Stage Notes Archive")) throw new Error("archive README missing title");

for (const archived of [
  "docs/archive/stage-notes/ADMIN_MASTER_DATA_RELATIONS.md",
  "docs/archive/stage-notes/ADMIN_READONLY_PAGE.md",
  "docs/archive/stage-notes/MASTER_DATA_DEV_BADGE.md",
  "docs/archive/stage-notes/UI_RESULT_SEPARATION_STAGE1.md",
]) {
  mustExist(archived);
}

console.log("docs index/archive smoke test passed");

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { execFileSync } = require("child_process");

const root = path.resolve(__dirname, "..", "..", "..");

function full(relative) {
  return path.join(root, relative);
}

function mustExist(relative) {
  if (!fs.existsSync(full(relative))) throw new Error(`missing documentation path: ${relative}`);
  return fs.readFileSync(full(relative), "utf8");
}

function trackedMarkdown() {
  return execFileSync(
    "git",
    ["ls-files", "--cached", "--others", "--exclude-standard", "--", "*.md"],
    { cwd: root, encoding: "utf8" }
  )
    .split(/\r?\n/)
    .filter(Boolean)
    .filter((relative, index, paths) => fs.existsSync(full(relative)) && paths.indexOf(relative) === index)
    .sort();
}

const required = [
  "AGENTS.md",
  "NEXT_CHAT_PROMPT.md",
  "NEXT_CHAT_HANDOFF.md",
  "docs/README.md",
  "docs/DOCUMENTATION_SYSTEM.md",
  "docs/current/README.md",
  "docs/current/CURRENT_STATUS.md",
  "docs/reference/README.md",
  "docs/generated/README.md",
  "docs/archive/README.md",
  "docs/generated/BACKEND_ROUTE_MAP.md",
  "docs/generated/BACKEND_STRUCTURE_PLAN.md",
  "docs/generated/LEGACY_PATH_DEPENDENCIES.md",
  "docs/generated/POSTGRES_ALEMBIC_READINESS.md",
  "docs/archive/history/ADMIN_AND_BACKEND_HISTORY.md",
  "docs/archive/history/DATA_AND_SEED_HISTORY.md",
  "docs/archive/history/GAME_UI_RUNTIME_HISTORY.md",
  "docs/archive/history/SAVE_SYSTEM_HISTORY.md",
  "docs/archive/history/PROJECT_HISTORY.md",
  "docs/archive/history/POSTGRES_V295_BASELINE_HISTORY.md",
  "docs/archive/history/PRODUCTION_RELEASE_PREPARATION_HISTORY.md",
];
for (const relative of required) mustExist(relative);

const expectedHistorySections = new Map([
  ["docs/archive/history/ADMIN_AND_BACKEND_HISTORY.md", 84],
  ["docs/archive/history/DATA_AND_SEED_HISTORY.md", 17],
  ["docs/archive/history/GAME_UI_RUNTIME_HISTORY.md", 11],
  ["docs/archive/history/SAVE_SYSTEM_HISTORY.md", 10],
  ["docs/archive/history/PROJECT_HISTORY.md", 9],
]);
for (const [relative, expected] of expectedHistorySections) {
  const headers = [...mustExist(relative).matchAll(/^## 원본: `([^`]+)`$/gm)].map((match) => match[1]);
  if (headers.length !== expected) throw new Error(`${relative} source section count differs: ${headers.length} !== ${expected}`);
  if (new Set(headers).size !== expected) throw new Error(`${relative} has duplicate source section paths`);
  if (headers.some((source) => !source.startsWith("docs/archive/stage-notes/"))) {
    throw new Error(`${relative} lost an original stage-note path`);
  }
}

for (const obsolete of [
  "docs/handoff",
  "docs/archive/stage-notes",
  "docs/archive/postgres-baseline",
  "docs/archive/production-deployment",
  "docs/current/ROADMAP.md",
  "docs/current/NEXT_STEPS.md",
  "docs/current/BACKEND_ROUTE_MAP.md",
  "docs/current/POSTGRES_ALEMBIC_READINESS.md",
]) {
  if (fs.existsSync(full(obsolete))) throw new Error(`obsolete documentation path remains: ${obsolete}`);
}

const docsIndex = mustExist("docs/README.md");
for (const marker of ["Upgrade RPG Docs Hub", "Current Status", "Reference Index", "Generated Index", "Archive Index"]) {
  if (!docsIndex.includes(marker)) throw new Error(`docs index missing marker: ${marker}`);
}
if (docsIndex.includes("## Obsidian에서 열기")) throw new Error("docs index must not contain user-run Obsidian instructions");

const prompt = mustExist("NEXT_CHAT_PROMPT.md");
for (const marker of ["AGENTS.md", "NEXT_CHAT_HANDOFF.md", "docs/current/CURRENT_STATUS.md"]) {
  if (!prompt.includes(marker)) throw new Error(`next-chat prompt missing entry link: ${marker}`);
}
if (prompt.includes("latest:")) throw new Error("next-chat prompt must not duplicate mutable status markers");

const rootReadme = mustExist("README.md");
for (const marker of [
  "로컬에서 게임 확인하기",
  "docker compose up -d postgres adminer",
  "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000",
  "python -m http.server 5500 --bind 127.0.0.1",
  "http://127.0.0.1:5500/index.html",
  "http://127.0.0.1:5500/admin.html",
  "docker compose stop",
]) {
  if (!rootReadme.includes(marker)) throw new Error(`root README missing local-run marker: ${marker}`);
}
const bashBlocks = [...rootReadme.matchAll(/```bash\r?\n([\s\S]*?)```/g)];
if (bashBlocks.length !== 6) throw new Error(`root README bash block count differs: ${bashBlocks.length} !== 6`);
for (const match of bashBlocks) {
  const prefix = rootReadme.slice(Math.max(0, match.index - 420), match.index);
  for (const label of ["실행 위치:", "Python `.venv` 상태:", "새 설치 여부:"]) {
    if (!prefix.includes(label)) throw new Error(`root README command block missing label: ${label}`);
  }
}
const executableGuidance = bashBlocks.map((match) => match[1]).join("\n");
for (const unsafe of ["docker compose down -v", "setup_dev_db.py --reset", "alembic upgrade", "alembic downgrade", "alembic stamp"]) {
  if (executableGuidance.includes(unsafe)) throw new Error(`unsafe command entered README code block: ${unsafe}`);
}

const sizeBudgets = new Map([
  ["AGENTS.md", 20000],
  ["NEXT_CHAT_PROMPT.md", 2500],
  ["NEXT_CHAT_HANDOFF.md", 12000],
  ["docs/current/CURRENT_STATUS.md", 16000],
]);
for (const [relative, budget] of sizeBudgets) {
  const size = fs.statSync(full(relative)).size;
  if (size > budget) throw new Error(`${relative} exceeds ${budget} bytes: ${size}`);
}

const markdown = trackedMarkdown();
if (markdown.length > 100) throw new Error(`tracked Markdown budget exceeded: ${markdown.length} > 100`);
const current = markdown.filter((relative) => relative.startsWith("docs/current/") && relative !== "docs/current/README.md");
if (current.length > 15) throw new Error(`current document budget exceeded: ${current.length} > 15`);

const linkScope = markdown.filter((relative) =>
  relative === "README.md" ||
  relative === "AGENTS.md" ||
  relative === "NEXT_CHAT_PROMPT.md" ||
  relative === "NEXT_CHAT_HANDOFF.md" ||
  relative === "docs/README.md" ||
  relative === "docs/DOCUMENTATION_SYSTEM.md" ||
  relative.startsWith("docs/current/") ||
  relative.startsWith("docs/reference/") ||
  relative.startsWith("docs/contracts/") ||
  relative.startsWith("docs/guides/")
);
const markdownLink = /\[[^\]]*\]\(([^)]+)\)/g;
for (const relative of linkScope) {
  const source = fs.readFileSync(full(relative), "utf8");
  for (const match of source.matchAll(markdownLink)) {
    const rawTarget = match[1].trim().replace(/^<|>$/g, "");
    if (!rawTarget || rawTarget.startsWith("#") || /^[a-z]+:/i.test(rawTarget)) continue;
    const withoutAnchor = rawTarget.split("#", 1)[0].split("?", 1)[0];
    if (!withoutAnchor) continue;
    const resolved = withoutAnchor.startsWith("/")
      ? path.join(root, withoutAnchor.slice(1))
      : path.resolve(path.dirname(full(relative)), withoutAnchor);
    if (!fs.existsSync(resolved)) throw new Error(`broken Markdown link: ${relative} -> ${rawTarget}`);
  }
}

const hashes = new Map();
for (const relative of markdown) {
  const digest = crypto.createHash("sha256").update(fs.readFileSync(full(relative))).digest("hex");
  if (!hashes.has(digest)) hashes.set(digest, []);
  hashes.get(digest).push(relative);
}
const duplicates = [...hashes.values()].filter((paths) => paths.length > 1);
if (duplicates.length) throw new Error(`exact Markdown duplicates remain: ${JSON.stringify(duplicates)}`);

const gitignore = mustExist(".gitignore");
if (!gitignore.includes(".obsidian/")) throw new Error(".obsidian/ must remain ignored");

const documentationSystem = mustExist("docs/DOCUMENTATION_SYSTEM.md");
for (const marker of [
  "작업 종료 문서 마감",
  "표준 Markdown 링크",
  "docs/generated/",
  "docs/archive/history/",
]) {
  if (!documentationSystem.includes(marker)) throw new Error(`documentation system missing marker: ${marker}`);
}
if (documentationSystem.includes("## Obsidian 사용")) throw new Error("documentation system must not contain user-run Obsidian instructions");

const agents = mustExist("AGENTS.md");
for (const marker of ["Obsidian의 ignored 로컬 vault 설정", "Codex가 탐색 효율 중심으로 유지", "비기능 포맷 변경"]) {
  if (!agents.includes(marker)) throw new Error(`AGENTS.md missing persistent local-tool rule: ${marker}`);
}

console.log(`docs structure smoke passed: markdown=${markdown.length}, current=${current.length}`);

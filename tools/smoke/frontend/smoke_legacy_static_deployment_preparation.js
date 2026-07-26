const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const root = path.resolve(__dirname, "..", "..", "..");
const output = path.join(root, "frontend", "legacy-dist");
const builder = path.join(root, "tools", "build_legacy_static_site.mjs");
const productionApi = "https://upgrade-rpg-api.onrender.com/api/v1";

const build = spawnSync(process.execPath, [builder], {
  cwd: root,
  encoding: "utf8",
});
assert.equal(build.status, 0, build.stderr || build.stdout);
assert.match(build.stdout, /secrets or database credentials included: no/);

const topLevel = fs.readdirSync(output).sort();
assert.deepEqual(topLevel, ["admin.html", "index.html", "src"]);

for (const entrypoint of ["index.html", "admin.html"]) {
  const html = fs.readFileSync(path.join(output, entrypoint), "utf8");
  const configIndex = html.indexOf('src="src/api/runtime-config.js"');
  const clientIndex = html.indexOf('src="src/api/game-api-client.js"');
  assert(configIndex >= 0, `${entrypoint}: runtime-config.js is missing`);
  assert(clientIndex > configIndex, `${entrypoint}: runtime config must load before the API client`);
}

const runtimeConfig = fs.readFileSync(path.join(output, "src", "api", "runtime-config.js"), "utf8");
assert(runtimeConfig.includes(productionApi), "production API base URL differs");
assert(runtimeConfig.includes('"localhost"'), "localhost bypass is missing");
assert(runtimeConfig.includes('"127.0.0.1"'), "127.0.0.1 bypass is missing");
assert(runtimeConfig.includes("if (!isLocal)"), "non-local runtime switch is missing");
assert(!runtimeConfig.includes("ADMIN_WRITE_DEV_KEY"), "admin write key must not be in runtime config");

const files = [];
function walk(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) walk(absolute);
    else files.push(path.relative(output, absolute).replaceAll("\\", "/"));
  }
}
walk(output);
assert(files.every((file) => file === "index.html" || file === "admin.html" || /\.(?:js|css)$/.test(file)));
assert(!files.some((file) => /(?:^|\/)(?:backend|deploy|docs|tools|\.git)(?:\/|$)/.test(file)));
assert(!files.some((file) => /\.md$/i.test(file)), "documentation must not be published");

console.log("legacy static deployment preparation smoke passed");
console.log(`- public entries: index.html/admin.html`);
console.log(`- packaged runtime files: ${files.length}`);
console.log("- local API preserved / non-local API pinned / admin secret embedded: yes/yes/no");

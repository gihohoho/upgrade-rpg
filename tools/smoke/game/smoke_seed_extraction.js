#!/usr/bin/env node
/** Smoke test for generated seed JSON files. */
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");
const seedDir = path.join(root, "backend", "seeds", "generated");
const manifestPath = path.join(seedDir, "manifest.json");

function readJson(fileName) {
  return JSON.parse(fs.readFileSync(path.join(seedDir, fileName), "utf8"));
}

if (!fs.existsSync(manifestPath)) {
  console.error("Missing backend/seeds/generated/manifest.json. Run node tools/extract_seed_data.js first.");
  process.exit(1);
}

const manifest = readJson("manifest.json");
const required = [
  "characters.json",
  "skills.json",
  "skill_books.json",
  "bosses.json",
  "field_zones.json",
  "item_templates.json",
  "drop_tables.json",
  "drop_table_items.json",
  "enhancement_rules.json",
];

required.forEach((fileName) => {
  const data = readJson(fileName);
  if (!data || (Array.isArray(data) && data.length === 0)) {
    throw new Error(`${fileName} is empty or invalid`);
  }
});

const bosses = readJson("bosses.json");
const fieldZones = readJson("field_zones.json");
const skills = readJson("skills.json");
const dropItems = readJson("drop_table_items.json");

if (bosses.length !== manifest.counts.bosses) throw new Error("boss count mismatch");
if (fieldZones.length !== manifest.counts.fieldZones) throw new Error("field zone count mismatch");
if (skills.length !== manifest.counts.skills) throw new Error("skill count mismatch");
if (dropItems.length !== manifest.counts.dropTableItems) throw new Error("drop item count mismatch");

console.log("Seed extraction smoke test passed");
console.log(manifest.counts);

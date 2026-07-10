#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..", "..", "..");
const runtimePath = path.join(root, "src", "api", "master-data-runtime-switch.js");
const adapterPath = path.join(root, "src", "api", "master-data-adapter.js");
const renderPath = path.join(root, "src", "ui", "render-ui.js");

function fail(message) {
	console.error(message);
	process.exit(1);
}

for (const filePath of [runtimePath, adapterPath, renderPath]) {
	if (!fs.existsSync(filePath)) fail(`필수 파일이 없습니다: ${filePath}`);
}

const runtime = fs.readFileSync(runtimePath, "utf8");
const adapter = fs.readFileSync(adapterPath, "utf8");
const render = fs.readFileSync(renderPath, "utf8");

[
	"fieldZones: 0",
	"staticZoneByLevel",
	"staticZoneByName",
	"field.img = staticField.img",
	"render 단계에서 안전한 기본 이미지",
].forEach((needle) => {
	if (!runtime.includes(needle)) fail(`runtime switch에 필드 이미지 보정 코드가 없습니다: ${needle}`);
});

[
	"img: zone.imageUrl || raw.img || null",
	"hasImage: !!zone.hasImage",
].forEach((needle) => {
	if (!adapter.includes(needle)) fail(`adapter에 필드 이미지 메타 코드가 없습니다: ${needle}`);
});

[
	"fieldImg",
	`field.img && field.img !== "undefined"`,
	"text=Zone${field.level || zoneIdx + 1}",
].forEach((needle) => {
	if (!render.includes(needle)) fail(`render-ui에 필드 이미지 fallback 코드가 없습니다: ${needle}`);
});

console.log("field zone asset fallback smoke test passed");

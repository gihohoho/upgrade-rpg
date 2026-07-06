const assert = require("assert");
const contract = require("../src/api/api-response-contract.js");

assert(contract, "GAME_API_CONTRACT should load");
assert.strictEqual(contract.RESPONSE_VERSION, "game-api-response.v1");

const ok = contract.createApiSuccessResponse({
	type: contract.ACTION_TYPES.ITEM_EQUIP,
	data: { itemName: "테스트 장비" },
	ui: { updateFullUI: true },
});
assert.strictEqual(ok.ok, true);
assert.strictEqual(ok.type, "item.equip");
assert.strictEqual(ok.error, null);
assert.strictEqual(ok.data.itemName, "테스트 장비");

const fail = contract.createApiErrorResponse({
	type: contract.ACTION_TYPES.BOSS_SUMMON,
	code: contract.ERROR_CODES.COOLDOWN_ACTIVE,
	message: "쿨타임 중",
});
assert.strictEqual(fail.ok, false);
assert.strictEqual(fail.error.code, "COOLDOWN_ACTIVE");

const normalized = contract.normalizeActionResultToApiResponse({
	ok: true,
	type: "combat.attack",
	payload: { target: "field" },
	data: { totalDamage: 100 },
	logs: [],
	effects: [{ type: "damageText", text: "100" }],
	ui: { updateCombatUI: true },
	createdAt: 123,
});
assert.strictEqual(normalized.ok, true);
assert.strictEqual(normalized.type, "combat.attack");
assert.strictEqual(normalized.createdAt, 123);
assert.strictEqual(normalized.effects.length, 1);

for (const [key, example] of Object.entries(contract.API_RESPONSE_EXAMPLES)) {
	assert.strictEqual(typeof example.ok, "boolean", `${key}: ok should be boolean`);
	assert(example.responseVersion, `${key}: responseVersion required`);
	assert(example.type, `${key}: type required`);
	assert(example.data && typeof example.data === "object", `${key}: data required`);
	assert(Array.isArray(example.logs), `${key}: logs should be array`);
	assert(Array.isArray(example.effects), `${key}: effects should be array`);
}

console.log("API response contract smoke test passed");

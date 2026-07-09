const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

function assert(condition, message) {
  if (!condition) throw new Error(message);
  console.log(`[OK] ${message}`);
}

const adminJs = read("src/api/admin-page-readonly.js");
const clientJs = read("src/api/game-api-client.js");
const routePy = read("backend/app/api/routes/admin_master_data_routes.py");
const schemaPy = read("backend/app/schemas/admin.py");
const servicePy = read("backend/app/services/admin_service_legacy_markers.py");
const checkPy = read("backend/scripts/check_admin_readonly_api.py");
const adminHtml = read("admin.html");

assert(adminJs.includes('v165.admin-create-apply-limited'), 'admin page version is v134 safe selects');
assert(adminHtml.includes('v165 admin create apply limited'), 'admin footer is v134 safe selects');
assert(adminJs.includes('baseValues: values.originals'), 'admin preview/apply sends original base values');
assert(adminJs.includes('stale guard'), 'admin UI explains stale guard');
assert(adminJs.includes('payload.staleGuardEnabled'), 'admin UI renders stale guard state');
assert(adminJs.includes('payload.staleCount'), 'admin UI renders stale count');
assert(adminJs.includes('staleChanges'), 'admin UI renders stale changes');
assert(adminJs.includes('오래된 초안 검사'), 'admin UI includes stale draft panel');

assert(clientJs.includes('baseValues: opts.baseValues || undefined'), 'API client forwards baseValues');
assert(schemaPy.includes('base_values') && schemaPy.includes('alias="baseValues"'), 'admin schemas accept baseValues alias');
assert(routePy.includes('base_values=payload.base_values'), 'admin routes pass base_values to service');
assert(servicePy.includes('safe_base_values'), 'service normalizes safe base values');
assert(servicePy.includes('stale_changes'), 'service tracks stale changes');
assert(servicePy.includes('current_value_changed_since_form_loaded'), 'service detects changed current DB value');
assert(servicePy.includes('stale_guard_base_values_required'), 'service requires base values for apply');
assert(servicePy.includes('base_values_required_for_apply'), 'service blocks apply without base values');
assert(servicePy.includes('staleGuardEnabled'), 'service reports stale guard enabled');
assert(servicePy.includes('staleCount'), 'service reports stale count');
assert(servicePy.includes('staleChanges'), 'service returns stale change details');
assert(checkPy.includes('master_edit_stale_preview'), 'live check verifies stale preview');
assert(checkPy.includes('staleCount'), 'live check checks staleCount');

console.log('[PASS] smoke_admin_edit_stale_guard');

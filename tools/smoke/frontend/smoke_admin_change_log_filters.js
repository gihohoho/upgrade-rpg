const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, "..", "..", "..");
const read = (file) => fs.readFileSync(path.join(root, file), 'utf8');

function assert(condition, message) {
  if (!condition) {
    console.error(`[FAIL] ${message}`);
    process.exit(1);
  }
  console.log(`[OK] ${message}`);
}

const adminHtml = read('admin.html');
const adminJs = read('src/api/admin-page-readonly.js');
const clientJs = read('src/api/game-api-client.js');
const routePy = read('backend/app/api/routes/admin_change_log_routes.py') + read('backend/app/api/routes/admin_route_params.py');
const servicePy = read('backend/app/services/admin/admin_change_log_service.py');

assert(adminHtml.includes('data-admin-change-log-filter-target-type'), 'admin.html has change log target type filter');
assert(adminHtml.includes('data-admin-change-log-filter-changed-key'), 'admin.html has changed field filter');
assert(adminHtml.includes('data-admin-action="apply-change-log-filters"'), 'admin.html has apply change log filters action');
assert(adminHtml.includes('data-admin-action="reset-change-log-filters"'), 'admin.html has reset change log filters action');
assert(adminHtml.includes('value="update"') && adminHtml.includes('value="rollback"') && adminHtml.includes('value="create"') && adminHtml.includes('value="create_delete"') && adminHtml.includes('value="create_delete_restore"'), 'admin.html exposes current update/rollback/create lifecycle action filter options');

assert(adminJs.includes('function readChangeLogFiltersFromDom()'), 'admin page can read change log filters');
assert(adminJs.includes('function resetChangeLogFilters'), 'admin page can reset change log filters');
assert(adminJs.includes('function describeChangeLogFilters'), 'admin page can describe change log filters');
assert(adminJs.includes('window.readAdminChangeLogFilters = readChangeLogFiltersFromDom'), 'change log filter reader exposed on window');
assert(adminJs.includes('window.resetAdminChangeLogFilters = resetChangeLogFilters'), 'change log filter reset exposed on window');
assert(adminJs.includes('window.refreshAdminChangeLogs = refreshAdminChangeLogs'), 'change log refresh exposed on window');
assert(adminJs.includes('adminChangeLogFilterReady'), 'readiness includes change log filter DOM check');
assert(adminJs.includes('changedKey') && adminJs.includes('targetType') && adminJs.includes('action'), 'admin page passes changedKey/targetType/action filters');

assert(clientJs.includes('changedKey') && clientJs.includes('applied') && clientJs.includes('sort'), 'game api client sends new change log query params');
assert(routePy.includes('changed_key: str | None') && routePy.includes('alias="changedKey"'), 'admin route accepts changedKey query param');
assert(routePy.includes('applied: bool | None') && routePy.includes('sort: str | None'), 'admin route accepts applied/sort query params');
assert(servicePy.includes('ADMIN_CHANGE_LOG_ACTION_FILTERS'), 'admin change log service declares allowed change log action filters');
assert(servicePy.includes('def _clean_admin_change_log_filters'), 'admin change log service cleans change log filters');
assert(servicePy.includes('def _build_admin_change_log_where_clauses'), 'admin change log service builds change log clauses');
assert(servicePy.includes('AdminChangeLog.before_json.op("?")'), 'admin change log service filters JSONB by changed key safely');
assert(servicePy.includes('def _admin_change_log_order_by'), 'admin change log service supports change log sorting');

console.log('[PASS] smoke_admin_change_log_filters');

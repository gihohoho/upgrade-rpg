const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
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
const routePy = read('backend/app/api/routes/admin.py');
const securityPy = read('backend/app/core/security.py');
const configPy = read('backend/app/core/config.py');
const envExample = read('backend/.env.example');
const checkScript = read('backend/scripts/check_admin_readonly_api.py');

assert(adminHtml.includes('section-admin-write-guard'), 'admin.html has write guard section');
assert(adminHtml.includes('data-admin-write-dev-key'), 'admin.html has dev key input');
assert(adminHtml.includes('data-admin-write-key-status'), 'admin.html has dev key status');
assert(adminHtml.includes('data-admin-action="save-admin-write-dev-key"'), 'admin.html can save dev key');
assert(adminHtml.includes('data-admin-action="clear-admin-write-dev-key"'), 'admin.html can clear dev key');

assert(adminJs.includes('v130.admin-write-dev-key-guard'), 'admin page version updated');
assert(adminJs.includes('function requireAdminWriteDevKeyForUi'), 'admin JS blocks write actions when key missing');
assert(adminJs.includes('saveAdminWriteDevKeyFromInput'), 'admin JS can save write dev key');
assert(adminJs.includes('clearAdminWriteDevKey'), 'admin JS can clear write dev key');
assert(adminJs.includes('adminWriteGuardReady'), 'readiness checks write guard UI');
assert(adminJs.includes('adminWriteDevKeySet'), 'readiness reports write key state');

assert(clientJs.includes('ADMIN_WRITE_DEV_KEY_STORAGE_KEY'), 'client stores admin write dev key in sessionStorage');
assert(clientJs.includes('getAdminWriteHeaders'), 'client builds admin write headers');
assert(clientJs.includes('"X-Admin-Dev-Key"'), 'client sends X-Admin-Dev-Key header');
assert(clientJs.includes('headers: getAdminWriteHeaders()'), 'client adds write header to guarded APIs');

assert(configPy.includes('admin_write_dev_key'), 'backend settings include admin write dev key');
assert(envExample.includes('ADMIN_WRITE_DEV_KEY'), '.env.example documents admin write dev key');
assert(securityPy.includes('require_admin_write_dev_key'), 'security dependency exists');
assert(securityPy.includes('X-Admin-Dev-Key'), 'security dependency reads X-Admin-Dev-Key');
assert(routePy.includes('Depends(require_admin_write_dev_key)'), 'write routes require dev key dependency');
assert(routePy.includes('X-Admin-Dev-Key'), 'write route metadata mentions dev key');
assert(checkScript.includes('master_edit_apply_missing_key_blocked'), 'live check verifies missing key is blocked');

console.log('[PASS] smoke_admin_write_dev_key_guard');

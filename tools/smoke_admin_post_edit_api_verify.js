const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const adminJs = fs.readFileSync(path.join(root, 'src/api/admin-page-readonly.js'), 'utf8');
const adminHtml = fs.readFileSync(path.join(root, 'admin.html'), 'utf8');
const docs = fs.readFileSync(path.join(root, 'docs/ADMIN_POST_EDIT_API_VERIFY.md'), 'utf8');
const changelog = fs.readFileSync(path.join(root, 'docs/CHANGELOG.md'), 'utf8');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(adminJs.includes('v144.admin-combo-relation-guard'), 'version should be v128');
assert(adminJs.includes('runPostWriteMasterApiVerification'), 'post write verify helper missing');
assert(adminJs.includes('await runPostWriteMasterApiVerification(values.domain, values.id'), 'apply flow should auto verify edited target');
assert(adminJs.includes('rollbackTarget.domain'), 'rollback flow should auto verify rollback target domain');
assert(adminJs.includes('rollbackTarget.id'), 'rollback flow should auto verify rollback target id');
assert(adminJs.includes('contextLabel'), 'verify result should include context label');
assert(adminJs.includes('autoAfterWrite'), 'verify result should include autoAfterWrite flag');
assert(adminJs.includes('postWriteApiVerifyReady'), 'readiness should expose post write verify');
assert(adminJs.includes('window.runPostWriteMasterApiVerification = runPostWriteMasterApiVerification'), 'console helper export missing');
assert(adminJs.includes('currentAdminChangeLogDetailPayload'), 'rollback target detail state missing');

assert(adminHtml.includes('v144 admin combo relation guard'), 'footer should be v128');
assert(adminHtml.includes('적용/되돌리기 후 master-data API 자동 확인'), 'subtitle should mention auto verify');
assert(docs.includes('DB 적용 후 자동 확인'), 'docs should explain apply auto verify');
assert(docs.includes('되돌리기 후 자동 확인'), 'docs should explain rollback auto verify');
assert(changelog.includes('## v128'), 'changelog should include v128');

console.log('[smoke] admin post-edit API verify checks passed');

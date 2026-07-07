const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const adminJsPath = path.join(root, 'src/api/admin-page-readonly.js');
const adminHtmlPath = path.join(root, 'admin.html');
const docsPath = path.join(root, 'docs/ADMIN_MASTER_API_VERIFY.md');

const adminJs = fs.readFileSync(adminJsPath, 'utf8');
const adminHtml = fs.readFileSync(adminHtmlPath, 'utf8');
const docs = fs.readFileSync(docsPath, 'utf8');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(adminJs.includes('v134.admin-safe-selects'), 'version should be v134 admin safe selects');
assert(adminJs.includes('verifySelectedMasterDataApi'), 'verifySelectedMasterDataApi helper missing');
assert(adminJs.includes('findMasterApiRow'), 'findMasterApiRow helper missing');
assert(adminJs.includes('buildMasterApiVerifyComparisons'), 'buildMasterApiVerifyComparisons helper missing');
assert(adminJs.includes('ADMIN_TO_MASTER_API_FIELD_MAP'), 'admin to master API field map missing');
assert(adminJs.includes('window.RpgGameApi.fetchMasterData'), 'verify flow should fetch /game/master-data');
assert(adminJs.includes('data-admin-master-api-verify-result'), 'verify result target missing');
assert(adminJs.includes('verify-master-api-target'), 'verify button action missing');
assert(adminJs.includes('window.verifySelectedMasterDataApi = verifySelectedMasterDataApi'), 'console helper export missing');
assert(adminJs.includes('masterApiVerifyReady'), 'readiness flag missing');
assert(adminJs.includes('runPostWriteMasterApiVerification'), 'post-write auto verification helper missing');
assert(adminJs.includes('postWriteApiVerifyReady'), 'post-write readiness flag missing');
assert(adminJs.includes('autoAfterWrite'), 'autoAfterWrite result flag missing');

assert(adminHtml.includes('Guarded Admin + API Verify'), 'admin page title copy not updated');
assert(adminHtml.includes('v134 admin safe selects'), 'footer version not updated');

assert(docs.includes('/game/master-data'), 'docs should mention game master-data API');
assert(docs.includes('await verifySelectedMasterDataApi()'), 'docs should mention console helper');

console.log('[smoke] admin master-data API verify checks passed');

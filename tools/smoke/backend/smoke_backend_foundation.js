const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, "..", "..", "..");
const required = [
  'backend/README.md',
  'backend/pyproject.toml',
  'backend/.env.example',
  'backend/app/main.py',
  'backend/app/core/config.py',
  'backend/app/core/response.py',
  'backend/app/db/session.py',
  'backend/app/api/router.py',
  'backend/app/api/routes/health.py',
  'backend/app/api/routes/game.py',
  'backend/app/api/routes/admin.py',
  'backend/sql/schema_draft.sql',
  'docs/ADMIN_REQUIREMENTS_V1.md',
  'docs/DB_SCHEMA_DRAFT.md',
  'docs/BACKEND_ARCHITECTURE.md',
  'docs/BACKEND_API_ROUTES_DRAFT.md',
];

const missing = required.filter((file) => !fs.existsSync(path.join(root, file)));
if (missing.length > 0) {
  console.error('Missing backend foundation files:');
  for (const file of missing) console.error(`- ${file}`);
  process.exit(1);
}

const responseContract = fs.readFileSync(path.join(root, 'backend/app/core/response.py'), 'utf8');
if (!responseContract.includes('game-api-response.v1')) {
  console.error('Missing game-api-response.v1 marker in backend response helper.');
  process.exit(1);
}

const adminRequirements = fs.readFileSync(path.join(root, 'docs/ADMIN_REQUIREMENTS_V1.md'), 'utf8');
for (const keyword of ['아이템 관리', '보스 관리', '드랍률 관리', '강화 규칙 관리', '캐릭터 관리', '스킬 관리', '수정 전 값 저장']) {
  if (!adminRequirements.includes(keyword)) {
    console.error(`Missing admin requirement keyword: ${keyword}`);
    process.exit(1);
  }
}

console.log('Backend foundation smoke test passed.');

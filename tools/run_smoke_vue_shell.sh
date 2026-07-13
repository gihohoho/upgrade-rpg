#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python tools/smoke/frontend/smoke_vue_shell_structure.py
python tools/smoke/frontend/smoke_vue_readonly_api_client.py
python tools/smoke/frontend/smoke_vue_readonly_api_status_panel.py
python tools/smoke/frontend/smoke_vue_admin_readonly_catalog_panel.py
python tools/smoke/frontend/smoke_vue_admin_readonly_relations_panel.py
node --check frontend/vue-app/vite.config.js
node --check frontend/vue-app/src/main.js
node --check frontend/vue-app/src/router/index.js

if [ -d "frontend/vue-app/node_modules" ]; then
  (cd frontend/vue-app && npm run build)
else
  echo "INFO: frontend/vue-app/node_modules not found; skipped npm run build. Run npm install in frontend/vue-app to enable build verification."
fi
node --check frontend/vue-app/src/api/config.js
node --check frontend/vue-app/src/api/readOnlyRoutes.js
node --check frontend/vue-app/src/api/readOnlyClient.js
node --check frontend/vue-app/src/api/adminReadOnlyApi.js
node --check frontend/vue-app/src/api/gameReadOnlyApi.js
node --check frontend/vue-app/src/api/healthReadOnlyApi.js
node --check frontend/vue-app/src/api/index.js

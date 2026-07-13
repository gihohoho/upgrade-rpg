#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python tools/smoke/frontend/smoke_vue_shell_structure.py
node --check frontend/vue-app/vite.config.js
node --check frontend/vue-app/src/main.js
node --check frontend/vue-app/src/router/index.js

if [ -d "frontend/vue-app/node_modules" ]; then
  (cd frontend/vue-app && npm run build)
else
  echo "INFO: frontend/vue-app/node_modules not found; skipped npm run build. Run npm install in frontend/vue-app to enable build verification."
fi

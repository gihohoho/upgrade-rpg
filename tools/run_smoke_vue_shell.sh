#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python tools/smoke/frontend/smoke_vue_shell_structure.py
python tools/smoke/frontend/smoke_vue_readonly_api_client.py
python tools/smoke/frontend/smoke_vue_readonly_api_status_panel.py
python tools/smoke/frontend/smoke_vue_admin_readonly_catalog_panel.py
python tools/smoke/frontend/smoke_vue_admin_readonly_relations_panel.py
python tools/smoke/frontend/smoke_vue_auth_character_gate.py
python tools/smoke/frontend/smoke_vue_admin_auth_routing.py
python tools/smoke/frontend/smoke_vue_admin_preview_workflows.py
python tools/smoke/frontend/smoke_vue_admin_apply_confirmation_gates.py
python tools/report_vue_game_domain_dependencies.py --check
node tools/smoke/frontend/smoke_vue_game_domain_foundation.js
node tools/smoke/frontend/smoke_vue_game_town_hud.js
node tools/smoke/frontend/smoke_vue_game_field_combat_ui.js
node tools/smoke/frontend/smoke_vue_game_boss_combat_ui.js
node tools/smoke/frontend/smoke_vue_game_combat_runtime.js
node tools/smoke/frontend/smoke_vue_game_server_snapshot_load.js
node tools/smoke/frontend/smoke_vue_game_serialized_save_queue.js
node tools/smoke/frontend/smoke_vue_game_inventory_equipment_ui.js
node tools/smoke/frontend/smoke_vue_game_storage_trash_ui.js
node tools/smoke/frontend/smoke_vue_game_skill_enhancement_ui.js
node tools/smoke/frontend/smoke_vue_game_shop_settings_ui.js
node tools/smoke/frontend/smoke_vue_game_legacy_frame_modal_readability.js
node --check frontend/vue-app/vite.config.js

if [ -d "frontend/vue-app/node_modules" ]; then
  (cd frontend/vue-app && npm run build)
else
  echo "INFO: frontend/vue-app/node_modules not found; skipped npm run build. Run npm ci in frontend/vue-app to enable build verification."
fi
node --check frontend/vue-app/src/api/config.js
node --check frontend/vue-app/src/api/readOnlyRoutes.js
node --check frontend/vue-app/src/api/readOnlyClient.js
node --check frontend/vue-app/src/api/adminReadOnlyApi.js
node --check frontend/vue-app/src/api/gameReadOnlyApi.js
node --check frontend/vue-app/src/api/healthReadOnlyApi.js
node --check frontend/vue-app/src/api/index.js

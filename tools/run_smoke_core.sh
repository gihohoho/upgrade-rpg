#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[core smoke] project root: $ROOT_DIR"

node tools/smoke_admin_edit_stale_guard.js
node tools/smoke_admin_write_dev_key_guard.js
node tools/smoke_admin_guarded_edit_apply.js
node tools/smoke_admin_change_log_rollback.js
node tools/smoke_admin_create_blueprint_readonly.js
node tools/smoke_admin_create_draft_preview.js
node tools/smoke_admin_create_apply_limited.js
node tools/smoke_admin_create_apply_fieldzones.js
node tools/smoke_admin_create_apply_bosses.js
node tools/smoke_admin_create_apply_skills_droptables.js
node tools/smoke_admin_create_apply_items_dropitems.js
node tools/smoke_admin_create_apply_level_links.js
node tools/smoke_admin_create_lifecycle_guide.js
node tools/smoke_admin_create_lifecycle_guard_helper.js
node tools/smoke_admin_create_lifecycle_result_summary.js
node tools/smoke_admin_create_lifecycle_batch_check.js
node tools/smoke_admin_js_split_readiness.js
node tools/smoke_admin_layout_shell_split.js
node tools/smoke_admin_change_log_split_contract.js
node tools/smoke_admin_change_logs_split.js
node tools/smoke_admin_create_lifecycle_split_contract.js
node tools/smoke_admin_create_lifecycle_split.js
node tools/smoke_admin_edit_draft_split_contract.js
node tools/smoke_admin_edit_draft_split.js
node tools/smoke_admin_master_catalog_split.js
node tools/smoke_admin_overview_snapshots_split.js
node tools/smoke_admin_field_help_split.js
node tools/smoke_admin_settings_helpers_split.js
node tools/smoke_admin_bootstrap_bindings_readiness.js
node tools/smoke_admin_thin_entry_cleanup.js
node tools/smoke_admin_create_delete_rollback.js
node tools/smoke_admin_create_delete_restore.js
node tools/smoke_admin_layout_navigation_shell.js
node tools/smoke_admin_post_edit_api_verify.js
node tools/smoke_admin_master_api_verify.js
node tools/smoke_runtime_stacked_enhance_space_guard.js
node tools/smoke_runtime_stackable_items.js
node tools/smoke_save_data_integrity_verify.js
node tools/smoke_save_data_restore_reload_lock.js
node tools/smoke_save_data_restore_guard.js
python tools/smoke_admin_change_log_filter_binding.py
python tools/smoke_admin_change_logs_schema_guard.py
python tools/smoke_admin_readonly_api_structure.py
python tools/smoke_backend_admin_service_split_contract.py
python tools/smoke_backend_admin_overview_snapshots_service_split.py
python tools/smoke_backend_admin_master_catalog_service_split.py
python tools/smoke_backend_admin_create_lifecycle_service_split.py
python tools/smoke_backend_admin_change_log_service_split.py
python tools/smoke_backend_admin_edit_draft_service_split.py
python tools/smoke_backend_admin_shared_utils_service_split.py
python tools/smoke_backend_admin_config_readiness_service_split.py
python tools/smoke_backend_admin_route_response_helper.py
python tools/smoke_backend_admin_route_params_error_helpers.py
python tools/smoke_backend_admin_route_response_data_meta_helpers.py
python tools/smoke_backend_admin_route_module_split.py
python tools/smoke_backend_admin_overview_route_module_split.py
python tools/smoke_backend_admin_route_map_contract.py
python tools/smoke_backend_admin_route_module_import_contract.py
python tools/smoke_backend_admin_runtime_route_contract.py
python tools/smoke_backend_admin_route_service_legacy_cleanup.py
python tools/smoke_backend_admin_service_facade_contract.py
python tools/smoke_admin_create_blueprint_api_structure.py
python tools/smoke_save_snapshot_integrity_api_structure.py
python tools/smoke_save_snapshot_api_structure.py

# Some legacy smoke scripts may leave short-lived background jobs/timers open in
# non-interactive shells. Clean them up so CI/container runs can return promptly.
if jobs -pr >/dev/null 2>&1; then
  jobs -pr | xargs -r kill >/dev/null 2>&1 || true
fi

echo "[core smoke] passed"
exit 0

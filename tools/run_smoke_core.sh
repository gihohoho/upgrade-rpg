#!/usr/bin/env bash
set -euo pipefail

node tools/smoke/game/smoke_docs_index_archive.js

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[core smoke] project root: $ROOT_DIR"

node tools/smoke/game/smoke_equipment_progression_formulas.js
python tools/check_runtime_blocking_io.py --strict
python tools/smoke/backend/smoke_master_data_latency_guard.py
node tools/smoke/game/smoke_master_data_auto_boot_policy.js
python tools/check_frontend_static_deployment_plan.py --strict
node tools/smoke/frontend/smoke_legacy_static_deployment_preparation.js
node tools/smoke/frontend/smoke_admin_edit_stale_guard.js
node tools/smoke/frontend/smoke_admin_write_dev_key_guard.js
node tools/smoke/frontend/smoke_admin_guarded_edit_apply.js
node tools/smoke/frontend/smoke_admin_change_log_rollback.js
node tools/smoke/frontend/smoke_admin_rollback_snapshot_preview.js
node tools/smoke/frontend/smoke_admin_preview_result_summary.js
node tools/smoke/frontend/smoke_admin_preview_browser_verification.js
node tools/smoke/frontend/smoke_admin_preview_live_api_render_check.js
node tools/smoke/frontend/smoke_admin_workspace_navigation.js
node tools/smoke/frontend/smoke_admin_catalog_help_compact_ux.js
node tools/smoke/frontend/smoke_admin_practical_ux_bundle.js
node tools/smoke/frontend/smoke_admin_create_blueprint_readonly.js
node tools/smoke/frontend/smoke_admin_create_draft_preview.js
node tools/smoke/frontend/smoke_admin_create_apply_limited.js
node tools/smoke/frontend/smoke_admin_create_apply_fieldzones.js
node tools/smoke/frontend/smoke_admin_create_apply_bosses.js
node tools/smoke/frontend/smoke_admin_create_apply_skills_droptables.js
node tools/smoke/frontend/smoke_admin_create_apply_items_dropitems.js
node tools/smoke/frontend/smoke_admin_create_apply_level_links.js
node tools/smoke/frontend/smoke_admin_create_lifecycle_guide.js
node tools/smoke/frontend/smoke_admin_create_lifecycle_guard_helper.js
node tools/smoke/frontend/smoke_admin_create_lifecycle_result_summary.js
node tools/smoke/frontend/smoke_admin_create_lifecycle_batch_check.js
node tools/smoke/frontend/smoke_admin_js_split_readiness.js
node tools/smoke/frontend/smoke_admin_layout_shell_split.js
node tools/smoke/frontend/smoke_admin_change_log_split_contract.js
node tools/smoke/frontend/smoke_admin_change_logs_split.js
node tools/smoke/frontend/smoke_admin_create_lifecycle_split_contract.js
node tools/smoke/frontend/smoke_admin_create_lifecycle_split.js
node tools/smoke/frontend/smoke_admin_edit_draft_split_contract.js
node tools/smoke/frontend/smoke_admin_edit_draft_split.js
node tools/smoke/frontend/smoke_admin_master_catalog_split.js
node tools/smoke/frontend/smoke_admin_overview_snapshots_split.js
node tools/smoke/frontend/smoke_admin_field_help_split.js
node tools/smoke/frontend/smoke_admin_settings_helpers_split.js
node tools/smoke/frontend/smoke_admin_bootstrap_bindings_readiness.js
node tools/smoke/frontend/smoke_admin_thin_entry_cleanup.js
node tools/smoke/frontend/smoke_v370_admin_account_management.js
node tools/smoke/frontend/smoke_v370_account_character_gate.js
node tools/smoke/frontend/smoke_v371_email_account_frontend.js
node tools/smoke/frontend/smoke_admin_create_delete_rollback.js
node tools/smoke/frontend/smoke_admin_create_delete_restore.js
node tools/smoke/frontend/smoke_admin_layout_navigation_shell.js
node tools/smoke/frontend/smoke_admin_post_edit_api_verify.js
node tools/smoke/frontend/smoke_admin_master_api_verify.js
node tools/smoke/game/smoke_runtime_stacked_enhance_space_guard.js
node tools/smoke/game/smoke_runtime_stackable_items.js
node tools/smoke/game/smoke_runtime_item_quality_of_life.js
node tools/smoke/game/smoke_save_data_integrity_verify.js
node tools/smoke/game/smoke_save_data_restore_reload_lock.js
node tools/smoke/game/smoke_save_data_restore_guard.js
python tools/smoke/frontend/smoke_admin_change_log_filter_binding.py
python tools/smoke/frontend/smoke_admin_change_logs_schema_guard.py
python tools/smoke/frontend/smoke_admin_readonly_api_structure.py
python tools/smoke/contracts/smoke_backend_admin_service_split_contract.py
python tools/smoke/contracts/smoke_backend_admin_overview_snapshots_service_split.py
python tools/smoke/contracts/smoke_backend_admin_master_catalog_service_split.py
python tools/smoke/contracts/smoke_backend_admin_create_lifecycle_service_split.py
python tools/smoke/contracts/smoke_backend_admin_change_log_service_split.py
python tools/smoke/contracts/smoke_backend_admin_edit_draft_service_split.py
python tools/smoke/contracts/smoke_backend_admin_shared_utils_service_split.py
python tools/smoke/contracts/smoke_backend_admin_config_readiness_service_split.py
python tools/smoke/contracts/smoke_backend_admin_route_response_helper.py
python tools/smoke/contracts/smoke_backend_admin_route_params_error_helpers.py
python tools/smoke/contracts/smoke_backend_admin_route_response_data_meta_helpers.py
python tools/smoke/contracts/smoke_backend_admin_route_module_split.py
python tools/smoke/contracts/smoke_backend_admin_overview_route_module_split.py
python tools/smoke/contracts/smoke_backend_admin_route_map_contract.py
python tools/smoke/contracts/smoke_backend_admin_route_module_import_contract.py
python tools/smoke/contracts/smoke_backend_admin_runtime_route_contract.py
python tools/smoke/contracts/smoke_backend_admin_route_operation_contract.py
python tools/smoke/contracts/smoke_backend_admin_openapi_route_contract.py
python tools/smoke/contracts/smoke_backend_admin_response_metadata_contract.py
python tools/smoke/contracts/smoke_backend_admin_request_metadata_contract.py
python tools/smoke/contracts/smoke_backend_admin_schema_model_contract.py
python tools/smoke/contracts/smoke_backend_admin_schema_field_constraint_contract.py
python tools/smoke/contracts/smoke_backend_admin_request_payload_validation_contract.py
python tools/smoke/contracts/smoke_backend_admin_validation_error_compatibility_contract.py
python tools/smoke/contracts/smoke_backend_admin_request_content_negotiation_contract.py
python tools/smoke/contracts/smoke_backend_admin_request_media_size_boundary_contract.py
python tools/smoke/contracts/smoke_backend_admin_request_header_encoding_contract.py
python tools/smoke/contracts/smoke_backend_admin_request_transport_header_observation_contract.py
python tools/smoke/contracts/smoke_backend_admin_write_replay_safety_contract.py
python tools/smoke/contracts/smoke_admin_frontend_schema_contract_readiness.py
python tools/smoke/contracts/smoke_backend_admin_route_service_legacy_cleanup.py
python tools/smoke/contracts/smoke_backend_admin_service_facade_contract.py
python tools/smoke/frontend/smoke_admin_create_blueprint_api_structure.py
python tools/smoke/game/smoke_save_snapshot_integrity_api_structure.py
python tools/smoke/game/smoke_save_snapshot_api_structure.py

# Some legacy smoke scripts may leave short-lived background jobs/timers open in
# non-interactive shells. Clean them up so CI/container runs can return promptly.
if jobs -pr >/dev/null 2>&1; then
  jobs -pr | xargs -r kill >/dev/null 2>&1 || true
fi

python tools/smoke/contracts/smoke_admin_contract_registry_sync.py
python tools/smoke/contracts/smoke_backend_admin_preview_integration.py
python tools/smoke/backend/smoke_backend_packaging_contract.py
python tools/smoke/backend/smoke_backend_local_cors.py
python tools/smoke/backend/smoke_backend_route_map_report.py
python tools/smoke/backend/smoke_v370_account_auth_backend.py
python tools/smoke/backend/smoke_v370_account_admin_management.py
python tools/smoke/backend/smoke_v371_email_account_backend.py
python tools/smoke/backend/smoke_v371_email_identity_migration_source.py
python tools/smoke/backend/smoke_v371_owner_admin_bootstrap.py
python tools/smoke/backend/smoke_v377_auth_public_security.py
python tools/smoke/backend/smoke_v377_auth_email_outbox.py
python tools/smoke/backend/smoke_v377_auth_security_migration.py
python tools/smoke/backend/smoke_v377_email_security_environment.py
python tools/smoke/backend/smoke_v377_email_release.py
python tools/smoke/backend/smoke_postgres_alembic_readiness.py
python tools/smoke/backend/smoke_backend_alembic_async_env.py
python tools/smoke/backend/smoke_postgres_runtime_readonly_state.py
python tools/smoke/backend/smoke_windows_subprocess_decode.py
python tools/smoke/backend/smoke_postgres_schema_equivalence.py
python tools/smoke/backend/smoke_postgres_backup_restore_preflight.py
python tools/smoke/backend/smoke_postgres_backup_creation.py
python tools/smoke/backend/smoke_postgres_restore_rehearsal_database_creation.py
python tools/smoke/backend/smoke_postgres_restore_rehearsal.py
python tools/smoke/backend/smoke_postgres_migration_test_database_creation.py
# The v295-v310 initial-revision/stamp/round-trip/deployment-readiness smokes
# remain preserved as historical evidence. They assume a single v295 source
# head and must not be replayed against the v377 model graph; the v371 source
# parity plus v377 migration guard smoke above are the current contracts.
python tools/smoke/backend/smoke_runtime_engine_source_binding_inspector.py
python tools/smoke/backend/smoke_runtime_config_hardening.py
python tools/smoke/backend/smoke_neon_production_database_bootstrap.py
python tools/smoke/backend/smoke_production_secrets_tls_container_static.py
python tools/smoke/backend/smoke_production_capacity_tls_network_plan.py
python tools/smoke/backend/smoke_production_managed_postgres_reverse_proxy_selection.py
python tools/smoke/backend/smoke_production_compose_config_render.py
python tools/smoke/backend/smoke_production_deployment_plan.py
python tools/smoke/backend/smoke_production_provider_selection.py
if [[ "${SKIP_GHCR_HANDOFF_SMOKES:-0}" != "1" ]]; then
  python tools/smoke/backend/smoke_github_actions_ghcr_static_plan.py
  python tools/smoke/backend/smoke_codex_handoff_readiness.py
  python tools/smoke/game/smoke_next_chat_handoff.py
fi
python tools/smoke/contracts/smoke_backend_admin_preview_side_effect_contract.py
python tools/smoke/contracts/smoke_backend_admin_service_mutation_boundary_contract.py
python tools/smoke/contracts/smoke_backend_admin_diff_engine_contract.py
python tools/smoke/contracts/smoke_backend_admin_change_log_shared_diff.py
python tools/smoke/contracts/smoke_backend_admin_rollback_snapshot_contract.py
python tools/smoke/contracts/smoke_backend_admin_rollback_preview_snapshot.py

echo "[core smoke] passed"

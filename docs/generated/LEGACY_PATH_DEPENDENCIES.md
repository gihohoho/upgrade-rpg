# Legacy Path Dependencies — v334

이 문서는 `tools/report_legacy_path_dependencies.py`가 현재 프로젝트 파일을 스캔해서 만든 legacy 경로 의존성 보고서입니다.

목적은 Vue/FastAPI/DB 전환 전에 **움직이면 깨질 가능성이 높은 경로**를 먼저 고정하는 것입니다. 이 문서는 새 contract가 아니라 구조 전환 보조 문서입니다.

## v334 결론

- `admin.html`, `index.html`, `src/`, `backend/`, `tools/smoke/`는 아직 이동하지 않습니다.
- 새 Vue 앱은 기존 파일을 대체하지 않고 `frontend/vue-app/`에 별도로 만드는 방식이 가장 안전합니다.
- `legacy/` 폴더로 기존 파일을 옮기는 작업은 smoke 경로 alias/copy 전략이 확정된 뒤에만 진행합니다.
- 문서 구조 정리와 무관하게 DB/env/seed/auth/API body/route/write 로직은 변경하지 않습니다.

## 주요 경로 참조 요약

| 대상 | 존재 | 참조 수 | 참조 파일 수 | 판단 |
| --- | --- | --- | --- | --- |
| `admin.html` | O | 165 | 86 | 절대 이동 금지 |
| `index.html` | O | 120 | 54 | 절대 이동 금지 |
| `src/` | O | 1844 | 188 | 절대 이동 금지 |
| `src/api/` | O | 600 | 149 | Vue 이식 후보이지만 현 위치 유지 |
| `src/api/admin/` | O | 323 | 114 | Vue 관리자 이식 후보이지만 현 위치 유지 |
| `src/data/` | O | 38 | 16 | DB seed 준비 전 이동 금지 |
| `src/rules/` | O | 16 | 9 | 콘텐츠 개발 보류, 현 위치 유지 |
| `src/state/` | O | 10 | 9 | Vue store 후보, 현 위치 유지 |
| `src/systems/` | O | 29 | 12 | domain module 후보, 현 위치 유지 |
| `src/ui/` | O | 13 | 10 | Vue component 대체 후보, 현 위치 유지 |
| `src/styles/` | O | 18 | 13 | Vue CSS 분해 후보, 현 위치 유지 |
| `backend/app/api/routes/` | O | 429 | 65 | route path/contract 보호 |
| `backend/app/services/` | O | 248 | 81 | service contract 보호 |
| `backend/seeds/` | O | 11 | 8 | 사용자 승인 전 변경 금지 |
| `tools/run_smoke_core.sh` | O | 69 | 53 | 검증 기준 유지 |
| `tools/smoke/` | O | 276 | 80 | 경로 의존성 기준 |

## 참조 파일 예시

아래는 각 경로 문자열이 발견된 파일 예시입니다. 전체 목록이 아니라 처음 감지된 일부 예시입니다.

| 대상 | 참조 파일 예시 |
|---|---|
| `admin.html` | `AGENTS.md`<br>`README.md`<br>`admin.html`<br>`deploy/render-static-site.example.json`<br>`deploy/review/render-frontend-static-and-cors-attempt-v349.json`<br>`deploy/review/render-v351-provider-release-v355.json`<br>`docs/CHANGELOG.md`<br>`docs/current/CURRENT_STATUS.md` |
| `index.html` | `AGENTS.md`<br>`README.md`<br>`admin.html`<br>`backend/app/services/auth_email_delivery.py`<br>`deploy/render-static-site.example.json`<br>`deploy/review/render-frontend-static-and-cors-attempt-v349.json`<br>`deploy/review/render-v351-provider-release-v355.json`<br>`docs/CHANGELOG.md` |
| `src/` | `NEXT_CHAT_HANDOFF.md`<br>`README.md`<br>`admin.html`<br>`backend/seeds/generated/drop_table_items.json`<br>`backend/seeds/generated/item_templates.json`<br>`backend/seeds/generated/skills.json`<br>`deploy/render-static-site.example.json`<br>`deploy/review/render-frontend-static-and-cors-attempt-v349.json` |
| `src/api/` | `admin.html`<br>`deploy/render-static-site.example.json`<br>`deploy/review/render-frontend-static-and-cors-attempt-v349.json`<br>`deploy/v351-public-release-gates.example.json`<br>`docs/CHANGELOG.md`<br>`docs/current/FRONTEND_STATIC_DEPLOYMENT_PLAN.md`<br>`docs/reference/backend/BACKEND_ARCHITECTURE.md`<br>`docs/reference/frontend/VUE_FASTAPI_DB_TRANSITION_PLAN.md` |
| `src/api/admin/` | `admin.html`<br>`deploy/review/render-frontend-static-and-cors-attempt-v349.json`<br>`docs/CHANGELOG.md`<br>`docs/reference/frontend/VUE_FASTAPI_DB_TRANSITION_PLAN.md`<br>`docs/reference/frontend/VUE_READONLY_API_CLIENT.md`<br>`index.html`<br>`src/api/admin-page-readonly.js`<br>`src/api/admin/README.md` |
| `src/data/` | `docs/reference/assets/EQUIPMENT_PROGRESSION_FORMULA_AUDIT.md`<br>`docs/reference/frontend/VUE_FASTAPI_DB_TRANSITION_PLAN.md`<br>`index.html`<br>`src/data/README.md`<br>`src/state/STATE_SPLIT_READY.md`<br>`src/ui/render-ui.js`<br>`tools/extract_seed_data.js`<br>`tools/report_legacy_path_dependencies.py` |
| `src/rules/` | `docs/reference/frontend/VUE_FASTAPI_DB_TRANSITION_PLAN.md`<br>`index.html`<br>`src/rules/README.md`<br>`src/state/STATE_SPLIT_READY.md`<br>`tools/extract_seed_data.js`<br>`tools/report_legacy_path_dependencies.py`<br>`tools/smoke/frontend/smoke_action_results.js`<br>`tools/smoke/game/smoke_runtime_item_quality_of_life.js` |
| `src/state/` | `docs/reference/frontend/VUE_FASTAPI_DB_TRANSITION_PLAN.md`<br>`frontend/vue-app/src/stores/README.md`<br>`index.html`<br>`tools/extract_seed_data.js`<br>`tools/report_legacy_path_dependencies.py`<br>`tools/smoke/frontend/smoke_action_results.js`<br>`tools/smoke/game/smoke_runtime_item_quality_of_life.js`<br>`tools/smoke/game/smoke_runtime_stackable_items.js` |
| `src/systems/` | `deploy/review/render-frontend-static-and-cors-attempt-v349.json`<br>`docs/reference/assets/EQUIPMENT_PROGRESSION_FORMULA_AUDIT.md`<br>`docs/reference/frontend/VUE_FASTAPI_DB_TRANSITION_PLAN.md`<br>`index.html`<br>`tools/extract_seed_data.js`<br>`tools/report_legacy_path_dependencies.py`<br>`tools/smoke/frontend/smoke_action_results.js`<br>`tools/smoke/frontend/smoke_v370_account_character_gate.js` |
| `src/ui/` | `docs/reference/frontend/VUE_FASTAPI_DB_TRANSITION_PLAN.md`<br>`index.html`<br>`tools/check_frontend_static_deployment_plan.py`<br>`tools/report_legacy_path_dependencies.py`<br>`tools/smoke/frontend/smoke_action_results.js`<br>`tools/smoke/frontend/smoke_v370_account_character_gate.js`<br>`tools/smoke/frontend/smoke_v371_email_account_frontend.js`<br>`tools/smoke/game/smoke_runtime_item_quality_of_life.js` |
| `src/styles/` | `NEXT_CHAT_HANDOFF.md`<br>`admin.html`<br>`docs/reference/frontend/VUE_FASTAPI_DB_TRANSITION_PLAN.md`<br>`index.html`<br>`tools/report_legacy_path_dependencies.py`<br>`tools/smoke/frontend/smoke_v370_account_character_gate.js`<br>`tools/smoke/frontend/smoke_v370_admin_account_management.js`<br>`tools/smoke/frontend/smoke_v371_email_account_frontend.js` |
| `backend/app/api/routes/` | `backend/app/api/routes/admin_openapi_route_contract.py`<br>`backend/app/api/routes/admin_request_metadata_contract.py`<br>`backend/app/api/routes/admin_response_metadata_contract.py`<br>`backend/app/api/routes/admin_route_map_contract.py`<br>`backend/app/api/routes/admin_route_module_import_contract.py`<br>`backend/app/api/routes/admin_route_operation_contract.py`<br>`backend/app/api/routes/admin_route_services.py`<br>`backend/app/api/routes/admin_runtime_route_contract.py` |
| `backend/app/services/` | `backend/app/api/routes/admin_preview_side_effect_contract.py`<br>`backend/app/api/routes/admin_route_error_helpers.py`<br>`backend/app/api/routes/admin_service_mutation_boundary_contract.py`<br>`backend/app/services/admin/README.md`<br>`backend/app/services/admin/admin_shared_utils.py`<br>`backend/app/services/admin_service.py`<br>`backend/app/services/admin_service_facade_contract.py`<br>`backend/app/services/admin_service_legacy_markers.py` |
| `backend/seeds/` | `backend/seeds/README.md`<br>`docs/CHANGELOG.md`<br>`docs/guides/LOCAL_DEV_SETUP.md`<br>`tools/extract_seed_data.js`<br>`tools/report_legacy_path_dependencies.py`<br>`tools/smoke/game/smoke_equipment_progression_formulas.js`<br>`tools/smoke/game/smoke_runtime_item_quality_of_life.js`<br>`tools/smoke/game/smoke_seed_extraction.js` |
| `tools/run_smoke_core.sh` | `.github/workflows/publish-backend-ghcr.yml`<br>`AGENTS.md`<br>`deploy/github-actions-ghcr-static-plan.example.json`<br>`docs/CHANGELOG.md`<br>`docs/current/ACCOUNT_AUTH_AND_CHARACTER_SLOTS.md`<br>`docs/current/ACCOUNT_EMAIL_VERIFICATION_RECOVERY_AND_DELETION.md`<br>`docs/current/CURRENT_STATUS.md`<br>`docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md` |
| `tools/smoke/` | `backend/README.md`<br>`backend/seeds/README.md`<br>`deploy/github-actions-ghcr-static-plan.example.json`<br>`deploy/neon-database-initialization-migration.example.json`<br>`docs/CHANGELOG.md`<br>`docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md`<br>`docs/guides/LOCAL_DEV_SETUP.md`<br>`docs/guides/MASTER_DATA_BROWSER_CHECKLIST.md` |

## HTML 진입점 직접 로드 관계

현재 legacy 화면은 HTML이 JS/CSS를 직접 로드합니다. Vue 이식 전까지 이 순서를 유지해야 합니다.

### `admin.html` 직접 로드 파일

- `src/styles/account-admin.css?v=371`
- `src/api/runtime-config.js`
- `src/api/auth-session.js?v=371`
- `src/api/game-api-client.js?v=371`
- `src/api/admin-layout-shell.js`
- `src/api/admin/admin-workspace-navigation.js`
- `src/api/admin/admin-field-help.js`
- `src/api/admin/admin-settings-helpers.js`
- `src/api/admin/admin-preview-diff.js`
- `src/api/admin/admin-preview-verification.js`
- `src/api/admin/admin-change-logs.js`
- `src/api/admin/admin-create-lifecycle.js`
- `src/api/admin/admin-edit-draft.js`
- `src/api/admin/admin-preview-live-verification.js`
- `src/api/admin/admin-long-value-modal.js`
- `src/api/admin/admin-button-safety.js`
- `src/api/admin/admin-master-catalog.js`
- `src/api/admin/admin-detail-shortcuts.js`
- `src/api/admin/admin-overview-snapshots.js`
- `src/api/admin/admin-account-management.js?v=371`
- `src/api/admin-page-readonly.js?v=370`

### `index.html` 직접 로드 파일

- `src/styles/style.css?v=362`
- `src/styles/account.css?v=371`
- `src/api/runtime-config.js`
- `src/api/auth-session.js?v=371`
- `src/api/game-api-client.js?v=371`
- `src/api/save-data-bridge.js?v=370`
- `src/api/save-data-slots.js?v=370`
- `src/api/admin-readonly-overview.js?v=370`
- `src/api/save-data-sync-policy.js?v=370`
- `src/api/save-data-preview.js?v=370`
- `src/api/save-data-integrity.js?v=370`
- `src/api/save-data-restore-guard.js?v=370`
- `src/api/master-data-bridge.js`
- `src/api/master-data-adapter.js`
- `src/api/master-data-boot-policy.js`
- `src/data/skills.js?v=369`
- `src/state/game-state.js?v=362`
- `src/utils/icon-utils.js?v=369`
- `src/data/boss-factories.js`
- `src/data/bosses.js`
- `src/rules/abyss-fragment-rules.js`
- `src/rules/boss-display-rules.js?v=369`
- `src/rules/boss-drop-rules.js?v=362`
- `src/data/boss-bootstrap.js`
- `src/data/zones.js?v=360`
- `src/systems/stat-system.js?v=360`
- `src/ui/render-ui.js?v=371`
- `src/systems/action-result-system.js?v=360`
- `src/systems/item-system.js?v=363`
- `src/systems/combat-system.js?v=370`
- `src/ui/account-gate.js?v=371`
- `src/app/main.js?v=370`
- `src/api/master-data-runtime-switch.js?v=369`
- `src/api/master-data-runtime-validator.js`
- `src/api/master-data-browser-checklist.js`
- `src/api/master-data-dev-badge.js`
- `src/api/save-data-dev-badge.js?v=370`

## core smoke 실행 목록

`tools/run_smoke_core.sh`가 직접 실행하는 검사 목록입니다. 파일 이동 전에는 이 목록의 경로 의존성을 먼저 확인해야 합니다.

| 순서 | 명령 |
| --- | --- |
| 1 | `node tools/smoke/game/smoke_docs_index_archive.js` |
| 2 | `node tools/smoke/game/smoke_equipment_progression_formulas.js` |
| 3 | `python tools/check_runtime_blocking_io.py` |
| 4 | `python tools/smoke/backend/smoke_master_data_latency_guard.py` |
| 5 | `node tools/smoke/game/smoke_master_data_auto_boot_policy.js` |
| 6 | `python tools/check_frontend_static_deployment_plan.py` |
| 7 | `node tools/smoke/frontend/smoke_legacy_static_deployment_preparation.js` |
| 8 | `node tools/smoke/frontend/smoke_admin_edit_stale_guard.js` |
| 9 | `node tools/smoke/frontend/smoke_admin_write_dev_key_guard.js` |
| 10 | `node tools/smoke/frontend/smoke_admin_guarded_edit_apply.js` |
| 11 | `node tools/smoke/frontend/smoke_admin_change_log_rollback.js` |
| 12 | `node tools/smoke/frontend/smoke_admin_rollback_snapshot_preview.js` |
| 13 | `node tools/smoke/frontend/smoke_admin_preview_result_summary.js` |
| 14 | `node tools/smoke/frontend/smoke_admin_preview_browser_verification.js` |
| 15 | `node tools/smoke/frontend/smoke_admin_preview_live_api_render_check.js` |
| 16 | `node tools/smoke/frontend/smoke_admin_workspace_navigation.js` |
| 17 | `node tools/smoke/frontend/smoke_admin_catalog_help_compact_ux.js` |
| 18 | `node tools/smoke/frontend/smoke_admin_practical_ux_bundle.js` |
| 19 | `node tools/smoke/frontend/smoke_admin_create_blueprint_readonly.js` |
| 20 | `node tools/smoke/frontend/smoke_admin_create_draft_preview.js` |
| 21 | `node tools/smoke/frontend/smoke_admin_create_apply_limited.js` |
| 22 | `node tools/smoke/frontend/smoke_admin_create_apply_fieldzones.js` |
| 23 | `node tools/smoke/frontend/smoke_admin_create_apply_bosses.js` |
| 24 | `node tools/smoke/frontend/smoke_admin_create_apply_skills_droptables.js` |
| 25 | `node tools/smoke/frontend/smoke_admin_create_apply_items_dropitems.js` |
| 26 | `node tools/smoke/frontend/smoke_admin_create_apply_level_links.js` |
| 27 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_guide.js` |
| 28 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_guard_helper.js` |
| 29 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_result_summary.js` |
| 30 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_batch_check.js` |
| 31 | `node tools/smoke/frontend/smoke_admin_js_split_readiness.js` |
| 32 | `node tools/smoke/frontend/smoke_admin_layout_shell_split.js` |
| 33 | `node tools/smoke/frontend/smoke_admin_change_log_split_contract.js` |
| 34 | `node tools/smoke/frontend/smoke_admin_change_logs_split.js` |
| 35 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_split_contract.js` |
| 36 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_split.js` |
| 37 | `node tools/smoke/frontend/smoke_admin_edit_draft_split_contract.js` |
| 38 | `node tools/smoke/frontend/smoke_admin_edit_draft_split.js` |
| 39 | `node tools/smoke/frontend/smoke_admin_master_catalog_split.js` |
| 40 | `node tools/smoke/frontend/smoke_admin_overview_snapshots_split.js` |
| 41 | `node tools/smoke/frontend/smoke_admin_field_help_split.js` |
| 42 | `node tools/smoke/frontend/smoke_admin_settings_helpers_split.js` |
| 43 | `node tools/smoke/frontend/smoke_admin_bootstrap_bindings_readiness.js` |
| 44 | `node tools/smoke/frontend/smoke_admin_thin_entry_cleanup.js` |
| 45 | `node tools/smoke/frontend/smoke_v370_admin_account_management.js` |
| 46 | `node tools/smoke/frontend/smoke_v370_account_character_gate.js` |
| 47 | `node tools/smoke/frontend/smoke_v371_email_account_frontend.js` |
| 48 | `node tools/smoke/frontend/smoke_admin_create_delete_rollback.js` |
| 49 | `node tools/smoke/frontend/smoke_admin_create_delete_restore.js` |
| 50 | `node tools/smoke/frontend/smoke_admin_layout_navigation_shell.js` |
| 51 | `node tools/smoke/frontend/smoke_admin_post_edit_api_verify.js` |
| 52 | `node tools/smoke/frontend/smoke_admin_master_api_verify.js` |
| 53 | `node tools/smoke/game/smoke_runtime_stacked_enhance_space_guard.js` |
| 54 | `node tools/smoke/game/smoke_runtime_stackable_items.js` |
| 55 | `node tools/smoke/game/smoke_runtime_item_quality_of_life.js` |
| 56 | `node tools/smoke/game/smoke_save_data_integrity_verify.js` |
| 57 | `node tools/smoke/game/smoke_save_data_restore_reload_lock.js` |
| 58 | `node tools/smoke/game/smoke_save_data_restore_guard.js` |
| 59 | `python tools/smoke/frontend/smoke_admin_change_log_filter_binding.py` |
| 60 | `python tools/smoke/frontend/smoke_admin_change_logs_schema_guard.py` |
| 61 | `python tools/smoke/frontend/smoke_admin_readonly_api_structure.py` |
| 62 | `python tools/smoke/contracts/smoke_backend_admin_service_split_contract.py` |
| 63 | `python tools/smoke/contracts/smoke_backend_admin_overview_snapshots_service_split.py` |
| 64 | `python tools/smoke/contracts/smoke_backend_admin_master_catalog_service_split.py` |
| 65 | `python tools/smoke/contracts/smoke_backend_admin_create_lifecycle_service_split.py` |
| 66 | `python tools/smoke/contracts/smoke_backend_admin_change_log_service_split.py` |
| 67 | `python tools/smoke/contracts/smoke_backend_admin_edit_draft_service_split.py` |
| 68 | `python tools/smoke/contracts/smoke_backend_admin_shared_utils_service_split.py` |
| 69 | `python tools/smoke/contracts/smoke_backend_admin_config_readiness_service_split.py` |
| 70 | `python tools/smoke/contracts/smoke_backend_admin_route_response_helper.py` |
| 71 | `python tools/smoke/contracts/smoke_backend_admin_route_params_error_helpers.py` |
| 72 | `python tools/smoke/contracts/smoke_backend_admin_route_response_data_meta_helpers.py` |
| 73 | `python tools/smoke/contracts/smoke_backend_admin_route_module_split.py` |
| 74 | `python tools/smoke/contracts/smoke_backend_admin_overview_route_module_split.py` |
| 75 | `python tools/smoke/contracts/smoke_backend_admin_route_map_contract.py` |
| 76 | `python tools/smoke/contracts/smoke_backend_admin_route_module_import_contract.py` |
| 77 | `python tools/smoke/contracts/smoke_backend_admin_runtime_route_contract.py` |
| 78 | `python tools/smoke/contracts/smoke_backend_admin_route_operation_contract.py` |
| 79 | `python tools/smoke/contracts/smoke_backend_admin_openapi_route_contract.py` |
| 80 | `python tools/smoke/contracts/smoke_backend_admin_response_metadata_contract.py` |
| 81 | `python tools/smoke/contracts/smoke_backend_admin_request_metadata_contract.py` |
| 82 | `python tools/smoke/contracts/smoke_backend_admin_schema_model_contract.py` |
| 83 | `python tools/smoke/contracts/smoke_backend_admin_schema_field_constraint_contract.py` |
| 84 | `python tools/smoke/contracts/smoke_backend_admin_request_payload_validation_contract.py` |
| 85 | `python tools/smoke/contracts/smoke_backend_admin_validation_error_compatibility_contract.py` |
| 86 | `python tools/smoke/contracts/smoke_backend_admin_request_content_negotiation_contract.py` |
| 87 | `python tools/smoke/contracts/smoke_backend_admin_request_media_size_boundary_contract.py` |
| 88 | `python tools/smoke/contracts/smoke_backend_admin_request_header_encoding_contract.py` |
| 89 | `python tools/smoke/contracts/smoke_backend_admin_request_transport_header_observation_contract.py` |
| 90 | `python tools/smoke/contracts/smoke_backend_admin_write_replay_safety_contract.py` |
| 91 | `python tools/smoke/contracts/smoke_admin_frontend_schema_contract_readiness.py` |
| 92 | `python tools/smoke/contracts/smoke_backend_admin_route_service_legacy_cleanup.py` |
| 93 | `python tools/smoke/contracts/smoke_backend_admin_service_facade_contract.py` |
| 94 | `python tools/smoke/frontend/smoke_admin_create_blueprint_api_structure.py` |
| 95 | `python tools/smoke/game/smoke_save_snapshot_integrity_api_structure.py` |
| 96 | `python tools/smoke/game/smoke_save_snapshot_api_structure.py` |
| 97 | `python tools/smoke/contracts/smoke_admin_contract_registry_sync.py` |
| 98 | `python tools/smoke/contracts/smoke_backend_admin_preview_integration.py` |
| 99 | `python tools/smoke/backend/smoke_backend_packaging_contract.py` |
| 100 | `python tools/smoke/backend/smoke_backend_local_cors.py` |
| 101 | `python tools/smoke/backend/smoke_backend_route_map_report.py` |
| 102 | `python tools/smoke/backend/smoke_v370_account_auth_backend.py` |
| 103 | `python tools/smoke/backend/smoke_v370_account_admin_management.py` |
| 104 | `python tools/smoke/backend/smoke_v371_email_account_backend.py` |
| 105 | `python tools/smoke/backend/smoke_v371_email_identity_migration_source.py` |
| 106 | `python tools/smoke/backend/smoke_v371_owner_admin_bootstrap.py` |
| 107 | `python tools/smoke/backend/smoke_postgres_alembic_readiness.py` |
| 108 | `python tools/smoke/backend/smoke_backend_alembic_async_env.py` |
| 109 | `python tools/smoke/backend/smoke_postgres_runtime_readonly_state.py` |
| 110 | `python tools/smoke/backend/smoke_windows_subprocess_decode.py` |
| 111 | `python tools/smoke/backend/smoke_postgres_schema_equivalence.py` |
| 112 | `python tools/smoke/backend/smoke_postgres_backup_restore_preflight.py` |
| 113 | `python tools/smoke/backend/smoke_postgres_backup_creation.py` |
| 114 | `python tools/smoke/backend/smoke_postgres_restore_rehearsal_database_creation.py` |
| 115 | `python tools/smoke/backend/smoke_postgres_restore_rehearsal.py` |
| 116 | `python tools/smoke/backend/smoke_postgres_migration_test_database_creation.py` |
| 117 | `python tools/smoke/backend/smoke_runtime_engine_source_binding_inspector.py` |
| 118 | `python tools/smoke/backend/smoke_runtime_config_hardening.py` |
| 119 | `python tools/smoke/backend/smoke_neon_production_database_bootstrap.py` |
| 120 | `python tools/smoke/backend/smoke_production_secrets_tls_container_static.py` |
| 121 | `python tools/smoke/backend/smoke_production_capacity_tls_network_plan.py` |
| 122 | `python tools/smoke/backend/smoke_production_managed_postgres_reverse_proxy_selection.py` |
| 123 | `python tools/smoke/backend/smoke_production_compose_config_render.py` |
| 124 | `python tools/smoke/backend/smoke_production_deployment_plan.py` |
| 125 | `python tools/smoke/backend/smoke_production_provider_selection.py` |
| 126 | `python tools/smoke/contracts/smoke_backend_admin_preview_side_effect_contract.py` |
| 127 | `python tools/smoke/contracts/smoke_backend_admin_service_mutation_boundary_contract.py` |
| 128 | `python tools/smoke/contracts/smoke_backend_admin_diff_engine_contract.py` |
| 129 | `python tools/smoke/contracts/smoke_backend_admin_change_log_shared_diff.py` |
| 130 | `python tools/smoke/contracts/smoke_backend_admin_rollback_snapshot_contract.py` |
| 131 | `python tools/smoke/contracts/smoke_backend_admin_rollback_preview_snapshot.py` |

## smoke 내부에서 많이 발견된 경로 문자열

| 경로 문자열 | smoke 참조 수 |
| --- | --- |
| `admin.html` | 114 |
| `src/api/admin-page-readonly.js` | 111 |
| `index.html` | 59 |
| `src/api/game-api-client.js` | 45 |
| `src/api/save-data-dev-badge.js` | 44 |
| `tools/run_smoke_core.sh` | 43 |
| `backend/app/services/admin_service_legacy_markers.py` | 37 |
| `src/api/save-data-restore-guard.js` | 32 |
| `backend/app/api/routes/admin_master_data_routes.py` | 24 |
| `src/api/admin/admin-change-logs.js` | 22 |
| `backend/app/api/routes/admin_change_log_routes.py` | 19 |
| `src/api/save-data-sync-policy.js` | 19 |
| `src/api/admin/admin-create-lifecycle.js` | 18 |
| `backend/app/services/admin_service_split_contract.py` | 17 |
| `src/api/admin/admin-edit-draft.js` | 16 |
| `src/app/main.js` | 16 |
| `src/api/admin/admin-master-catalog.js` | 15 |
| `src/api/admin-layout-shell.js` | 14 |
| `src/pages/AdminShell.vue` | 13 |
| `src/api/master-data-runtime-switch.js` | 12 |
| `backend/app/api/routes/admin_response_data_helpers.py` | 11 |
| `src/api/admin/admin-field-help.js` | 11 |
| `backend/app/services/admin_service.py` | 10 |
| `backend/app/services/admin/__init__.py` | 10 |
| `src/api/save-data-preview.js` | 10 |
| `backend/app/schemas/admin.py` | 9 |
| `src/utils/icon-utils.js` | 9 |
| `src/systems/item-system.js` | 9 |
| `src/api/admin/admin-overview-snapshots.js` | 9 |
| `backend/app/api/routes/game.py` | 8 |
| `backend/app/services/game_service.py` | 8 |
| `backend/app/api/routes/admin_overview_snapshot_routes.py` | 8 |
| `backend/app/api/routes/admin_route_params.py` | 8 |
| `src/api/master-data-adapter.js` | 8 |
| `backend/app/api/routes/admin.py` | 7 |
| `src/data/skills.js` | 7 |
| `src/systems/combat-system.js` | 7 |
| `src/api/admin/admin-settings-helpers.js` | 7 |
| `src/styles/base.css` | 7 |
| `src/pages/GameShell.vue` | 7 |

## Vue 앱 생성 위치 결정

### 결정

새 Vue 앱은 다음 위치에 생성하는 것이 안전합니다.

```txt
frontend/vue-app/
```

### 이유

- 기존 `src/`는 현재 Vue 소스 폴더가 아니라 legacy 브라우저 JS/CSS 폴더입니다.
- Vite/Vue 기본 `src/`와 현재 legacy `src/`가 충돌하면 기호가 나중에 파일 위치를 구분하기 어려워집니다.
- `admin.html`과 `index.html`이 루트에서 `src/...`를 직접 읽고 있어서, 현재 `src/`를 Vue 앱용으로 재사용하면 기존 smoke가 깨질 가능성이 큽니다.
- `frontend/vue-app/`는 기존 legacy와 분리되어 있어서, Vue shell을 만들어도 기존 게임/관리자 화면을 그대로 검증할 수 있습니다.

### 아직 하지 않을 것

- `admin.html` 이동
- `index.html` 이동
- 기존 `src/` 이름 변경
- `legacy/` 폴더로 대이동
- Vue 앱에서 기존 route/API body 변경
- DB/env/seed/auth/write guard 변경

## 재생성 방법

실행 위치: 프로젝트 루트
Python `.venv` 상태: `backend/.venv` 사용
새 설치 여부: 없음

```bash
python tools/report_legacy_path_dependencies.py --write
```

검사만 할 때:

실행 위치: 프로젝트 루트
Python `.venv` 상태: `backend/.venv` 사용
새 설치 여부: 없음

```bash
python tools/report_legacy_path_dependencies.py --check
```

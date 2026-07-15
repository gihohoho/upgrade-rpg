# Legacy Path Dependencies — v269

이 문서는 `tools/report_legacy_path_dependencies.py`가 현재 프로젝트 파일을 스캔해서 만든 legacy 경로 의존성 보고서입니다.

목적은 Vue/FastAPI/DB 전환 전에 **움직이면 깨질 가능성이 높은 경로**를 먼저 고정하는 것입니다. 이 문서는 새 contract가 아니라 구조 전환 보조 문서입니다.

## v269 결론

- `admin.html`, `index.html`, `src/`, `backend/`, `tools/smoke/`는 아직 이동하지 않습니다.
- 새 Vue 앱은 기존 파일을 대체하지 않고 `frontend/vue-app/`에 별도로 만드는 방식이 가장 안전합니다.
- `legacy/` 폴더로 기존 파일을 옮기는 작업은 smoke 경로 alias/copy 전략이 확정된 뒤에만 진행합니다.
- 이번 단계에서는 DB/env/seed/auth/API body/route/write 로직을 변경하지 않습니다.

## 주요 경로 참조 요약

| 대상 | 존재 | 참조 수 | 참조 파일 수 | 판단 |
| --- | --- | --- | --- | --- |
| `admin.html` | O | 262 | 136 | 절대 이동 금지 |
| `index.html` | O | 133 | 64 | 절대 이동 금지 |
| `src/` | O | 1505 | 306 | 절대 이동 금지 |
| `src/api/` | O | 1042 | 271 | Vue 이식 후보이지만 현 위치 유지 |
| `src/api/admin/` | O | 580 | 217 | Vue 관리자 이식 후보이지만 현 위치 유지 |
| `src/data/` | O | 64 | 23 | DB seed 준비 전 이동 금지 |
| `src/rules/` | O | 25 | 11 | 콘텐츠 개발 보류, 현 위치 유지 |
| `src/state/` | O | 12 | 10 | Vue store 후보, 현 위치 유지 |
| `src/systems/` | O | 49 | 19 | domain module 후보, 현 위치 유지 |
| `src/ui/` | O | 14 | 11 | Vue component 대체 후보, 현 위치 유지 |
| `src/styles/` | O | 19 | 9 | Vue CSS 분해 후보, 현 위치 유지 |
| `backend/app/api/routes/` | O | 527 | 118 | route path/contract 보호 |
| `backend/app/services/` | O | 389 | 150 | service contract 보호 |
| `backend/seeds/` | O | 21 | 10 | 사용자 승인 전 변경 금지 |
| `tools/run_smoke_core.sh` | O | 115 | 103 | 검증 기준 유지 |
| `tools/smoke/` | O | 384 | 164 | 경로 의존성 기준 |

## 참조 파일 예시

아래는 각 경로 문자열이 발견된 파일 예시입니다. 전체 목록이 아니라 처음 감지된 일부 예시입니다.

| 대상 | 참조 파일 예시 |
|---|---|
| `admin.html` | `AGENTS.md`<br>`CHANGELOG.md`<br>`README.md`<br>`admin.html`<br>`docs/ADMIN_CHANGE_LOGS_SPLIT.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_SPLIT.md`<br>`docs/ADMIN_LAYOUT_NAVIGATION_SHELL.md`<br>`docs/ADMIN_LAYOUT_SHELL_SPLIT.md` |
| `index.html` | `AGENTS.md`<br>`CHANGELOG.md`<br>`README.md`<br>`admin.html`<br>`docs/CHANGELOG.md`<br>`docs/archive/stage-notes/ADMIN_PAGE_URL_HELPER.md`<br>`docs/archive/stage-notes/ADMIN_READONLY_PAGE.md`<br>`docs/archive/stage-notes/CODE_MAP.md` |
| `src/` | `AGENTS.md`<br>`CHANGELOG.md`<br>`README.md`<br>`admin.html`<br>`docs/ADMIN_CHANGE_LOGS_SPLIT.md`<br>`docs/ADMIN_CHANGE_LOG_SPLIT_CONTRACT.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_SPLIT.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT.md` |
| `src/api/` | `CHANGELOG.md`<br>`admin.html`<br>`docs/ADMIN_CHANGE_LOGS_SPLIT.md`<br>`docs/ADMIN_CHANGE_LOG_SPLIT_CONTRACT.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_SPLIT.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT.md`<br>`docs/ADMIN_EDIT_DRAFT_SPLIT.md`<br>`docs/ADMIN_EDIT_DRAFT_SPLIT_CONTRACT.md` |
| `src/api/admin/` | `CHANGELOG.md`<br>`admin.html`<br>`docs/ADMIN_CHANGE_LOGS_SPLIT.md`<br>`docs/ADMIN_CHANGE_LOG_SPLIT_CONTRACT.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_SPLIT.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT.md`<br>`docs/ADMIN_EDIT_DRAFT_SPLIT.md`<br>`docs/ADMIN_EDIT_DRAFT_SPLIT_CONTRACT.md` |
| `src/data/` | `docs/MASTER_DATA_PARITY_CHECKER.md`<br>`docs/archive/stage-notes/BACKEND_SPLIT_CHECKLIST.md`<br>`docs/archive/stage-notes/BACKEND_SPLIT_STAGE2_PLAN.md`<br>`docs/archive/stage-notes/CODE_MAP.md`<br>`docs/archive/stage-notes/FRONTEND_MASTER_DATA_BRIDGE.md`<br>`docs/archive/stage-notes/SEED_EXTRACTION.md`<br>`docs/archive/stage-notes/SKILL_DAMAGE_TEXT_FIX.md`<br>`docs/archive/stage-notes/SKILL_STRUCTURE_READY.md` |
| `src/rules/` | `docs/archive/stage-notes/BACKEND_SPLIT_CHECKLIST.md`<br>`docs/archive/stage-notes/BACKEND_SPLIT_STAGE2_PLAN.md`<br>`docs/archive/stage-notes/CODE_MAP.md`<br>`docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`<br>`index.html`<br>`src/rules/README.md`<br>`src/state/STATE_SPLIT_READY.md`<br>`tools/extract_seed_data.js` |
| `src/state/` | `docs/archive/stage-notes/BACKEND_SPLIT_STAGE2_PLAN.md`<br>`docs/archive/stage-notes/CODE_MAP.md`<br>`docs/archive/stage-notes/SKILL_STRUCTURE_READY.md`<br>`docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`<br>`frontend/vue-app/src/stores/README.md`<br>`index.html`<br>`tools/extract_seed_data.js`<br>`tools/report_legacy_path_dependencies.py` |
| `src/systems/` | `docs/archive/stage-notes/BACKEND_SPLIT_CHECKLIST.md`<br>`docs/archive/stage-notes/BACKEND_SPLIT_STAGE2_PLAN.md`<br>`docs/archive/stage-notes/CODE_MAP.md`<br>`docs/archive/stage-notes/DAMAGE_TEXT_POSITION_FIX.md`<br>`docs/archive/stage-notes/EQUIP_SKILL_BOSS_RESULT_STAGE3.md`<br>`docs/archive/stage-notes/KILL_REWARD_RESULT_STAGE2.md`<br>`docs/archive/stage-notes/SEED_EXTRACTION.md`<br>`docs/archive/stage-notes/SKILL_STRUCTURE_READY.md` |
| `src/ui/` | `docs/archive/stage-notes/CODE_MAP.md`<br>`docs/archive/stage-notes/EQUIP_SKILL_BOSS_RESULT_STAGE3.md`<br>`docs/archive/stage-notes/MASTER_DATA_FIELD_ZONE_ASSET_FALLBACK.md`<br>`docs/archive/stage-notes/SKILL_STRUCTURE_READY.md`<br>`docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`<br>`index.html`<br>`tools/report_legacy_path_dependencies.py`<br>`tools/smoke/frontend/smoke_action_results.js` |
| `src/styles/` | `docs/archive/stage-notes/CSS_AUDIT.md`<br>`docs/archive/stage-notes/CSS_MERGE_REPORT.md`<br>`docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`<br>`index.html`<br>`tools/report_legacy_path_dependencies.py`<br>`tools/smoke/frontend/smoke_vue_admin_readonly_catalog_panel.py`<br>`tools/smoke/frontend/smoke_vue_admin_readonly_relations_panel.py`<br>`tools/smoke/frontend/smoke_vue_readonly_api_status_panel.py` |
| `backend/app/api/routes/` | `CHANGELOG.md`<br>`backend/app/api/routes/admin_openapi_route_contract.py`<br>`backend/app/api/routes/admin_request_metadata_contract.py`<br>`backend/app/api/routes/admin_response_metadata_contract.py`<br>`backend/app/api/routes/admin_route_map_contract.py`<br>`backend/app/api/routes/admin_route_module_import_contract.py`<br>`backend/app/api/routes/admin_route_operation_contract.py`<br>`backend/app/api/routes/admin_route_services.py` |
| `backend/app/services/` | `CHANGELOG.md`<br>`backend/app/api/routes/admin_preview_side_effect_contract.py`<br>`backend/app/api/routes/admin_route_error_helpers.py`<br>`backend/app/api/routes/admin_service_mutation_boundary_contract.py`<br>`backend/app/services/admin/README.md`<br>`backend/app/services/admin/admin_shared_utils.py`<br>`backend/app/services/admin_service.py`<br>`backend/app/services/admin_service_facade_contract.py` |
| `backend/seeds/` | `backend/seeds/README.md`<br>`docs/CHANGELOG.md`<br>`docs/LOCAL_DEV_SETUP.md`<br>`docs/MASTER_DATA_PARITY_CHECKER.md`<br>`docs/archive/stage-notes/SEED_EXTRACTION.md`<br>`docs/archive/stage-notes/SEED_IMPORT.md`<br>`tools/extract_seed_data.js`<br>`tools/report_legacy_path_dependencies.py` |
| `tools/run_smoke_core.sh` | `AGENTS.md`<br>`CHANGELOG.md`<br>`NEXT_CHAT_PROMPT.md`<br>`docs/ADMIN_CHANGE_LOGS_SPLIT.md`<br>`docs/ADMIN_CHANGE_LOG_SPLIT_CONTRACT.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_GUIDE.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_SPLIT.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT.md` |
| `tools/smoke/` | `CHANGELOG.md`<br>`backend/README.md`<br>`backend/seeds/README.md`<br>`docs/ADMIN_BOOTSTRAP_BINDINGS_READINESS.md`<br>`docs/ADMIN_CATALOG_COMPACT_HELP_UX.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_GUIDE.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_SPLIT.md`<br>`docs/ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT.md` |

## HTML 진입점 직접 로드 관계

현재 legacy 화면은 HTML이 JS/CSS를 직접 로드합니다. Vue 이식 전까지 이 순서를 유지해야 합니다.

### `admin.html` 직접 로드 파일

- `src/api/game-api-client.js`
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
- `src/api/admin-page-readonly.js`

### `index.html` 직접 로드 파일

- `src/styles/style.css`
- `src/api/game-api-client.js`
- `src/api/save-data-bridge.js`
- `src/api/save-data-slots.js`
- `src/api/admin-readonly-overview.js`
- `src/api/save-data-sync-policy.js`
- `src/api/save-data-preview.js`
- `src/api/save-data-integrity.js`
- `src/api/save-data-restore-guard.js`
- `src/api/master-data-bridge.js`
- `src/api/master-data-adapter.js`
- `src/api/master-data-boot-policy.js`
- `src/data/skills.js`
- `src/state/game-state.js`
- `src/utils/icon-utils.js`
- `src/data/boss-factories.js`
- `src/data/bosses.js`
- `src/rules/abyss-fragment-rules.js`
- `src/rules/boss-display-rules.js`
- `src/rules/boss-drop-rules.js`
- `src/data/boss-bootstrap.js`
- `src/data/zones.js`
- `src/systems/stat-system.js`
- `src/ui/render-ui.js`
- `src/systems/action-result-system.js`
- `src/systems/item-system.js`
- `src/systems/combat-system.js`
- `src/app/main.js`
- `src/api/master-data-runtime-switch.js`
- `src/api/master-data-runtime-validator.js`
- `src/api/master-data-browser-checklist.js`
- `src/api/master-data-dev-badge.js`
- `src/api/save-data-dev-badge.js`

## core smoke 실행 목록

`tools/run_smoke_core.sh`가 직접 실행하는 검사 목록입니다. 파일 이동 전에는 이 목록의 경로 의존성을 먼저 확인해야 합니다.

| 순서 | 명령 |
| --- | --- |
| 1 | `node tools/smoke_docs_index_archive.js` |
| 2 | `node tools/smoke/frontend/smoke_admin_edit_stale_guard.js` |
| 3 | `node tools/smoke/frontend/smoke_admin_write_dev_key_guard.js` |
| 4 | `node tools/smoke/frontend/smoke_admin_guarded_edit_apply.js` |
| 5 | `node tools/smoke/frontend/smoke_admin_change_log_rollback.js` |
| 6 | `node tools/smoke/frontend/smoke_admin_rollback_snapshot_preview.js` |
| 7 | `node tools/smoke/frontend/smoke_admin_preview_result_summary.js` |
| 8 | `node tools/smoke/frontend/smoke_admin_preview_browser_verification.js` |
| 9 | `node tools/smoke/frontend/smoke_admin_preview_live_api_render_check.js` |
| 10 | `node tools/smoke/frontend/smoke_admin_workspace_navigation.js` |
| 11 | `node tools/smoke/frontend/smoke_admin_catalog_help_compact_ux.js` |
| 12 | `node tools/smoke/frontend/smoke_admin_practical_ux_bundle.js` |
| 13 | `node tools/smoke/frontend/smoke_admin_create_blueprint_readonly.js` |
| 14 | `node tools/smoke/frontend/smoke_admin_create_draft_preview.js` |
| 15 | `node tools/smoke/frontend/smoke_admin_create_apply_limited.js` |
| 16 | `node tools/smoke/frontend/smoke_admin_create_apply_fieldzones.js` |
| 17 | `node tools/smoke/frontend/smoke_admin_create_apply_bosses.js` |
| 18 | `node tools/smoke/frontend/smoke_admin_create_apply_skills_droptables.js` |
| 19 | `node tools/smoke/frontend/smoke_admin_create_apply_items_dropitems.js` |
| 20 | `node tools/smoke/frontend/smoke_admin_create_apply_level_links.js` |
| 21 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_guide.js` |
| 22 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_guard_helper.js` |
| 23 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_result_summary.js` |
| 24 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_batch_check.js` |
| 25 | `node tools/smoke/frontend/smoke_admin_js_split_readiness.js` |
| 26 | `node tools/smoke/frontend/smoke_admin_layout_shell_split.js` |
| 27 | `node tools/smoke/frontend/smoke_admin_change_log_split_contract.js` |
| 28 | `node tools/smoke/frontend/smoke_admin_change_logs_split.js` |
| 29 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_split_contract.js` |
| 30 | `node tools/smoke/frontend/smoke_admin_create_lifecycle_split.js` |
| 31 | `node tools/smoke/frontend/smoke_admin_edit_draft_split_contract.js` |
| 32 | `node tools/smoke/frontend/smoke_admin_edit_draft_split.js` |
| 33 | `node tools/smoke/frontend/smoke_admin_master_catalog_split.js` |
| 34 | `node tools/smoke/frontend/smoke_admin_overview_snapshots_split.js` |
| 35 | `node tools/smoke/frontend/smoke_admin_field_help_split.js` |
| 36 | `node tools/smoke/frontend/smoke_admin_settings_helpers_split.js` |
| 37 | `node tools/smoke/frontend/smoke_admin_bootstrap_bindings_readiness.js` |
| 38 | `node tools/smoke/frontend/smoke_admin_thin_entry_cleanup.js` |
| 39 | `node tools/smoke/frontend/smoke_admin_create_delete_rollback.js` |
| 40 | `node tools/smoke/frontend/smoke_admin_create_delete_restore.js` |
| 41 | `node tools/smoke/frontend/smoke_admin_layout_navigation_shell.js` |
| 42 | `node tools/smoke/frontend/smoke_admin_post_edit_api_verify.js` |
| 43 | `node tools/smoke/frontend/smoke_admin_master_api_verify.js` |
| 44 | `node tools/smoke/game/smoke_runtime_stacked_enhance_space_guard.js` |
| 45 | `node tools/smoke/game/smoke_runtime_stackable_items.js` |
| 46 | `node tools/smoke/game/smoke_save_data_integrity_verify.js` |
| 47 | `node tools/smoke/game/smoke_save_data_restore_reload_lock.js` |
| 48 | `node tools/smoke/game/smoke_save_data_restore_guard.js` |
| 49 | `python tools/smoke/frontend/smoke_admin_change_log_filter_binding.py` |
| 50 | `python tools/smoke/frontend/smoke_admin_change_logs_schema_guard.py` |
| 51 | `python tools/smoke/frontend/smoke_admin_readonly_api_structure.py` |
| 52 | `python tools/smoke/contracts/smoke_backend_admin_service_split_contract.py` |
| 53 | `python tools/smoke/contracts/smoke_backend_admin_overview_snapshots_service_split.py` |
| 54 | `python tools/smoke/contracts/smoke_backend_admin_master_catalog_service_split.py` |
| 55 | `python tools/smoke/contracts/smoke_backend_admin_create_lifecycle_service_split.py` |
| 56 | `python tools/smoke/contracts/smoke_backend_admin_change_log_service_split.py` |
| 57 | `python tools/smoke/contracts/smoke_backend_admin_edit_draft_service_split.py` |
| 58 | `python tools/smoke/contracts/smoke_backend_admin_shared_utils_service_split.py` |
| 59 | `python tools/smoke/contracts/smoke_backend_admin_config_readiness_service_split.py` |
| 60 | `python tools/smoke/contracts/smoke_backend_admin_route_response_helper.py` |
| 61 | `python tools/smoke/contracts/smoke_backend_admin_route_params_error_helpers.py` |
| 62 | `python tools/smoke/contracts/smoke_backend_admin_route_response_data_meta_helpers.py` |
| 63 | `python tools/smoke/contracts/smoke_backend_admin_route_module_split.py` |
| 64 | `python tools/smoke/contracts/smoke_backend_admin_overview_route_module_split.py` |
| 65 | `python tools/smoke/contracts/smoke_backend_admin_route_map_contract.py` |
| 66 | `python tools/smoke/contracts/smoke_backend_admin_route_module_import_contract.py` |
| 67 | `python tools/smoke/contracts/smoke_backend_admin_runtime_route_contract.py` |
| 68 | `python tools/smoke/contracts/smoke_backend_admin_route_operation_contract.py` |
| 69 | `python tools/smoke/contracts/smoke_backend_admin_openapi_route_contract.py` |
| 70 | `python tools/smoke/contracts/smoke_backend_admin_response_metadata_contract.py` |
| 71 | `python tools/smoke/contracts/smoke_backend_admin_request_metadata_contract.py` |
| 72 | `python tools/smoke/contracts/smoke_backend_admin_schema_model_contract.py` |
| 73 | `python tools/smoke/contracts/smoke_backend_admin_schema_field_constraint_contract.py` |
| 74 | `python tools/smoke/contracts/smoke_backend_admin_request_payload_validation_contract.py` |
| 75 | `python tools/smoke/contracts/smoke_backend_admin_validation_error_compatibility_contract.py` |
| 76 | `python tools/smoke/contracts/smoke_backend_admin_request_content_negotiation_contract.py` |
| 77 | `python tools/smoke/contracts/smoke_backend_admin_request_media_size_boundary_contract.py` |
| 78 | `python tools/smoke/contracts/smoke_backend_admin_request_header_encoding_contract.py` |
| 79 | `python tools/smoke/contracts/smoke_backend_admin_request_transport_header_observation_contract.py` |
| 80 | `python tools/smoke/contracts/smoke_backend_admin_write_replay_safety_contract.py` |
| 81 | `python tools/smoke/contracts/smoke_admin_frontend_schema_contract_readiness.py` |
| 82 | `python tools/smoke/contracts/smoke_backend_admin_route_service_legacy_cleanup.py` |
| 83 | `python tools/smoke/contracts/smoke_backend_admin_service_facade_contract.py` |
| 84 | `python tools/smoke/frontend/smoke_admin_create_blueprint_api_structure.py` |
| 85 | `python tools/smoke/game/smoke_save_snapshot_integrity_api_structure.py` |
| 86 | `python tools/smoke/game/smoke_save_snapshot_api_structure.py` |
| 87 | `python tools/smoke/contracts/smoke_admin_contract_registry_sync.py` |
| 88 | `python tools/smoke/contracts/smoke_backend_admin_preview_integration.py` |
| 89 | `python tools/smoke/backend/smoke_backend_packaging_contract.py` |
| 90 | `python tools/smoke/backend/smoke_backend_local_cors.py` |
| 91 | `python tools/smoke/backend/smoke_backend_route_map_report.py` |
| 92 | `python tools/smoke/backend/smoke_postgres_alembic_readiness.py` |
| 93 | `python tools/smoke/backend/smoke_backend_alembic_async_env.py` |
| 94 | `python tools/smoke/backend/smoke_postgres_runtime_readonly_state.py` |
| 95 | `python tools/smoke/backend/smoke_windows_subprocess_decode.py` |
| 96 | `python tools/smoke/backend/smoke_postgres_schema_equivalence.py` |
| 97 | `python tools/smoke/backend/smoke_postgres_backup_restore_preflight.py` |
| 98 | `python tools/smoke/backend/smoke_postgres_backup_creation.py` |
| 99 | `python tools/smoke/backend/smoke_postgres_restore_rehearsal_database_creation.py` |
| 100 | `python tools/smoke/backend/smoke_postgres_restore_rehearsal.py` |
| 101 | `python tools/smoke/backend/smoke_postgres_migration_test_database_creation.py` |
| 102 | `python tools/smoke/backend/smoke_postgres_initial_alembic_revision_creation.py` |
| 103 | `python tools/smoke/backend/smoke_postgres_initial_alembic_revision_manual_review.py` |
| 104 | `python tools/smoke/backend/smoke_postgres_migration_test_database_upgrade.py` |
| 105 | `python tools/smoke/backend/smoke_postgres_migration_test_database_downgrade.py` |
| 106 | `python tools/smoke/backend/smoke_postgres_migration_test_database_roundtrip.py` |
| 107 | `python tools/smoke/backend/smoke_postgres_source_baseline_stamp_preflight.py` |
| 108 | `python tools/smoke/backend/smoke_postgres_restore_rehearsal_stamp_guard.py` |
| 109 | `python tools/smoke/backend/smoke_postgres_source_baseline_stamp_guard.py` |
| 110 | `python tools/smoke/backend/smoke_postgres_baseline_completion_state.py` |
| 111 | `python tools/smoke/backend/smoke_postgres_next_revision_preflight.py` |
| 112 | `python tools/smoke/backend/smoke_postgres_deployment_runtime_readiness.py` |
| 113 | `python tools/smoke/backend/smoke_runtime_engine_source_binding_inspector.py` |
| 114 | `python tools/smoke/backend/smoke_runtime_config_hardening.py` |
| 115 | `python tools/smoke/backend/smoke_production_secrets_tls_container_static.py` |
| 116 | `python tools/smoke/backend/smoke_production_capacity_tls_network_plan.py` |
| 117 | `python tools/smoke/backend/smoke_production_managed_postgres_reverse_proxy_selection.py` |
| 118 | `python tools/smoke/backend/smoke_production_compose_config_render.py` |
| 119 | `python tools/smoke/backend/smoke_codex_handoff_readiness.py` |
| 120 | `python tools/smoke/game/smoke_next_chat_handoff.py` |
| 121 | `python tools/smoke/contracts/smoke_backend_admin_preview_side_effect_contract.py` |
| 122 | `python tools/smoke/contracts/smoke_backend_admin_service_mutation_boundary_contract.py` |
| 123 | `python tools/smoke/contracts/smoke_backend_admin_diff_engine_contract.py` |
| 124 | `python tools/smoke/contracts/smoke_backend_admin_change_log_shared_diff.py` |
| 125 | `python tools/smoke/contracts/smoke_backend_admin_rollback_snapshot_contract.py` |
| 126 | `python tools/smoke/contracts/smoke_backend_admin_rollback_preview_snapshot.py` |

## smoke 내부에서 많이 발견된 경로 문자열

| 경로 문자열 | smoke 참조 수 |
| --- | --- |
| `src/api/admin-page-readonly.js` | 109 |
| `admin.html` | 108 |
| `index.html` | 46 |
| `src/api/save-data-dev-badge.js` | 44 |
| `src/api/game-api-client.js` | 41 |
| `tools/run_smoke_core.sh` | 38 |
| `backend/app/services/admin_service_legacy_markers.py` | 37 |
| `src/api/save-data-restore-guard.js` | 32 |
| `backend/app/api/routes/admin_master_data_routes.py` | 24 |
| `src/api/admin/admin-change-logs.js` | 22 |
| `backend/app/api/routes/admin_change_log_routes.py` | 19 |
| `src/api/save-data-sync-policy.js` | 19 |
| `src/api/admin/admin-create-lifecycle.js` | 18 |
| `backend/app/services/admin_service_split_contract.py` | 17 |
| `src/api/admin/admin-edit-draft.js` | 16 |
| `src/api/admin/admin-master-catalog.js` | 15 |
| `src/api/admin-layout-shell.js` | 14 |
| `src/pages/AdminShell.vue` | 13 |
| `backend/app/api/routes/admin_response_data_helpers.py` | 11 |
| `src/api/admin/admin-field-help.js` | 11 |
| `src/app/main.js` | 11 |
| `backend/app/services/admin_service.py` | 10 |
| `backend/app/services/admin/__init__.py` | 10 |
| `src/api/save-data-preview.js` | 10 |
| `backend/app/schemas/admin.py` | 9 |
| `src/api/admin/admin-overview-snapshots.js` | 9 |
| `src/api/master-data-runtime-switch.js` | 9 |
| `backend/app/api/routes/admin_overview_snapshot_routes.py` | 8 |
| `backend/app/api/routes/admin_route_params.py` | 8 |
| `backend/app/api/routes/admin.py` | 7 |
| `src/api/admin/admin-settings-helpers.js` | 7 |
| `src/styles/base.css` | 7 |
| `src/pages/GameShell.vue` | 7 |
| `src/api/master-data-adapter.js` | 7 |
| `src/api/save-data-slots.js` | 7 |
| `backend/app/api/routes/game.py` | 6 |
| `backend/app/services/admin/admin_change_log_service.py` | 6 |
| `backend/app/api/routes/admin_response_meta_helpers.py` | 6 |
| `src/components/AdminMasterDetailPanel.vue` | 6 |
| `backend/Dockerfile` | 5 |

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

## 다음 단계 후보

v270에서는 사용자 승인 후 아래 중 하나를 진행하는 것이 안전합니다.

1. `frontend/vue-app/`에 Vite + Vue 기본 shell만 생성
2. 기존 `admin.html`/`index.html`은 그대로 유지
3. Vue shell에서 아직 실제 관리자/게임 로직은 연결하지 않음
4. root legacy smoke와 Vue shell smoke를 분리해서 검증

## 재생성 방법

실행 위치: 프로젝트 루트

```bash
python tools/report_legacy_path_dependencies.py --write
```

검사만 할 때:

실행 위치: 프로젝트 루트

```bash
python tools/report_legacy_path_dependencies.py --check
```

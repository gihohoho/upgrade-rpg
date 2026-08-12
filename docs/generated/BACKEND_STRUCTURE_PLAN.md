# Backend Structure Plan — v274

이 문서는 현재 `backend/` 구조를 실제 파일 기준으로 점검하고, Vue/FastAPI/DB 전환 전에 무엇을 유지하고 무엇을 나중에 정리할지 정리한 문서입니다.

중요: v274는 **문서화/분석 단계**입니다. 실제 route path, API body, DB, 인증, write 로직은 변경하지 않습니다.

## v274 결론

- `backend/app/api/routes/`는 지금처럼 route path/contract 보호 대상으로 유지합니다.
- `backend/app/services/admin_service.py` facade는 유지합니다.
- `backend/app/services/admin/`의 분리된 service들은 당장 이동하지 않습니다.
- `backend/app/schemas/`, `backend/app/models/`, `backend/app/db/`는 PostgreSQL/Alembic 준비 전까지 구조 변경하지 않습니다.
- Vue에서는 당분간 안전한 `GET` read-only API만 연결합니다.
- Preview/Apply/write API는 인증/권한/Write Guard 설계 전까지 Vue에서 확장하지 않습니다.

## 절대 변경 금지 유지 항목

- route path
- API response body
- Preview/Apply request body
- Write Guard
- actual write logic
- DB schema
- env
- seed
- authentication
- existing smoke/contract meaning

## 현재 backend 파일 수

| 영역 | 파일 수 | 판단 |
|---|---:|---|
| `backend/app/api/routes/` | 36 | route path/contract 보호 |
| `backend/app/services/` | 23 | facade 유지 후 단계적 정리 |
| `backend/app/schemas/` | 7 | API body 안정성 때문에 보존 |
| `backend/app/models/` | 11 | DB 전환 전 보존 |
| `backend/app/db/` | 3 | Alembic/DB 계획 전 보존 |
| `backend/app/core/` | 4 | 설정/응답/CORS/security 보호 |

## 현재 route include 구조

`backend/app/api/router.py` 기준:

- `api_router.include_router(health.router, tags=["health"])`
- `api_router.include_router(auth.router, prefix="/auth", tags=["auth"])`
- `api_router.include_router(account.router, prefix="/account", tags=["account"])`
- `api_router.include_router(account_admin.router, prefix="/account-admin", tags=["account-admin"])`
- `api_router.include_router(game.router, prefix="/game", tags=["game"])`
- `api_router.include_router(admin.router, prefix="/admin", tags=["admin"])`

`backend/app/api/routes/admin.py` 기준:

- `router.include_router(admin_overview_snapshot_router)`
- `router.include_router(admin_master_data_router)`
- `router.include_router(admin_change_log_router)`

이 구조 때문에 `health`, `game`, `admin` route prefix는 전환 중에도 그대로 유지해야 합니다.

## Route 파일별 판단

| 파일 | 현재 성격 | v274 판단 |
| --- | --- | --- |
| `backend/app/api/routes/__init__.py` | 검토 필요 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/account.py` | 검토 필요 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/account_admin.py` | 검토 필요 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin.py` | admin-readonly-or-facade | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_change_log_routes.py` | admin-readonly-or-facade | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_diff_engine_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_master_data_routes.py` | admin-readonly-or-facade | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_openapi_route_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_overview_snapshot_routes.py` | admin-readonly-or-facade | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_preview_side_effect_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_request_content_negotiation_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_request_header_encoding_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_request_media_size_boundary_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_request_metadata_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_request_payload_validation_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_request_transport_header_observation_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_response_data_helpers.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_response_helpers.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_response_meta_helpers.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_response_metadata_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_rollback_snapshot_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_route_error_helpers.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_route_map_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_route_module_import_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_route_operation_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_route_params.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_route_services.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_runtime_route_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_schema_field_constraint_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_schema_model_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_service_mutation_boundary_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_validation_error_compatibility_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/admin_write_replay_safety_contract.py` | contract/readiness 보호 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/auth.py` | 검토 필요 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/game.py` | game API 후보 | 이동 금지 / route path 유지 |
| `backend/app/api/routes/health.py` | safe-readonly | 이동 금지 / route path 유지 |

## Service 파일별 판단

| 파일 | 현재 성격 | v274 판단 |
| --- | --- | --- |
| `backend/app/services/__init__.py` | 검토 필요 | facade 유지 후 단계적 분리 |
| `backend/app/services/account_character_service.py` | 검토 필요 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/__init__.py` | admin service helper | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/account_user_management_service.py` | admin service helper | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/admin_change_log_service.py` | admin workflow service 보호 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/admin_config.py` | admin service helper | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/admin_create_lifecycle_service.py` | admin workflow service 보호 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/admin_diff_engine.py` | admin preview/diff/snapshot 보호 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/admin_edit_draft_service.py` | admin workflow service 보호 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/admin_master_catalog_service.py` | admin service helper | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/admin_overview_snapshots_service.py` | admin service helper | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/admin_preview_enrichment.py` | admin preview/diff/snapshot 보호 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/admin_readiness_service.py` | contract/readiness 보호 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/admin_rollback_snapshot.py` | admin preview/diff/snapshot 보호 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/admin_shared_utils.py` | admin service helper | facade 유지 후 단계적 분리 |
| `backend/app/services/admin/README.md` | admin service 설명 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin_service.py` | AdminService facade 유지 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin_service_facade_contract.py` | service split contract 보호 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin_service_legacy_markers.py` | 검토 필요 | facade 유지 후 단계적 분리 |
| `backend/app/services/admin_service_split_contract.py` | service split contract 보호 | facade 유지 후 단계적 분리 |
| `backend/app/services/auth_email_delivery.py` | 검토 필요 | facade 유지 후 단계적 분리 |
| `backend/app/services/auth_service.py` | 검토 필요 | facade 유지 후 단계적 분리 |
| `backend/app/services/game_service.py` | game service 후보 | facade 유지 후 단계적 분리 |

## Schema 파일 판단

| 파일 | v274 판단 |
| --- | --- |
| `backend/app/schemas/__init__.py` | API 응답/요청 body 안정성 때문에 보존 |
| `backend/app/schemas/account.py` | API 응답/요청 body 안정성 때문에 보존 |
| `backend/app/schemas/account_admin.py` | API 응답/요청 body 안정성 때문에 보존 |
| `backend/app/schemas/admin.py` | API 응답/요청 body 안정성 때문에 보존 |
| `backend/app/schemas/auth.py` | API 응답/요청 body 안정성 때문에 보존 |
| `backend/app/schemas/common.py` | API 응답/요청 body 안정성 때문에 보존 |
| `backend/app/schemas/game.py` | API 응답/요청 body 안정성 때문에 보존 |

## Model 파일 판단

| 파일 | v274 판단 |
| --- | --- |
| `backend/app/models/__init__.py` | PostgreSQL/Alembic 실제 전환 전 보존 |
| `backend/app/models/admin.py` | PostgreSQL/Alembic 실제 전환 전 보존 |
| `backend/app/models/boss.py` | PostgreSQL/Alembic 실제 전환 전 보존 |
| `backend/app/models/character.py` | PostgreSQL/Alembic 실제 전환 전 보존 |
| `backend/app/models/enhancement.py` | PostgreSQL/Alembic 실제 전환 전 보존 |
| `backend/app/models/field.py` | PostgreSQL/Alembic 실제 전환 전 보존 |
| `backend/app/models/item.py` | PostgreSQL/Alembic 실제 전환 전 보존 |
| `backend/app/models/mailbox.py` | PostgreSQL/Alembic 실제 전환 전 보존 |
| `backend/app/models/mixins.py` | PostgreSQL/Alembic 실제 전환 전 보존 |
| `backend/app/models/skill.py` | PostgreSQL/Alembic 실제 전환 전 보존 |
| `backend/app/models/user.py` | PostgreSQL/Alembic 실제 전환 전 보존 |

## DB/Core 파일 판단

| 파일 | v274 판단 |
| --- | --- |
| `backend/app/db/__init__.py` | DB 연결/세션 준비 영역, 실제 변경 보류 |
| `backend/app/db/base.py` | DB 연결/세션 준비 영역, 실제 변경 보류 |
| `backend/app/db/session.py` | DB 연결/세션 준비 영역, 실제 변경 보류 |
| `backend/app/core/__init__.py` | 설정/응답/security 영역, 변경 시 smoke 필요 |
| `backend/app/core/config.py` | 설정/응답/security 영역, 변경 시 smoke 필요 |
| `backend/app/core/response.py` | 설정/응답/security 영역, 변경 시 smoke 필요 |
| `backend/app/core/security.py` | 설정/응답/security 영역, 변경 시 smoke 필요 |

## Vue read-only API와 backend 연결 판단

현재 Vue에서 연결해도 되는 안전 범위:

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`

다음에 연결 후보로 검토할 수 있는 범위:

- 관리자 카탈로그 조회용 `GET` API
- 관리자 상세 조회용 `GET` API
- snapshot 목록 조회용 `GET` API
- change log 조회용 `GET` API

아직 연결하지 말아야 할 범위:

- create preview/apply
- edit preview/apply
- rollback preview/apply
- delete/restore preview/apply
- save snapshot write 계열
- 인증/권한이 필요한 관리자 write 계열

## FastAPI 구조 정리 순서 제안

1. 현재 route map 자동 보고서 작성
2. read-only route 목록만 Vue에 단계적으로 연결
3. service facade 의존성 문서화
4. DB/Alembic 도입 전 seed/source-of-truth 문서화
5. 인증/권한 설계 문서화
6. Write Guard와 관리자 Preview/Apply body 보호 계약 재확인
7. 그 후에만 service 파일 이동 또는 route module 재배치 검토

## v275 추천 작업

`v275 Backend route map 자동 보고서 + Vue read-only route 후보 확정`

v275에서 해도 되는 일:

- `backend/app/api/routes/`의 실제 route 목록을 자동 추출하는 도구 추가
- `docs/generated/BACKEND_ROUTE_MAP.md` 생성
- Vue에서 연결 가능한 `GET` 후보를 문서로 분류

v275에서 아직 하지 말아야 할 일:

- route path 변경
- response body 변경
- write API Vue 연결
- 인증 추가
- DB/Alembic 실제 migration 생성

# Backend Route Map — v275

이 문서는 FastAPI route 파일을 정적으로 분석해서 현재 API 목록을 정리한 자동 보고서입니다.

중요: v275는 **route 목록 문서화 + Vue read-only 후보 확정 단계**입니다. 실제 route path, 요청 body, 응답 body, DB, 인증, write 로직은 변경하지 않습니다.

## 생성 방식

- 도구: `tools/report_backend_route_map.py`
- 산출물: `docs/current/BACKEND_ROUTE_MAP.md`
- 방식: `app.main`을 import하지 않고 route 파일의 `@router.get/post(...)` decorator를 정적으로 분석합니다.
- 이유: 단순 문서 생성이 `asyncpg` 같은 로컬 DB 의존성 설치 상태에 막히지 않게 하기 위해서입니다.

## 보호 항목

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

## Route 수 요약

| 기준 | 값 |
|---|---:|
| 전체 route 수 | 27 |
| 중복 method/path | 0 |

### Method별 수

| method | count |
| --- | --- |
| `GET` | 15 |
| `POST` | 12 |

### Group별 수

| group | count |
| --- | --- |
| `admin` | 21 |
| `game` | 4 |
| `health` | 2 |

중복 method/path:

없음

## Vue에서 이미 자동 smoke 화면에 쓰는 route

| route | group | query/body 힌트 | response type | endpoint |
| --- | --- | --- | --- | --- |
| `GET /api/v1/admin/requirements` | admin | - | admin.requirements | `get_admin_requirements` |
| `GET /api/v1/health` | health | - | system.health | `health_check` |

## Vue read-only 연결 후보

아래 route는 모두 `GET`입니다. 다만 일부는 DB 상태에 영향을 받으므로, 화면에 자동 호출하기 전에 loading/error/empty 상태를 먼저 설계해야 합니다.

| route | group | query/body 힌트 | response type | endpoint |
| --- | --- | --- | --- | --- |
| `GET /api/v1/admin/change-logs` | admin | limit, targetType, targetId, action, changedKey, applied, sort | admin.change_logs | `list_admin_change_logs` |
| `GET /api/v1/admin/change-logs/{change_log_id}` | admin | path: change_log_id; Vue wrapper may expose changeLogId and translate it | admin.change_log.detail | `get_admin_change_log_detail` |
| `GET /api/v1/admin/master-data/catalog` | admin | domain, limit, page, query, enabled, sort | admin.master_data.catalog | `list_admin_master_catalog_rows` |
| `GET /api/v1/admin/master-data/create-blueprint` | admin | domain | admin.master_data.create_blueprint | `get_admin_master_create_blueprint` |
| `GET /api/v1/admin/master-data/detail` | admin | domain, id | admin.master_data.detail | `get_admin_master_catalog_detail` |
| `GET /api/v1/admin/master-data/domains` | admin | - | admin.master_data.domains | `list_admin_master_catalog_domains` |
| `GET /api/v1/admin/master-data/relations` | admin | domain, id, limit | admin.master_data.relations | `get_admin_master_catalog_relations` |
| `GET /api/v1/admin/overview` | admin | - | admin.overview | `get_admin_readonly_overview` |
| `GET /api/v1/admin/save-snapshots` | admin | limit, userId, slotKey, source, defaultOnly, sort | admin.save_snapshots | `list_admin_save_snapshots` |
| `GET /api/v1/game/load` | game | slotKey | game.load | `load_game` |
| `GET /api/v1/game/master-data` | game | includeAssets | game.master_data | `get_master_data` |
| `GET /api/v1/game/save-slots` | game | - | game.save_slots | `list_save_slots` |

### v275에서 확인한 Vue query 이름 주의점

- `GET /api/v1/admin/master-data/detail`의 row 식별자 query 이름은 `id`입니다.
- `GET /api/v1/admin/master-data/relations`의 row 식별자 query 이름도 `id`입니다.
- Vue wrapper에서는 사용자가 이해하기 쉽게 `rowId`를 받을 수 있지만, 실제 요청 query는 `id`로 변환해야 합니다.
- v275에서 `frontend/vue-app/src/api/adminReadOnlyApi.js`의 read-only query 변환을 이 기준에 맞췄습니다.

## Vue 연결 보류 route

아래 route는 DB 상태 확인, POST preview, Apply/write 계열이므로 Vue read-only 자동 화면에는 아직 넣지 않습니다.

| route | group | response type | 보류 이유 |
| --- | --- | --- | --- |
| `POST /api/v1/admin/change-logs/{change_log_id}/create-delete-apply` | admin | admin.change_log.create_delete_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST /api/v1/admin/change-logs/{change_log_id}/create-delete-preview` | admin | admin.change_log.create_delete_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST /api/v1/admin/change-logs/{change_log_id}/create-delete-restore-apply` | admin | admin.change_log.create_delete_restore_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST /api/v1/admin/change-logs/{change_log_id}/create-delete-restore-preview` | admin | admin.change_log.create_delete_restore_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST /api/v1/admin/change-logs/{change_log_id}/rollback-apply` | admin | admin.change_log.rollback_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST /api/v1/admin/change-logs/{change_log_id}/rollback-preview` | admin | admin.change_log.rollback_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST /api/v1/admin/change-preview` | admin | admin.change.preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST /api/v1/admin/master-data/create-apply` | admin | admin.master_data.create_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST /api/v1/admin/master-data/create-preview` | admin | admin.master_data.create_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST /api/v1/admin/master-data/edit-apply` | admin | admin.master_data.edit_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST /api/v1/admin/master-data/edit-preview` | admin | admin.master_data.edit_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST /api/v1/game/save` | game | game.save | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `GET /api/v1/health/db` | health | system.health.db | DB 연결 확인용 GET, 자동 화면 연결 보류 |

## 전체 route map

| method | full path | endpoint | source | response type | v275 판단 |
| --- | --- | --- | --- | --- | --- |
| `GET` | `/api/v1/admin/change-logs` | `list_admin_change_logs` | `backend/app/api/routes/admin_change_log_routes.py:35` | admin.change_logs | Vue read-only 후보 |
| `GET` | `/api/v1/admin/change-logs/{change_log_id}` | `get_admin_change_log_detail` | `backend/app/api/routes/admin_change_log_routes.py:82` | admin.change_log.detail | Vue read-only 후보 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/create-delete-apply` | `apply_admin_create_delete_rollback` | `backend/app/api/routes/admin_change_log_routes.py:123` | admin.change_log.create_delete_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/create-delete-preview` | `preview_admin_create_delete_rollback` | `backend/app/api/routes/admin_change_log_routes.py:101` | admin.change_log.create_delete_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/create-delete-restore-apply` | `apply_admin_create_delete_restore` | `backend/app/api/routes/admin_change_log_routes.py:169` | admin.change_log.create_delete_restore_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/create-delete-restore-preview` | `preview_admin_create_delete_restore` | `backend/app/api/routes/admin_change_log_routes.py:147` | admin.change_log.create_delete_restore_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/rollback-apply` | `apply_admin_change_log_rollback` | `backend/app/api/routes/admin_change_log_routes.py:215` | admin.change_log.rollback_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/rollback-preview` | `preview_admin_change_log_rollback` | `backend/app/api/routes/admin_change_log_routes.py:193` | admin.change_log.rollback_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST` | `/api/v1/admin/change-preview` | `preview_admin_change` | `backend/app/api/routes/admin_overview_snapshot_routes.py:90` | admin.change.preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `GET` | `/api/v1/admin/master-data/catalog` | `list_admin_master_catalog_rows` | `backend/app/api/routes/admin_master_data_routes.py:48` | admin.master_data.catalog | Vue read-only 후보 |
| `POST` | `/api/v1/admin/master-data/create-apply` | `apply_admin_master_data_create` | `backend/app/api/routes/admin_master_data_routes.py:119` | admin.master_data.create_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `GET` | `/api/v1/admin/master-data/create-blueprint` | `get_admin_master_create_blueprint` | `backend/app/api/routes/admin_master_data_routes.py:80` | admin.master_data.create_blueprint | Vue read-only 후보 |
| `POST` | `/api/v1/admin/master-data/create-preview` | `preview_admin_master_data_create` | `backend/app/api/routes/admin_master_data_routes.py:96` | admin.master_data.create_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `GET` | `/api/v1/admin/master-data/detail` | `get_admin_master_catalog_detail` | `backend/app/api/routes/admin_master_data_routes.py:143` | admin.master_data.detail | Vue read-only 후보 |
| `GET` | `/api/v1/admin/master-data/domains` | `list_admin_master_catalog_domains` | `backend/app/api/routes/admin_master_data_routes.py:33` | admin.master_data.domains | Vue read-only 후보 |
| `POST` | `/api/v1/admin/master-data/edit-apply` | `apply_admin_master_data_edit` | `backend/app/api/routes/admin_master_data_routes.py:217` | admin.master_data.edit_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST` | `/api/v1/admin/master-data/edit-preview` | `preview_admin_master_data_edit` | `backend/app/api/routes/admin_master_data_routes.py:187` | admin.master_data.edit_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `GET` | `/api/v1/admin/master-data/relations` | `get_admin_master_catalog_relations` | `backend/app/api/routes/admin_master_data_routes.py:164` | admin.master_data.relations | Vue read-only 후보 |
| `GET` | `/api/v1/admin/overview` | `get_admin_readonly_overview` | `backend/app/api/routes/admin_overview_snapshot_routes.py:34` | admin.overview | Vue read-only 후보 |
| `GET` | `/api/v1/admin/requirements` | `get_admin_requirements` | `backend/app/api/routes/admin_overview_snapshot_routes.py:25` | admin.requirements | Vue 자동 smoke 화면 사용 중 |
| `GET` | `/api/v1/admin/save-snapshots` | `list_admin_save_snapshots` | `backend/app/api/routes/admin_overview_snapshot_routes.py:57` | admin.save_snapshots | Vue read-only 후보 |
| `GET` | `/api/v1/game/load` | `load_game` | `backend/app/api/routes/game.py:45` | game.load | Vue read-only 후보 |
| `GET` | `/api/v1/game/master-data` | `get_master_data` | `backend/app/api/routes/game.py:14` | game.master_data | Vue read-only 후보 |
| `POST` | `/api/v1/game/save` | `save_game` | `backend/app/api/routes/game.py:100` | game.save | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `GET` | `/api/v1/game/save-slots` | `list_save_slots` | `backend/app/api/routes/game.py:71` | game.save_slots | Vue read-only 후보 |
| `GET` | `/api/v1/health` | `health_check` | `backend/app/api/routes/health.py:11` | system.health | Vue 자동 smoke 화면 사용 중 |
| `GET` | `/api/v1/health/db` | `database_health_check` | `backend/app/api/routes/health.py:17` | system.health.db | DB 연결 확인용 GET, 자동 화면 연결 보류 |

## v276 추천

다음 단계는 `v276 Vue admin read-only catalog mini panel`을 추천합니다.

권장 범위:

1. `GET /api/v1/admin/master-data/domains`만 먼저 Vue 관리자 shell에 연결합니다.
2. 성공/오류/빈 데이터 상태만 확인합니다.
3. 카탈로그 row 목록, 상세, 관계 조회는 그다음 단계로 미룹니다.
4. Preview/Apply/write route는 계속 보류합니다.
5. DB/Alembic/인증/env/seed는 변경하지 않습니다.

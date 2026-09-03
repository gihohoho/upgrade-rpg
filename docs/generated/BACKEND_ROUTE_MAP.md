# Backend Route Map — v377

이 문서는 FastAPI route 파일을 정적으로 분석해서 현재 API 목록을 정리한 자동 보고서입니다.

중요: v377 local migration과 인증 요청 보호 복구는 완료됐습니다. 이 보고서 생성은 DB, 인증 상태와 저장 데이터를 변경하지 않습니다.

```txt
latest: v392.vue-game-legacy-frame-modal-readability
strict result: vue-game-legacy-frame-modal-readability
source head: v377_auth_email_public_security
local/Neon DB current: v377_auth_email_public_security / v377_auth_email_public_security
actual target v377 apply: local 1 / Neon 1
private email environment: prepared
legacy stale evidence: source 8db9bcb / preserved
recovery1 roundtrip/local backup/apply: source 345872a / verified
local auth POST: protection store available / legacy no-email login compatible
local Brevo E2E: Naver delivery / link verification / login verified
provider finalize: local multi-worker ownership diagnosed / direct provider healthy
recovery2 roundtrip/Neon backup/apply: verified / one attempt each
public backend/static: v377/v378 live
next safe stage: migrate-vue-game-combat-runtime-foundation
```

## 생성 방식

- 도구: `tools/report_backend_route_map.py`
- 산출물: `docs/generated/BACKEND_ROUTE_MAP.md`
- 방식: `app.main`을 import하지 않고 route 파일의 GET/POST/PUT/PATCH/DELETE decorator를 정적으로 분석합니다.
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
- credential secrecy
- existing smoke/contract meaning

## Route 수 요약

| 기준 | 값 |
|---|---:|
| 전체 route 수 | 48 |
| 중복 method/path | 0 |

### Method별 수

| method | count |
| --- | --- |
| `DELETE` | 1 |
| `GET` | 21 |
| `POST` | 26 |

### Group별 수

| group | count |
| --- | --- |
| `account` | 3 |
| `account-admin` | 6 |
| `admin` | 21 |
| `auth` | 12 |
| `game` | 4 |
| `health` | 2 |

중복 method/path:

없음

## Vue에서 이미 자동 smoke 화면에 쓰는 route

| route | group | query/body 힌트 | response type | endpoint |
| --- | --- | --- | --- | --- |
| `GET /api/v1/health` | health | - | system.health | `health_check` |

## legacy 계정·관리자 화면에서 사용하는 route

아래 경로는 v377 이메일 계정 gate, 캐릭터 슬롯, 저장 브리지 또는 관리자 회원관리 화면에 연결됩니다. 이메일 인증·복구 링크처럼 명시적으로 public인 경로를 제외한 계정·게임 저장·관리자 경로는 실제 Bearer 인증을 요구합니다.

| route | group | query/body 힌트 | response type | endpoint |
| --- | --- | --- | --- | --- |
| `POST /api/v1/account-admin/bootstrap` | account-admin | - | account_admin.bootstrap | `bootstrap_first_account_admin` |
| `GET /api/v1/account-admin/bootstrap-status` | account-admin | - | account_admin.bootstrap_status | `get_account_admin_bootstrap_status` |
| `GET /api/v1/account-admin/users` | account-admin | page, limit, query, status, sort | account_admin.users | `list_account_admin_users` |
| `GET /api/v1/account-admin/users/{user_id}` | account-admin | - | account_admin.user_detail | `get_account_admin_user_detail` |
| `POST /api/v1/account-admin/users/{user_id}/status-apply` | account-admin | - | account_admin.user_status_apply | `apply_account_admin_user_status` |
| `POST /api/v1/account-admin/users/{user_id}/status-preview` | account-admin | - | account_admin.user_status_preview | `preview_account_admin_user_status` |
| `GET /api/v1/account/characters` | account | - | account.characters | `list_account_characters` |
| `POST /api/v1/account/characters` | account | - | account.character.create | `create_account_character` |
| `DELETE /api/v1/account/characters/{account_character_id}` | account | - | account.character.delete | `delete_account_character` |
| `POST /api/v1/auth/account-deletion/confirm` | auth | - | auth.account_deletion.confirm | `confirm_account_deletion` |
| `GET /api/v1/auth/account-deletion/preview` | auth | - | auth.account_deletion.preview | `preview_account_deletion` |
| `POST /api/v1/auth/account-deletion/request` | auth | - | auth.account_deletion.request | `request_account_deletion` |
| `POST /api/v1/auth/login` | auth | - | auth.login | `login` |
| `POST /api/v1/auth/logout` | auth | - | auth.logout | `logout` |
| `GET /api/v1/auth/me` | auth | - | auth.me | `get_me` |
| `POST /api/v1/auth/recover-username` | auth | - | auth.recover_username | `recover_username` |
| `POST /api/v1/auth/register` | auth | - | auth.register | `register` |
| `POST /api/v1/auth/request-password-reset` | auth | - | auth.request_password_reset | `request_password_reset` |
| `POST /api/v1/auth/resend-verification` | auth | - | auth.resend_verification | `resend_verification` |
| `POST /api/v1/auth/reset-password` | auth | - | auth.reset_password | `reset_password` |
| `POST /api/v1/auth/verify-email` | auth | - | auth.verify_email | `verify_email` |
| `GET /api/v1/game/load` | game | slotKey, accountCharacterId | game.load | `load_game` |
| `POST /api/v1/game/save` | game | - | game.save | `save_game` |
| `GET /api/v1/game/save-slots` | game | - | game.save_slots | `list_save_slots` |

## Vue read-only 연결 후보

아래 route는 모두 `GET`입니다. 다만 일부는 DB 상태에 영향을 받으므로, 화면에 자동 호출하기 전에 loading/error/empty 상태를 먼저 설계해야 합니다.

| route | group | query/body 힌트 | response type | endpoint |
| --- | --- | --- | --- | --- |
| `GET /api/v1/game/master-data` | game | includeAssets | game.master_data | `get_master_data` |

### query 이름 주의점

- `GET /api/v1/admin/master-data/detail`의 row 식별자 query 이름은 `id`입니다.
- `GET /api/v1/admin/master-data/relations`의 row 식별자 query 이름도 `id`입니다.
- Vue wrapper에서는 사용자가 이해하기 쉽게 `rowId`를 받을 수 있지만, 실제 요청 query는 `id`로 변환해야 합니다.
- `GET /api/v1/game/load`는 `slotKey`와 `accountCharacterId`가 모두 필요합니다.

## Vue 연결 보류 route

아래 route에는 DB 상태 확인, Vue에서 `dryRun: true`로만 연결한 관리자 Preview, 실제 Apply와 아직 연결하지 않은 경로가 함께 있습니다. 표의 보류 이유는 실제 write 연결 판단에만 사용합니다.

| route | group | response type | 보류 이유 |
| --- | --- | --- | --- |
| `GET /api/v1/admin/change-logs` | admin | admin.change_logs | GET route, 추가 검토 필요 |
| `GET /api/v1/admin/change-logs/{change_log_id}` | admin | admin.change_log.detail | GET route, 추가 검토 필요 |
| `POST /api/v1/admin/change-logs/{change_log_id}/create-delete-apply` | admin | admin.change_log.create_delete_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST /api/v1/admin/change-logs/{change_log_id}/create-delete-preview` | admin | admin.change_log.create_delete_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST /api/v1/admin/change-logs/{change_log_id}/create-delete-restore-apply` | admin | admin.change_log.create_delete_restore_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST /api/v1/admin/change-logs/{change_log_id}/create-delete-restore-preview` | admin | admin.change_log.create_delete_restore_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST /api/v1/admin/change-logs/{change_log_id}/rollback-apply` | admin | admin.change_log.rollback_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST /api/v1/admin/change-logs/{change_log_id}/rollback-preview` | admin | admin.change_log.rollback_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST /api/v1/admin/change-preview` | admin | admin.change.preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `GET /api/v1/admin/master-data/catalog` | admin | admin.master_data.catalog | GET route, 추가 검토 필요 |
| `POST /api/v1/admin/master-data/create-apply` | admin | admin.master_data.create_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `GET /api/v1/admin/master-data/create-blueprint` | admin | admin.master_data.create_blueprint | GET route, 추가 검토 필요 |
| `POST /api/v1/admin/master-data/create-preview` | admin | admin.master_data.create_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `GET /api/v1/admin/master-data/detail` | admin | admin.master_data.detail | GET route, 추가 검토 필요 |
| `GET /api/v1/admin/master-data/domains` | admin | admin.master_data.domains | GET route, 추가 검토 필요 |
| `POST /api/v1/admin/master-data/edit-apply` | admin | admin.master_data.edit_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST /api/v1/admin/master-data/edit-preview` | admin | admin.master_data.edit_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `GET /api/v1/admin/master-data/relations` | admin | admin.master_data.relations | GET route, 추가 검토 필요 |
| `GET /api/v1/admin/overview` | admin | admin.overview | GET route, 추가 검토 필요 |
| `GET /api/v1/admin/requirements` | admin | admin.requirements | GET route, 추가 검토 필요 |
| `GET /api/v1/admin/save-snapshots` | admin | admin.save_snapshots | GET route, 추가 검토 필요 |
| `GET /api/v1/health/db` | health | system.health.db | DB 연결 확인용 GET, 자동 화면 연결 보류 |

## 전체 route map

| method | full path | endpoint | source | response type | v377 판단 |
| --- | --- | --- | --- | --- | --- |
| `POST` | `/api/v1/account-admin/bootstrap` | `bootstrap_first_account_admin` | `backend/app/api/routes/account_admin.py:48` | account_admin.bootstrap | legacy 계정/관리자 화면 사용 중 |
| `GET` | `/api/v1/account-admin/bootstrap-status` | `get_account_admin_bootstrap_status` | `backend/app/api/routes/account_admin.py:30` | account_admin.bootstrap_status | legacy 계정/관리자 화면 사용 중 |
| `GET` | `/api/v1/account-admin/users` | `list_account_admin_users` | `backend/app/api/routes/account_admin.py:68` | account_admin.users | legacy 계정/관리자 화면 사용 중 |
| `GET` | `/api/v1/account-admin/users/{user_id}` | `get_account_admin_user_detail` | `backend/app/api/routes/account_admin.py:99` | account_admin.user_detail | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/account-admin/users/{user_id}/status-apply` | `apply_account_admin_user_status` | `backend/app/api/routes/account_admin.py:141` | account_admin.user_status_apply | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/account-admin/users/{user_id}/status-preview` | `preview_account_admin_user_status` | `backend/app/api/routes/account_admin.py:114` | account_admin.user_status_preview | legacy 계정/관리자 화면 사용 중 |
| `GET` | `/api/v1/account/characters` | `list_account_characters` | `backend/app/api/routes/account.py:18` | account.characters | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/account/characters` | `create_account_character` | `backend/app/api/routes/account.py:36` | account.character.create | legacy 계정/관리자 화면 사용 중 |
| `DELETE` | `/api/v1/account/characters/{account_character_id}` | `delete_account_character` | `backend/app/api/routes/account.py:55` | account.character.delete | legacy 계정/관리자 화면 사용 중 |
| `GET` | `/api/v1/admin/change-logs` | `list_admin_change_logs` | `backend/app/api/routes/admin_change_log_routes.py:35` | admin.change_logs | GET route, 추가 검토 필요 |
| `GET` | `/api/v1/admin/change-logs/{change_log_id}` | `get_admin_change_log_detail` | `backend/app/api/routes/admin_change_log_routes.py:82` | admin.change_log.detail | GET route, 추가 검토 필요 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/create-delete-apply` | `apply_admin_create_delete_rollback` | `backend/app/api/routes/admin_change_log_routes.py:123` | admin.change_log.create_delete_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/create-delete-preview` | `preview_admin_create_delete_rollback` | `backend/app/api/routes/admin_change_log_routes.py:101` | admin.change_log.create_delete_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/create-delete-restore-apply` | `apply_admin_create_delete_restore` | `backend/app/api/routes/admin_change_log_routes.py:169` | admin.change_log.create_delete_restore_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/create-delete-restore-preview` | `preview_admin_create_delete_restore` | `backend/app/api/routes/admin_change_log_routes.py:147` | admin.change_log.create_delete_restore_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/rollback-apply` | `apply_admin_change_log_rollback` | `backend/app/api/routes/admin_change_log_routes.py:215` | admin.change_log.rollback_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST` | `/api/v1/admin/change-logs/{change_log_id}/rollback-preview` | `preview_admin_change_log_rollback` | `backend/app/api/routes/admin_change_log_routes.py:193` | admin.change_log.rollback_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `POST` | `/api/v1/admin/change-preview` | `preview_admin_change` | `backend/app/api/routes/admin_overview_snapshot_routes.py:90` | admin.change.preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `GET` | `/api/v1/admin/master-data/catalog` | `list_admin_master_catalog_rows` | `backend/app/api/routes/admin_master_data_routes.py:48` | admin.master_data.catalog | GET route, 추가 검토 필요 |
| `POST` | `/api/v1/admin/master-data/create-apply` | `apply_admin_master_data_create` | `backend/app/api/routes/admin_master_data_routes.py:119` | admin.master_data.create_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `GET` | `/api/v1/admin/master-data/create-blueprint` | `get_admin_master_create_blueprint` | `backend/app/api/routes/admin_master_data_routes.py:80` | admin.master_data.create_blueprint | GET route, 추가 검토 필요 |
| `POST` | `/api/v1/admin/master-data/create-preview` | `preview_admin_master_data_create` | `backend/app/api/routes/admin_master_data_routes.py:96` | admin.master_data.create_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `GET` | `/api/v1/admin/master-data/detail` | `get_admin_master_catalog_detail` | `backend/app/api/routes/admin_master_data_routes.py:143` | admin.master_data.detail | GET route, 추가 검토 필요 |
| `GET` | `/api/v1/admin/master-data/domains` | `list_admin_master_catalog_domains` | `backend/app/api/routes/admin_master_data_routes.py:33` | admin.master_data.domains | GET route, 추가 검토 필요 |
| `POST` | `/api/v1/admin/master-data/edit-apply` | `apply_admin_master_data_edit` | `backend/app/api/routes/admin_master_data_routes.py:217` | admin.master_data.edit_apply | write/Apply 계열, 인증/Write Guard 설계 전 보류 |
| `POST` | `/api/v1/admin/master-data/edit-preview` | `preview_admin_master_data_edit` | `backend/app/api/routes/admin_master_data_routes.py:187` | admin.master_data.edit_preview | POST preview 후보, 요청 body 계약/화면 설계 전 보류 |
| `GET` | `/api/v1/admin/master-data/relations` | `get_admin_master_catalog_relations` | `backend/app/api/routes/admin_master_data_routes.py:164` | admin.master_data.relations | GET route, 추가 검토 필요 |
| `GET` | `/api/v1/admin/overview` | `get_admin_readonly_overview` | `backend/app/api/routes/admin_overview_snapshot_routes.py:34` | admin.overview | GET route, 추가 검토 필요 |
| `GET` | `/api/v1/admin/requirements` | `get_admin_requirements` | `backend/app/api/routes/admin_overview_snapshot_routes.py:25` | admin.requirements | GET route, 추가 검토 필요 |
| `GET` | `/api/v1/admin/save-snapshots` | `list_admin_save_snapshots` | `backend/app/api/routes/admin_overview_snapshot_routes.py:57` | admin.save_snapshots | GET route, 추가 검토 필요 |
| `POST` | `/api/v1/auth/account-deletion/confirm` | `confirm_account_deletion` | `backend/app/api/routes/auth.py:371` | auth.account_deletion.confirm | legacy 계정/관리자 화면 사용 중 |
| `GET` | `/api/v1/auth/account-deletion/preview` | `preview_account_deletion` | `backend/app/api/routes/auth.py:317` | auth.account_deletion.preview | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/auth/account-deletion/request` | `request_account_deletion` | `backend/app/api/routes/auth.py:338` | auth.account_deletion.request | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/auth/login` | `login` | `backend/app/api/routes/auth.py:139` | auth.login | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/auth/logout` | `logout` | `backend/app/api/routes/auth.py:300` | auth.logout | legacy 계정/관리자 화면 사용 중 |
| `GET` | `/api/v1/auth/me` | `get_me` | `backend/app/api/routes/auth.py:289` | auth.me | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/auth/recover-username` | `recover_username` | `backend/app/api/routes/auth.py:219` | auth.recover_username | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/auth/register` | `register` | `backend/app/api/routes/auth.py:118` | auth.register | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/auth/request-password-reset` | `request_password_reset` | `backend/app/api/routes/auth.py:240` | auth.request_password_reset | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/auth/resend-verification` | `resend_verification` | `backend/app/api/routes/auth.py:198` | auth.resend_verification | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/auth/reset-password` | `reset_password` | `backend/app/api/routes/auth.py:261` | auth.reset_password | legacy 계정/관리자 화면 사용 중 |
| `POST` | `/api/v1/auth/verify-email` | `verify_email` | `backend/app/api/routes/auth.py:169` | auth.verify_email | legacy 계정/관리자 화면 사용 중 |
| `GET` | `/api/v1/game/load` | `load_game` | `backend/app/api/routes/game.py:44` | game.load | legacy 계정/관리자 화면 사용 중 |
| `GET` | `/api/v1/game/master-data` | `get_master_data` | `backend/app/api/routes/game.py:14` | game.master_data | Vue read-only 후보 |
| `POST` | `/api/v1/game/save` | `save_game` | `backend/app/api/routes/game.py:103` | game.save | legacy 계정/관리자 화면 사용 중 |
| `GET` | `/api/v1/game/save-slots` | `list_save_slots` | `backend/app/api/routes/game.py:79` | game.save_slots | legacy 계정/관리자 화면 사용 중 |
| `GET` | `/api/v1/health` | `health_check` | `backend/app/api/routes/health.py:11` | system.health | Vue 자동 smoke 화면 사용 중 |
| `GET` | `/api/v1/health/db` | `database_health_check` | `backend/app/api/routes/health.py:17` | system.health.db | DB 연결 확인용 GET, 자동 화면 연결 보류 |

## 다음 추천 단계

`next safe stage: migrate-vue-game-combat-runtime-foundation`

private environment, local migration, recovery2 synthetic 왕복·Neon backup·exact v377 apply,
signed backend image와 legacy static의 공개 배포를 승인된 단일 시도로 완료했습니다.
인증 POST는 공개 서비스에서 422/202와 `Cache-Control: no-store` 계약을 확인했습니다.

권장 범위:

1. v392에서 legacy형 좌우 게임 창·utility modal·최소 12px 가독성을 복원했으므로 다음은 server save·보상·난수 드랍과 분리해 client 전투 runtime controller 기반을 준비합니다.
2. production 관리자 복구, 재인증 request, dev key header와 실제 Apply는 별도 exact DB-write 승인을 받기 전까지 연결하지 않습니다.
3. 완료된 migration·publish·Render deploy와 기호가 확인한 Docker·로그인은 단순 확인을 위해 재실행하지 않습니다.

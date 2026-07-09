# Upgrade RPG v202 패키지

현재 안정 버전: **v202 backend admin change log service split**

새 채팅 인수인계 ZIP: **rpg_v202_backend_admin_change_log_service_split_ready.zip**

## 요약

v202에서는 백엔드 `AdminService` facade를 유지한 상태로, **change logs 목록/상세/rollback** 묶음을 `AdminChangeLogService` mixin으로 실제 분리했습니다.

`backend/app/api/routes/admin.py`의 URL/path와 `backend/app/schemas/admin.py`의 schema/API 응답 구조는 변경하지 않았습니다.

## v202에서 정리한 것

- `backend/app/services/admin/admin_change_log_service.py` 추가
- `AdminChangeLogService` mixin 추가
- `AdminService(AdminOverviewSnapshotsService, AdminMasterCatalogService, AdminChangeLogService, AdminCreateLifecycleService)` 구조로 변경
- change logs 목록/상세/rollback 관련 public/helper 메서드 이동
- `/admin/change-logs` schema guard 유지
- `apply_admin_change_log_rollback()` 성공 경로 `return preview` 보강
- `tools/smoke_backend_admin_change_log_service_split.py` 추가
- `tools/run_smoke_core.sh`에 새 smoke 포함
- 기존 static smoke를 분리 구조에 맞게 legacy marker로 유지

## 현재 백엔드 admin service 상태

- `backend/app/services/admin_service.py` — route가 계속 import하는 facade
- `backend/app/services/admin/admin_overview_snapshots_service.py` — v199.1 분리 완료
- `backend/app/services/admin/admin_master_catalog_service.py` — v200 분리 완료
- `backend/app/services/admin/admin_create_lifecycle_service.py` — v201 분리 완료
- `backend/app/services/admin/admin_change_log_service.py` — v202 분리 완료
- 다음 후보:
  - `admin_edit_draft_service.py`
  - `admin_shared_utils.py`

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v202.backend-admin-change-log-service-split
```

```js
checkAdminReadOnlyPageReady().backendChangeLogServiceSplitReady
```

예상값:

```txt
true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상값:

```txt
change-logs-extracted-v202
```

## 검증

- `bash tools/run_smoke_core.sh` 통과
- `python tools/smoke_backend_admin_change_log_service_split.py` 통과
- `python tools/smoke_backend_admin_create_lifecycle_service_split.py` 통과
- `python tools/smoke_backend_admin_master_catalog_service_split.py` 통과
- `python tools/smoke_backend_admin_overview_snapshots_service_split.py` 통과
- `python tools/smoke_backend_admin_service_split_contract.py` 통과
- `python tools/smoke_seed_import_long_asset_columns.py` 통과
- `python tools/smoke_seed_import_structure.py` 통과
- `node --check src/api/admin-page-readonly.js` 통과
- `python -m compileall -q backend/app backend/scripts tools` 통과

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음

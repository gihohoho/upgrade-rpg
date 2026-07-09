# Current Status

현재 기준: **v202 backend admin change log service split**

이 패키지 기준 ZIP: **rpg_v202_backend_admin_change_log_service_split_ready.zip**

## 완료된 관리자 JS 분리/정리

- v185: layout shell 분리
- v187: change logs 분리
- v189.1: create lifecycle 분리 + helper export hotfix
- v191: edit draft 분리
- v192: master catalog/detail 분리
- v193: overview/snapshots 분리
- v194: bootstrap/bindEvents thin entry 계약 고정
- v195: thin entry cleanup
- v196: field help/value hints/equip slot label 분리
- v197: settings helpers/API URL/write key/page URL helper 분리

## 백엔드 admin service 분리 상태

- v198: backend admin service split contract 고정
- v199.1: overview/save snapshots service 분리 + hotfix
- v200: master catalog/detail/relations service 분리
- v201: create lifecycle service 분리
- v202: change logs/detail/rollback service 분리

## v202 완료 내용

- `backend/app/services/admin/admin_change_log_service.py` 추가
- `AdminChangeLogService` mixin 추가
- `AdminService(AdminOverviewSnapshotsService, AdminMasterCatalogService, AdminChangeLogService, AdminCreateLifecycleService)` 구조로 변경
- change logs 목록/상세/rollback 관련 public/helper 메서드 이동
- `apply_admin_change_log_rollback()` 성공 경로 `return preview` 보강
- route/schema/API 응답 구조 변경 없음
- `tools/smoke_backend_admin_change_log_service_split.py` 추가
- core smoke에 새 smoke 포함

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().backendChangeLogServiceSplitReady
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
v202.backend-admin-change-log-service-split
true
change-logs-extracted-v202
```

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- `.env`, `.gitignore` 변경 없음
- 기존 로컬 DB가 오래된 상태라 `admin_change_logs` 테이블이 없으면, 데이터 삭제 없이 `python scripts/setup_dev_db.py --create-schema --verify`만 실행

## 검증

- `bash tools/run_smoke_core.sh` 통과
- `python tools/smoke_backend_admin_change_log_service_split.py` 통과
- `python tools/smoke_seed_import_long_asset_columns.py` 통과
- `python tools/smoke_seed_import_structure.py` 통과
- `python -m compileall -q backend/app backend/scripts tools` 통과

# Current Status

현재 기준: **v199.1 backend admin overview/snapshots service hotfix**

이 패키지 기준 ZIP: **rpg_v199_1_backend_admin_overview_snapshots_service_hotfix_ready.zip**

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
- v199: overview/save snapshots service 실제 1차 분리

## v199 완료 내용

- `backend/app/services/admin/` 폴더 추가
- `backend/app/services/admin/admin_overview_snapshots_service.py` 추가
- `AdminOverviewSnapshotsService` 추가
- `AdminService` facade는 유지하면서 overview/save snapshots 메서드만 mixin으로 이동
- route/schema/API 응답 구조 변경 없음
- `tools/smoke_backend_admin_overview_snapshots_service_split.py` 추가
- core smoke에 새 smoke 포함

## v199.1 hotfix 내용

- `/api/v1/admin/save-snapshots` 500 오류 수정
- `_count_filled_items` staticmethod 누락 복구
- snapshot summary runtime smoke 추가

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().backendOverviewSnapshotsServiceSplitReady
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
v199.1.backend-admin-overview-snapshots-service-hotfix
true
overview-snapshots-extracted-v199.1
```

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음

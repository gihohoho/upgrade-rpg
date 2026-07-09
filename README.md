# Upgrade RPG v199 패키지

현재 안정 버전: **v199 backend admin overview/snapshots service split**

새 채팅 인수인계 ZIP: **rpg_v199_backend_admin_overview_snapshots_service_split_ready.zip**

## 요약

v199에서는 v198에서 고정한 백엔드 admin service 분리 계약을 기준으로, 가장 안전한 첫 묶음인 **overview/save snapshots 서비스**를 실제로 1차 분리했습니다.

`backend/app/api/routes/admin.py`와 schema는 변경하지 않았고, 기존 `AdminService` facade도 그대로 유지했습니다.

## v199에서 정리한 것

- `backend/app/services/admin/` 폴더 추가
- `backend/app/services/admin/__init__.py` 추가
- `backend/app/services/admin/admin_overview_snapshots_service.py` 추가
- `AdminOverviewSnapshotsService` mixin 추가
- `AdminService(AdminOverviewSnapshotsService)` 구조로 변경
- overview/save snapshots 관련 public/helper 메서드를 외부 서비스로 이동
- 기존 route/schema/API 응답 구조 유지
- `tools/smoke_backend_admin_overview_snapshots_service_split.py` 추가
- `tools/run_smoke_core.sh`에 새 smoke 포함
- 기존 `tools/smoke_admin_readonly_api_structure.py`를 분리 구조에 맞게 갱신

## 현재 백엔드 admin service 상태

- `backend/app/services/admin_service.py` — route가 계속 import하는 facade
- `backend/app/services/admin/admin_overview_snapshots_service.py` — v199 분리 완료
- 다음 후보:
  - `admin_master_catalog_service.py`
  - `admin_create_lifecycle_service.py`
  - `admin_change_log_service.py`
  - `admin_edit_draft_service.py`
  - `admin_shared_utils.py`

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v199.backend-admin-overview-snapshots-service-split
```

```js
checkAdminReadOnlyPageReady().backendOverviewSnapshotsServiceSplitReady
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
overview-snapshots-extracted-v199
```

## 검증

- `bash tools/run_smoke_core.sh` 통과
- `bash tools/run_smoke_all.sh` 통과
- `python tools/smoke_backend_admin_overview_snapshots_service_split.py` 통과
- `python tools/smoke_backend_admin_service_split_contract.py` 통과
- `node --check src/api/admin-page-readonly.js` 통과
- `python -m compileall -q backend/app` 통과

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음

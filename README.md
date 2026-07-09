# Upgrade RPG v200 패키지

현재 안정 버전: **v200 backend admin master catalog/detail service split**

새 채팅 인수인계 ZIP: **rpg_v200_backend_admin_master_catalog_service_split_ready.zip**

## 요약

v200에서는 백엔드 `AdminService` facade를 유지한 상태로, **master catalog/detail/relations** 묶음을 `AdminMasterCatalogService` mixin으로 실제 분리했습니다.

`backend/app/api/routes/admin.py`와 schema/API 응답 구조는 변경하지 않았습니다.

## v200에서 정리한 것

- `backend/app/services/admin/admin_master_catalog_service.py` 추가
- `AdminMasterCatalogService` mixin 추가
- `AdminService(AdminOverviewSnapshotsService, AdminMasterCatalogService)` 구조로 변경
- master catalog/detail/relations 관련 public/helper 메서드 이동
- shared read-only serializer/helper 일부 이동
- `tools/smoke_backend_admin_master_catalog_service_split.py` 추가
- `tools/run_smoke_core.sh`에 새 smoke 포함
- 기존 static smoke를 분리 구조에 맞게 갱신

## 현재 백엔드 admin service 상태

- `backend/app/services/admin_service.py` — route가 계속 import하는 facade
- `backend/app/services/admin/admin_overview_snapshots_service.py` — v199.1 분리 완료
- `backend/app/services/admin/admin_master_catalog_service.py` — v200 분리 완료
- 다음 후보:
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
v200.backend-admin-master-catalog-service-split
```

```js
checkAdminReadOnlyPageReady().backendMasterCatalogServiceSplitReady
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
master-catalog-extracted-v200
```

## 검증

- `bash tools/run_smoke_core.sh` 통과
- `bash tools/run_smoke_all.sh` 대부분 통과 후 시간 제한, 남은 python smoke 개별 통과
- `python tools/smoke_backend_admin_master_catalog_service_split.py` 통과
- `python tools/smoke_backend_admin_overview_snapshots_service_split.py` 통과
- `python tools/smoke_backend_admin_service_split_contract.py` 통과
- `node --check src/api/admin-page-readonly.js` 통과
- `python -m compileall -q backend/app` 통과

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음

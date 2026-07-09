# Backend Admin Service Split Contract

v198에서는 `backend/app/services/admin_service.py`를 바로 쪼개지 않고, 먼저 어떤 기능 묶음을 어떤 파일로 분리할지 계약과 smoke로 고정했습니다.

## 추가 파일

- `backend/app/services/admin_service_split_contract.py`
- `tools/smoke_backend_admin_service_split_contract.py`

## 계약 상태

```txt
contract-frozen-v198
```

## 분리 후보

- `backend/app/services/admin/admin_overview_snapshots_service.py`
- `backend/app/services/admin/admin_master_catalog_service.py`
- `backend/app/services/admin/admin_edit_draft_service.py`
- `backend/app/services/admin/admin_create_lifecycle_service.py`
- `backend/app/services/admin/admin_change_log_service.py`
- `backend/app/services/admin/admin_shared_utils.py`

## 유지해야 하는 것

v198에서는 아래를 바꾸지 않았습니다.

- API route path
- request/response schema
- DB schema
- seed
- `AdminService` facade import 위치

즉, 실제 분리는 다음 단계부터 하더라도 `backend/app/api/routes/admin.py`는 계속 `AdminService`를 호출하는 형태로 유지하는 방향입니다.

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().backendServiceSplitContractReady
getAdminBackendServiceSplitContractReadiness().status
```

예상:

```txt
true
contract-frozen-v198
```

## 검증

```bash
위치: 프로젝트 루트
python tools/smoke_backend_admin_service_split_contract.py
```

```bash
위치: 프로젝트 루트
bash tools/run_smoke_core.sh
```

## 다음 단계

v199에서는 계약을 기준으로 백엔드 서비스 실제 분리 1단계를 진행하는 것이 좋습니다.

추천 첫 분리 대상:

- overview/save snapshots

이 묶음은 관리자 쓰기 기능과 직접 연결되지 않아 상대적으로 안전합니다.

## v199 진행 상태

v199에서 첫 실제 분리로 `overview-snapshots` 묶음을 `backend/app/services/admin/admin_overview_snapshots_service.py`로 이동했습니다.

- route/schema 변경 없음
- `AdminService` facade 유지
- `tools/smoke_backend_admin_overview_snapshots_service_split.py`로 분리 상태 검증

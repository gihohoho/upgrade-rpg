# Backend Admin Route Params/Error Helpers — v210

v210에서는 `backend/app/api/routes/admin.py` 안에 반복되던 FastAPI dependency/query 기본값과 `change-logs` route-level 예외 fallback payload 생성을 별도 helper로 분리했다.

## 추가 파일

- `backend/app/api/routes/admin_route_params.py`
  - `ADMIN_CURRENT_USER_DEP`
  - `ADMIN_DB_SESSION_DEP`
  - `ADMIN_WRITE_GUARD_DEP`
  - master catalog / change logs / save snapshot query 기본값
- `backend/app/api/routes/admin_route_error_helpers.py`
  - `build_admin_change_logs_unavailable_payload()`

## 유지 조건

- route path 변경 없음
- `backend/app/schemas/admin.py` 변경 없음
- API 응답 envelope 변경 없음
- DB/env 변경 없음
- `AdminService` facade 유지

## 확인값

```js
checkAdminReadOnlyPageReady().version
// v210.backend-admin-route-params-error-helpers

checkAdminReadOnlyPageReady().backendRouteParamsReady
// true

checkAdminReadOnlyPageReady().backendRouteErrorHelperReady
// true

getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-route-params-errors-v210
```

## 검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke/contracts/smoke_backend_admin_route_params_error_helpers.py
python -m compileall -q backend/app backend/scripts tools
```

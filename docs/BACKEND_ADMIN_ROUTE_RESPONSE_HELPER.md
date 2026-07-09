# Backend Admin Route Response Helper — v208

v208에서는 `backend/app/api/routes/admin.py`가 직접 `app.core.response.ok_response`를 호출하지 않고, 관리자 라우터 전용 wrapper인 `admin_ok_response()`를 통하도록 정리했다.

## 목적

- 관리자 라우터의 응답 생성 지점을 한 곳으로 모은다.
- 다음 단계에서 `admin.py`를 기능별 sub-router로 나눌 때 응답 envelope 변경 위험을 줄인다.
- 기존 route path, schema, API 응답 구조는 유지한다.

## 변경 파일

- `backend/app/api/routes/admin_response_helpers.py` 추가
- `backend/app/api/routes/admin.py`의 `ok_response()` 호출을 `admin_ok_response()`로 교체
- `backend/app/services/admin_service_split_contract.py` splitStatus 갱신
- `src/api/admin-page-readonly.js` readiness 버전/계약 갱신
- `tools/smoke_backend_admin_route_response_helper.py` 추가
- `tools/run_smoke_core.sh`에 v208 smoke 추가

## 유지 조건

- route path 변경 없음
- schema 변경 없음
- DB/env 변경 없음
- 응답 envelope 변경 없음
- AdminService facade 유지

## 확인값

관리자 페이지 콘솔:

```js
checkAdminReadOnlyPageReady().version
// v208.backend-admin-route-response-helper

checkAdminReadOnlyPageReady().backendRouteResponseHelperReady
// true

getAdminBackendServiceSplitContractReadiness().splitStatus
// route-response-helper-v208
```

## 검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_response_helper.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

# Upgrade RPG v210 패키지

현재 안정 버전: **v210 backend admin route params/error helpers**

새 채팅 인수인계 ZIP: **rpg_v210_backend_admin_route_params_error_helpers_ready.zip**

## 이번 v209~v210에서 정리한 것

v209~v210에서는 관리자 백엔드 라우터의 반복되는 dependency/query 기본값과 `change-logs` 로컬 fallback payload 생성을 별도 helper로 분리했습니다. 기존 API 경로, schema, 응답 데이터 구조, DB/env는 바꾸지 않았습니다.

## 핵심 변경

- `backend/app/api/routes/admin_route_params.py` 추가
- `backend/app/api/routes/admin_route_error_helpers.py` 추가
- `backend/app/api/routes/admin.py`의 반복 `Depends(...)`, `Query(...)` 기본값을 helper 상수로 정리
- `/admin/change-logs` route-level 예외 fallback payload 생성을 helper로 이동
- `backend/app/services/admin_service_split_contract.py`의 `splitStatus`를 `admin-route-params-errors-v210`로 갱신
- `src/api/admin-page-readonly.js`의 readiness 버전을 v210으로 갱신
- v210 전용 smoke test 추가

## 확인값

관리자 페이지 콘솔:

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v210.backend-admin-route-params-error-helpers
```

```js
checkAdminReadOnlyPageReady().backendRouteParamsReady
```

예상:

```txt
true
```

```js
checkAdminReadOnlyPageReady().backendRouteErrorHelperReady
```

예상:

```txt
true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
admin-route-params-errors-v210
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_params_error_helpers.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

## 서버 실행

실행 위치: backend 폴더

```bash
uvicorn app.main:app --reload
```

DB reset/seed 재실행은 필요 없습니다.

# Upgrade RPG v208 패키지

현재 안정 버전: **v208 backend admin route response helper**

새 채팅 인수인계 ZIP: **rpg_v208_backend_admin_route_response_helper_ready.zip**

## 이번 v207~v208에서 정리한 것

v207~v208에서는 관리자 백엔드 라우터의 응답 생성 지점을 `admin_ok_response()` helper로 모았습니다. 기존 API 경로, schema, 응답 데이터 구조, DB/env는 바꾸지 않았습니다.

## 핵심 변경

- `backend/app/api/routes/admin_response_helpers.py` 추가
- `backend/app/api/routes/admin.py`의 `ok_response()` 직접 호출 제거
- 기존 모든 관리자 route는 동일한 payload/data/meta 구조 유지
- `backend/app/services/admin_service_split_contract.py`의 `splitStatus`를 `route-response-helper-v208`로 갱신
- `src/api/admin-page-readonly.js`의 readiness 버전을 v208로 갱신
- v208 전용 smoke test 추가

## 확인값

관리자 페이지 콘솔:

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v208.backend-admin-route-response-helper
```

```js
checkAdminReadOnlyPageReady().backendRouteResponseHelperReady
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
route-response-helper-v208
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_response_helper.py
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

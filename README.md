# Upgrade RPG v212 패키지

현재 안정 버전: **v212 backend admin route data/meta helpers**

새 채팅 인수인계 ZIP: **rpg_v212_backend_admin_route_data_meta_helpers_ready.zip**

## 이번 v211~v212에서 정리한 것

v211~v212에서는 관리자 백엔드 라우터 `backend/app/api/routes/admin.py` 안에 반복되던 응답 `data={...}` 요약 생성과 `meta={...}` 안내 문구 생성을 별도 helper로 분리했습니다.

기존 API 경로, request/response schema, 응답 envelope, DB/env는 바꾸지 않았습니다.

## 주요 변경 파일

- `backend/app/api/routes/admin_response_data_helpers.py` 추가
- `backend/app/api/routes/admin_response_meta_helpers.py` 추가
- `backend/app/api/routes/admin.py`에서 response data/meta helper 사용
- `backend/app/services/admin_service_split_contract.py`의 `splitStatus`를 `admin-route-data-meta-helpers-v212`로 갱신
- `src/api/admin-page-readonly.js`의 readiness 버전을 v212로 갱신
- `tools/smoke_backend_admin_route_response_data_meta_helpers.py` 추가
- 기존 smoke test 일부를 v212 구조에 맞게 조정

## 확인값

관리자 페이지 콘솔:

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v212.backend-admin-route-data-meta-helpers
```

```js
checkAdminReadOnlyPageReady().backendRouteResponseDataHelperReady
```

예상:

```txt
true
```

```js
checkAdminReadOnlyPageReady().backendRouteResponseMetaHelperReady
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
admin-route-data-meta-helpers-v212
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_response_data_meta_helpers.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

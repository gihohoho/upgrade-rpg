# Upgrade RPG v214 패키지

현재 안정 버전: **v214 backend admin route module split**

새 채팅 인수인계 ZIP: **rpg_v214_backend_admin_route_module_split_ready.zip**

## 이번 v213~v214에서 정리한 것

v213~v214에서는 관리자 백엔드 라우터 `backend/app/api/routes/admin.py`를 기능별 route module로 분리했습니다.

- v213: master-data 관련 route를 `admin_master_data_routes.py`로 분리
- v214: change-log/rollback/create-delete 관련 route를 `admin_change_log_routes.py`로 분리
- 기존 `admin.py`는 overview/save-snapshots/change-preview와 include facade 역할로 축소

기존 API 경로, request/response schema, 응답 envelope, DB/env는 바꾸지 않았습니다.

## 주요 변경 파일

- `backend/app/api/routes/admin_master_data_routes.py` 추가
- `backend/app/api/routes/admin_change_log_routes.py` 추가
- `backend/app/api/routes/admin.py`를 router include facade로 축소
- `backend/app/services/admin_service_split_contract.py`의 `splitStatus`를 `admin-route-module-split-v214`로 갱신
- `src/api/admin-page-readonly.js`의 readiness 버전을 v214로 갱신
- `tools/smoke_backend_admin_route_module_split.py` 추가
- 기존 smoke test 일부를 v214 구조에 맞게 조정

## 확인값

관리자 페이지 콘솔:

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v214.backend-admin-route-module-split
```

```js
checkAdminReadOnlyPageReady().backendRouteModuleSplitReady
```

예상:

```txt
true
```

```js
checkAdminReadOnlyPageReady().backendRouteMasterDataModuleReady
```

예상:

```txt
true
```

```js
checkAdminReadOnlyPageReady().backendRouteChangeLogModuleReady
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
admin-route-module-split-v214
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_module_split.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

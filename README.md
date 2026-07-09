# Upgrade RPG v216 패키지

현재 안정 버전: **v216 backend admin route overview facade split**

새 채팅 인수인계 ZIP: **rpg_v216_backend_admin_overview_route_facade_split_ready.zip**

## 이번 v215~v216에서 정리한 것

v215~v216에서는 관리자 백엔드 라우터 `backend/app/api/routes/admin.py`에 남아 있던 overview/save-snapshot/readiness route까지 기능별 route module로 분리했습니다.

- v215: requirements / overview / save-snapshots / change-preview route를 `admin_overview_snapshot_routes.py`로 분리
- v216: `admin.py`를 include-router facade 수준으로 축소
- 기존 master-data route module 유지
- 기존 change-log route module 유지
- API path/schema/응답 구조 변경 없음
- DB/env 변경 없음

## 주요 변경 파일

- `backend/app/api/routes/admin.py`
- `backend/app/api/routes/admin_overview_snapshot_routes.py`
- `backend/app/services/admin_service_split_contract.py`
- `src/api/admin-page-readonly.js`
- `tools/smoke_backend_admin_overview_route_module_split.py`
- `tools/run_smoke_core.sh`

## 관리자 콘솔 확인

```js
checkAdminReadOnlyPageReady().version
// v216.backend-admin-route-overview-facade-split
```

```js
checkAdminReadOnlyPageReady().backendRouteOverviewSnapshotModuleReady
// true
```

```js
checkAdminReadOnlyPageReady().backendRouteFacadeReady
// true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-route-overview-facade-split-v216
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_overview_route_module_split.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

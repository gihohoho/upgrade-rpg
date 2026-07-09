# Upgrade RPG v224 패키지

현재 안정 버전: **v224 backend admin route module import contract**

새 채팅 인수인계 ZIP: **rpg_v224_backend_admin_route_ownership_import_contract_ready.zip**

## 이번 v223~v224에서 정리한 것

v223~v224에서는 관리자 route module 분리 상태를 더 강하게 고정했습니다. 기존에는 route가 각 파일에 “있는지” 중심으로 봤다면, 이제는 route가 **정해진 파일에만 존재하는지**, route type marker가 중복되지 않는지, route module들이 공통 service factory/import 패턴을 지키는지까지 확인합니다.

- v223: `backend/app/api/routes/admin_route_map_contract.py` strict ownership 검증 강화
- v223: route decorator 실제 수와 contract 수가 같은지 검증
- v223: 각 route method/path가 지정된 module에만 존재하는지 검증
- v223: 각 response `type="..."` marker가 지정된 module에만 존재하는지 검증
- v224: `backend/app/api/routes/admin_route_module_import_contract.py` 추가
- v224: route module이 `create_admin_service()` factory를 쓰는지 검증
- v224: route module이 `AdminService()`를 직접 생성하지 않는지 검증
- v224: route module import/dependency 기본 패턴 검증
- API path/schema/응답 구조 변경 없음
- DB/env 변경 없음

## 주요 변경 파일

- `backend/app/api/routes/admin_route_map_contract.py`
- `backend/app/api/routes/admin_route_module_import_contract.py`
- `backend/app/api/routes/admin_master_data_routes.py`
- `backend/app/api/routes/admin_change_log_routes.py`
- `backend/app/api/routes/admin_overview_snapshot_routes.py`
- `backend/app/services/admin_service_split_contract.py`
- `src/api/admin-page-readonly.js`
- `tools/smoke_backend_admin_route_map_contract.py`
- `tools/smoke_backend_admin_route_module_import_contract.py`
- `tools/run_smoke_core.sh`

## 관리자 콘솔 확인

```js
checkAdminReadOnlyPageReady().version
// v224.backend-admin-route-module-import-contract
```

```js
checkAdminReadOnlyPageReady().backendRouteOwnershipStrictReady
// true
```

```js
checkAdminReadOnlyPageReady().backendRouteModuleImportContractReady
// true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-route-module-import-contract-v224
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_map_contract.py
python tools/smoke_backend_admin_route_module_import_contract.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

참고: 전체 `run_smoke_core.sh`는 로컬/도구 환경에서 시간이 오래 걸릴 수 있습니다. 이번 패키지에서는 v224 전용 smoke, backend split smoke, frontend readiness smoke, seed import, compileall을 별도 실행으로 통과 확인했습니다.

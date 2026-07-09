# Upgrade RPG v218 패키지

현재 안정 버전: **v218 backend admin route map contract**

새 채팅 인수인계 ZIP: **rpg_v218_backend_admin_route_map_contract_ready.zip**

## 이번 v217~v218에서 정리한 것

v217~v218에서는 관리자 백엔드 라우터 `backend/app/api/routes/admin.py`에 남아 있던 legacy static-smoke marker 주석을 제거하고, 실제 route 소유 파일을 검증하는 route map contract를 추가했습니다.

- v217: 오래된 smoke가 `admin.py` 주석 대신 실제 route module/helper 파일을 보도록 조정
- v217: `admin.py` 하단의 긴 legacy marker 주석 제거
- v218: `backend/app/api/routes/admin_route_map_contract.py` 추가
- v218: route ownership map/readiness 추가
- 기존 master-data / change-log / overview-snapshot route module 유지
- API path/schema/응답 구조 변경 없음
- DB/env 변경 없음

## 주요 변경 파일

- `backend/app/api/routes/admin.py`
- `backend/app/api/routes/admin_route_map_contract.py`
- `backend/app/services/admin_service_split_contract.py`
- `src/api/admin-page-readonly.js`
- `tools/smoke_backend_admin_route_map_contract.py`
- `tools/run_smoke_core.sh`
- legacy admin route smoke 일부

## 관리자 콘솔 확인

```js
checkAdminReadOnlyPageReady().version
// v218.backend-admin-route-map-contract
```

```js
checkAdminReadOnlyPageReady().backendRouteMapContractReady
// true
```

```js
checkAdminReadOnlyPageReady().backendRouteLegacySmokeCleanupReady
// true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-route-map-contract-v218
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_map_contract.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

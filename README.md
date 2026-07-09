# Upgrade RPG v220 패키지

현재 안정 버전: **v220 backend admin route service dependency + legacy marker cleanup**

새 채팅 인수인계 ZIP: **rpg_v220_backend_admin_route_service_legacy_cleanup_ready.zip**

## 이번 v219~v220에서 정리한 것

v219~v220에서는 관리자 route module의 service 생성 방식을 한 곳으로 모으고, `backend/app/services/admin_service.py`에 남아 있던 긴 legacy smoke marker 문자열을 별도 파일로 분리했습니다.

- v219: `backend/app/api/routes/admin_route_services.py` 추가
- v219: `admin_overview_snapshot_routes.py`, `admin_master_data_routes.py`, `admin_change_log_routes.py`가 `create_admin_service()`를 통해 service facade 생성
- v220: `backend/app/services/admin_service_legacy_markers.py` 추가
- v220: `admin_service.py`에서 legacy marker 상수 제거
- v220: `admin_service.py`는 19줄짜리 실제 facade만 유지
- 오래된 smoke는 `admin_service.py` 대신 legacy marker 파일을 보도록 조정
- API path/schema/응답 구조 변경 없음
- DB/env 변경 없음

## 주요 변경 파일

- `backend/app/api/routes/admin_route_services.py`
- `backend/app/api/routes/admin_overview_snapshot_routes.py`
- `backend/app/api/routes/admin_master_data_routes.py`
- `backend/app/api/routes/admin_change_log_routes.py`
- `backend/app/services/admin_service.py`
- `backend/app/services/admin_service_legacy_markers.py`
- `backend/app/services/admin_service_split_contract.py`
- `src/api/admin-page-readonly.js`
- `tools/smoke_backend_admin_route_service_legacy_cleanup.py`
- `tools/run_smoke_core.sh`
- legacy admin smoke 일부

## 관리자 콘솔 확인

```js
checkAdminReadOnlyPageReady().version
// v220.backend-admin-route-service-legacy-cleanup
```

```js
checkAdminReadOnlyPageReady().backendRouteServiceDependencyReady
// true
```

```js
checkAdminReadOnlyPageReady().backendServiceLegacyMarkersReady
// true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-service-legacy-marker-cleanup-v220
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_service_legacy_cleanup.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

참고: 이번 패키지에서는 `run_smoke_core.sh`가 v220 smoke까지 통과하는 로그를 확인했고, 도구 시간 제한 때문에 마지막 tail smoke/seed/compileall은 별도 명령으로 통과 확인했습니다.

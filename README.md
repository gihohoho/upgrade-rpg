# Upgrade RPG v228 패키지

현재 안정 버전: **v228 backend admin route operation contract**

새 채팅 인수인계 ZIP: **rpg_v228_backend_admin_route_operation_contract_ready.zip**

## 이번 v227~v228에서 정리한 것

v227~v228에서는 관리자 route module 분리 상태를 한 단계 더 안전하게 고정했습니다. 기존 v226은 FastAPI 앱에 실제 등록된 `/api/v1/admin/...` route 목록을 static ownership map과 비교했고, 이번 단계는 각 route의 endpoint/function name과 `admin_ok_response(type="...")` response marker까지 함께 검증합니다.

- v227: `backend/app/api/routes/admin_route_operation_contract.py` 추가
- v227: 관리자 route 21개의 endpoint/function name, response type marker, owner file 고정
- v227: static route ownership map과 operation metadata 비교
- v227: route source의 endpoint/type/admin_ok_response 연결 검증
- v227: FastAPI runtime route endpoint/name 비교
- v228: `backend/app/services/admin_service_split_contract.py` splitStatus 갱신
- v228: `src/api/admin-page-readonly.js` readiness 버전/flag 갱신
- v228: `tools/smoke_backend_admin_route_operation_contract.py` 추가
- v228: `tools/run_smoke_core.sh`에 route operation smoke 연결
- route path/schema/API 응답 구조 변경 없음
- DB/env 변경 없음

## 확인 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_route_operation_contract.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

## 관리자 페이지 콘솔 확인

```js
checkAdminReadOnlyPageReady().version
// v228.backend-admin-route-operation-contract
```

```js
checkAdminReadOnlyPageReady().backendRouteOperationContractReady
// true
```

```js
checkAdminReadOnlyPageReady().backendRuntimeRouteEndpointMetadataReady
// true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-route-operation-contract-v228
```

## 서버 재실행

실행 위치: backend 폴더

```bash
uvicorn app.main:app --reload
```

DB reset/seed 재실행은 필요 없습니다.

## 참고

`run_smoke_core.sh`는 로컬/도구 환경에서 시간이 오래 걸릴 수 있습니다. 이번 패키지에서는 core smoke가 backend overview route module split 지점까지 통과한 뒤 도구 시간 제한에 걸렸고, 남은 tail smoke / v228 operation route smoke / seed / compileall은 별도 실행으로 통과 확인했습니다.

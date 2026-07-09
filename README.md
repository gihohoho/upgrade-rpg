# Upgrade RPG v230 패키지

현재 안정 버전: **v230 backend admin OpenAPI route contract**

새 채팅 인수인계 ZIP: **rpg_v230_backend_admin_openapi_route_contract_ready.zip**

## 이번 v229~v230에서 정리한 것

v229~v230에서는 관리자 route module 분리 상태를 FastAPI OpenAPI 문서 레이어까지 고정했습니다. 기존 v228은 route endpoint/function name과 `admin_ok_response(type="...")` marker를 runtime route와 대조했고, 이번 단계는 `/openapi.json`에 노출되는 method/path/operationId/tag/200 response까지 함께 검증합니다.

- v229: `backend/app/api/routes/admin_openapi_route_contract.py` 추가
- v229: FastAPI OpenAPI schema의 `/api/v1/admin/...` route 21개 추출/검증
- v229: OpenAPI operationId가 runtime endpoint name 기준과 일치하는지 검증
- v229: OpenAPI admin tag와 200 response metadata 유지 검증
- v230: `backend/app/services/admin_service_split_contract.py` splitStatus 갱신
- v230: `src/api/admin-page-readonly.js` readiness 버전/flag 갱신
- v230: `tools/smoke_backend_admin_openapi_route_contract.py` 추가
- v230: `tools/run_smoke_core.sh`에 OpenAPI route smoke 연결
- route path/schema/API 응답 구조 변경 없음
- DB/env 변경 없음

## 확인 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_openapi_route_contract.py
python tools/smoke_backend_admin_route_operation_contract.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

## 관리자 페이지 콘솔 확인

```js
checkAdminReadOnlyPageReady().version
// v230.backend-admin-openapi-route-contract
```

```js
checkAdminReadOnlyPageReady().backendOpenApiRouteContractReady
// true
```

```js
checkAdminReadOnlyPageReady().backendOpenApiRouteMetadataReady
// true
```

```js
checkAdminReadOnlyPageReady().backendOpenApiOperationIdMetadataReady
// true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-openapi-route-contract-v230
```

## 서버 재실행

실행 위치: backend 폴더

```bash
uvicorn app.main:app --reload
```

DB reset/seed 재실행은 필요 없습니다.

## 참고

`run_smoke_core.sh`는 로컬/도구 환경에서 시간이 오래 걸릴 수 있습니다. 필요한 경우 v230 전용 smoke와 seed/compileall을 먼저 나눠서 확인해도 됩니다.

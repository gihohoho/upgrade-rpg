# RPG Admin Backend Split Ready

현재 안정 버전: **v232 backend admin response metadata contract**

새 채팅 인수인계 ZIP: **rpg_v232_backend_admin_response_metadata_contract_ready.zip**

## 현재 상태

- Vue/FastAPI 기반 RPG 관리자 페이지 정리 진행 중
- 관리자 API route path/schema/response body 구조 변경 없음
- DB/env 변경 없음
- `admin.py`는 include-router facade로 축소 완료
- 관리자 route module / runtime route / OpenAPI route / response metadata contract까지 검증 연결 완료

## 이번 버전 핵심

- `backend/app/api/routes/admin_response_metadata_contract.py` 추가
- FastAPI runtime route의 `status_code`, `response_model`, `include_in_schema` metadata 고정
- OpenAPI summary / response code / response description drift 검증
- route별 200 응답과 필요한 422 validation 응답 유지 확인

## 관리자 콘솔 확인

```js
checkAdminReadOnlyPageReady().version
// v232.backend-admin-response-metadata-contract
```

```js
checkAdminReadOnlyPageReady().backendResponseMetadataContractReady
// true
```

```js
checkAdminReadOnlyPageReady().backendRuntimeResponseDefaultsReady
// true
```

```js
checkAdminReadOnlyPageReady().backendOpenApiResponseCodeMetadataReady
// true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
// admin-response-metadata-contract-v232
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_response_metadata_contract.py
python tools/smoke_backend_admin_openapi_route_contract.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

## 다음 추천 작업

v233 backend admin route request/dependency metadata contract

- query/path/body parameter metadata 검증
- apply route write guard dependency 유지 확인
- route path/schema/API 응답 구조 변경 없음

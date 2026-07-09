# Backend Ready — v230

현재 안정 버전: `v230.backend-admin-openapi-route-contract`

## 백엔드 상태

- `backend/app/api/routes/admin_openapi_route_contract.py` 추가 완료
- `backend/app/services/admin_service_split_contract.py` splitStatus: `admin-openapi-route-contract-v230`
- 관리자 route path/schema/API 응답 구조 변경 없음
- DB/env 변경 없음

## 핵심 보장

- 관리자 route 21개의 method/path는 기존과 동일합니다.
- 각 route의 endpoint/function name이 contract에 고정되었습니다.
- FastAPI runtime 등록 route의 endpoint/name이 static operation metadata와 일치하는지 검증합니다.
- OpenAPI schema에 노출되는 admin route method/path/operationId/tag/200 response metadata가 contract와 일치하는지 검증합니다.

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_openapi_route_contract.py
python tools/smoke_backend_admin_route_operation_contract.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

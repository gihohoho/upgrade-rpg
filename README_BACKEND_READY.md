# Backend Ready — v232

현재 안정 버전: `v232.backend-admin-response-metadata-contract`

## 백엔드 상태

- `backend/app/api/routes/admin_response_metadata_contract.py` 추가 완료
- `backend/app/services/admin_service_split_contract.py` splitStatus: `admin-response-metadata-contract-v232`
- 관리자 route path/schema/API 응답 구조 변경 없음
- DB/env 변경 없음

## 핵심 보장

- 관리자 route 21개의 method/path는 기존과 동일합니다.
- 각 route의 endpoint/function name과 OpenAPI operationId가 contract에 고정되었습니다.
- FastAPI runtime 등록 route의 기본 응답 metadata가 유지되는지 검증합니다.
- route별 `status_code` 미지정, `response_model` 미지정, OpenAPI 포함 상태가 유지되는지 검증합니다.
- OpenAPI summary / 200 response / 필요한 422 validation response metadata가 contract와 일치하는지 검증합니다.

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

# 다음 채팅 시작 프롬프트 — RPG v228 이후

이 프로젝트는 Vue/FastAPI 기반 RPG 관리자 페이지/백엔드 정리 작업이다. 질문자는 코딩을 잘 모르는 기호이므로, 설명은 한국어로 쉽게 하고 터미널 명령은 항상 실행 위치를 먼저 적은 뒤 복사 가능한 코드 블록으로 준다.

현재 기준 ZIP은 `rpg_v228_backend_admin_route_operation_contract_ready.zip` 이다.

## 현재 안정 상태

- `checkAdminReadOnlyPageReady().version`: `v228.backend-admin-route-operation-contract`
- `getAdminBackendServiceSplitContractReadiness().splitStatus`: `admin-route-operation-contract-v228`
- API route path/schema/response 구조 변경 없음
- DB/env 변경 없음

## 최근 완료 작업

- `backend/app/api/routes/admin_route_operation_contract.py` 추가
- 관리자 route 21개의 endpoint/function name, response type marker, owner file을 contract로 고정
- static route ownership map과 operation metadata 대조
- FastAPI runtime route endpoint/name과 static operation metadata 대조
- `tools/smoke_backend_admin_route_operation_contract.py` 추가
- `tools/run_smoke_core.sh`에 operation contract smoke 연결

## 다음 추천 작업

v229 backend admin route OpenAPI metadata smoke:

1. FastAPI OpenAPI schema에 노출되는 `/api/v1/admin/...` route method/path/operationId 추출
2. `admin_route_operation_contract.py`의 endpoint metadata와 OpenAPI operationId 대조
3. route path/schema/API 응답 구조 변경 없이 smoke만 강화
4. v229 전용 smoke 추가

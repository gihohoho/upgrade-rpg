# 다음 채팅 시작 프롬프트 — RPG v230 이후

이 프로젝트는 Vue/FastAPI 기반 RPG 관리자 페이지/백엔드 정리 작업이다. 질문자는 코딩을 잘 모르는 기호이므로, 설명은 한국어로 쉽게 하고 터미널 명령은 항상 실행 위치를 먼저 적은 뒤 복사 가능한 코드 블록으로 준다. git 명령은 `git add`, `git commit`, `git push`를 프로젝트 루트에서 한 번에 복사 가능한 하나의 코드블록으로 제공한다.

현재 기준 ZIP은 `rpg_v230_backend_admin_openapi_route_contract_ready.zip` 이다.

## 현재 안정 상태

- `checkAdminReadOnlyPageReady().version`: `v230.backend-admin-openapi-route-contract`
- `getAdminBackendServiceSplitContractReadiness().splitStatus`: `admin-openapi-route-contract-v230`
- API route path/schema/response 구조 변경 없음
- DB/env 변경 없음

## 최근 완료 작업

- `backend/app/api/routes/admin_openapi_route_contract.py` 추가
- FastAPI OpenAPI schema에 노출되는 `/api/v1/admin/...` route 21개 검증
- OpenAPI method/path/operationId/tag/200 response metadata를 static operation contract와 대조
- `tools/smoke_backend_admin_openapi_route_contract.py` 추가
- `tools/run_smoke_core.sh`에 OpenAPI route contract smoke 연결

## 다음 추천 작업

v231 backend admin route response-model/status metadata smoke:

1. FastAPI runtime/OpenAPI route response metadata 추출
2. route별 response_model/status_code/default response drift 검증
3. route path/schema/API 응답 구조 변경 없이 smoke만 강화
4. v231 전용 smoke 추가

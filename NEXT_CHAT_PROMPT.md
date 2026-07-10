# 다음 채팅 시작 프롬프트 — RPG v232 이후

이 프로젝트는 Vue/FastAPI 기반 RPG 관리자 페이지/백엔드 정리 작업이다. 질문자는 코딩을 잘 모르는 기호이므로, 설명은 한국어로 쉽게 하고 터미널 명령은 항상 실행 위치를 먼저 적은 뒤 복사 가능한 코드 블록으로 준다. git 명령은 `git add`, `git commit`, `git push`를 프로젝트 루트에서 한 번에 복사 가능한 하나의 코드블록으로 제공한다.

현재 기준 ZIP은 `rpg_v232_backend_admin_response_metadata_contract_ready.zip` 이다.

## 현재 안정 상태

- `checkAdminReadOnlyPageReady().version`: `v232.backend-admin-response-metadata-contract`
- `getAdminBackendServiceSplitContractReadiness().splitStatus`: `admin-response-metadata-contract-v232`
- API route path/schema/response body 구조 변경 없음
- DB/env 변경 없음

## 최근 완료 작업

- `backend/app/api/routes/admin_response_metadata_contract.py` 추가
- FastAPI runtime route의 기본 응답 metadata 검증
- OpenAPI summary / 200 response / 422 validation response metadata를 static operation contract와 대조
- `tools/smoke_backend_admin_response_metadata_contract.py` 추가
- `tools/run_smoke_core.sh`에 response metadata contract smoke 연결

## 다음 추천 작업

v233 backend admin route request/dependency metadata contract:

1. FastAPI runtime route dependency/query/body metadata 추출
2. route별 query/path/body parameter drift 검증
3. apply route의 write guard dependency 유지 검증
4. route path/schema/API 응답 구조 변경 없이 smoke만 강화

# Next Steps — after v239.2

다음 추천 단계는 **v240 backend admin request payload and 422 validation contract**입니다.

## 목표

1. 정상 request payload alias 직렬화 결과 고정
2. preview/apply request가 route/service 진입 전까지 동일하게 parsing되는지 검증
3. 잘못된 payload가 예상한 `422 validation detail` 형태로 거절되는지 검증
4. write guard 유지
5. route path/API 응답 body 구조 유지
6. DB/env 변경 없음

## 추천 구현 파일

- `backend/app/api/routes/admin_request_payload_validation_contract.py`
- `tools/smoke_backend_admin_request_payload_validation_contract.py`
- 필요하면 `docs/BACKEND_ADMIN_REQUEST_PAYLOAD_VALIDATION_CONTRACT.md`

## 작업 원칙

- 실제 DB 쓰기 호출 금지
- apply 계열 write guard 유지
- request validation contract만 추가
- 새 smoke를 `tools/run_smoke_core.sh`에 연결
- 안정적으로 가능하면 v240 smoke와 readiness marker까지 한 번에 진행 가능

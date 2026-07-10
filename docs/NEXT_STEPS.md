# Next Steps — after v238

다음 추천 단계는 **v239~v240 backend admin request example/payload contract**입니다.

## 목표

1. OpenAPI request body example 또는 대표 payload fixture 추가
2. preview/apply request의 alias 직렬화 결과 고정
3. 잘못된 payload가 예상한 422 validation detail 형태로 거절되는지 검증
4. 정상 payload가 route/service 진입 전까지 동일하게 파싱되는지 검증
5. route path/API 응답 body 구조 유지
6. DB/env 변경 없음

## 추천 구현 파일

- `backend/app/api/routes/admin_request_payload_contract.py`
- `tools/smoke_backend_admin_request_payload_contract.py`

## 작업 원칙

- 실제 DB 쓰기 호출 금지
- write guard 유지
- validation contract만 추가
- 새 smoke를 `tools/run_smoke_core.sh`에 연결

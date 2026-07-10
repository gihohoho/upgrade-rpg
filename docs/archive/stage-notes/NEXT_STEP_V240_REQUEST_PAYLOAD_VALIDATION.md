# Next Step — v240 Backend Admin Request Payload and 422 Validation Contract

## 목표

관리자 route의 request parsing 경계를 고정합니다. 실제 DB 쓰기는 실행하지 않고, FastAPI/Pydantic validation 단계까지만 검증합니다.

## 검증 후보

- 정상 payload가 alias 기준으로 들어왔을 때 올바른 model로 parsing되는지 확인
- `confirmText`, `reason`, `dryRun`, `baseValues` alias 유지 확인
- invalid payload의 대표 `422 validation detail` 구조 확인
- apply 계열 route의 `X-Admin-Dev-Key` write guard 유지 확인

## 지켜야 할 것

- route path 변경 없음
- API 응답 body 구조 변경 없음
- DB/env 변경 없음
- 실제 apply 쓰기 실행 없음

## smoke 후보

- `tools/smoke/contracts/smoke_backend_admin_request_payload_validation_contract.py`

## 버전 후보

- readiness version: `v240.backend-admin-request-payload-validation-contract`
- splitStatus: 큰 구조 변경이 아니라면 `admin-schema-field-constraint-contract-v238` 유지 가능

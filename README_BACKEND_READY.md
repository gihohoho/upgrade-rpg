# Backend Ready — v246

현재 안정 버전: `v250.backend-admin-rollback-snapshot`

Backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- FastAPI/Starlette/Pydantic 환경 차이는 허용 결과와 세부 오류 구조로 검증
- backend/frontend `extractedFiles`와 `routeContract` 전체 순서 parity 유지
- preview request 5종의 반복 parsing 결과 일관성 유지
- apply route 5종의 `ADMIN_WRITE_GUARD_DEP` 유지
- `Idempotency-Key`는 현재 미지원으로 명시
- 격리 계약 검사에서 service 호출과 DB 쓰기 시도 0회

## 개발 테스트 의존성

FastAPI `TestClient` 계약 검사를 위해 dev 의존성에 `httpx2`가 포함되어 있습니다.

실행 위치: backend 폴더

```bash
python -m pip install -e ".[dev]"
```

## 검증

실행 위치: 프로젝트 루트

```bash
python tools/smoke_backend_admin_write_replay_safety_contract.py && python tools/smoke_backend_admin_frontend_contract_parity.py && node tools/smoke_admin_readonly_page.js && python -m compileall -q backend/app backend/scripts tools
```

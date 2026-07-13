# Backend Ready

현재 안정 버전: `v250.backend-admin-rollback-snapshot`

Backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- FastAPI/Starlette/Pydantic 환경 차이는 허용 결과와 세부 오류 구조로 검증
- backend/frontend `extractedFiles`와 `routeContract` parity 유지
- preview request 반복 parsing 결과 일관성 유지
- apply route의 Write Guard 유지
- 격리 계약 검사에서 service 호출과 DB 쓰기 시도 0회

## 현재 방향

Backend 자체의 기능 확장보다 Vue/FastAPI/DB 전환 준비를 우선합니다.
단, route path/API response body/write guard는 사용자 승인 없이 변경하지 않습니다.

## 개발 테스트 의존성

실행 위치: `backend` 폴더

```bash
python -m pip install -e ".[dev]"
```

## 검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh && python -m compileall -q backend/app backend/scripts tools
```

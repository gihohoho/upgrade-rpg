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
단, route path/API response body/write guard는 사용자 승인 없이 변경하지 않습니다. v273에서는 Vue 개발 서버 local CORS 오류만 수정했고 `.env` 파일은 변경하지 않았습니다.

## 개발 테스트 의존성

실행 위치: `backend` 폴더  
`.venv` 상태: 켜진 상태

```bash
python -m pip install -e ".[dev]"
```

## v273 local CORS 참고

Vue 개발 서버는 `http://127.0.0.1:5173`, FastAPI는 `http://127.0.0.1:8000`에서 실행되므로 브라우저 CORS 검사가 발생합니다. v273에서는 local/debug 환경에서 Vite 개발 서버 origin을 기본 허용하도록 보강했습니다. CORS 변경은 FastAPI 서버 재시작 후 반영됩니다.

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
bash tools/run_smoke_core.sh && python -m compileall -q backend/app backend/scripts tools
```

# v287-v288 PostgreSQL baseline preflight

- Windows Docker subprocess 출력의 UTF-8/cp949 혼합 decode 오류를 수정했습니다.
- 실제 DB는 모델/실제 테이블 22개, 전체 748 rows, `alembic_version` 없음으로 확인됐습니다.
- 분류는 `existing-schema-without-alembic-baseline`입니다.
- 상세 schema 동등성 읽기 전용 도구를 추가했습니다.
- 실제 backend virtualenv: `backend/.venv`.

# Backend Ready

현재 안정 readiness: `v250.backend-admin-rollback-snapshot`

Backend splitStatus: `admin-schema-field-constraint-contract-v238`

현재 프로젝트 작업 버전: `v288.postgres-baseline-schema-equivalence-preflight`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- backend/frontend contract parity 유지
- apply route Write Guard 유지
- 기존 route path/API response body/write 의미 유지
- DB schema/data/env/seed/revision 변경 없음

## 상세 schema 비교

backend 가상환경 활성화:

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash에서 실행

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
```

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
bash tools/run_smoke_core.sh && python -m compileall -q backend/app backend/scripts backend/alembic tools
```

# Backend Ready — v306

현재 안정 readiness: `v250.backend-admin-rollback-snapshot`  
Backend splitStatus: `admin-schema-field-constraint-contract-v238`  
현재 프로젝트 작업 버전: `v306.postgres-next-revision-readonly-preflight`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- backend/frontend contract parity 유지
- apply route Write Guard 유지
- 기존 route path/API response body/write 의미 유지
- 실제 backend virtualenv: `backend/.venv`

## PostgreSQL / Alembic 상태

- 최초 revision `v295_initial_schema` 수동 검토 통과
- isolated migration DB upgrade → downgrade base → upgrade 왕복 성공
- restore rehearsal와 source baseline stamp/post-check 통과
- source/rehearsal application 22 tables / 748 rows 보존
- source current revision `v295_initial_schema`
- v302/v304 실행 보고서 `verified`
- classification `alembic-managed-baseline-complete`
- v305 completion state 실제 통과
- v306 next-revision read-only preflight 준비 완료
- 새 revision/autogenerate/upgrade/downgrade는 미승인

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

# Backend Ready — v304

현재 안정 readiness: `v250.backend-admin-rollback-snapshot`  
Backend splitStatus: `admin-schema-field-constraint-contract-v238`  
현재 프로젝트 작업 버전: `v304.postgres-source-baseline-stamp-final-guard`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- backend/frontend contract parity 유지
- apply route Write Guard 유지
- 기존 route path/API response body/write 의미 유지
- 실제 backend virtualenv: `backend/.venv`

## PostgreSQL / Alembic 상태

- source: 22 tables / 748 rows / schema differences=0 / no Alembic
- verified backup과 restore rehearsal 완료
- 최초 revision `v295_initial_schema` 수동 검토 통과
- isolated migration DB upgrade → downgrade base → upgrade 왕복 성공
- v301 source baseline stamp preflight 실제 통과
- v302 rehearsal stamp 실제 실행 완료
- v303 rehearsal post-check `restore-rehearsal-stamp-current-state-verified`
- v302 execution report `verified`
- v304 source final guard 준비 완료
- 원본 source stamp 실제 실행은 아직 미승인

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

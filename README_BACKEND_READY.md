# Backend Ready — v309

현재 안정 readiness: `v250.backend-admin-rollback-snapshot`  
Backend splitStatus: `admin-schema-field-constraint-contract-v238`  
현재 프로젝트 작업 버전: `v309.runtime-engine-source-binding-inspector-fix`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- backend/frontend contract parity 유지
- apply route Write Guard 유지
- 기존 route path/API response body/write 의미 유지
- 실제 backend virtualenv: `backend/.venv`

## PostgreSQL / Alembic 상태

- baseline classification `alembic-managed-baseline-complete`
- source/rehearsal application 22 tables / 748 rows 보존
- source current revision `v295_initial_schema`
- v302/v304 실행 보고서 `verified`
- v305 completion state 실제 통과
- v306 candidate operation 0개 / 새 revision 불필요 실제 통과
- v307 deployment/runtime read-only checker 준비 완료
- v308 runtime hardening 적용 완료
- v309 runtime engine source-binding AST 검사기 오탐 수정
- 새 revision/autogenerate/upgrade/downgrade/stamp는 미승인

## v307에서 확인할 항목

- runtime URL exact `rpg_game` + `postgresql+asyncpg`
- FastAPI startup DB mutation 없음
- Docker PostgreSQL running/healthy
- DB health read-only contract
- `.env` key inventory와 production hardening warnings
- manual migration runbook 경계

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

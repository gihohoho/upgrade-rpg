# Backend Ready — v290

현재 안정 readiness: `v250.backend-admin-rollback-snapshot`  
Backend splitStatus: `admin-schema-field-constraint-contract-v238`  
현재 프로젝트 작업 버전: `v290.postgres-backup-restore-preflight-gate`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- backend/frontend contract parity 유지
- apply route Write Guard 유지
- 기존 route path/API response body/write 의미 유지
- DB schema/data/env/seed/revision 변경 없음
- 실제 backend virtualenv: `backend/.venv`

## PostgreSQL 상태

- 실제 22 tables / model 22 tables
- 총 748 rows
- Alembic revision과 `alembic_version` 없음
- 기존 데이터 보존형 baseline 대상
- v289 FLOAT alias normalization 유지
- v290 backup/restore preflight는 읽기 전용이며 실제 dump/restore/DB 생성·삭제를 수행하지 않음

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

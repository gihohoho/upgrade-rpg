# Backend Ready — v294

현재 안정 readiness: `v250.backend-admin-rollback-snapshot`  
Backend splitStatus: `admin-schema-field-constraint-contract-v238`  
현재 프로젝트 작업 버전: `v294.postgres-migration-empty-database-create-tool`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- backend/frontend contract parity 유지
- apply route Write Guard 유지
- 기존 route path/API response body/write 의미 유지
- 실제 backend virtualenv: `backend/.venv`

## PostgreSQL 상태

- source 22 tables / 748 rows / schema differences=0
- verified custom backup 생성 완료
- restore rehearsal 22 tables / 748 rows / differences=0 완료
- source 작업 전후 동일 확인
- v294은 `rpg_game_migration_empty_v290`이 없을 때만 빈 DB 하나 생성
- 생성 후 0 tables / 0 rows / `alembic_version` 없음 확인
- source/rehearsal 변경, DB drop, restore, Alembic mutation은 차단

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

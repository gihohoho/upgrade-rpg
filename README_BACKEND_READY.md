# Backend Ready — v292

현재 안정 readiness: `v250.backend-admin-rollback-snapshot`  
Backend splitStatus: `admin-schema-field-constraint-contract-v238`  
현재 프로젝트 작업 버전: `v292.postgres-restore-rehearsal-database-create-tool`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- backend/frontend contract parity 유지
- apply route Write Guard 유지
- 기존 route path/API response body/write 의미 유지
- 실제 backend virtualenv: `backend/.venv`

## PostgreSQL 상태

- 실제 22 tables / model 22 tables
- 총 748 rows
- Alembic revision과 `alembic_version` 없음
- schema equivalence `structurally-equivalent`, 차이 0개
- verified custom backup 생성 완료
- v292는 target `rpg_game_restore_rehearsal_v290` 존재 여부 확인 후 없을 때만 빈 DB 생성
- target owner `rpg_user`, template `template0`, source encoding/collation 경계 고정
- restore/drop/Alembic mutation은 계속 차단

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

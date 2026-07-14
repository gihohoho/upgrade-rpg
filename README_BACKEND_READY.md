# Backend Ready — v293

현재 안정 readiness: `v250.backend-admin-rollback-snapshot`  
Backend splitStatus: `admin-schema-field-constraint-contract-v238`  
현재 프로젝트 작업 버전: `v293.postgres-restore-rehearsal-execute-tool`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- backend/frontend contract parity 유지
- apply route Write Guard 유지
- 기존 route path/API response body/write 의미 유지
- 실제 backend virtualenv: `backend/.venv`

## PostgreSQL 상태

- 실제 source 22 tables / 748 rows
- Alembic revision과 `alembic_version` 없음
- schema equivalence `structurally-equivalent`, 차이 0개
- verified custom backup 생성 완료
- target `rpg_game_restore_rehearsal_v290` 빈 DB 생성 완료
- v293은 exact backup을 해당 target에만 single transaction으로 restore
- restore 후 table별 row count와 SQLAlchemy schema equivalence 검증
- source 변경, target drop, Alembic mutation은 계속 차단

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

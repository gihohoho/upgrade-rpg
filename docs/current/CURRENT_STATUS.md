# Current Status — v292

## 기준

- 최신 작업: `v292.postgres-restore-rehearsal-database-create-tool`
- 기준 ZIP: `rpg_v292_postgres_restore_rehearsal_database_creation_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## PostgreSQL 실제 상태

```txt
PostgreSQL 16.14
rpg_game / rpg_user
model/public tables: 22 / 22
total rows: 748
alembic_version/current revision: 없음
classification: existing-schema-without-alembic-baseline
schema: structurally-equivalent / differences=0
```

## 실제 backup 완료

```txt
result: backup-created-and-verified
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
size: 126.60 KB
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source tables/rows: 22 / 748
TOC definitions/data: 22 / 22
```

## v292 완료

- target DB catalog existence check
- existing target blocks create/restore/drop
- verified backup manifest/size/SHA-256 gate
- exact target `rpg_game_restore_rehearsal_v290`
- owner `rpg_user`, template `template0`
- source-compatible encoding/collation/provider
- target empty/Alembic-absent verification
- source before/after 22 tables / 748 rows verification
- no restore/drop/.env/Docker/Alembic/API/auth/game-content change

## 다음 사용자 실행

```bash
python tools/create_postgres_restore_rehearsal_database.py --execute
```

성공 결과를 확인한 뒤에만 target DB restore 작업을 별도 승인합니다.

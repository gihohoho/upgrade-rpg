# Current Status — v299

## 기준

- 최신 작업: `v299.postgres-migration-test-downgrade-base-ready`
- 기준 ZIP: `rpg_v299_postgres_migration_test_downgrade_base_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 PostgreSQL 완료 상태

```txt
source rpg_game: 22 tables / 748 rows / differences=0 / alembic_version 없음
restore rehearsal: 22 tables / 748 rows / differences=0 / alembic_version 없음
migration test DB: 23 public tables / total rows 1
migration current revision: v295_initial_schema
migration schema: structurally-equivalent / differences=0
```

## 최초 revision

```txt
revision: v295_initial_schema
file: backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py
SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
upgrade: create_table 22 / create_index 42
downgrade: drop_index 42 / drop_table 22
manual review: passed
```

## v298 실제 upgrade 완료

```txt
result: migration-test-database-upgraded-and-verified
model tables: 22
alembic control row: 1
current revision: v295_initial_schema
differences: 0
source/rehearsal preserved: 22/748
```

## v299 다음 실행

사용자 승인 완료 범위:

```bash
python tools/downgrade_postgres_migration_test_database.py --execute
```

대상은 `rpg_game_migration_empty_v290` 하나입니다. 성공 후에는 빈 `alembic_version` placeholder만 남아야 합니다.

원본 DB upgrade/stamp, DB 삭제, 자동 재-upgrade는 아직 금지합니다.

# Current Status — v300

## 기준

- 최신 작업: `v300.postgres-migration-roundtrip-reupgrade-ready`
- 기준 ZIP: `rpg_v300_postgres_migration_roundtrip_reupgrade_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 PostgreSQL 완료 상태

```txt
source rpg_game: 22 tables / 748 rows / differences=0 / alembic_version 없음
restore rehearsal: 22 tables / 748 rows / differences=0 / alembic_version 없음
migration test DB: public tables 1 / total rows 0
migration tables: ['alembic_version']
migration current revision: 없음
migration schema: review-required / differences=22
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

## 실제 왕복 진행 상태

```txt
v298 first upgrade: passed / 23 public tables / differences=0
v299 downgrade base: passed / 1 placeholder table / differences=22
v300 second upgrade: 실행 대기
source/rehearsal preserved: 22/748
```

## v300 다음 실행

```bash
python tools/reupgrade_postgres_migration_test_database.py --inspect && python tools/reupgrade_postgres_migration_test_database.py --execute
```

대상은 `rpg_game_migration_empty_v290` 하나입니다. 두 번째 upgrade 결과가 v298 첫 upgrade와 정확히 같아야 성공합니다.

원본 DB upgrade/stamp, DB 삭제, 자동 추가 downgrade는 아직 금지합니다.

# Current Status — v298

## 기준

- 최신 작업: `v298.postgres-initial-alembic-manual-review-upgrade-ready`
- 기준 ZIP: `rpg_v298_postgres_initial_alembic_manual_review_upgrade_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 PostgreSQL 완료 상태

```txt
source rpg_game: 22 tables / 748 rows / differences=0 / alembic_version 없음
restore rehearsal: 22 tables / 748 rows / differences=0 / alembic_version 없음
migration workspace: alembic_version 1 table / 0 rows / recorded revision 없음
```

## 최초 revision 생성 완료

```txt
revision: v295_initial_schema
file: backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py
SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
upgrade: create_table 22 / create_index 42
downgrade: drop_index 42 / drop_table 22
```

## v298 수동 검토 완료

- model/revision tables: `22 / 22`
- columns: `209 / 209`
- indexes: `42 / 42`
- Foreign Key: `21`
- explicit Unique: `6`
- Check: `0`
- type/length/nullable/PK/FK/ondelete/onupdate/unique/index/server default 일치
- FLOAT 2개는 PostgreSQL `DOUBLE PRECISION` alias 정책과 일치
- downgrade는 exact reverse create order
- FK dependency order 위반 0개

결론:

```txt
approved-for-isolated-empty-migration-database-upgrade-only
```

## 다음 단계

먼저 읽기 전용:

```bash
python tools/upgrade_postgres_migration_test_database.py --inspect
```

별도 사용자 승인 후에만:

```bash
python tools/upgrade_postgres_migration_test_database.py --execute
```

아직 원본 DB upgrade/stamp, migration DB downgrade, DB 삭제는 금지합니다.

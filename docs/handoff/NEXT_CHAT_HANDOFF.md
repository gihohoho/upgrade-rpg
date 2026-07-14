# NEXT CHAT HANDOFF — Upgrade RPG v298

## 기준 ZIP

- `rpg_v298_postgres_initial_alembic_manual_review_upgrade_ready.zip`

## 현재 기준

- 최신 작업: `v298.postgres-initial-alembic-manual-review-upgrade-ready`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 사용자/진행 방식

사용자는 코딩을 거의 모르는 기호입니다. 모든 명령 바로 위에 실행 위치와 `.venv` 상태를 적습니다.

- backend: `backend`에서 `source .venv/Scripts/activate`
- Vue/npm: `frontend/vue-app`, Python `.venv` 불필요
- Git: 프로젝트 루트 한 줄 블록

## 실제 PostgreSQL 상태

```txt
source rpg_game: 22 tables / 748 rows / schema differences=0 / alembic_version 없음
restore rehearsal rpg_game_restore_rehearsal_v290: 22 tables / 748 rows / differences=0
migration test DB rpg_game_migration_empty_v290:
  public tables: [alembic_version]
  total rows: 0 (alembic_version 0 rows)
  recorded revisions: []
```

verified backup:

```txt
local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
```

민감한 `local-backups/`는 Git/ZIP/채팅에서 제외합니다.

## 최초 revision 실제 생성 결과

```txt
revision ID: v295_initial_schema
revision file: backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
upgrade create_table: 22
upgrade create_index: 42
downgrade drop_table: 22
reviewed tables/columns: 22 / 209
```

## v298 수동 검토 결과

- revision SHA와 review bundle SHA 일치
- model/revision tables `22 / 22`
- columns `209 / 209`
- indexes `42 / 42`
- FK `21`, explicit Unique `6`, Check `0`
- type/length/nullable/PK/FK/ondelete/onupdate/unique/index/server default 일치
- FLOAT 2개는 PostgreSQL `DOUBLE PRECISION` alias 정책과 일치
- downgrade는 exact reverse create order
- FK dependency order 위반 0개
- `op.execute`와 data operation 없음

수동 검토 결론:

```txt
approved-for-isolated-empty-migration-database-upgrade-only
```

원본 DB upgrade/stamp 승인은 아님.

## 다음 경계

먼저 읽기 전용 확인:

```bash
python tools/upgrade_postgres_migration_test_database.py --inspect
```

성공 기준:

```txt
result: ready-for-separate-upgrade-approval
migration tables: ['alembic_version']
recorded revisions: []
```

사용자 별도 승인 후에만 내부 `alembic upgrade head`를 target DB에 실행합니다:

```bash
python tools/upgrade_postgres_migration_test_database.py --execute
```

예상 성공 결과:

```txt
result: migration-test-database-upgraded-and-verified
target public tables: 23
target model tables: 22
target total rows including Alembic control row: 1
target current revision: ['v295_initial_schema']
target schema: structurally-equivalent / differences=0
```

아직 금지:

```txt
source rpg_game upgrade/stamp
migration DB downgrade
createdb/dropdb/pg_restore
.env/Docker volume 변경
```

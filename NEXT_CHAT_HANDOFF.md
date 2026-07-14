# NEXT CHAT HANDOFF — Upgrade RPG v299

## 기준 ZIP

- `rpg_v299_postgres_migration_test_downgrade_base_ready.zip`

## 현재 기준

- 최신 작업: `v299.postgres-migration-test-downgrade-base-ready`
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
  public tables: 23
  model tables: 22
  total rows: 1 (Alembic control row only)
  current revision: v295_initial_schema
  schema differences: 0
```

verified backup:

```txt
local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
```

민감한 `local-backups/`와 `local-review-artifacts/`는 Git/ZIP/채팅에서 제외합니다.

## 최초 revision

```txt
revision ID: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
upgrade create_table/create_index: 22 / 42
downgrade drop_table/drop_index: 22 / 42
manual review: passed
```

## 첫 upgrade 실제 성공

```txt
result: migration-test-database-upgraded-and-verified
target public tables: 23
target model tables: 22
target current revision: ['v295_initial_schema']
target schema: structurally-equivalent / differences=0
source/rehearsal preserved: 22/748
```

upgrade report:

```txt
local-review-artifacts/alembic/v295_initial_schema.upgrade-v298.json
```

## 다음 첫 작업 — 승인 완료

```bash
python tools/downgrade_postgres_migration_test_database.py --execute
```

허용 범위:

- target은 `rpg_game_migration_empty_v290`만
- exact `alembic downgrade base` 한 번
- source/rehearsal DB 작업 전후 비교
- 성공 후 빈 `alembic_version` placeholder만 허용
- 자동 retry 없음

성공 기대:

```txt
result: migration-test-database-downgraded-to-base-and-verified
target public tables after downgrade: 1
target application tables remaining: 0
target current revisions: []
expected empty-workspace schema: review-required / differences=22
source/rehearsal preserved: 22/748
```

아직 금지:

```txt
source rpg_game upgrade/stamp
migration DB 자동 재-upgrade
createdb/dropdb/pg_restore
.env/Docker volume 변경
```

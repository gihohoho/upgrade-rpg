# NEXT CHAT HANDOFF — Upgrade RPG v300

## 기준 ZIP

- `rpg_v300_postgres_migration_roundtrip_reupgrade_ready.zip`

## 현재 기준

- 최신 작업: `v300.postgres-migration-roundtrip-reupgrade-ready`
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
  public tables: 1
  tables: ['alembic_version']
  total rows: 0
  current revision: 없음
  schema differences: 22 (empty workspace expected)
```

verified backup과 실제 DB 보고서는 `local-backups/`, `local-review-artifacts/`에 있으며 Git/ZIP/채팅에서 제외합니다.

## 최초 revision

```txt
revision ID: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
upgrade create_table/create_index: 22 / 42
downgrade drop_table/drop_index: 22 / 42
manual review: passed
```

## 실제 왕복 진행

```txt
v298 first upgrade: passed / 23 public tables / differences=0
v299 downgrade base: passed / 1 placeholder table / differences=22
source/rehearsal preserved: 22/748
```

필수 로컬 보고서:

```txt
local-review-artifacts/alembic/v295_initial_schema.upgrade-v298.json
local-review-artifacts/alembic/v295_initial_schema.downgrade-v299.json
```

## 다음 첫 작업 — 사용자 승인 완료

```bash
python tools/reupgrade_postgres_migration_test_database.py --inspect && python tools/reupgrade_postgres_migration_test_database.py --execute
```

허용 범위:

- target은 `rpg_game_migration_empty_v290`만
- exact `alembic upgrade head` 한 번
- 첫/두 번째 upgrade signature exact 비교
- source/rehearsal DB 작업 전후 비교
- 자동 retry 없음

성공 기대:

```txt
result: migration-test-database-roundtrip-upgraded-and-verified
target public tables: 23
target current revision: ['v295_initial_schema']
target schema: structurally-equivalent / differences=0
first/second upgrade signatures: identical
source/rehearsal preserved: 22/748
```

아직 금지:

```txt
source rpg_game upgrade/downgrade/stamp
migration DB 자동 추가 downgrade
createdb/dropdb/pg_restore
.env/Docker volume 변경
```

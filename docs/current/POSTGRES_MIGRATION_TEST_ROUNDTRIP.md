# PostgreSQL isolated migration round-trip re-upgrade — v300

## 실제 전제 상태

```txt
v298 first upgrade: migration-test-database-upgraded-and-verified
v299 downgrade: migration-test-database-downgraded-to-base-and-verified
current target: rpg_game_migration_empty_v290
public tables: ['alembic_version']
recorded revisions: []
total rows: 0
differences: 22
```

## 허용 작업

대상 DB에 exact command 한 번만 허용합니다.

```bash
python -m alembic --config alembic.ini upgrade head
```

실제 사용자 명령은 프로젝트 루트에서 다음 도구를 사용합니다.

```bash
python tools/reupgrade_postgres_migration_test_database.py --inspect && python tools/reupgrade_postgres_migration_test_database.py --execute
```

## 필수 로컬 증거

```txt
local-review-artifacts/alembic/v295_initial_schema.upgrade-v298.json
local-review-artifacts/alembic/v295_initial_schema.downgrade-v299.json
```

둘 중 하나라도 없거나 revision/SHA/result가 다르면 실행하지 않습니다.

## 성공 조건

```txt
result: migration-test-database-roundtrip-upgraded-and-verified
public tables: 23
model tables: 22
total rows: 1
current revision: ['v295_initial_schema']
schema: structurally-equivalent / differences=0
first/second upgrade signatures: identical
source/rehearsal preserved: 22/748
```

비교 signature에는 DB/user, public table 목록, table별 row count, total rows, Alembic revision, schema classification, difference count가 포함됩니다.

## 금지

- 이 단계에서 downgrade 재실행
- source/rehearsal DB write
- stamp/revision 생성
- createdb/dropdb/pg_restore
- `.env` 또는 Docker volume 변경
- 자동 retry

성공 보고서:

```txt
local-review-artifacts/alembic/v295_initial_schema.roundtrip-upgrade-v300.json
```

이 로컬 보고서는 Git/전달 ZIP/채팅에 포함하지 않습니다.

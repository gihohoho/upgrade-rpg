# Current Status — v302

## 기준

- 최신 작업: `v302.postgres-restore-rehearsal-stamp-head-guard-ready`
- 기준 ZIP: `rpg_v302_postgres_restore_rehearsal_stamp_guard_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 PostgreSQL 완료 상태

```txt
source rpg_game: 22 tables / 748 rows / differences=0 / alembic_version 없음
restore rehearsal: 22 tables / 748 rows / differences=0 / alembic_version 없음
migration test DB: 23 public tables / 1 total row
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

## 실제 완료 증거

```txt
v298 first upgrade: passed
v299 downgrade base: passed
v300 second upgrade: passed
first/second upgrade signatures: identical
sequence: upgrade -> downgrade base -> upgrade verified
source/rehearsal preserved: 22/748
v301 source baseline preflight: passed on user PC
v301 result: ready-for-separate-restore-rehearsal-stamp-approval
```

## v302 현재 단계

restore rehearsal DB만 대상으로 하는 baseline stamp guard가 준비됐습니다.

```bash
python tools/stamp_postgres_restore_rehearsal_database.py --inspect
```

`--inspect`는 mutation 없이 다음을 확인합니다.

- exact target `rpg_game_restore_rehearsal_v290`
- exact revision `v295_initial_schema`와 SHA-256
- source/rehearsal/migration DB 현재 경계
- rehearsal 22개 application table 구조 digest
- rehearsal 전체 748개 row-content digest
- 실제 stamp 성공 시 허용되는 변화가 `alembic_version` 1 table/1 row뿐인지에 대한 postcondition

실제 `stamp head`는 아직 승인되지 않았습니다.

# Current Status — v301

## 기준

- 최신 작업: `v301.postgres-source-baseline-stamp-readonly-preflight-handoff`
- 기준 ZIP: `rpg_v301_postgres_source_baseline_stamp_preflight_handoff_ready.zip`
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

## 실제 왕복 완료

```txt
v298 first upgrade: passed
v299 downgrade base: passed
v300 second upgrade: passed
first/second upgrade signatures: identical
sequence: upgrade -> downgrade base -> upgrade verified
source/rehearsal preserved: 22/748
```

## v301 현재 단계

원본 DB baseline stamp 여부를 판단하기 위한 읽기 전용 preflight 도구가 준비됐습니다.

```bash
python tools/check_postgres_source_baseline_stamp_preflight.py --strict
```

통과 후에도 원본 DB를 바로 stamp하지 않습니다. 먼저 restore rehearsal DB stamp rehearsal guard를 준비하고 별도 승인을 받습니다.

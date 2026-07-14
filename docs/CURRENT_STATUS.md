# Current Status — v303

## 기준

- 최신 작업: `v303.postgres-restore-rehearsal-stamp-postcheck-recovery`
- 기준 ZIP: `rpg_v303_postgres_restore_rehearsal_stamp_postcheck_recovery.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 PostgreSQL/Alembic 진행 상태

```txt
source rpg_game:
  22 tables / 748 rows / differences=0
  alembic_version 없음
  source stamp 미승인

restore rehearsal rpg_game_restore_rehearsal_v290:
  v302 stamp actual execution 사용자 승인 및 실행 완료 보고
  v303 read-only post-check 실제 결과 수집 대기

migration rpg_game_migration_empty_v290:
  23 public tables / 1 total row
  current revision v295_initial_schema
  differences=0
```

## 고정 revision

```txt
revision: v295_initial_schema
file: backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py
SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
manual review: passed
```

## 실제 완료 증거

```txt
v298 first upgrade: passed
v299 downgrade base: passed
v300 second upgrade: passed
upgrade -> downgrade base -> upgrade verified
v301 source baseline preflight: passed on user PC
v302 rehearsal pre-stamp inspect: passed on user PC
v302 rehearsal stamp: user approved and executed
```

v302 stamp 전 승인 application digest:

```txt
schema: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

## v302 inspect 오류 원인

stamp 후 `alembic_version`이 정상 추가됐지만 v302 `--inspect`가 22-table 사전 상태만
허용해 `rehearsal table list differs from approved snapshot`으로 차단했습니다.
DB 재실행이나 rollback이 필요한 오류가 아니라 post-check 판정 버그입니다.

## v303 다음 첫 작업

```bash
python tools/stamp_postgres_restore_rehearsal_database.py --inspect
```

v303은 DB를 읽기만 하며 pre/post-stamp를 자동 구분합니다. 실제 stamp 재실행은 금지합니다.

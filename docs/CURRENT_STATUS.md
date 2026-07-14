# Current Status — v304

## 기준

- 최신 작업: `v304.postgres-source-baseline-stamp-final-guard`
- 기준 ZIP: `rpg_v304_postgres_source_baseline_stamp_final_guard_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 PostgreSQL/Alembic 진행 상태

```txt
source rpg_game:
  22 application tables / 748 rows / differences=0
  alembic_version 없음 / current revision 없음
  source stamp 실제 실행 미승인

restore rehearsal rpg_game_restore_rehearsal_v290:
  23 public tables / 749 total rows
  application 22 tables / 748 rows preserved
  current revision v295_initial_schema
  v303 post-check passed
  v302 execution report verified

migration rpg_game_migration_empty_v290:
  23 public tables / 1 total row
  current revision v295_initial_schema
  differences=0
```

## 고정 증거

```txt
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

## 사용자 PC 실제 완료

```txt
v298 first upgrade: passed
v299 downgrade base: passed
v300 second upgrade: passed
v301 source preflight: passed
v302 rehearsal pre-stamp inspect: passed
v302 rehearsal stamp: passed
v303 rehearsal post-check: passed
result: restore-rehearsal-stamp-current-state-verified
```

## v304 다음 첫 작업

```bash
python tools/stamp_postgres_source_database.py --inspect
```

이 명령은 source/rehearsal/migration DB와 로컬 증거를 읽기만 합니다. 정상 통과해도 원본 source stamp는 다시 별도 명시 승인 전까지 실행하지 않습니다.

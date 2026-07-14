# NEXT CHAT HANDOFF — Upgrade RPG v301

## 기준 ZIP

- `rpg_v301_postgres_source_baseline_stamp_preflight_handoff_ready.zip`

## 현재 기준

- 최신 작업: `v301.postgres-source-baseline-stamp-readonly-preflight-handoff`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 사용자/진행 방식

사용자는 코딩을 거의 모르는 기호입니다. 모든 명령 바로 위에 실행 위치와 `.venv` 상태를 적습니다.

- backend: `backend`에서 `source .venv/Scripts/activate`
- Vue/npm: `frontend/vue-app`, Python `.venv` 불필요
- Git: 프로젝트 루트 한 줄 블록
- 위험한 DB/env/migration 작업은 작은 승인 경계로 진행

## 실제 완료 상태

```txt
source rpg_game:
  22 tables / 748 rows
  schema differences=0
  alembic_version 없음

restore rehearsal rpg_game_restore_rehearsal_v290:
  22 tables / 748 rows
  schema differences=0
  alembic_version 없음

migration test rpg_game_migration_empty_v290:
  public tables 23 / model tables 22
  total rows 1
  current revision v295_initial_schema
  schema differences=0
```

verified backup:

```txt
rpg_game_20260714_130403_KST_v290.custom.dump
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
```

reviewed revision:

```txt
revision: v295_initial_schema
SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
manual review: passed
22 tables / 209 columns / 42 indexes
```

실제 사용자 PC 왕복 결과:

```txt
v298 first upgrade: passed
v299 downgrade base: passed
v300 second upgrade: passed
first/second upgrade signatures: identical
sequence: upgrade -> downgrade base -> upgrade verified
source/rehearsal preserved: 22/748
```

## v301 추가

```txt
tools/check_postgres_source_baseline_stamp_preflight.py
tools/smoke/backend/smoke_postgres_source_baseline_stamp_preflight.py
docs/current/POSTGRES_SOURCE_BASELINE_STAMP_PREFLIGHT.md
```

v301 도구는 읽기 전용입니다. 다음을 검증하지만 mutation은 하지 않습니다.

- source 22 tables / 748 rows / schema differences=0
- source에 `alembic_version` 없음
- exact backup/SHA와 restore evidence
- exact reviewed revision/SHA
- v300 round-trip evidence와 현재 migration DB head 일치
- source/rehearsal/migration DB 경계

## 다음 첫 작업

```bash
python tools/check_postgres_source_baseline_stamp_preflight.py --strict
```

성공 기대:

```txt
result: ready-for-separate-restore-rehearsal-stamp-approval
```

## 성공 후 다음 안전 경계

원본 DB를 바로 stamp하지 않습니다.
먼저 `rpg_game_restore_rehearsal_v290`에만 exact `alembic stamp head`를 적용하는 v302 guard를 준비하고 별도 승인을 받습니다.

아직 금지:

```txt
source rpg_game upgrade/downgrade/stamp
restore rehearsal stamp 실제 실행
migration DB 추가 mutation
createdb/dropdb/pg_restore
.env/Docker volume 변경
새 revision 생성
```

## 로컬 민감/생성 자료

다음은 Git/전달 ZIP/채팅에서 제외합니다.

```txt
local-backups/
local-review-artifacts/
backend/.env
backend/.venv
```

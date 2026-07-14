# NEXT CHAT HANDOFF — Upgrade RPG v302

## 전달 ZIP

- `rpg_v302_postgres_restore_rehearsal_stamp_guard_ready.zip`

## 현재 기준

- 최신 작업: `v302.postgres-restore-rehearsal-stamp-head-guard-ready`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 PostgreSQL 상태

```txt
source rpg_game: 22 tables / 748 rows / differences=0 / no alembic_version
restore rehearsal rpg_game_restore_rehearsal_v290: 22 tables / 748 rows / differences=0 / no alembic_version
migration rpg_game_migration_empty_v290: public tables 23 / total rows 1
migration current revision v295_initial_schema
migration schema differences=0
```

## 검증된 증거

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
v298 first upgrade: passed
v299 downgrade base: passed
v300 second upgrade: passed
upgrade -> downgrade base -> upgrade verified
first/second upgrade signatures: identical
source/rehearsal preserved: 22 tables / 748 rows
```

로컬 backup과 review evidence는 Git/ZIP/채팅에 포함하지 않습니다.

## v301 사용자 실제 결과

사용자 PC에서 아래 preflight가 실제 통과했습니다.

```txt
source tables/rows: 22/748
source alembic_version: False
source schema: structurally-equivalent / differences=0
reviewed revision: v295_initial_schema
migration test current revision: ['v295_initial_schema']
result: ready-for-separate-restore-rehearsal-stamp-approval
```

원본 source stamp 승인은 아닙니다.

## v302 추가

```txt
tools/stamp_postgres_restore_rehearsal_database.py
tools/smoke/backend/smoke_postgres_restore_rehearsal_stamp_guard.py
docs/current/POSTGRES_RESTORE_REHEARSAL_STAMP_GUARD.md
```

v302 guard는 다음을 고정합니다.

- exact target: `rpg_game_restore_rehearsal_v290`
- exact revision: `v295_initial_schema`
- exact SHA-256 재검증
- 허용 Alembic command: `stamp head`
- application 22 tables의 schema SHA-256
- 전체 748 application rows의 row-content SHA-256
- source/rehearsal/migration DB signature 비교
- 성공 시 허용되는 차이: `alembic_version` 1 table / 1 revision row만
- actual `--execute`에는 exact target/revision confirmation 둘 다 필요

이번 v302 준비 작업에서는 실제 PostgreSQL stamp를 실행하지 않았습니다. 전용 smoke는 fake subprocess로만 실행 경계를 검증했습니다.

## 다음 첫 작업

사용자 PC에서 읽기 전용 inspect 결과를 수집합니다.

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/stamp_postgres_restore_rehearsal_database.py --inspect
```

정상 핵심 결과:

```txt
exact target DB: rpg_game_restore_rehearsal_v290
exact revision: v295_initial_schema
source preflight: ready-for-separate-restore-rehearsal-stamp-approval
rehearsal application tables/rows: 22/748
rehearsal schema digest: <SHA-256>
rehearsal data digest: <SHA-256>
result: ready-for-separate-restore-rehearsal-stamp-execution-approval
actual stamp still requires separate user approval
```

inspect가 통과해도 actual stamp를 실행하지 않습니다. 전체 결과를 확인하고 사용자에게 별도 승인 경계를 제시한 뒤 멈춥니다.

## 다음 안전 순서

1. v302 `--inspect` 사용자 실제 결과 확인
2. exact target/revision/SHA와 pre-stamp digests 확인
3. 사용자에게 실제 rehearsal stamp mutation 범위 설명
4. 사용자 별도 명시 승인
5. 승인 후 rehearsal DB에서만 exact `stamp head`
6. application schema/data signatures 동일 확인
7. `alembic_version` 1 table/1 row와 current revision 확인
8. source/migration DB signatures 동일 확인
9. 성공 뒤에만 원본 source stamp guard 설계 여부 검토
10. 원본 source stamp는 다시 별도 승인

## 절대 실행 금지

사용자 명시 승인 전:

- `python tools/stamp_postgres_restore_rehearsal_database.py --execute ...`
- 원본 `rpg_game` stamp/upgrade/downgrade
- migration test DB 추가 upgrade/downgrade/stamp
- DB create/drop/restore
- Docker container/volume 삭제
- `.env`, seed, 인증, API route/body/write 로직 변경
- 새 Alembic revision 생성
- 게임 콘텐츠 변경

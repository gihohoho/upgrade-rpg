# NEXT CHAT HANDOFF — Upgrade RPG v304

## 기준 ZIP

- `rpg_v304_postgres_source_baseline_stamp_final_guard_ready.zip`

## 현재 버전

- 최신 작업: `v304.postgres-source-baseline-stamp-final-guard`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 DB 상태

```txt
source rpg_game:
  22 application tables / 748 rows
  schema differences=0
  alembic_version 없음 / current revision 없음
  source stamp 실제 실행 미승인

restore rehearsal rpg_game_restore_rehearsal_v290:
  public tables/rows 23/749
  application tables/rows 22/748
  current revision v295_initial_schema
  v303 post-check passed
  v302 execution report verified

migration rpg_game_migration_empty_v290:
  public tables 23
  total rows 1
  migration current revision v295_initial_schema
  differences=0
```

## 고정 증거

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

로컬 backup과 review evidence는 Git/ZIP/채팅에 포함하지 않습니다.

## 사용자 PC에서 실제 완료

```txt
v298 first upgrade: passed
v299 downgrade base: passed
v300 second upgrade: passed
upgrade -> downgrade base -> upgrade verified
first/second upgrade signatures: identical
v301 source baseline preflight: passed
v302 rehearsal pre-stamp inspect: passed
v302 rehearsal stamp: passed
v303 rehearsal post-check: passed
v303 result: restore-rehearsal-stamp-current-state-verified
v302 execution report: verified
```

## v304 추가 내용

추가 파일:

```txt
tools/stamp_postgres_source_database.py
tools/smoke/backend/smoke_postgres_source_baseline_stamp_guard.py
docs/current/POSTGRES_SOURCE_BASELINE_STAMP_FINAL_GUARD.md
```

읽기 전용 `--inspect`는 다음을 동시에 확인합니다.

- exact source target `rpg_game`
- exact revision/SHA-256
- verified backup/SHA-256
- source 22 tables / 748 rows / no Alembic
- source schema differences=0
- source application schema/data digest exact match
- rehearsal 23/749 / revision / v302 report verified
- migration DB verified v300 endpoint
- source/rehearsal application integrity exact equality

실행 경로는 향후 별도 승인 후에만 사용하며 target, revision, backup SHA, rehearsal result 네 confirmation이 모두 정확해야 합니다.

## 다음 첫 작업

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/stamp_postgres_source_database.py --inspect
```

정상 기대 핵심:

```txt
lifecycle state: pre-stamp
exact target DB: rpg_game
exact revision: v295_initial_schema
source public tables/rows: 22/748
source current revision: []
source application tables/rows: 22/748
source application schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
source application data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
rehearsal post-stamp: verified / 23/749
migration test current revision: ['v295_initial_schema']
source/rehearsal application digests identical: yes
result: ready-for-separate-source-baseline-stamp-execution-approval
```

통과해도 source `--execute`는 실행하지 않습니다. 전체 결과를 확인한 뒤 실제 source stamp는 다시 별도 명시 승인을 받습니다.

## 다음 안전 순서

1. v304 `--inspect` 실제 결과 확인
2. source/rehearsal digests, backup, revision, reports 재확인
3. source stamp 실제 실행 여부 별도 명시 승인
4. 승인 후 exact confirmation flags가 포함된 명령 1회 실행
5. 실패 시 자동 재시도 금지, `--inspect`로 post-state 확인
6. source 23/749, revision, application digest 보존 확인
7. rehearsal/migration DB 무변경 확인
8. v304 source execution report 검증
9. Alembic baseline 운영 완료 문서화

## 절대 변경/실행 금지

- 사용자 별도 승인 전 source `--execute`
- source `upgrade`/`downgrade`
- rehearsal stamp 재실행
- migration test DB 추가 변경
- 새 Alembic revision 생성
- DB 생성/삭제/복원
- Docker container/volume 삭제
- `.env`, seed, 인증
- 기존 API route path/response body
- 실제 write 로직/Write Guard
- Preview/Apply request body
- 게임 콘텐츠/밸런스 변경

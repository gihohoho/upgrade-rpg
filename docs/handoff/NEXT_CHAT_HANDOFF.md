# NEXT CHAT HANDOFF — Upgrade RPG v303

## 전달 ZIP

- `rpg_v303_postgres_restore_rehearsal_stamp_postcheck_recovery.zip`

## 현재 기준

- 최신 작업: `v303.postgres-restore-rehearsal-stamp-postcheck-recovery`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 PostgreSQL/Alembic 상태

```txt
source rpg_game:
  22 tables / 748 rows / differences=0
  alembic_version 없음
  source stamp 미승인

restore rehearsal rpg_game_restore_rehearsal_v290:
  v302 pre-stamp inspect 통과
  v302 stamp 사용자 명시 승인 및 실제 실행 완료 보고
  v303 post-stamp read-only 검증 결과 수집 대기

migration rpg_game_migration_empty_v290:
  public tables 23 / total rows 1
  migration current revision v295_initial_schema
  differences=0
```

## 고정 증거

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
v298 first upgrade: passed
v299 downgrade base: passed
v300 second upgrade: passed
first/second upgrade signatures: identical
v301 source preflight: passed
```

v302 stamp 전 사용자 PC 실제 application digest:

```txt
application tables/rows: 22/748
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

로컬 backup과 review evidence는 Git/ZIP/채팅에 포함하지 않습니다.

## 발생한 문제와 원인

v302 실제 stamp 실행 후 기존 `--inspect`가 다음 오류를 냈습니다.

```txt
SourceBaselinePreflightError: rehearsal table list differs from approved snapshot
```

원인은 DB 손상이나 stamp 실패가 아니라 v302 검사기 버그입니다. 기존 inspect가 stamp 후에도
`alembic_version`이 없는 22-table 사전 상태만 허용했습니다. 같은 stamp 명령은 절대 재실행하지 않습니다.

## v303 수정

`tools/stamp_postgres_restore_rehearsal_database.py --inspect`가 다음을 수행하도록 수정했습니다.

- pre-stamp / post-stamp 자동 분류
- post-stamp exact `23 public tables / 749 rows` 검증
- application `22 tables / 748 rows` 분리 검증
- stamp 전 승인 schema/data digest exact 비교
- exact revision/SHA-256 재검증
- source DB 22/748/no Alembic 유지 확인
- migration DB가 verified v300 endpoint와 일치하는지 확인
- v302 local execution report가 있으면 before/after/current signature 비교
- report가 없어도 current state를 검증하고 별도 recovery 상태로 분류
- inspect에서 subprocess/DB write/재시도/rollback을 전혀 실행하지 않음

## 다음 첫 작업

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

정상 기대 핵심:

```txt
lifecycle state: post-stamp
exact target DB: rpg_game_restore_rehearsal_v290
exact revision: v295_initial_schema
public tables/rows: 23/749
current revision: ['v295_initial_schema']
application tables/rows: 22/748
application schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
application data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
approved pre-stamp application digests preserved: yes
source DB current state preserved: yes
migration test DB current state preserved: yes
```

보고서가 있으면:

```txt
v302 execution report: verified
result: restore-rehearsal-stamp-current-state-verified
```

보고서가 없으면:

```txt
v302 execution report: missing
result: restore-rehearsal-stamp-current-state-verified-report-missing
```

두 경우 모두 stamp 재실행 금지입니다.

## 다음 안전 순서

1. v303 post-stamp `--inspect` 실제 결과 확인
2. `23/749`, revision, application digest 보존 확인
3. v302 execution report가 `verified`인지 `missing`인지 확인
4. `verified`이면 rehearsal stamp 단계 완료 문서화
5. `missing`이면 DB 변경 없이 local evidence 복구 도구만 설계
6. 그 뒤에만 원본 `rpg_game` source stamp용 별도 read-only guard 설계
7. 원본 source stamp 실제 실행은 다시 별도 명시 승인

## 절대 변경/실행 금지

- v302 rehearsal `--execute` 재실행
- 원본 `rpg_game` stamp/upgrade/downgrade
- migration test DB 추가 upgrade/downgrade/stamp
- 새 Alembic revision 생성
- DB 생성/삭제/복원
- Docker container/volume 삭제
- `.env`, seed, 인증
- 기존 API route path/response body
- 실제 write 로직/Write Guard
- Preview/Apply request body
- 게임 콘텐츠/밸런스 변경

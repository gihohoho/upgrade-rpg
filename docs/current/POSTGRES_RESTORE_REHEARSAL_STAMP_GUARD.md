# PostgreSQL restore rehearsal baseline stamp post-check — v303

## 현재 상황

사용자 PC에서 다음 단계가 실제로 진행됐습니다.

```txt
v301 source baseline stamp preflight: passed
v302 rehearsal --inspect: passed
v302 rehearsal stamp execution: user approved and executed
```

stamp 전 실제 승인 digest:

```txt
application tables/rows: 22 / 748
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

그 직후 기존 v302 `--inspect`는 다음 오류를 냈습니다.

```txt
SourceBaselinePreflightError: rehearsal table list differs from approved snapshot
```

이 오류는 stamp를 다시 해야 한다는 뜻이 아닙니다. v302 `--inspect`가 stamp 이후에도
`alembic_version`이 없는 22-table 사전 상태만 허용했던 검사기 버그입니다.

## v303 수정 사항

`tools/stamp_postgres_restore_rehearsal_database.py --inspect`가 rehearsal DB의
현재 상태를 먼저 읽고 다음 두 상태를 구분합니다.

```txt
pre-stamp:
  22 public tables / 748 rows / no alembic_version

post-stamp:
  23 public tables / 749 rows
  application tables/rows: 22 / 748
  alembic_version: 1 table / 1 row
  current revision: v295_initial_schema
```

post-stamp에서는 다음을 모두 읽기 전용으로 검증합니다.

- exact target: `rpg_game_restore_rehearsal_v290`
- exact revision: `v295_initial_schema`
- revision SHA-256
- 22개 application table / 748개 application row 유지
- stamp 전 승인 schema/data digest 유지
- 원본 `rpg_game`이 22/748, no Alembic 상태로 유지
- migration test DB가 검증된 v300 endpoint와 일치
- 로컬 v302 실행 보고서가 있으면 실행 전후 signature와 현재 상태 일치

## 읽기 전용 post-check

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

이 명령은 다음을 실행하지 않습니다.

```txt
stamp 재실행
rollback
upgrade/downgrade
DB create/drop/restore
source DB mutation
application row write
.env/Docker 변경
```

## 정상 기대 결과

v302 실행 보고서가 정상 생성돼 있으면:

```txt
lifecycle state: post-stamp
public tables/rows: 23/749
current revision: ['v295_initial_schema']
application tables/rows: 22/748
approved pre-stamp application digests preserved: yes
source DB current state preserved: yes
migration test DB current state preserved: yes
v302 execution report: verified
result: restore-rehearsal-stamp-current-state-verified
```

stamp는 성공했지만 실행 보고서 저장 전에 후속 검사가 끊긴 경우에도 current DB 상태가
정상이라면 다음처럼 분류합니다.

```txt
v302 execution report: missing
result: restore-rehearsal-stamp-current-state-verified-report-missing
```

이 경우에도 stamp를 다시 실행하지 않습니다. 별도의 로컬 evidence 복구 단계만 검토합니다.

## 사용자 PC 실제 v303 결과

```txt
lifecycle state: post-stamp
public tables/rows: 23/749
current revision: ['v295_initial_schema']
application tables/rows: 22/748
approved pre-stamp application digests preserved: yes
source DB current state preserved: yes
migration test DB current state preserved: yes
v302 execution report: verified
result: restore-rehearsal-stamp-current-state-verified
```

이 결과로 restore rehearsal stamp 단계는 완료됐으며 v304 source final guard 준비 단계로 이동했습니다.

## 계속 금지

- v302 `--execute` 재실행
- 원본 `rpg_game` stamp/upgrade/downgrade
- migration test DB 추가 변경
- 새 Alembic revision
- DB create/drop/restore
- Docker volume 삭제
- `.env`, seed, 인증, API route/body, Write Guard 변경

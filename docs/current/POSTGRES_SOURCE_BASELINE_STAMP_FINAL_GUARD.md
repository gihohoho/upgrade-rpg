# PostgreSQL source baseline stamp final guard and post-check — v304

## 목적과 완료 상태

v304는 원본 PostgreSQL DB `rpg_game`의 baseline stamp를 exact target/revision/backup/rehearsal 경계로 제한하고, 실행 전후 application schema/data를 비교하기 위해 준비됐습니다.

사용자 별도 승인 후 source baseline stamp가 정확히 한 번 실행됐고, 읽기 전용 post-check와 로컬 execution report 검증까지 완료됐습니다.

## 정확히 고정된 경계

```txt
target DB: rpg_game
owner/user: rpg_user
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
required rehearsal result: restore-rehearsal-stamp-current-state-verified
```

승인 application digest:

```txt
schema: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

## 실행 전에 검증했던 것

- `.env`의 source DB가 정확히 `rpg_game`인지
- source가 22 application tables / 748 rows / no Alembic인지
- source schema differences가 0인지
- verified backup, revision, manual review가 유지되는지
- rehearsal이 23/749, `v295_initial_schema`, v302 report verified인지
- migration DB가 v300 왕복 endpoint인지
- source/rehearsal application integrity가 정확히 같은지

사전 성공 결과:

```txt
result: ready-for-separate-source-baseline-stamp-execution-approval
```

## 실제 실행에 사용된 승인 경계

```txt
--confirm-target rpg_game
--confirm-revision v295_initial_schema
--confirm-backup-sha256 b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
--confirm-rehearsal-result restore-rehearsal-stamp-current-state-verified
```

허용된 변화는 다음뿐이었습니다.

```txt
source application tables/rows: 22/748 그대로
source application schema/data digest: 그대로
new control table: alembic_version 1개
new control row: v295_initial_schema 1개
public tables/rows after: 23/749
restore rehearsal DB: 무변경
migration DB: 무변경
```

## 사용자 PC 실제 post-check 결과

```txt
lifecycle state: post-stamp
source public tables/rows: 23/749
source application tables/rows: 22/748
source current revision: ['v295_initial_schema']
source/rehearsal application digests identical: yes
v304 execution report: verified
result: source-baseline-stamp-current-state-verified
```

기존 application 22개 table / 748 rows와 schema/data digest는 보존됐습니다.

## 현재 사용 방법

읽기 전용 post-check는 여전히 사용할 수 있습니다.

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/stamp_postgres_source_database.py --inspect
```

하지만 source stamp는 완료됐으므로 `--execute`를 다시 실행하지 않습니다.

현재 baseline 전체 완료 상태는 v305 도구로 확인합니다.

```bash
python tools/check_postgres_baseline_completion_state.py --strict
```

## 계속 금지

- source/rehearsal stamp 재실행
- 새 revision/autogenerate
- source/rehearsal/migration upgrade/downgrade
- DB create/drop/restore
- `.env`, Docker volume, seed, 인증, API/write 변경
- 게임 콘텐츠/밸런스 변경

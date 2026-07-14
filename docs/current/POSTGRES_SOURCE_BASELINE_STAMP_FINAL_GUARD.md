# PostgreSQL source baseline stamp final guard — v304

## 목적

원본 PostgreSQL DB `rpg_game`에 Alembic baseline을 기록하기 전에 마지막 읽기 전용 안전 검사를 수행합니다.

이번 v304 준비 단계는 원본 DB를 변경하지 않습니다. 실제 source `stamp head`는 기호님의 별도 명시 승인 전까지 실행하지 않습니다.

## 정확히 고정된 경계

```txt
target DB: rpg_game
owner/user: rpg_user
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
required rehearsal result: restore-rehearsal-stamp-current-state-verified
```

## 읽기 전용 inspect가 확인하는 것

- `.env`의 실제 source DB 이름이 정확히 `rpg_game`인지
- source가 아직 22 application tables / 748 rows / no Alembic인지
- source schema가 SQLAlchemy model과 `differences=0`인지
- source application schema/data digest가 v302 승인값과 같은지
- 검증된 backup 파일, manifest, source snapshot, v293 restore report가 모두 유지되는지
- revision 파일과 SHA-256, 자동/수동 검토 결과가 유지되는지
- restore rehearsal DB가 23 public tables / 749 rows / revision `v295_initial_schema`인지
- v302 rehearsal 실행 보고서가 `verified`인지
- migration DB가 v300 왕복 검증 endpoint와 동일한지
- source와 rehearsal의 22개 application table 전체 구조/행 digest가 같은지

승인 application digest:

```txt
schema: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

## inspect 명령

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

## 향후 실제 실행 경계

v304에는 향후 별도 승인 후 사용할 실행 경로가 있지만, 다음 네 확인값이 모두 정확히 일치해야만 열립니다.

```txt
--confirm-target rpg_game
--confirm-revision v295_initial_schema
--confirm-backup-sha256 b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
--confirm-rehearsal-result restore-rehearsal-stamp-current-state-verified
```

실제 실행이 승인되더라도 허용되는 변화는 아래뿐입니다.

```txt
source application tables/rows: 22/748 그대로
source application schema/data digest: 그대로
new control table: alembic_version 1개
new control row: v295_initial_schema 1개
public tables/rows after: 23/749
restore rehearsal DB: 무변경
migration DB: 무변경
```

## 실패 대응

실제 source stamp 단계에서 `blocked-or-failed`가 발생하면 같은 실행 명령을 자동 재시도하지 않습니다. stamp 자체는 성공했지만 post-check나 로컬 보고서 저장에서 실패했을 수 있기 때문입니다.

그 경우 `--inspect`만 다시 실행해 pre/post 상태를 읽기 전용으로 분류합니다.

## 이번 v304에서 실행하지 않은 것

- 원본 `rpg_game` stamp/upgrade/downgrade
- rehearsal/migration DB mutation
- DB create/drop/restore
- 새 revision 생성
- `.env`, Docker volume, seed, 인증, API/write 로직 변경
- 게임 콘텐츠/밸런스 변경

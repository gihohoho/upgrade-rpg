# PostgreSQL restore rehearsal baseline stamp guard — v302

## 목적

원본 `rpg_game`을 건드리기 전에, 원본과 동일하게 복원된
`rpg_game_restore_rehearsal_v290`에서만 Alembic baseline stamp가 예상대로
동작하는지 검증하기 위한 안전 가드입니다.

v301 읽기 전용 preflight는 사용자 PC에서 실제 통과했습니다.

```txt
result: ready-for-separate-restore-rehearsal-stamp-approval
source: 22 tables / 748 rows / no alembic_version
differences: 0
migration current revision: v295_initial_schema
```

## 추가 파일

```txt
tools/stamp_postgres_restore_rehearsal_database.py
tools/smoke/backend/smoke_postgres_restore_rehearsal_stamp_guard.py
```

## 정확히 고정된 경계

```txt
target DB: rpg_game_restore_rehearsal_v290
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
allowed Alembic command: alembic stamp head
```

다음 DB는 대상이 될 수 없습니다.

```txt
rpg_game
rpg_game_migration_empty_v290
```

## 읽기 전용 inspect

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

`--inspect`는 다음만 읽습니다.

- v301 source preflight 조건
- verified backup/restore evidence
- exact revision 파일과 SHA-256
- source/rehearsal/migration 현재 상태
- rehearsal 22개 application table의 구조
- rehearsal 748개 전체 row 내용
- source와 migration DB의 구조/row 내용

stamp, upgrade, downgrade, DB 생성·삭제·복원, `.env` 변경, row write는 실행하지 않습니다.

## 강화된 signature 검증

v302는 table count만 비교하지 않습니다.

각 public table에 대해 다음을 읽기 전용으로 수집합니다.

- column/type/nullability/PK/FK/unique/index/check 구조 SHA-256
- 전체 row를 canonical JSON으로 변환한 row-content SHA-256
- table별 row count
- 전체 schema/data combined SHA-256

실제 stamp 전후에는 22개 application table만 추려 다음 값이 완전히 같은지 확인합니다.

```txt
application table list
application total rows: 748
schemaDigest
dataDigest
combinedDigest
```

## 실제 stamp 성공 조건

별도 승인 후 실행되더라도 성공으로 인정되는 유일한 변화는 다음입니다.

```txt
before: 22 public tables / 748 rows / no alembic_version
after:  23 public tables / 749 rows
new table: alembic_version
new rows: 1
current revision: ['v295_initial_schema']
application schema/data signatures: identical
source DB signatures: identical
migration DB signatures: identical
```

## 실행 이중 확인

실제 mutation 경로는 `--execute`만으로 실행되지 않습니다.
정확한 target과 revision 확인 인자가 모두 필요합니다.

```txt
--confirm-target rpg_game_restore_rehearsal_v290
--confirm-revision v295_initial_schema
```

하지만 **현재 단계에서는 실제 실행 명령을 사용하지 않습니다.**
기호님이 `--inspect` 전체 결과를 공유하고 별도로 승인한 뒤에만 실행 여부를 검토합니다.

## 실행 후 로컬 증거

실제 stamp가 성공하면 아래 보고서를 로컬에만 저장하도록 준비했습니다.

```txt
local-review-artifacts/alembic/v295_initial_schema.restore-rehearsal-stamp-v302.json
```

이 경로는 Git과 전달 ZIP에서 제외됩니다.

## 계속 금지

- 원본 `rpg_game`의 stamp/upgrade/downgrade
- 승인 없는 rehearsal stamp 실행
- migration test DB 추가 upgrade/downgrade/stamp
- DB create/drop/restore
- Docker container/volume 삭제
- `.env`, seed, 인증, API route/body, 실제 write 변경
- 새 Alembic revision 생성

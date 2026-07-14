# PostgreSQL restore rehearsal — v293

## 목적

v293은 사용자 PC에서 생성·검증된 exact custom dump를 원본 `rpg_game`이 아니라 이미 생성된 빈 DB `rpg_game_restore_rehearsal_v290`에만 복원하는 단계입니다.

승인된 backup:

```txt
local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source tables/rows: 22 / 748
```

## 실행 전 필수 gate

`tools/restore_postgres_rehearsal_database.py`는 다음을 모두 다시 확인합니다.

- schema/preflight가 `ready-for-user-approval`
- source DB/user가 `rpg_game` / `rpg_user`
- source table 목록과 table별 row count가 backup snapshot과 동일
- backup filename, size, manifest, source snapshot sidecar, SHA-256 동일
- source와 target DB의 owner/encoding/collation/locale metadata 동일
- target DB가 정확히 `rpg_game_restore_rehearsal_v290`
- target public table 0개, row 0개, `alembic_version` 없음
- 기존 restore 성공 보고서가 없음

하나라도 다르면 `pg_restore`를 실행하지 않습니다.

## restore 명령 경계

내부 명령은 target DB에만 고정됩니다.

```txt
docker exec -i upgrade_rpg_postgres pg_restore
--dbname=rpg_game_restore_rehearsal_v290
--username=rpg_user
--no-password
--exit-on-error
--single-transaction
--no-owner
--no-privileges
```

사용하지 않는 옵션/명령:

```txt
--create
--clean
createdb
dropdb
alembic revision/upgrade/downgrade/stamp
```

`--single-transaction`을 사용하므로 restore 중 오류가 발생하면 부분 schema/data가 commit되지 않도록 합니다. 오류 후 target이 다시 빈 상태인지 읽기 전용으로 확인하며, 자동 재시도나 자동 삭제는 하지 않습니다.

## restore 후 검증

restore 성공 뒤 다음을 모두 확인합니다.

- target public tables: 22
- target total rows: 748
- target table 목록이 backup source snapshot과 동일
- target table별 row count가 backup source snapshot과 동일
- SQLAlchemy model과 target schema 구조 차이 0개
- target `alembic_version` 없음
- source tables/rows/table별 counts가 작업 전후 동일
- source/target catalog metadata가 작업 전후 동일

검증에 실패해도 target DB를 자동 삭제하거나 정리하지 않습니다. 결과를 보존하고 다음 행동을 별도 승인받습니다.

## 실행 명령

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/restore_postgres_rehearsal_database.py --execute
```

성공 기대값:

```txt
result: restore-rehearsal-completed-and-verified
target public tables: 22
target total rows: 748
target schema: structurally-equivalent / differences=0
target alembic_version: absent
source tables before/after: 22 / 22
source rows before/after: 748 / 748
```

성공 시 local report가 생성됩니다.

```txt
local-backups/postgres/<dump filename>.restore-rehearsal-v293.json
```

backup과 report는 민감한 로컬 산출물이므로 Git, ZIP, 채팅에 포함하지 않습니다.

## 다음 승인 경계

restore 결과 확인 후 다음 중 하나를 별도 결정합니다.

1. 리허설 DB를 잠시 보존하고 empty migration test DB 준비로 이동
2. 리허설 DB 삭제 승인 후 `dropdb` 한 단계 수행

Alembic revision 생성·upgrade·downgrade·stamp는 계속 별도 승인 전 금지입니다.

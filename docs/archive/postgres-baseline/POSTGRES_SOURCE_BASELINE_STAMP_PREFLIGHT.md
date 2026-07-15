# PostgreSQL source baseline stamp preflight — v301

## 목적

기존 데이터가 있는 원본 `rpg_game`에 Alembic baseline을 기록하기 전에, 지금까지의 backup/restore/revision/왕복 migration 증거와 현재 DB 상태를 다시 읽기 전용으로 확인합니다.

이 단계에서는 `stamp head`를 실행하지 않습니다.

## 현재 실제 전제

```txt
source rpg_game: 22 tables / 748 rows / differences=0 / alembic_version 없음
restore rehearsal: 22 tables / 748 rows / differences=0 / alembic_version 없음
migration test: 23 public tables / current v295_initial_schema / differences=0
round trip: upgrade -> downgrade base -> upgrade / signatures identical
```

## 실행

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_source_baseline_stamp_preflight.py --strict
```

## 읽기 전용 확인 항목

- exact verified backup 파일명과 SHA-256
- source snapshot 22 tables / 748 rows
- restore rehearsal 22 tables / 748 rows / differences=0
- reviewed revision `v295_initial_schema`와 exact SHA-256
- manual/automated revision review 통과
- v300 round-trip 보고서 성공 및 first/second signature 동일
- 현재 migration DB가 revision head와 differences=0 상태인지
- 현재 source가 differences=0이고 `alembic_version`이 없는지

## 성공 결과

```txt
result: ready-for-separate-restore-rehearsal-stamp-approval
```

이 결과는 원본 stamp 승인이 아닙니다. 다음 mutation은 source 복사본인 `rpg_game_restore_rehearsal_v290`에서만 별도 승인 후 stamp rehearsal로 진행합니다.


## 사용자 PC 실제 결과

2026-07-14 사용자 PC에서 `--strict`가 실제 통과했습니다.

```txt
source tables/rows: 22/748
source alembic_version: False
source schema: structurally-equivalent / differences=0
reviewed revision: v295_initial_schema
migration test current revision: ['v295_initial_schema']
result: ready-for-separate-restore-rehearsal-stamp-approval
```

이 결과를 근거로 v302 restore rehearsal stamp guard 준비 단계로 이동했습니다. 원본 source stamp는 승인되지 않았습니다.

## 다음 안전 단계

1. restore rehearsal DB가 현재 22 tables / 748 rows / no Alembic인지 재확인
2. exact target URL을 restore rehearsal DB로 고정
3. exact command를 `alembic stamp head` 하나로 제한
4. 전후 schema와 application row counts가 동일한지 확인
5. `alembic_version` table 1개와 revision row 1개만 추가됐는지 확인
6. source와 migration DB 무변경 확인
7. rehearsal stamp 통과 후에도 source stamp는 다시 별도 승인

## 금지

```txt
source rpg_game stamp/upgrade/downgrade
restore rehearsal stamp 사용자 승인 전 실행
새 revision 생성
DB create/drop/restore
.env/Docker 변경
```

# PostgreSQL / Alembic 최초 baseline 전략 — v301

## 실제 분류

기호 컴퓨터의 실제 PostgreSQL 결과는 다음과 같습니다.

```txt
classification: existing-schema-without-alembic-baseline
model tables: 22
public tables: 22
total rows: 748
alembic_version: 없음
current revision: 없음
DB health: 정상
```

따라서 전략은 **기존 `create_all()` schema와 데이터를 보존하는 baseline 방식**으로 확정합니다.

## 지금 바로 stamp하면 안 되는 이유

`stamp head`는 실제 schema를 생성하거나 수정하지 않고 revision 이력만 기록합니다.

현재 테이블 개수만 22개로 일치한다는 사실만으로는 아래 구조가 완전히 같은지 알 수 없습니다.

- 컬럼 이름과 누락 여부
- PostgreSQL type, 길이, precision/scale
- nullable
- primary key
- foreign key 및 delete/update 규칙
- unique constraint
- index
- check constraint

구조가 다른 상태에서 stamp하면 불일치를 숨길 수 있습니다.

## 승인 전 안전 순서

1. 현재 DB와 SQLAlchemy metadata 상세 schema 동등성 점검
2. DB backup 파일 생성
3. backup 복원 리허설
4. 최초 revision 파일 생성
5. revision 파일 전체 수동 검토
6. 별도 빈 임시 PostgreSQL DB에서 `upgrade head`
7. 빈 DB 결과와 SQLAlchemy metadata 동등성 점검
8. downgrade/upgrade 왕복 검증
9. 기존 DB와 최초 revision 결과가 완전히 같다는 증거 확보
10. 사용자 명시 승인 후 기존 DB에만 baseline stamp 검토

## 현재 데이터 보존 기준

현재 확인된 row 748개는 삭제 대상이 아닙니다.

특히 다음 데이터는 사용자 진행 상태와 운영 검증 이력을 포함할 가능성이 있어 반드시 보존합니다.

```txt
users: 1
user_profiles: 1
characters: 1
user_save_snapshots: 2
admin_change_logs: 13
```

## 다음 읽기 전용 점검

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
```

결과가 `structurally-equivalent`이고 차이가 0개일 때도 바로 stamp하지 않습니다. backup/restore와 별도 빈 DB migration 검증이 먼저입니다.

결과가 `review-required`이면 차이 항목별 보존/수정 계획부터 작성합니다.

## 계속 실행 금지

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
```

## v288~v289 schema 비교 결론

v288 실제 차이 2개는 `FLOAT`와 `DOUBLE PRECISION`의 PostgreSQL alias 표현 차이였습니다.
v289 checker에서 alias를 정규화했으며 실제 DB와 model 자체는 변경하지 않았습니다.

v289 checker 재실행에서 차이 0개가 확인되면 다음 단계는 backup/restore 리허설 경계 확정입니다.
그래도 바로 revision 생성이나 `stamp head`를 실행하지 않습니다.

## v290 backup/restore preflight 경계

- `tools/check_postgres_backup_restore_preflight.py`가 v289 schema equivalence 차이 0개를 선행 gate로 사용합니다.
- backup은 `local-backups/postgres/`의 custom-format dump로 계획하며 Git/전달 ZIP에서 제외합니다.
- 원본 `rpg_game`에는 restore하지 않습니다.
- restore rehearsal DB와 empty migration test DB는 서로 분리합니다.
- 실제 backup/restore/DB 생성·삭제/Alembic mutation은 사용자 승인 전 실행하지 않습니다.


## v293 restore rehearsal 결과

verified custom backup이 isolated target에 복원되었고 22 tables / 748 rows / schema differences=0, source before/after 동일이 확인되었습니다.

## v294 empty migration DB 단계

`rpg_game_migration_empty_v290`을 `template0` 기반 빈 DB로 생성하되 source와 restore rehearsal DB는 보존합니다. 생성 후 0 tables / 0 rows / `alembic_version` 없음이 확인되어야 최초 revision 생성 계획으로 넘어갑니다. 기존 `rpg_game` stamp와 Alembic revision/upgrade/downgrade는 아직 금지입니다.
## v295 최초 revision 생성·자동 검토 경계

- user PC에서 `rpg_game_migration_empty_v290`이 0 tables / 0 rows / `alembic_version` 없음으로 확인되었습니다.
- `tools/create_postgres_initial_alembic_revision.py`만 revision generation entry point로 사용합니다.
- child process `DATABASE_URL`만 empty migration DB로 override하며 `.env`는 수정하지 않습니다.
- revision ID는 `v295_initial_schema`로 고정합니다.
- 생성 후 22 tables / 209 columns / nullable / PK / FK / unique / index를 자동 검토합니다.
- source/rehearsal/migration DB가 전후 동일해야 성공합니다.
- 생성된 schema-only review bundle을 수동 검토한 뒤에만 empty DB `upgrade head` 승인을 검토합니다.
- source DB stamp, upgrade/downgrade, drop은 계속 금지입니다.



## v300 왕복 검증 완료

사용자 PC에서 isolated migration DB에 대해 다음 순서가 실제 성공했습니다.

```txt
upgrade head -> downgrade base -> upgrade head
first/second upgrade signatures: identical
current revision: v295_initial_schema
schema differences: 0
source/rehearsal preserved: 22 tables / 748 rows
```

## v301 source baseline stamp preflight

`tools/check_postgres_source_baseline_stamp_preflight.py`는 source DB를 변경하지 않고 다음을 한 번에 재검사합니다.

- source 22 tables / 748 rows / differences=0 / no Alembic
- exact verified backup/SHA와 restore evidence
- exact reviewed revision/SHA
- v300 round-trip 보고서와 현재 migration DB head 일치

성공 결과는 source stamp 승인이 아닙니다. 다음 mutation은 source 복사본인 `rpg_game_restore_rehearsal_v290`에서 별도 승인 후 `stamp head` rehearsal로 진행합니다.

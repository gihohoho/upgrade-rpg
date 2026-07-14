# PostgreSQL 빈 migration test DB 생성 — v294

## 목적

최초 Alembic revision을 원본 `rpg_game`이나 복원 리허설 DB에서 실행하지 않고, 완전히 분리된 빈 DB에서 검증하기 위한 준비 단계입니다.

```txt
source DB: rpg_game
verified restore DB: rpg_game_restore_rehearsal_v290
empty migration test DB: rpg_game_migration_empty_v290
```

## 선행 완료 상태

- source: 22 tables / 748 rows / schema differences=0
- verified backup SHA-256 확인 완료
- restore rehearsal: 22 tables / 748 rows / schema differences=0
- source before/after 동일
- restore report 생성 완료

## v294 도구

```txt
tools/create_postgres_migration_test_database.py
```

실행 전 gate:

1. schema/preflight가 계속 정상인지 확인
2. exact backup 파일명과 SHA-256 재확인
3. v293 restore report 성공 결과 재확인
4. source live table 목록과 table별 row counts 재확인
5. restore rehearsal live 22 tables / 748 rows / differences=0 재확인
6. `rpg_game_migration_empty_v290`가 존재하지 않는지 확인

생성 방식:

```txt
createdb
owner: rpg_user
template: template0
encoding/collation/locale: source와 동일
```

생성 후 검증:

- migration test DB public tables 0개
- total rows 0개
- `alembic_version` 없음
- source 22 tables / 748 rows 유지
- restore rehearsal 22 tables / 748 rows 유지

## 실행 명령

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_migration_test_database.py --execute
```

## 성공 기대값

```txt
result: migration-test-database-created-empty-and-verified
migration test DB: rpg_game_migration_empty_v290
target public tables: 0
target total rows: 0
target alembic_version: absent
source tables/rows before/after: 22/748 -> 22/748
rehearsal tables/rows before/after: 22/748 -> 22/748
```

## 여전히 금지

- `python -m alembic revision --autogenerate`
- `python -m alembic upgrade head`
- `python -m alembic downgrade`
- `python -m alembic stamp head`
- `dropdb`
- source/rehearsal DB write
- `.env` 변경
- Docker container/volume 변경

빈 DB 생성 성공 결과를 확인한 뒤 최초 revision 생성은 별도 승인과 수동 검토 경계로 진행합니다.

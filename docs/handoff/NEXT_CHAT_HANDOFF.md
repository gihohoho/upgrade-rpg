# NEXT CHAT HANDOFF — Upgrade RPG v294

## 기준 ZIP

- `rpg_v294_postgres_migration_test_database_creation_ready.zip`

## 현재 기준

- 최신 작업: `v294.postgres-migration-empty-database-create-tool`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 사용자/진행 방식

사용자는 코딩을 거의 모르는 기호입니다. 항상 한국어로 쉽고 자세하게 설명합니다. 모든 터미널 명령 바로 위에 실행 위치와 Python `.venv` 상태를 적습니다.

- backend 명령: `backend`에서 `source .venv/Scripts/activate`
- Vue/npm 명령: `frontend/vue-app`, Python `.venv` 불필요
- Git 명령: 프로젝트 루트에서 한 줄

## 실제 PostgreSQL source 상태

```txt
PostgreSQL: 16.14
DB/user: rpg_game / rpg_user
SQLAlchemy model tables: 22
public tables: 22
total rows: 748
alembic_version/current revision: 없음
classification: existing-schema-without-alembic-baseline
schema equivalence: structurally-equivalent / differences=0
```

## 사용자 PC 실제 backup 결과

```txt
result: backup-created-and-verified
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
size: 126.60 KB
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source tables/rows: 22 / 748
TOC table definitions/data entries: 22 / 22
```

backup과 `local-backups/`는 민감 데이터이므로 Git/ZIP/채팅에 포함하지 않습니다.

## 사용자 PC 실제 restore rehearsal 결과

```txt
result: restore-rehearsal-completed-and-verified
target DB: rpg_game_restore_rehearsal_v290
target public tables: 22
target total rows: 748
target schema: structurally-equivalent / differences=0
target alembic_version: absent
source tables before/after: 22 / 22
source rows before/after: 748 / 748
```

restore report:

```txt
local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump.restore-rehearsal-v293.json
```

## v294 추가

```txt
tools/create_postgres_migration_test_database.py
tools/smoke/backend/smoke_postgres_migration_test_database_creation.py
docs/current/POSTGRES_MIGRATION_TEST_DB_CREATION.md
```

도구 안전 경계:

- exact backup filename/SHA-256와 v293 restore report 재검증
- source live table 목록과 table별 row counts가 backup snapshot과 같은지 확인
- rehearsal live 22 tables / 748 rows / schema differences=0 확인
- source/rehearsal owner, encoding, collation, locale metadata 동일 확인
- target 고정: `rpg_game_migration_empty_v290`
- target이 이미 존재하면 즉시 중단
- 없을 때만 `createdb`, owner `rpg_user`, `template0`
- 생성 후 target 0 tables / 0 rows / `alembic_version` 없음 확인
- source/rehearsal 작업 전후 동일 확인
- pg_restore/dropdb/.env/Docker/Alembic 작업 없음

## 사용자 PC에서 다음 실행

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

성공 기대값:

```txt
result: migration-test-database-created-empty-and-verified
migration test DB: rpg_game_migration_empty_v290
target public tables: 0
target total rows: 0
target alembic_version: absent
source tables/rows before/after: 22/748 -> 22/748
rehearsal tables/rows before/after: 22/748 -> 22/748
```

## 다음 승인 경계

v294 실제 결과를 먼저 확인한 뒤 최초 Alembic revision 생성 계획을 작성합니다.

아직 금지:

- `python -m alembic revision --autogenerate`
- `python -m alembic upgrade head`
- `python -m alembic downgrade`
- `python -m alembic stamp head`
- source/rehearsal/migration DB `dropdb`

## 계속 보류

- 게임 콘텐츠 개발
- Vue Preview/Apply/write/인증 연결
- 원본 DB schema/data 변경
- seed/.env/API route/body/write guard 변경
- Docker container/volume 삭제

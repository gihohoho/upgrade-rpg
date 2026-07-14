# NEXT CHAT HANDOFF — Upgrade RPG v293

## 기준 ZIP

- `rpg_v293_postgres_restore_rehearsal_ready.zip`

## 현재 기준

- 최신 작업: `v293.postgres-restore-rehearsal-execute-tool`
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

## 사용자 PC 실제 빈 target 결과

```txt
result: restore-rehearsal-database-created-empty-and-verified
target DB: rpg_game_restore_rehearsal_v290
owner/user: rpg_user
template: template0
public tables: 0
alembic_version: absent
source tables before/after: 22 / 22
source rows before/after: 748 / 748
```

## v293 추가

```txt
tools/restore_postgres_rehearsal_database.py
tools/smoke/backend/smoke_postgres_restore_rehearsal.py
docs/current/POSTGRES_RESTORE_REHEARSAL.md
```

도구 안전 경계:

- exact backup filename/manifest/source snapshot/SHA-256 재검증
- source table 목록과 table별 row counts가 backup snapshot과 같은지 확인
- source/target owner, encoding, collation, locale metadata 동일 확인
- target이 여전히 정확히 0 tables/0 rows일 때만 실행
- target 고정: `rpg_game_restore_rehearsal_v290`
- `pg_restore --single-transaction --exit-on-error --no-owner --no-privileges`
- `--create`, `--clean`, createdb, dropdb 없음
- restore 후 target 22 tables / 748 rows / table별 counts 동일 확인
- target SQLAlchemy schema `structurally-equivalent`, differences=0 확인
- source 작업 전후 table 목록/counts 동일 확인
- 실패 시 자동 retry/clean/drop 없음
- target drop, `.env`, Docker, Alembic 작업 없음

## 사용자 PC에서 다음 실행

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

## 다음 승인 경계

v293 실제 결과를 먼저 확인한 뒤 다음을 결정합니다.

- restore rehearsal DB를 보존할지 삭제할지
- 별도 `rpg_game_migration_empty_v290` 빈 DB 생성으로 이동할지

`dropdb`, Alembic revision/upgrade/downgrade/stamp는 아직 금지입니다.

## 계속 보류

- 게임 콘텐츠 개발
- Vue Preview/Apply/write/인증 연결
- 원본 DB schema/data 변경
- seed/.env/API route/body/write guard 변경
- Docker container/volume 삭제

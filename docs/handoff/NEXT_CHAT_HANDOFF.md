# NEXT CHAT HANDOFF — Upgrade RPG v292

## 기준 ZIP

- `rpg_v292_postgres_restore_rehearsal_database_creation_ready.zip`

## 현재 기준

- 최신 작업: `v292.postgres-restore-rehearsal-database-create-tool`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 사용자/진행 방식

사용자는 코딩을 거의 모르는 기호입니다. 항상 한국어로 쉽고 자세하게 설명합니다.
모든 터미널 명령 바로 위에 실행 위치와 Python `.venv` 상태를 적습니다.

- backend 명령: `backend`에서 `source .venv/Scripts/activate`
- Vue/npm 명령: `frontend/vue-app`, Python `.venv` 불필요
- Git 명령: 프로젝트 루트에서 한 줄

## 실제 PostgreSQL 상태

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

보존 대상 예시:

```txt
users: 1
user_profiles: 1
characters: 1
user_save_snapshots: 2
admin_change_logs: 13
```

## 사용자 PC 실제 backup 결과

```txt
result: backup-created-and-verified
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
size: 126.60 KB
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source tables: 22
source rows: 748
TOC table definitions/data entries: 22 / 22
```

backup과 `local-backups/`는 민감 데이터이므로 Git/ZIP/채팅에 포함하지 않습니다.

## v292 추가

```txt
tools/create_postgres_restore_rehearsal_database.py
tools/smoke/backend/smoke_postgres_restore_rehearsal_database_creation.py
docs/current/POSTGRES_RESTORE_REHEARSAL_DB_CREATION.md
```

도구 안전 경계:

- 실행 직전 schema/preflight와 source 22 tables / 748 rows 재확인
- verified backup manifest, size, SHA-256 sidecar 재검증
- source `rpg_game`, target `rpg_game_restore_rehearsal_v290` 고정
- target 존재 여부를 PostgreSQL catalog에서 먼저 확인
- target이 이미 있으면 create/restore/drop 모두 중단
- 없을 때만 `createdb` 정확히 1회
- owner `rpg_user`, template `template0`
- source와 같은 encoding/collation/locale provider 사용
- 생성 후 target public tables 0, `alembic_version` 없음 확인
- 원본 22 tables / 748 rows 유지 재확인
- `pg_restore`, `dropdb`, `.env`, Docker, Alembic 작업 없음

## 사용자 PC에서 다음 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_restore_rehearsal_database.py --execute
```

성공 기대값:

```txt
result: restore-rehearsal-database-created-empty-and-verified
target public tables: 0
target alembic_version: absent
source tables before/after: 22 / 22
source rows before/after: 748 / 748
```

## 다음 승인 경계

v292 성공 결과를 먼저 확인한 뒤에만 verified dump를 target DB에 `pg_restore`하는 단계를 별도 승인받습니다.
실제 restore, target DB 삭제, Alembic revision/upgrade/downgrade/stamp는 아직 금지입니다.

## 계속 보류

- 게임 콘텐츠 개발
- Vue Preview/Apply/write/인증 연결
- 원본 DB schema/data 변경
- seed/.env/API route/body/write guard 변경
- Docker container/volume 삭제

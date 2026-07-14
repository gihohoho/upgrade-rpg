# Upgrade RPG

현재 기준: **v294.postgres-migration-empty-database-create-tool**

## 현재 구조

- 실제 게임 화면: 루트 `index.html`
- 실제 관리자 화면: 루트 `admin.html`
- legacy JS/CSS: 루트 `src/`
- 새 Vue 앱: `frontend/vue-app/`
- FastAPI 백엔드: `backend/`
- 실제 Python 가상환경: `backend/.venv`

Vue `/admin`에는 GET health, requirements, domains, catalog, detail, relations가 연결되어 있습니다. 게임 콘텐츠 개발과 Vue write/인증 확대는 계속 보류합니다.

## 실제 PostgreSQL 보존 기준

```txt
PostgreSQL 16.14 / rpg_game / rpg_user
SQLAlchemy model tables 22 / public tables 22
total rows 748
alembic_version 없음 / current revision 없음
classification existing-schema-without-alembic-baseline
schema equivalence structurally-equivalent / differences 0
```

## 실제 backup과 restore rehearsal 완료

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source tables/rows: 22 / 748
restore DB: rpg_game_restore_rehearsal_v290
restore tables/rows: 22 / 748
restore schema: structurally-equivalent / differences 0
```

`local-backups/`는 실제 사용자/게임 데이터가 포함될 수 있으므로 Git, Docker build context, 전달 ZIP, 채팅에서 제외합니다.

## v294 핵심

새 도구:

```txt
tools/create_postgres_migration_test_database.py
```

승인 범위는 아래 DB가 없을 때 빈 DB 하나만 생성하는 것입니다.

```txt
source (preserve): rpg_game
verified restore (preserve): rpg_game_restore_rehearsal_v290
create empty only: rpg_game_migration_empty_v290
```

안전 경계:

- exact backup/SHA-256와 v293 restore report 재검증
- source와 restore DB의 table별 row counts 재검증
- restore DB schema differences=0 재검증
- target이 이미 존재하면 즉시 중단
- `createdb`, owner `rpg_user`, `template0`
- 생성 후 target 0 tables / 0 rows / `alembic_version` 없음 확인
- source와 restore DB 작업 전후 동일 확인
- `pg_restore`, `dropdb`, Alembic revision/upgrade/downgrade/stamp 실행 금지

## 빈 migration test DB 실행

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

## 서버 실행

FastAPI:

실행 위치: `backend` 폴더  
`.venv` 상태: 켜진 상태

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Vue:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: Python 가상환경 필요 없음

```bash
npm run dev
```

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

상세 문서:

- `docs/current/POSTGRES_RESTORE_REHEARSAL.md`
- `docs/current/POSTGRES_MIGRATION_TEST_DB_CREATION.md`
- `docs/current/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md`
- `NEXT_CHAT_HANDOFF.md`

# Upgrade RPG

현재 기준: **v290.postgres-backup-restore-preflight-gate**

## 현재 구조

- 실제 게임 화면: 루트 `index.html`
- 실제 관리자 화면: 루트 `admin.html`
- legacy JS/CSS: 루트 `src/`
- 새 Vue 앱: `frontend/vue-app/`
- FastAPI 백엔드: `backend/`
- 실제 Python 가상환경: `backend/.venv`

Vue `/admin`에는 GET health, requirements, domains, catalog, detail, relations가 연결되어 있습니다.
게임 콘텐츠 개발과 write/인증 확대는 계속 보류합니다.

## 실제 PostgreSQL 보존 기준

```txt
PostgreSQL 16.14 / rpg_game / 12 MB
SQLAlchemy model tables 22 / public tables 22
total rows 748
alembic_version 없음 / current revision 없음
health/db HTTP 200
classification existing-schema-without-alembic-baseline
```

현재 DB는 삭제/초기화 대상이 아니라 기존 데이터 보존형 Alembic baseline 대상입니다.

## v290 핵심

v290은 실제 backup/restore를 실행하지 않고 다음 경계를 확정했습니다.

- schema equivalence 차이 0개 선행 gate
- host/container `pg_dump`, `pg_restore`, `createdb`, `dropdb` 사용 가능 여부 확인
- backup 폴더: `local-backups/postgres/`
- backup 파일명: `rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump`
- restore rehearsal DB: `rpg_game_restore_rehearsal_v290`
- empty migration test DB: `rpg_game_migration_empty_v290`
- 원본 `rpg_game` restore 금지
- 실제 실행은 사용자 단계별 승인 후 진행

## 먼저 실행할 읽기 전용 확인

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
python tools/check_postgres_backup_restore_preflight.py
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
`.venv` 상태: 필요 없음 / 꺼져 있어도 됨

```bash
npm run dev
```

## 실행 금지

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
pg_dump 실제 backup 명령
createdb 실제 DB 생성 명령
pg_restore 실제 restore 명령
dropdb 실제 DB 삭제 명령
```

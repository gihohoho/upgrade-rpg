# Upgrade RPG

현재 기준: **v300.postgres-migration-roundtrip-reupgrade-ready**

## 현재 구조

- 실제 게임 화면: 루트 `index.html`
- 실제 관리자 화면: 루트 `admin.html`
- legacy JS/CSS: 루트 `src/`
- 새 Vue 앱: `frontend/vue-app/`
- FastAPI 백엔드: `backend/`
- 실제 Python 가상환경: `backend/.venv`

게임 콘텐츠 개발과 Vue write/인증 확대는 계속 보류합니다.

## PostgreSQL / Alembic 실제 상태

```txt
source rpg_game: 22 tables / 748 rows / differences=0 / alembic_version 없음
restore rehearsal: 22 tables / 748 rows / differences=0 / alembic_version 없음
migration test DB: alembic_version placeholder 1 table / 0 rows
migration current revision: 없음
initial revision: v295_initial_schema
initial revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
first upgrade: passed / differences=0
verified downgrade base: passed / differences=22
```

## v300 핵심

사용자 PC에서 아래 왕복 중 앞의 두 단계가 실제 성공했습니다.

```txt
upgrade head -> downgrade base -> [두 번째 upgrade head 대기]
```

v300에서는 첫 v298 upgrade 보고서와 v299 downgrade 보고서를 모두 확인한 뒤, 같은 isolated DB에 exact `alembic upgrade head`를 한 번만 실행합니다.

```txt
tools/reupgrade_postgres_migration_test_database.py
tools/smoke/backend/smoke_postgres_migration_test_database_roundtrip.py
docs/current/POSTGRES_MIGRATION_TEST_ROUNDTRIP.md
```

성공 조건은 두 번째 upgrade의 테이블·행 수·revision·schema signature가 첫 번째 upgrade 결과와 정확히 같은 것입니다. 원본 DB, restore rehearsal DB, `.env`, Docker volume은 변경하지 않습니다.

## 다음 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/reupgrade_postgres_migration_test_database.py --inspect && python tools/reupgrade_postgres_migration_test_database.py --execute
```

## 서버 실행

FastAPI — 실행 위치: `backend`, `.venv` 켜짐

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Vue — 실행 위치: `frontend/vue-app`, Python `.venv` 불필요

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

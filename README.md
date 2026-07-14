# Upgrade RPG

현재 기준: **v299.postgres-migration-test-downgrade-base-ready**

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
migration test DB: 22 model tables + alembic_version / total rows 1
migration current revision: v295_initial_schema
initial revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
upgrade verification: passed / differences=0
```

## v299 핵심

사용자 PC에서 isolated migration DB의 `upgrade head`가 실제로 성공했습니다.

```txt
result: migration-test-database-upgraded-and-verified
public tables: 23
model tables: 22
current revision: v295_initial_schema
schema differences: 0
source/rehearsal DB: preserved
```

v299에서는 같은 isolated DB에서 exact `alembic downgrade base`만 허용하는 실행 가드를 추가했습니다.

```txt
tools/downgrade_postgres_migration_test_database.py
tools/smoke/backend/smoke_postgres_migration_test_database_downgrade.py
docs/current/POSTGRES_MIGRATION_TEST_DOWNGRADE.md
```

성공 조건은 애플리케이션 테이블 22개가 모두 제거되고 빈 `alembic_version` placeholder만 남는 것입니다. 원본 DB, restore rehearsal DB, `.env`, Docker volume은 변경하지 않습니다.

## 다음 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/downgrade_postgres_migration_test_database.py --execute
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

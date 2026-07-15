# Upgrade RPG

현재 기준: **v306.postgres-next-revision-readonly-preflight**

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
classification: alembic-managed-baseline-complete
source rpg_game: 23 public tables / 749 rows / application 22 tables / 748 rows
restore rehearsal: 23/749 / v295_initial_schema / report verified
migration test DB: 23/1 / v295_initial_schema / differences=0
initial revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source/rehearsal schema/data digest: identical
v302 rehearsal execution report: verified
v304 source execution report: verified
v305 completion check: passed
```

## v306 핵심

새 revision을 생성하지 않고 실제 후보 schema 변경이 있는지만 읽기 전용으로 판단합니다.

```txt
tools/check_postgres_next_revision_preflight.py
tools/smoke/backend/smoke_postgres_next_revision_preflight.py
docs/current/POSTGRES_NEXT_REVISION_PREFLIGHT.md
```

검사 범위:

- Alembic single base/single head
- 승인 SQLAlchemy model/Alembic env source SHA-256
- canonical schema differences=0
- PostgreSQL read-only transaction 안의 Alembic `compare_metadata()`
- type/server default/nullable/index/constraint 후보
- integer PK sequence ownership과 unowned sequence

새 revision/autogenerate/upgrade/downgrade/stamp는 별도 승인 전까지 금지합니다.

## 다음 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_next_revision_preflight.py --strict
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

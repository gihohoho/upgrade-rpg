# Upgrade RPG

현재 기준: **v308.runtime-config-hardening-ready**

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
current revision: v295_initial_schema
restore rehearsal: 23/749 / report verified
migration test DB: 23/1 / differences=0
source/rehearsal schema/data digest: identical
v302 rehearsal execution report: verified
v304 source execution report: verified
v305 completion check: passed
v306 next revision preflight: candidate operations 0 / next revision required no
v307 runtime readiness --require-health: passed / production warnings 12
```

## v308 핵심

DB, 실제 `.env`, 실행 중인 Docker 자원을 변경하지 않고 runtime code/config와 배포 초안을 보강했습니다.

```txt
backend/app/core/config.py
backend/app/db/session.py
backend/app/main.py
backend/.env.example
backend/Dockerfile
deploy/docker-compose.production.yml
tools/check_runtime_config_hardening.py
tools/smoke/backend/smoke_runtime_config_hardening.py
```

적용 내용:

- SQLAlchemy pool 5개 정책 명시
- shutdown `engine.dispose()` lifecycle
- production `DEBUG=true` 및 로컬 기본 secret 차단
- non-root FastAPI Dockerfile
- Adminer/PostgreSQL host port가 없는 별도 운영 Compose 초안
- local `docker-compose.yml`과 실제 `.env` 유지
- 자동 Alembic migration 없음

## 다음 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
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

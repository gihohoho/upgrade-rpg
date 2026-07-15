# Upgrade RPG

현재 기준: **v309.runtime-engine-source-binding-inspector-fix**

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

## v308 runtime hardening

- SQLAlchemy pool 5개 정책 명시
- shutdown `engine.dispose()` lifecycle
- production `DEBUG=true` 및 로컬 기본 secret 차단
- non-root FastAPI Dockerfile
- Adminer/PostgreSQL host port가 없는 별도 운영 Compose 초안
- local `docker-compose.yml`과 실제 `.env` 유지
- 자동 Alembic migration 없음

## v309 검사기 수정

실제 engine은 계속 `settings.database_url`을 사용했습니다. v308 오류는 여러 줄 `create_async_engine()` 호출을 한 줄 문자열로만 찾던 검사기 오탐이며, v309에서 AST 기반 판정과 회귀 smoke로 수정했습니다.

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

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

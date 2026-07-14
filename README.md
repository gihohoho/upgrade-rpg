# Upgrade RPG

현재 기준: **v301.postgres-source-baseline-stamp-readonly-preflight-handoff**

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
migration test DB: 23 public tables / revision v295_initial_schema / differences=0
initial revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
round-trip: upgrade -> downgrade base -> upgrade verified
first/second upgrade signatures: identical
```

## v301 핵심

원본 DB baseline stamp 전에 필요한 증거를 한 번에 읽기 전용으로 재검사합니다.

```txt
tools/check_postgres_source_baseline_stamp_preflight.py
tools/smoke/backend/smoke_postgres_source_baseline_stamp_preflight.py
docs/current/POSTGRES_SOURCE_BASELINE_STAMP_PREFLIGHT.md
```

이 도구는 stamp/upgrade/downgrade/DB 생성·삭제·복원이나 row write를 실행하지 않습니다.
통과 후에도 원본 DB를 바로 stamp하지 않고 restore rehearsal DB에서 먼저 stamp 동작을 검증합니다.

## 다음 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_source_baseline_stamp_preflight.py --strict
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

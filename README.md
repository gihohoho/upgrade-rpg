# Upgrade RPG

현재 기준: **v304.postgres-source-baseline-stamp-final-guard**

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
restore rehearsal: 23 public tables / 749 rows / v295_initial_schema / v303 post-check verified
migration test DB: 23 public tables / 1 row / v295_initial_schema / differences=0
initial revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
round-trip: upgrade -> downgrade base -> upgrade verified
first/second upgrade signatures: identical
v301 source preflight: passed
v302 rehearsal stamp: passed
v303 rehearsal post-check: passed / report verified
```

## v304 핵심

원본 source stamp 전용 최종 guard를 별도 도구로 추가했습니다.

```txt
tools/stamp_postgres_source_database.py
tools/smoke/backend/smoke_postgres_source_baseline_stamp_guard.py
docs/current/POSTGRES_SOURCE_BASELINE_STAMP_FINAL_GUARD.md
```

`--inspect`는 완전한 읽기 전용이며 source, backup, revision, verified rehearsal, migration endpoint와 22개 application table 전체 schema/data digest를 함께 검증합니다.

## 다음 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/stamp_postgres_source_database.py --inspect
```

원본 source stamp 실제 실행은 별도 승인 전까지 금지합니다.

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

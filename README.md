# Upgrade RPG

현재 기준: **v298.postgres-initial-alembic-manual-review-upgrade-ready**

## 현재 구조

- 실제 게임 화면: 루트 `index.html`
- 실제 관리자 화면: 루트 `admin.html`
- legacy JS/CSS: 루트 `src/`
- 새 Vue 앱: `frontend/vue-app/`
- FastAPI 백엔드: `backend/`
- 실제 Python 가상환경: `backend/.venv`

게임 콘텐츠 개발과 Vue write/인증 확대는 계속 보류합니다.

## PostgreSQL / Alembic 현재 상태

```txt
source rpg_game: 22 tables / 748 rows / differences=0 / alembic_version 없음
restore rehearsal: 22 tables / 748 rows / differences=0 / alembic_version 없음
migration test DB: alembic_version 1 table / 0 rows / recorded revision 없음
initial revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
manual review: passed
```

## v298 핵심

사용자가 생성한 review bundle을 실제 코드 기준으로 수동 검토했습니다.

```txt
tables: 22 / 22
columns: 209 / 209
indexes: 42 / 42
foreign keys: 21
explicit unique constraints: 6
check constraints: 0
```

타입, 길이, nullable, PK, FK, unique, index, server default가 모델과 일치합니다. downgrade는 upgrade table 생성 순서의 정확한 역순이며 FK 자식 테이블이 부모보다 먼저 삭제됩니다.

추가된 안전 도구:

```txt
tools/upgrade_postgres_migration_test_database.py
tools/smoke/backend/smoke_postgres_initial_alembic_revision_manual_review.py
tools/smoke/backend/smoke_postgres_migration_test_database_upgrade.py
```

실제 `upgrade head`는 사용자 별도 승인 전 실행하지 않습니다. 승인 후에도 target은 아래 하나로 고정됩니다.

```txt
rpg_game_migration_empty_v290
```

원본 `rpg_game`, restore rehearsal DB, `.env`, Docker volume은 변경하지 않습니다.

## 읽기 전용 다음 확인

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/upgrade_postgres_migration_test_database.py --inspect
```

`ready-for-separate-upgrade-approval`이 확인된 뒤에만 별도 승인을 받아 `--execute`를 사용합니다.

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

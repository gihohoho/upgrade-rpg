# Upgrade RPG

현재 기준: **v292.postgres-restore-rehearsal-database-create-tool**

## 현재 구조

- 실제 게임 화면: 루트 `index.html`
- 실제 관리자 화면: 루트 `admin.html`
- legacy JS/CSS: 루트 `src/`
- 새 Vue 앱: `frontend/vue-app/`
- FastAPI 백엔드: `backend/`
- 실제 Python 가상환경: `backend/.venv`

Vue `/admin`에는 GET health, requirements, domains, catalog, detail, relations가 연결되어 있습니다.
게임 콘텐츠 개발과 Vue write/인증 확대는 계속 보류합니다.

## 실제 PostgreSQL 보존 기준

```txt
PostgreSQL 16.14 / rpg_game / rpg_user
SQLAlchemy model tables 22 / public tables 22
total rows 748
alembic_version 없음 / current revision 없음
health/db HTTP 200
classification existing-schema-without-alembic-baseline
schema equivalence structurally-equivalent / differences 0
```

현재 DB는 초기화 대상이 아니라 기존 데이터 보존형 Alembic baseline 대상입니다.

## 실제 backup 완료

사용자 PC에서 다음 backup이 생성·검증되었습니다.

```txt
local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
size: 126.60 KB
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source tables/rows: 22 / 748
TOC table definitions/data entries: 22 / 22
```

`local-backups/`는 실제 사용자/게임 데이터가 포함될 수 있으므로 Git, Docker build context, 전달 ZIP, 채팅에서 제외합니다.

## v292 핵심

새 도구:

```txt
tools/create_postgres_restore_rehearsal_database.py
```

승인된 범위는 원본 DB와 분리된 빈 DB 하나를 만드는 것뿐입니다.

```txt
source: rpg_game
target: rpg_game_restore_rehearsal_v290
owner: rpg_user
template: template0
```

도구는 target 존재 여부를 먼저 확인하고, 이미 있으면 중단합니다. 없을 때만 생성한 뒤 target table 0개, `alembic_version` 없음, 원본 22 tables / 748 rows 유지 여부를 검증합니다.

아직 `pg_restore`, `dropdb`, Alembic 작업은 실행하지 않습니다.

## 빈 리허설 DB 생성 명령

먼저 가상환경 활성화:

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_restore_rehearsal_database.py --execute
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

- `docs/current/POSTGRES_BACKUP_CREATION.md`
- `docs/current/POSTGRES_RESTORE_REHEARSAL_DB_CREATION.md`
- `docs/current/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md`
- `NEXT_CHAT_HANDOFF.md`

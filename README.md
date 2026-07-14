# Upgrade RPG

현재 기준: **v284.alembic-async-env-fix**

## 현재 상태

- 실제 게임 화면: 루트 `index.html`
- 실제 관리자 화면: 루트 `admin.html`
- legacy JS/CSS: 루트 `src/`
- 새 Vue 앱: `frontend/vue-app/`
- FastAPI 백엔드: `backend/`
- 실제 Python 가상환경: `backend/.venv`

Vue `/admin`에는 안전한 GET health, requirements, domains, catalog, detail, relations가 연결되어 있습니다.

## v284 핵심

기호 컴퓨터에서 `python -m alembic current` 실행 시 확인된 `MissingGreenlet` 오류를 수정했습니다.

기존 동기식 Alembic 연결을 다음 asyncpg 호환 구조로 변경했습니다.

- `async_engine_from_config()`
- `async with connectable.connect()`
- `await connection.run_sync(...)`
- `asyncio.run(...)`

DB schema, 데이터, `.env`, seed, revision, upgrade/downgrade/stamp는 변경하지 않았습니다.

관련 문서:

```txt
docs/current/ALEMBIC_ASYNC_ENV_FIX.md
docs/current/POSTGRES_ALEMBIC_READINESS.md
docs/current/POSTGRES_ALEMBIC_LOCAL_CHECKLIST.md
```

## backend 가상환경 활성화

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 실행

```bash
.venv\Scripts\activate
```

## Alembic 읽기 전용 상태 확인

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_alembic_readonly_state.py
```

이 도구는 `history`, `heads`, `current`만 실행하며 DB 구조를 변경하지 않습니다.

## 기존 서버 실행

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

## 현재 실행 금지

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
```

## 다음 방향

v284 ZIP 적용 후 읽기 전용 Alembic 상태와 Docker/PostgreSQL 상태를 확인합니다. 실제 DB 상태가 확인되기 전에는 baseline migration이나 stamp를 만들지 않습니다.

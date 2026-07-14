# Upgrade RPG

현재 기준: **v289.postgres-float-type-normalization-handoff**

## 현재 구조

- 실제 게임 화면: 루트 `index.html`
- 실제 관리자 화면: 루트 `admin.html`
- legacy JS/CSS: 루트 `src/`
- 새 Vue 앱: `frontend/vue-app/`
- FastAPI 백엔드: `backend/`
- 실제 Python 가상환경: `backend/.venv`

Vue `/admin`에는 GET health, requirements, domains, catalog, detail, relations가 연결되어 있습니다.
게임 콘텐츠 개발과 write/인증 확대는 계속 보류합니다.

## 실제 PostgreSQL 상태

```txt
PostgreSQL 16.14 / rpg_game / 12 MB
SQLAlchemy model tables 22 / public tables 22
total rows 748
alembic_version 없음 / current revision 없음
health/db HTTP 200
classification existing-schema-without-alembic-baseline
```

현재 DB는 삭제/초기화 대상이 아니라 기존 데이터 보존형 Alembic baseline 대상입니다.

## v289 핵심

기존 checker에서 나온 아래 두 차이는 PostgreSQL 타입 alias 표현 차이였습니다.

```txt
FLOAT <-> DOUBLE PRECISION
```

v289 checker는 PostgreSQL 규칙에 맞게 precision 없는 `FLOAT`를 `DOUBLE PRECISION`으로 정규화합니다.
DB schema와 model은 변경하지 않았습니다.

## 다음 읽기 전용 확인

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
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
`.venv` 상태: 필요 없음 / 꺼져 있어도 됨

```bash
npm run dev
```

## 실행 금지

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
```

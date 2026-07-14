# Upgrade RPG

현재 기준: **v288.postgres-baseline-schema-equivalence-preflight**

## 현재 구조

- 실제 게임 화면: 루트 `index.html`
- 실제 관리자 화면: 루트 `admin.html`
- legacy JS/CSS: 루트 `src/`
- 새 Vue 앱: `frontend/vue-app/`
- FastAPI 백엔드: `backend/`
- 실제 Python 가상환경: `backend/.venv`

Vue `/admin`에는 안전한 GET health, requirements, domains, catalog, detail, relations가 연결되어 있습니다.

## 실제 PostgreSQL 상태

기호 컴퓨터에서 읽기 전용 점검으로 확인된 결과:

```txt
Docker Compose: upgraderpg, running(2)
PostgreSQL volume: upgraderpg_rpg_postgres_data
PostgreSQL: 16.14
DB: rpg_game
DB size: 12 MB
SQLAlchemy model tables: 22
public tables: 22
total rows: 748
alembic_version: 없음
current revision: 없음
health/db: HTTP 200, status=ok
classification: existing-schema-without-alembic-baseline
```

현재 DB는 삭제/초기화 대상이 아니라 **기존 데이터 보존형 Alembic baseline 대상**입니다.

## Windows Docker 출력 오류 수정

v287에서 subprocess 출력을 UTF-8/cp949 혼합 환경에서도 안전하게 읽도록 수정했습니다.

```txt
tools/_safe_subprocess.py
```

## 다음 읽기 전용 schema 비교

backend 가상환경 활성화:

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash에서 실행

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
```

비교 범위:

- columns/types/nullability
- primary key
- foreign key
- unique constraint
- index
- check constraint

관련 문서:

```txt
docs/current/POSTGRES_RUNTIME_READONLY_STATE.md
docs/current/POSTGRES_ALEMBIC_BASELINE_STRATEGY.md
docs/current/POSTGRES_SCHEMA_EQUIVALENCE_CHECK.md
docs/current/POSTGRES_ALEMBIC_READINESS.md
```

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

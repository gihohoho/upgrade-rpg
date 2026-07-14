# NEXT CHAT HANDOFF — Upgrade RPG v289

## 기준 ZIP

- `rpg_v289_postgres_float_normalization_handoff_ready.zip`

## 현재 버전

- 최신 작업: `v289.postgres-float-type-normalization-handoff`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- 실제 backend 가상환경: `backend/.venv`

## 실제 PostgreSQL 상태

```txt
Docker Compose project: upgraderpg
containers: running(2)
volume: upgraderpg_rpg_postgres_data
PostgreSQL: 16.14
DB: rpg_game / rpg_user
DB size: 12 MB
model tables: 22
public tables: 22
total rows: 748
alembic_version: 없음
current revision: 없음
health/db: HTTP 200, status=ok
classification: existing-schema-without-alembic-baseline
```

DB 초기화 금지. 기존 데이터 보존형 baseline 전략입니다.

## v288 실제 schema 비교

```txt
classification: review-required
differenceCount: 2
user_profiles.add_attack_speed: model=FLOAT db=DOUBLE PRECISION
user_profiles.farm_atk_bonus: model=FLOAT db=DOUBLE PRECISION
```

두 항목은 PostgreSQL에서 동일하게 double precision으로 처리되는 타입 alias 표현 차이입니다.

## v289 완료

- FLOAT alias 정규화 추가
- `FLOAT` -> `DOUBLE PRECISION`
- `FLOAT(1..24)` -> `REAL`
- `FLOAT(25..53)` -> `DOUBLE PRECISION`
- alias 정규화 smoke 보강
- handoff smoke 최신화 및 core smoke 등록
- 생성 `egg-info` 제거 및 ignore 규칙 추가
- 중복 `backend/env.example` 제거
- stale root/current/handoff 문서 v289 동기화
- DB/Docker/env/seed/migration 미변경

## 다음 첫 확인

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

기대 후보는 `structurally-equivalent`, 차이 0개입니다. 실제 결과를 먼저 수집합니다.

## 다음 작업 — v290

차이 0개 확인 후 원본 DB에 영향을 주지 않는 backup/restore preflight와 별도 테스트 DB 계획을 진행합니다.
실제 backup/restore/DB 생성·삭제는 사용자 승인 후 단계적으로 수행합니다.

## 실행 금지

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
```

## 설치 상태

- 새 라이브러리/프레임워크 없음
- Docker, Compose, SQLAlchemy, Alembic, asyncpg, psycopg, FastAPI 확인 완료
- npm package 변경 없음

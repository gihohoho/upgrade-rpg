# NEXT CHAT HANDOFF — Upgrade RPG v288

## 기준 ZIP

- `rpg_v288_postgres_baseline_schema_equivalence_preflight.zip`

## 현재 버전

- 최신 작업: `v288.postgres-baseline-schema-equivalence-preflight`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- 실제 backend 가상환경: `backend/.venv`

## 사용자 실제 PostgreSQL 결과

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

보존 대상 예시:

```txt
users 1
user_profiles 1
characters 1
user_save_snapshots 2
admin_change_logs 13
```

DB 초기화 금지. 기존 데이터 보존형 baseline 전략으로 확정했습니다.

## v287 완료

- Windows Docker output의 UTF-8/cp949 혼합 `UnicodeDecodeError` 수정
- `tools/_safe_subprocess.py` 추가
- runtime/prerequisite/Alembic read-only 도구에 공통 safe decode 적용
- 실제 DB 결과를 문서와 baseline 전략에 반영

## v288 완료

- `tools/check_postgres_schema_equivalence.py` 추가
- columns/types/nullability/PK/FK/unique/index/check 상세 비교
- DB 변경 없는 read-only 도구
- 전용 smoke와 core smoke 등록
- `docs/current/POSTGRES_SCHEMA_EQUIVALENCE_CHECK.md` 추가

## 다음 첫 작업 — v289

사용자에게 아래 실행 결과를 받습니다.

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

결과가:

- `structurally-equivalent`: backup/restore + 별도 빈 DB migration 검증 계획 작성
- `review-required`: category/table별 차이 분석
- `connection-failed`: 연결 환경만 점검

## 절대 실행 금지

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
- Docker, Compose, SQLAlchemy, Alembic, asyncpg, psycopg, FastAPI 설치 확인 완료
- npm package 변경 없음

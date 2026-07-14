# 다음 추천 단계

## 현재 완료

- Alembic asyncpg online 연결 정상
- PostgreSQL 실제 연결과 DB health 정상
- model/public table 22개 일치
- 전체 row 748개 및 보존 대상 데이터 확인
- 분류 `existing-schema-without-alembic-baseline` 확정
- Windows subprocess UTF-8/cp949 출력 오류 수정
- 상세 schema 동등성 읽기 전용 도구 추가

## 기호가 먼저 확인할 명령

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

## 다음 작업 — v289

결과에 따라 다음 중 하나로 진행합니다.

1. `structurally-equivalent`: backup/restore 및 별도 빈 DB migration 검증 계획
2. `review-required`: category/table별 schema 차이 분석과 보존 계획
3. `connection-failed`: 연결 환경만 점검하며 DB 변경 금지 유지

## 계속 실행 금지

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
```

## 설치 관련

- 새 라이브러리/프레임워크 추가 없음
- Docker/Python DB 패키지는 이미 모두 확인됨
- npm 패키지 변경 없음

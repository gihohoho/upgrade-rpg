# 다음 추천 단계

## v290 완료

- schema equivalence 결과를 선행 조건으로 사용하는 backup/restore preflight gate 추가
- host/container PostgreSQL client 네 도구 사용 가능 여부 점검 추가
- backup 위치·파일명·민감정보 보존 규칙 확정
- 원본/restore rehearsal/migration test DB 경계 확정
- restore 전후 table/row/schema 비교 계획 확정
- 실제 DB mutation은 실행하지 않음

## 먼저 실행할 명령

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
python tools/check_postgres_backup_restore_preflight.py
```

## 결과별 다음 행동

- `review-required`: 새로운 차이만 분석하고 backup/migration으로 넘어가지 않음
- `connection-failed`: `.venv`, `psycopg`, Docker/PostgreSQL 연결 상태만 확인하고 DB 변경 금지
- schema 차이 0개 + preflight `blocked`: 누락 도구 또는 Git 제외 규칙만 해결
- preflight `ready-for-user-approval`: 실제 backup 한 단계에 대한 사용자 승인 요청

## 설치 관련

- 프로젝트에 새 Python/npm 라이브러리 또는 프레임워크 추가 없음
- host PostgreSQL client가 없어도 container 내부 네 도구가 있으면 별도 설치 불필요
- host와 container 모두 도구가 없을 때만 PostgreSQL client 설치 여부를 결정
- npm package 변경 없음

## 계속 실행 금지

```txt
python scripts/setup_dev_db.py --reset
docker compose down -v
python -m alembic revision --autogenerate
python -m alembic upgrade head
python -m alembic downgrade
python -m alembic stamp head
pg_dump 실제 backup 명령
createdb 실제 DB 생성 명령
pg_restore 실제 restore 명령
dropdb 실제 DB 삭제 명령
```

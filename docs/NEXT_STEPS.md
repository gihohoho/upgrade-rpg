# 다음 추천 단계

## 현재 완료

- Alembic asyncpg online 연결 정상
- PostgreSQL 실제 연결과 DB health 정상
- 모델/실제 테이블 22개 일치
- 전체 748 rows와 보존 대상 데이터 확인
- 기존 데이터 보존형 baseline 전략 확정
- Windows UTF-8/cp949 subprocess 출력 수정
- 상세 schema 읽기 전용 비교 도구 추가
- PostgreSQL `FLOAT` / `DOUBLE PRECISION` alias false positive 정규화

## 먼저 다시 확인할 명령

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

## 다음 작업 — v290

`structurally-equivalent`, 차이 0개가 실제로 확인되면 다음을 진행합니다.

1. backup 파일 위치/파일명/민감정보 보존 규칙 확정
2. `pg_dump`, `pg_restore`, `createdb`, `dropdb` 사용 가능 여부 점검
3. 원본과 분리된 restore rehearsal DB 이름 확정
4. 원본 DB에는 쓰지 않는 backup/restore 절차 작성
5. restore 전후 테이블·row 수 검증 계획
6. 별도 빈 DB 최초 Alembic migration 검증 계획
7. 명령 실행은 사용자 승인 후 한 단계씩 진행

alias 정규화 후에도 `review-required`이면 새로운 차이만 분석하며 backup/migration 단계로 넘어가지 않습니다.

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
- Docker/Python DB 패키지 설치 확인 완료
- npm package 변경 없음

# Current Status — v288

## 현재 기준

- 최신 작업: `v288.postgres-baseline-schema-equivalence-preflight`
- 기준 ZIP: `rpg_v288_postgres_baseline_schema_equivalence_preflight.zip`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- 실제 backend 가상환경: `backend/.venv`

## 실제 DB 확인 완료

- Docker Compose 프로젝트 `upgraderpg`, 컨테이너 2개 실행
- PostgreSQL volume `upgraderpg_rpg_postgres_data`
- PostgreSQL 16.14, DB `rpg_game`, 12 MB
- SQLAlchemy model 22 tables / 실제 public 22 tables
- 전체 row 748개
- `alembic_version` 없음
- 현재 revision 없음
- `/api/v1/health/db` HTTP 200, `status=ok`
- 분류: `existing-schema-without-alembic-baseline`

## v287-v288 완료

- Windows subprocess UTF-8/cp949 안전 decode helper 추가
- PostgreSQL runtime/prerequisite/Alembic 상태 도구에 공통 decode 적용
- 실제 결과를 근거로 기존 데이터 보존형 baseline 전략 확정
- SQLAlchemy metadata와 실제 PostgreSQL의 column/type/nullability/PK/FK/unique/index/check 구조를 비교하는 읽기 전용 도구 추가
- 전용 smoke 2개 추가 및 core smoke 등록

## 변경하지 않은 것

- DB schema 및 748 rows
- Docker container/volume
- `.env`
- seed
- Alembic revision 생성
- upgrade/downgrade/stamp
- API route path/response body
- 인증/Write Guard/write 로직
- Vue GET 화면
- 게임 콘텐츠

## 기호가 다음으로 확인할 명령

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
```

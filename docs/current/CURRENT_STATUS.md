# Current Status — v289

## 현재 기준

- 최신 작업: `v289.postgres-float-type-normalization-handoff`
- 기준 ZIP: `rpg_v289_postgres_float_normalization_handoff_ready.zip`
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
SQLAlchemy model tables: 22
public tables: 22
total rows: 748
alembic_version: 없음
current revision: 없음
health/db: HTTP 200, status=ok
classification: existing-schema-without-alembic-baseline
```

## v288 실제 schema 비교 결과

두 차이는 모두 `user_profiles`의 SQLAlchemy `FLOAT`와 PostgreSQL reflection `DOUBLE PRECISION` 표현 차이였습니다.

```txt
add_attack_speed: FLOAT / DOUBLE PRECISION
farm_atk_bonus: FLOAT / DOUBLE PRECISION
```

## v289 완료

- PostgreSQL `FLOAT` alias 정규화를 schema 비교 도구에 추가
- precision 없는 `FLOAT`를 `DOUBLE PRECISION`으로 비교
- alias false positive 전용 smoke 추가
- 오래된 다음 채팅 smoke를 현재 인수인계 기준으로 갱신
- `backend/idle_rpg_backend.egg-info/` 생성 산출물 제거 및 `.gitignore` 등록
- 중복 `backend/env.example` 제거, `backend/.env.example`을 단일 예시 파일로 유지
- 루트/current/handoff 문서를 v289 기준으로 정리
- 실제 DB, Docker, `.env`, seed, migration은 변경하지 않음

## 다음 확인

실행 위치: 프로젝트 루트
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
```

실제 다른 차이가 없다면 `structurally-equivalent`, 차이 0개가 기대되지만 실행 결과를 먼저 수집합니다.

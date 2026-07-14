# NEXT CHAT HANDOFF — Upgrade RPG v290

## 기준 ZIP

- `rpg_v290_postgres_backup_restore_preflight_ready.zip`

## 현재 버전

- 최신 작업: `v290.postgres-backup-restore-preflight-gate`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- 실제 backend 가상환경: `backend/.venv`

## 실제 PostgreSQL 보존 기준

사용자 컴퓨터에서 이전 읽기 전용 단계로 확인된 기준:

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

원본 DB 초기화 금지. 기존 데이터 보존형 baseline 전략입니다.

## v289 schema alias 수정

v288 실제 차이 두 개:

```txt
user_profiles.add_attack_speed: model=FLOAT db=DOUBLE PRECISION
user_profiles.farm_atk_bonus: model=FLOAT db=DOUBLE PRECISION
```

v289 checker는 아래처럼 정규화합니다.

```txt
FLOAT -> DOUBLE PRECISION
FLOAT(1..24) -> REAL
FLOAT(25..53) -> DOUBLE PRECISION
```

## v289 실제 재실행 상태

기호 컴퓨터에서 v289 적용 후 결과는 다음 채팅 시작 시 다시 수집해야 합니다.
이번 ZIP 제작 샌드박스에서는 `psycopg`가 없어 checker가 `connection-failed`였고, PostgreSQL/Docker client도 없어 실제 DB 결과를 확인할 수 없었습니다.
따라서 `structurally-equivalent`, 차이 0개라고 미리 기록하지 않았습니다.

## v290 완료

- `tools/check_postgres_backup_restore_preflight.py` 추가
- schema equivalence가 `structurally-equivalent`, 차이 0개인지 선행 gate
- host 및 기존 `upgrade_rpg_postgres` container의 `pg_dump`, `pg_restore`, `createdb`, `dropdb` 버전/사용 가능 여부 확인
- backup 폴더 `local-backups/postgres/` 확정
- backup 파일명 `rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump` 확정
- SHA-256 sidecar/민감정보/Git/ZIP 제외 규칙 확정
- 원본 DB: `rpg_game`
- restore rehearsal DB: `rpg_game_restore_rehearsal_v290`
- empty migration test DB: `rpg_game_migration_empty_v290`
- restore 전후 table별 row count/total/schema 비교 계획 확정
- 별도 빈 DB 최초 Alembic 검증 계획 확정
- 전용 smoke와 core smoke 등록
- `/local-backups/`를 `.gitignore`, `.dockerignore`에 등록

## 이번 단계에서 실행하지 않은 것

```txt
backup 생성
restore
DB 생성/삭제
Docker container/volume 변경
.env 변경
seed
Alembic revision/upgrade/downgrade/stamp
API route/body/write/auth 변경
게임 콘텐츠 변경
```

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
python tools/check_postgres_backup_restore_preflight.py
```

## 결과 분기

- `review-required`: backup/migration으로 넘어가지 않고 새로운 차이 분석
- `connection-failed`: `.venv`, psycopg, Docker/PostgreSQL 연결만 확인
- preflight `blocked`: blocking reason만 해결
- preflight `ready-for-user-approval`: 실제 backup 생성 한 단계만 사용자 승인 요청

## 설치 상태

- 프로젝트 새 Python/npm 라이브러리 또는 프레임워크 추가 없음
- host PostgreSQL client가 없어도 기존 container 내부 도구가 확인되면 추가 설치 불필요
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

# Current Status — v290

## 현재 기준

- 최신 작업: `v290.postgres-backup-restore-preflight-gate`
- 기준 ZIP: `rpg_v290_postgres_backup_restore_preflight_ready.zip`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- 실제 backend 가상환경: `backend/.venv`

## 실제 PostgreSQL 보존 기준

사용자 컴퓨터에서 v287~v288에 읽기 전용으로 확인한 기준입니다.

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

보존 대상 예시:

```txt
users: 1
user_profiles: 1
characters: 1
user_save_snapshots: 2
admin_change_logs: 13
```

## v289 schema gate 상태

v288 실제 차이 2개는 모두 PostgreSQL `FLOAT` / `DOUBLE PRECISION` alias 표현 차이였습니다.
v289에서 alias 정규화를 추가했습니다.

```txt
FLOAT -> DOUBLE PRECISION
FLOAT(1..24) -> REAL
FLOAT(25..53) -> DOUBLE PRECISION
```

기호 컴퓨터에서 v289 적용 후 `structurally-equivalent`, 차이 0개 결과는 아직 이 ZIP 제작 환경에서 직접 확인할 수 없었습니다.
ZIP 제작 샌드박스에서는 `psycopg`가 없어 `connection-failed`가 나왔으며, 이는 기호 컴퓨터 DB 결과로 취급하지 않습니다.

## v290 완료

- schema checker를 선행 gate로 다시 실행하는 읽기 전용 backup/restore preflight 도구 추가
- host와 기존 PostgreSQL container 내부의 `pg_dump`, `pg_restore`, `createdb`, `dropdb` 버전/사용 가능 여부 점검
- backup 위치 `local-backups/postgres/` 확정
- 파일명 `rpg_game_YYYYMMDD_HHMMSS_KST_v290.custom.dump` 확정
- SHA-256 sidecar와 민감정보/Git/ZIP 제외 규칙 확정
- source DB `rpg_game` restore 금지 경계 확정
- restore rehearsal DB `rpg_game_restore_rehearsal_v290` 확정
- empty migration test DB `rpg_game_migration_empty_v290` 확정
- restore 전후 table/row count 및 schema 비교 계획 확정
- 별도 빈 DB 최초 Alembic 검증 계획 확정
- 전용 smoke와 core smoke 등록
- `/local-backups/` Git/Docker 제외 규칙 추가

## 이번 단계에서 실행하지 않은 것

- 실제 backup
- restore
- DB 생성/삭제
- Docker container/volume 변경
- `.env` 변경
- seed
- Alembic revision/upgrade/downgrade/stamp
- API route/body/write/auth 변경
- 게임 콘텐츠 변경

## 사용자 PC 첫 확인

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

첫 명령이 `structurally-equivalent`, 차이 0개가 아니면 중단합니다.
두 번째 명령이 `ready-for-user-approval`이면 실제 backup 한 단계만 별도 승인받아 진행합니다.

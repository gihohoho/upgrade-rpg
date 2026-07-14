# Current Status — v294

## 기준

- 최신 작업: `v294.postgres-migration-empty-database-create-tool`
- 기준 ZIP: `rpg_v294_postgres_migration_test_database_creation_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 PostgreSQL source 상태

```txt
PostgreSQL 16.14
rpg_game / rpg_user
model/public tables: 22 / 22
total rows: 748
alembic_version/current revision: 없음
classification: existing-schema-without-alembic-baseline
schema: structurally-equivalent / differences=0
```

## 실제 backup 완료

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
size: 126.60 KB
SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
source tables/rows: 22 / 748
TOC definitions/data: 22 / 22
```

## 실제 restore rehearsal 완료

```txt
result: restore-rehearsal-completed-and-verified
target: rpg_game_restore_rehearsal_v290
public tables/rows: 22 / 748
schema: structurally-equivalent / differences=0
alembic_version: 없음
source before/after: 22 tables / 748 rows
```

## v294 준비 완료

- exact backup/SHA-256와 v293 restore report 재검증
- source live 22 tables / 748 rows / table별 counts 재검증
- rehearsal live 22 tables / 748 rows / differences=0 재검증
- migration target 존재 시 즉시 중단
- 없을 때만 `rpg_game_migration_empty_v290` 빈 DB 생성
- owner `rpg_user`, `template0`, source와 같은 locale metadata
- 생성 후 0 tables / 0 rows / alembic_version 없음 확인
- source/rehearsal 작업 전후 동일 확인
- no restore/drop/.env/Docker/Alembic/API/auth/game-content change

## 다음 사용자 실행

```bash
python tools/create_postgres_migration_test_database.py --execute
```

성공 결과를 확인한 뒤 최초 Alembic revision 생성 계획과 수동 검토 절차를 별도 승인 경계로 진행합니다.

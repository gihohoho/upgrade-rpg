# Current Status — v293

## 기준

- 최신 작업: `v293.postgres-restore-rehearsal-execute-tool`
- 기준 ZIP: `rpg_v293_postgres_restore_rehearsal_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## PostgreSQL 실제 source 상태

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

## 실제 빈 restore rehearsal DB 완료

```txt
target: rpg_game_restore_rehearsal_v290
owner/user: rpg_user
template: template0
public tables: 0
alembic_version: 없음
source before/after: 22 tables / 748 rows
```

## v293 준비 완료

- exact backup/manifest/snapshot/SHA-256 재검증
- target empty gate
- `pg_restore --single-transaction --exit-on-error`
- target에만 restore하고 source는 read-only
- restore 후 22 tables / 748 rows / table별 counts 비교
- target SQLAlchemy schema equivalence 차이 0개 검사
- source before/after 동일 검사
- no create/drop/clean/.env/Docker/Alembic/API/auth/game-content change

## 다음 사용자 실행

```bash
python tools/restore_postgres_rehearsal_database.py --execute
```

성공 결과를 확인한 뒤 target DB 보존/삭제와 empty migration DB 준비를 별도 결정합니다.

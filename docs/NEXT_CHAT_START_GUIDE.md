# Next Chat Start Guide — v294

## 기준

- ZIP: `rpg_v294_postgres_migration_test_database_creation_ready.zip`
- backend virtualenv: `backend/.venv`
- source DB: `rpg_game`
- verified restore DB: `rpg_game_restore_rehearsal_v290`
- migration target DB: `rpg_game_migration_empty_v290`

## 현재 사용자 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_migration_test_database.py --execute
```

성공 기준은 `migration-test-database-created-empty-and-verified`, target 0 tables / 0 rows, `alembic_version` 없음, source/rehearsal before/after 동일입니다.

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

성공 후에도 Alembic revision/upgrade/downgrade/stamp와 `dropdb`는 별도 승인 전 금지합니다.

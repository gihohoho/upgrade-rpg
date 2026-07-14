# Next Chat Start Guide — v292

## 기준

- ZIP: `rpg_v292_postgres_restore_rehearsal_database_creation_ready.zip`
- backend virtualenv: `backend/.venv`
- source DB: `rpg_game`
- approved target DB: `rpg_game_restore_rehearsal_v290`
- verified backup: `local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump`

## 사용자 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/create_postgres_restore_rehearsal_database.py --execute
```

성공 기준은 `restore-rehearsal-database-created-empty-and-verified`, target tables 0, source 22 tables / 748 rows 유지입니다.

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

성공 후에도 `pg_restore`, `dropdb`, Alembic 작업은 별도 승인 전 금지합니다.

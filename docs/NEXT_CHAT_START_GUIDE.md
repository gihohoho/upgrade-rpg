# Next Chat Start Guide — v306

## 기준

- ZIP: `rpg_v306_postgres_next_revision_readonly_preflight_ready.zip`
- backend virtualenv: `backend/.venv`
- source DB: `rpg_game` — 23/749 / application 22/748 / `v295_initial_schema`
- restore DB: `rpg_game_restore_rehearsal_v290` — 23/749 / `v295_initial_schema`
- migration DB: `rpg_game_migration_empty_v290` — 23/1 / `v295_initial_schema`
- classification: `alembic-managed-baseline-complete`
- v305 completion check: passed

## 첫 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_next_revision_preflight.py --strict
```

이 명령은 revision 생성/autogenerate/upgrade/downgrade/stamp를 실행하지 않습니다.

# Next Chat Start Guide — v298

## 기준

- ZIP: `rpg_v298_postgres_initial_alembic_manual_review_upgrade_ready.zip`
- backend virtualenv: `backend/.venv`
- source DB: `rpg_game`
- verified restore DB: `rpg_game_restore_rehearsal_v290`
- migration workspace DB: `rpg_game_migration_empty_v290`
- revision ID: `v295_initial_schema`
- revision SHA-256: `24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa`
- manual review: passed

## 현재 사용자 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/upgrade_postgres_migration_test_database.py --inspect
```

`ready-for-separate-upgrade-approval`이 확인되면 실제 `upgrade head`는 별도 사용자 승인을 받은 뒤에만 실행합니다.

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

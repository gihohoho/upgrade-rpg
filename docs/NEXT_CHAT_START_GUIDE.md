# Next Chat Start Guide — v303

## 기준

- ZIP: `rpg_v303_postgres_restore_rehearsal_stamp_postcheck_recovery.zip`
- backend virtualenv: `backend/.venv`
- source DB: `rpg_game` — 22 tables / 748 rows / differences=0 / no Alembic
- restore DB: `rpg_game_restore_rehearsal_v290` — v302 stamp 실행 완료 보고, v303 post-check 대기
- migration DB: `rpg_game_migration_empty_v290` — 23 public tables / current `v295_initial_schema` / differences=0
- revision SHA-256: `24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa`
- approved schema digest: `7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921`
- approved data digest: `ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244`

## 첫 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/stamp_postgres_restore_rehearsal_database.py --inspect
```

이 명령은 post-stamp 상태를 읽기만 합니다. 오류가 나도 stamp를 다시 실행하거나 rollback하지 말고 전체 출력을 공유합니다.

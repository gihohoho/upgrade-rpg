# Next Chat Start Guide — v304

## 기준

- ZIP: `rpg_v304_postgres_source_baseline_stamp_final_guard_ready.zip`
- backend virtualenv: `backend/.venv`
- source DB: `rpg_game` — 22/748 / no Alembic
- restore DB: `rpg_game_restore_rehearsal_v290` — 23/749 / `v295_initial_schema` / report verified
- migration DB: `rpg_game_migration_empty_v290` — 23/1 / `v295_initial_schema`
- revision SHA-256: `24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa`
- backup SHA-256: `b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481`
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
python tools/stamp_postgres_source_database.py --inspect
```

이 명령은 읽기 전용입니다. 통과해도 source `--execute`는 별도 승인 전까지 실행하지 않습니다.

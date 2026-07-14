# Next Chat Start Guide — v301

## 기준

- ZIP: `rpg_v301_postgres_source_baseline_stamp_preflight_handoff_ready.zip`
- backend virtualenv: `backend/.venv`
- source DB: `rpg_game` — 22 tables / 748 rows / differences=0 / no Alembic
- restore DB: `rpg_game_restore_rehearsal_v290` — 22 tables / 748 rows / differences=0
- migration DB: `rpg_game_migration_empty_v290` — 23 public tables / current `v295_initial_schema` / differences=0
- revision SHA-256: `24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa`
- round-trip: upgrade → downgrade base → upgrade 완료, signatures identical

## 첫 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_source_baseline_stamp_preflight.py --strict
```

오류가 나면 재실행하거나 DB를 직접 수정하지 말고 전체 콘솔 결과를 공유합니다.
성공해도 원본 DB를 stamp하지 않고 restore rehearsal stamp guard 준비로 넘어갑니다.

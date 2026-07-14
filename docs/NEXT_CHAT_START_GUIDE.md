# Next Chat Start Guide — v302

## 기준

- ZIP: `rpg_v302_postgres_restore_rehearsal_stamp_guard_ready.zip`
- backend virtualenv: `backend/.venv`
- source DB: `rpg_game` — 22 tables / 748 rows / differences=0 / no Alembic
- restore DB: `rpg_game_restore_rehearsal_v290` — 22 tables / 748 rows / differences=0 / no Alembic
- migration DB: `rpg_game_migration_empty_v290` — 23 public tables / current `v295_initial_schema` / differences=0
- revision SHA-256: `24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa`
- round-trip: upgrade → downgrade base → upgrade 완료, signatures identical
- v301 source preflight: 사용자 PC 실제 통과

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

오류가 나면 재실행하거나 DB를 직접 수정하지 말고 전체 콘솔 결과를 공유합니다.
성공해도 실제 rehearsal stamp를 실행하지 않고 별도 승인 경계에서 멈춥니다.

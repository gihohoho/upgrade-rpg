# Next Chat Start Guide — v299

## 기준

- ZIP: `rpg_v299_postgres_migration_test_downgrade_base_ready.zip`
- backend virtualenv: `backend/.venv`
- source DB: `rpg_game`
- verified restore DB: `rpg_game_restore_rehearsal_v290`
- migration DB: `rpg_game_migration_empty_v290`
- current migration revision: `v295_initial_schema`
- revision SHA-256: `24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa`
- first upgrade: completed and verified

## 현재 사용자 실행

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/downgrade_postgres_migration_test_database.py --execute
```

오류가 나면 재실행하거나 DB를 직접 수정하지 말고 전체 콘솔 결과를 공유합니다.

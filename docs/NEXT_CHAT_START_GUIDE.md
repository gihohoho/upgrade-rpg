# Next Chat Start Guide — v290

## 1. ZIP 기준 확인

새 채팅에서는 다음 파일을 먼저 읽습니다.

```txt
NEXT_CHAT_PROMPT.md
NEXT_CHAT_HANDOFF.md
docs/current/CURRENT_STATUS.md
docs/NEXT_STEPS.md
docs/current/POSTGRES_BACKUP_RESTORE_PREP.md
```

## 2. backend 가상환경

실제 가상환경은 프로젝트 루트가 아니라 `backend/.venv`입니다.

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

## 3. 먼저 실행할 읽기 전용 검사

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_schema_equivalence.py
python tools/check_postgres_backup_restore_preflight.py
```

- schema checker가 차이 0개가 아니면 중단
- preflight가 `blocked`이면 원인만 해결
- `ready-for-user-approval`이어도 실제 backup은 사용자 승인 전 실행 금지

## 4. 코드 기준선 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

Vue 빌드가 필요할 때:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음 / 꺼져 있어도 됨

```bash
npm ci
npm run build
```

## 5. 다음 작업

v291 후보는 실제 결과를 받은 뒤 **backup 생성 한 단계만** 승인받아 실행하는 것입니다.
restore rehearsal DB 생성, restore, 비교, 삭제는 각각 다시 승인받습니다.

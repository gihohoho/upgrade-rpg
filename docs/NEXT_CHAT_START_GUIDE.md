# Next Chat Start Guide — v289

## 1. ZIP 기준 확인

새 채팅에서는 다음 파일을 먼저 읽습니다.

```txt
NEXT_CHAT_PROMPT.md
NEXT_CHAT_HANDOFF.md
docs/current/CURRENT_STATUS.md
docs/NEXT_STEPS.md
docs/current/POSTGRES_SCHEMA_EQUIVALENCE_CHECK.md
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
```

기대 후보는 `structurally-equivalent`, 차이 0개이지만 실제 결과를 먼저 수집합니다.

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

`node_modules`가 이미 있고 lock 파일과 맞는 개발 실행만 필요하면 `npm run dev`만 실행합니다.

## 5. 다음 작업

v290에서는 원본 DB에 쓰지 않는 backup/restore preflight와 별도 테스트 DB 경계를 준비합니다.
사용자 승인 전에는 backup/restore, DB 생성·삭제, Alembic revision/upgrade/stamp를 실행하지 않습니다.

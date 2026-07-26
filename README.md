# Upgrade RPG

현재 기준은 `v334.production-deploy-plan-reviewed-inputs-blocked`입니다.

코딩을 이어갈 때는 루트 `AGENTS.md`와 `NEXT_CHAT_HANDOFF.md`를 먼저 읽고, 현재 상태는 `docs/current/CURRENT_STATUS.md`에서 확인합니다.

## 로컬 개발서버 ON

- 백엔드 시작 : python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
- 프론트엔드 시작 : npm run dev

## 핵심 폴더

- `index.html`, `admin.html`, `src/`: legacy 게임·관리자
- `frontend/vue-app/`: Vue GET read-only 앱
- `backend/`: FastAPI, Alembic, dependency locks, production Dockerfile
- `deploy/`: 운영 Compose, 변수 inventory, 정적 배포 계약과 검증 증거
- `docs/current/`: 지금 적용되는 판단·계획·상태
- `docs/guides/`: 실제 개발·실행 가이드
- `docs/contracts/`: API·관리자 계약
- `docs/archive/`: 과거 단계 기록
- `tools/`: checker, report, smoke

전체 구조는 `docs/current/PROJECT_STRUCTURE.md`, 문서 색인은 `docs/README.md`를 봅니다.

## 운영 고정값

```txt
managed PostgreSQL + provider CA verify-full
external reverse proxy HTTPS
backend 1 replica / 1 worker
GHCR: ghcr.io/gihohoho/upgrade-rpg-backend
target: linux/amd64
production image: exact digest only
```

검증된 image의 isolated runtime 확인은 완료했습니다. 운영 배포 계획 검토도 완료했지만 실제 host/DB/proxy/secret 입력이 정해지지 않아 배포 승인은 닫혀 있습니다. `docs/current/PRODUCTION_DEPLOYMENT_PLAN.md`를 참고합니다.

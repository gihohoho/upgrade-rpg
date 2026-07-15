# Upgrade RPG

현재 기준: **v319.github-connector-actions-settings-reviewed**

Codex는 루트 `AGENTS.md`를 먼저 읽고, 현재 상태는 `docs/current/CURRENT_STATUS.md`에서 확인합니다.

## 핵심 구조

- legacy 게임: `index.html`
- legacy 관리자: `admin.html`
- legacy JS/CSS: `src/`
- Vue GET read-only 앱: `frontend/vue-app/`
- FastAPI: `backend/`
- 운영 review template: `deploy/`
- backend 가상환경: `backend/.venv`

## 운영 고정값

```txt
managed PostgreSQL + provider CA verify-full
external reverse proxy HTTPS
backend 1 replica / 1 worker
GHCR namespace: gihohoho
repository: ghcr.io/gihohoho/upgrade-rpg-backend
target: linux/amd64
```

## 첫 검사

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_codex_handoff_readiness.py --strict
```

Docker login/pull/build/push/up/down과 실제 credential 입력은 아직 금지입니다.

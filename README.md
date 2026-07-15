# Upgrade RPG

현재 기준: **v312.production-managed-postgres-reverse-proxy-config-render-ready**

## 현재 구조

- legacy 게임: `index.html`
- legacy 관리자: `admin.html`
- legacy JS/CSS: `src/`
- Vue GET read-only 앱: `frontend/vue-app/`
- FastAPI: `backend/`
- 운영 배포 review template: `deploy/`
- 실제 Python 가상환경: `backend/.venv`

게임 콘텐츠, Vue write/인증, 새 Alembic revision은 계속 보류합니다.

## PostgreSQL/Alembic

```txt
classification: alembic-managed-baseline-complete
source: public 23/749, application 22/748
current revision: v295_initial_schema
next revision candidate operations: 0
```

## 운영 기본 방향

```txt
managed PostgreSQL + provider CA verify-full
external reverse proxy HTTPS
backend 1 replica / 1 Uvicorn worker
pool 5 + overflow 10
max_connections review candidate 40
```

production Compose에는 backend만 있으며 bundled PostgreSQL/Adminer/DB volume/host port/build는 없습니다.

## 다음 첫 검사

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_production_managed_postgres_reverse_proxy_selection.py --strict
```

그다음 승인된 config render-only:

```bash
python tools/render_production_compose_config.py --execute --confirm-stage v312-config-render-only
```

이 wrapper는 실제 `.env`나 secret을 읽지 않고 `docker compose config`만 실행합니다. pull/build/up/down은 계속 금지입니다.

## 기본 검증

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

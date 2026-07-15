# Upgrade RPG

현재 기준: **v313.backend-image-source-digest-policy**

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

기호 PC에서 backend-only production Compose의 config render-only 검사가 통과했습니다.

## 이미지 정책

```txt
production reference: digest-only
registry provider: deferred
target platform: deferred
base image digest approved: no
pull/build/push approved: no/no/no
```

## 다음 첫 검사

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_backend_image_source_digest_policy.py --strict
```

이 검사는 파일만 읽습니다. Docker pull/build/push/up/down은 계속 금지입니다.

## 기본 검증

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

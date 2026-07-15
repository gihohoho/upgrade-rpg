# FastAPI managed PostgreSQL 운영 배포 template — v312

## 파일

```txt
backend/Dockerfile
deploy/docker-compose.production.yml
deploy/production.env.example
deploy/production-capacity-plan.example.json
deploy/production-architecture-selection.example.json
deploy/reverse-proxy/README.md
deploy/isolated-validation/README.md
deploy/secrets/README.md
```

## FastAPI image 경계

- Python 3.11 slim 기반 Dockerfile
- non-root `app` 사용자
- `.env`와 실제 secret을 image에 복사하지 않음
- Uvicorn 1 worker
- 자동 Alembic 없음
- production Compose에서는 `build:` 대신 exact digest `BACKEND_IMAGE` 요구

## production Compose 경계

- backend service 하나만 포함
- 관리형 PostgreSQL 사용, bundled PostgreSQL service/volume 없음
- Adminer 없음
- host `ports:` 없음
- external reverse proxy network에 `8000`만 expose
- provider CA는 Compose secret으로 mount
- DATABASE_URL은 `verify-full` 요구
- `ENVIRONMENT=production`, `DEBUG=false`
- backend read-only/tmpfs/no-new-privileges
- `/api/v1/health` healthcheck
- replica 1

## 승인 경계

현재 허용:

```txt
project wrapper를 통한 docker compose config render only
```

아직 금지:

```txt
실제 env/secret/CA 입력
image pull/build
container/network/volume create/start/stop/remove
managed DB 연결
DNS/reverse proxy 실제 공개
Alembic/DB mutation
```

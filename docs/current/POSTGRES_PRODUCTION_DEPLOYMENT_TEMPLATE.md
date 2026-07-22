# FastAPI managed PostgreSQL production template — v334

역사적 계약명 `운영 배포 template — v312`의 Adminer 제외, exact digest, `verify-full`, 자동 Alembic 금지 원칙을 그대로 유지합니다.

## 파일

```txt
backend/Dockerfile.production
deploy/docker-compose.production.yml
deploy/production.env.example
deploy/production-deploy-plan.example.json
deploy/review/isolated-image-pull-validation-v333.json
docs/current/PRODUCTION_DEPLOYMENT_PLAN.md
```

## 고정 경계

- verified exact digest image, `linux/amd64`, non-root UID/GID 65532
- managed PostgreSQL, provider CA `verify-full`
- external reverse proxy HTTPS, backend host port 없음
- backend replicas/workers 1/1
- read-only rootfs, tmpfs, no-new-privileges
- `/api/v1/health` healthcheck
- bundled PostgreSQL/Adminer/DB volume 없음
- startup/entrypoint Alembic 없음

v333에서 exact image의 isolated pull/runtime/cleanup을 완료했고 v334에서 production deploy plan을 검토했습니다. 실제 production host, DB, CA, proxy/domain, secret injection, edge network가 미확정이므로 deployment approval/execution은 `no/no`입니다.

실행 준비 commit의 exact SHA 승인 전에는 production GHCR login/pull, Compose up/down, container/network/volume, managed DB 연결, DNS/proxy 변경을 실행하지 않습니다.

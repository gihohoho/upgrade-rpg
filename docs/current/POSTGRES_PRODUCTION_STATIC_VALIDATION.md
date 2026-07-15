# Production secret / TLS / container static validation — v312

## 목적

v310에서 시작한 운영 template 정적 검증을 v312의 확정 구조인 **관리형 PostgreSQL + 외부 reverse proxy HTTPS + backend 1/1**에 맞춰 갱신합니다. 실제 secret, `.env`, Docker resource, DB, Alembic은 건드리지 않습니다.

## 현재 검사 범위

- production Compose service가 backend 하나뿐인지
- bundled PostgreSQL/Adminer/named DB volume이 없는지
- backend host `ports:`와 `build:`가 없는지
- digest-pinned `BACKEND_IMAGE`가 필수인지
- DATABASE_URL/JWT/Admin/CORS/provider CA/edge network가 fail-fast placeholder인지
- DATABASE_URL 예시가 `sslmode=verify-full`과 provider CA mount 경로를 사용하는지
- backend replica 1, Uvicorn worker 1 계약인지
- non-root/read-only/no-new-privileges/tmpfs/healthcheck인지
- 자동 Alembic이 없는지
- 실제 deployment/secret 경로가 Git 및 Docker build context에서 제외되는지

## 읽기 전용 명령

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_production_secrets_tls_container_static.py --strict
```

정상 결과:

```txt
required Compose placeholders: 7/7
managed PostgreSQL service absent: True
backend digest/CA/edge boundary: True/True/True
actual production secrets/TLS/container execution approved: no
result: production-static-validation-managed-db-template-verified-runtime-application-blocked
next safe stage: run-config-render-only-on-docker-capable-host
```

## 한계

이 검사는 실제 provider CA 유효성, hostname, credentials, network allowlist, image digest 공급망, Docker runtime을 확인하지 않습니다. 현재 실제 Docker 승인 범위는 별도 wrapper를 통한 config render only입니다.

# Backend readiness — v312

## 완료

- FastAPI + PostgreSQL async runtime
- Alembic baseline `v295_initial_schema`
- source/rehearsal baseline stamp 검증과 next revision candidate 0
- live DB health 및 local Docker PostgreSQL healthy 확인
- SQLAlchemy pool + shutdown `engine.dispose()`
- production unsafe local defaults fail-closed
- non-root single-worker backend Dockerfile
- 관리형 PostgreSQL + provider CA `verify-full` 선택
- 외부 reverse proxy HTTPS 선택
- backend 1 replica / 1 worker 선택
- production Compose를 backend-only immutable-image template로 변경
- config render-only 안전 wrapper와 fail-closed smoke 준비

## 아직 미완료

- 기호 PC의 실제 `docker compose config` render 결과
- 관리형 PostgreSQL 공급자/상품/region/private network 선택
- 실제 provider CA/endpoint/secret
- backend image registry/source/digest 승인
- reverse proxy 제품/DNS/certificate 선택
- image pull/build와 isolated container start 검증
- 실제 배포

현재 승인된 Docker 범위는 config render only입니다. 실제 image/container/network/volume 또는 DB에는 변화가 없습니다.

# Backend readiness — v313

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
- 기호 PC config render-only 통과
- digest-only image reference와 SBOM/provenance/signature/vulnerability gate 추가

## 아직 미완료

- registry provider/namespace/repository 선택
- target platform과 base image exact digest 승인
- 실제 registry credential과 backend image digest
- 관리형 PostgreSQL 공급자/상품/region/private network 선택
- actual provider CA/endpoint/secret
- reverse proxy 제품/DNS/certificate 선택
- image pull/build/push와 isolated container start 검증
- 실제 배포

현재 Docker image/container/network/volume 또는 실제 DB에는 변화가 없습니다.

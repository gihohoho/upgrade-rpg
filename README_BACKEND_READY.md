# Backend readiness — v311

## 완료

- FastAPI + PostgreSQL async runtime
- Alembic baseline `v295_initial_schema`
- source/rehearsal baseline stamp 검증
- next revision candidate 0
- live DB health 및 Docker PostgreSQL healthy 확인
- explicit SQLAlchemy pool + shutdown `engine.dispose()`
- production unsafe local defaults fail-closed
- non-root Dockerfile와 별도 production Compose template
- production secret/TLS/container 정적 checker 통과
- worker/pool/max_connections 계산 계획과 확장 시나리오
- 관리형 PostgreSQL 우선 검토와 bundled TLS 대안 경계
- reverse proxy/HTTPS/network allowlist 계획
- isolated container Stage 0~4 승인 경계

## 아직 미완료

- 실제 운영 DB/provider와 reverse proxy 제품 확정
- 실제 운영 secret/CA/TLS server 설정
- image digest 실제 승인
- Docker Compose config render 검증
- isolated production container build/run 검증
- 실제 배포

현재 FastAPI startup command에는 Alembic migration이 포함되지 않습니다. v311의 `max_connections=40`은 review 후보이며 실제 DB 설정이 아닙니다.

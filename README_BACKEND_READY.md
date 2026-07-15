# Backend readiness — v315

## 완료

- FastAPI + PostgreSQL async runtime
- Alembic baseline `v295_initial_schema`
- live DB health, pool, lifecycle, production guard
- 관리형 PostgreSQL + provider CA `verify-full`
- 외부 reverse proxy HTTPS
- backend 1 replica / 1 worker
- production Compose config render-only 기호 PC 실제 통과
- GHCR/private/digest-only backend image 정책
- GitHub/GHCR namespace: `gihohoho`
- repository: `ghcr.io/gihohoho/upgrade-rpg-backend`
- target platform: `linux/amd64`
- production base image exact manifest digest 승인
- 로컬 Dockerfile 보존 + `backend/Dockerfile.production` 분리
- Codex용 `AGENTS.md`와 v315 읽기 전용 handoff 검사

## 아직 미완료

- GitHub Actions 최소 permissions와 안전 trigger 설계
- SBOM/provenance/signature/vulnerability gate 설계
- `.github/workflows/` 생성 승인
- 실제 backend image build digest
- 관리형 PostgreSQL 공급자/상품/region/private network
- actual provider CA/endpoint/secret
- reverse proxy 제품/DNS/certificate
- image login/pull/build/push와 isolated container start
- 실제 배포

CI credential 우선안은 GitHub Actions `GITHUB_TOKEN`입니다. 실제 token/PAT/credential은 저장소·ZIP·채팅에 넣지 않으며, local credential은 아직 deferred입니다.

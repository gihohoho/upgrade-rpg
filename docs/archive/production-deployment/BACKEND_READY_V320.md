# Backend readiness — v320

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
- Codex용 `AGENTS.md`, GitHub Actions/GHCR workflow와 YAML AST fail-closed 검사
- ChatGPT Codex Connector의 `gihohoho/upgrade-rpg` 단일 repository 연결과 조회 검증
- repository Actions 8개 full-SHA allowlist와 full-length SHA 강제 적용
- `ghcr-production-publish` environment 생성과 `main` 전용 rule 적용
- checksum-pinned Trivy, BuildKit provenance/SBOM, Cosign exact-digest 검증 설계
- source-controlled reviewer hard gate `false`

## 아직 미완료

- 비공개 저장소 게시 승인 모델 선택: `github-enterprise-cloud-required-reviewer` / `owner-only-source-controlled-two-step` / `keep-publishing-disabled`
- 선택한 승인 모델의 보호 절차 구성과 검증
- Python dependency/build-system hash lock, pinned pip, immutable Dockerfile frontend 구성·검증
- GitHub Actions/environment live 설정 재확인
- 게시 승인 모델과 재현성 gate가 모두 검증된 뒤 source-controlled gate 변경과 첫 workflow 실행
- 실제 backend image build digest
- 관리형 PostgreSQL 공급자/상품/region/private network
- actual provider CA/endpoint/secret
- reverse proxy 제품/DNS/certificate
- image login/build/push 실행 결과와 isolated container start
- 실제 배포

CI credential 우선안은 GitHub Actions `GITHUB_TOKEN`입니다. 실제 token/PAT/credential은 저장소·채팅에 넣지 않으며, local credential은 아직 deferred입니다.

GitHub Free/Pro/Team의 required reviewer는 공개 저장소에서만 지원되므로, 현재 비공개 저장소에 collaborator를 추가하는 것만으로는 보호 규칙을 만들 수 없습니다. 승인 모델과 재현성 gate를 모두 구성·검증하고 GitHub 설정을 live 재확인하기 전에는 `PUBLISH_REVIEWER_GATE_READY`를 리터럴 `"false"`로 유지하며 workflow를 실행하지 않습니다.

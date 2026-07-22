# Current Status — v334

## 현재 결과

```txt
latest: v334.production-deploy-plan-reviewed-inputs-blocked
strict result: production-deploy-plan-reviewed-inputs-blocked
next safe stage: select-production-targets-and-complete-executable-deploy-plan
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend
publish lifecycle: attempt-recorded / publishReviewerGateReady=false
production deploy plan reviewed: yes
approval ready / approved / executed: no / no / no
```

## 검증된 배포 후보

- exact reference: `ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2`
- GitHub Actions run `29909291344`: build, SPDX SBOM, local/pushed Trivy HIGH/CRITICAL 0건, SLSA provenance/SBOM, Cosign sign/verify 성공
- artifacts: `8525220616`, `8525254543`
- v333 isolated validation: `linux/amd64`, UID 65532, read-only rootfs, `/tmp` tmpfs, no host port/volume, health 200
- isolated container/network/local image cleanup 완료; 실제 DB, Alembic, production secret/CA/network 미사용
- evidence: `deploy/review/isolated-image-pull-validation-v333.json`

CI credential은 GitHub Actions `GITHUB_TOKEN`입니다. local private GHCR pull은 GitHub CLI OAuth `read:packages`를 Docker credential store로 전달했고 token 값은 기록하지 않았습니다. source-controlled lifecycle gate는 `deploy/github-actions-ghcr-publish-lifecycle.json`의 `attempt-recorded`, gate `false`이며 기존 다섯 run은 rerun하지 않습니다.

## v334 운영 배포 계획 검토

`docs/current/PRODUCTION_DEPLOYMENT_PLAN.md`와 `deploy/production-deploy-plan.example.json`을 검토 완료했습니다. 이번 작업은 계획 검토와 repository 정리만 승인됐고 production resource는 변경하지 않았습니다.

미확정 입력:

- production host/provider/region/OS/access
- managed PostgreSQL provider/product/region/endpoint/network
- provider CA PEM과 host mount path
- reverse proxy 또는 ingress, domain, DNS, certificate 책임
- Git 밖의 secret injection 위치
- 사전 생성 external edge network
- managed DB backup 상태와 첫 배포 traffic rollback 담당

개인 비공개 저장소의 `ghcr-production-publish` environment에는 native required reviewer가 없고 관리자 우회가 가능합니다. 실제 deploy는 모든 입력을 확정한 실행 준비 commit의 정확한 SHA를 기호가 별도 승인해야 합니다.

## GitHub live 확인

2026-07-22T12:49:50Z 기준:

- Actions enabled, selected actions only, full-length SHA required
- default `GITHUB_TOKEN` read-only, Actions PR approval false
- `ghcr-production-publish` 존재, `main` only
- native required reviewer false, admins can bypass true
- latest verified run `29909291344` completed/success

## 문서·폴더 정리

- `docs/` 루트는 `README.md`, `CHANGELOG.md`만 유지
- current/guides/contracts/archive/handoff 역할 분리
- 동일한 docs 사본 제거, obsolete root smoke 134개를 `tools/smoke/` canonical 구조로 통합
- 오래된 v316 ZIP과 빈 `.agents` 제거
- `local-backups/` PostgreSQL backup과 `local-review-artifacts/` Alembic evidence는 보존
- canonical 구조: `docs/current/PROJECT_STRUCTURE.md`

## 개발과 안전 경계

- Alembic current `v295_initial_schema`, 새 revision 필요 없음
- Vue는 GET read-only만 연결, Preview/Apply/write/auth 보류
- 구체적 요청 전 DB mutation, Alembic mutation, auth/API write, 게임 콘텐츠·밸런스 변경 금지
- production Compose/container/network/volume/DNS/proxy 변경과 실제 deploy는 승인 전 금지
- `docker compose down -v`, 자동 migration/deploy/retry 금지

현재 필요한 extension·설치는 없습니다. 다음에는 운영 공급자와 domain 정보를 확정해 실행 가능한 deploy plan을 준비합니다.

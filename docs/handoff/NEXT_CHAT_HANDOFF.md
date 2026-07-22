# Upgrade RPG Codex handoff — v334

## 현재 상태

```txt
latest: v334.production-deploy-plan-reviewed-inputs-blocked
strict result: production-deploy-plan-reviewed-inputs-blocked
next safe stage: select-production-targets-and-complete-executable-deploy-plan
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility/platform: private / linux/amd64
verified reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:ff939391517452a3ec477adaa0f8556d3525f9d0c6fb5f9d0df11d8f3d8461d2
publish lifecycle: attempt-recorded / publishReviewerGateReady=false
production deploy plan reviewed: yes
approval ready/approved/executed: no/no/no
```

운영 구조는 managed PostgreSQL + provider CA `verify-full` + external reverse proxy HTTPS + backend replicas/workers 1/1입니다. Alembic current는 `v295_initial_schema`, 새 revision 필요 상태는 `no`입니다. Vue는 GET read-only만 연결합니다.

## 사용자 협업 규칙

- 기호에게 한국어로 쉽게 설명하고 모든 명령 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적습니다.
- 필요한 extension·권한·설치는 해결될 때까지 요청합니다.
- Codex가 정상 개발 서버를 재사용하고 필요한 경우 직접 시작·중지합니다.
- Codex가 변경 뒤 add/commit/push까지 직접 합니다. ZIP과 Git 명령 안내는 제공하지 않습니다.
- actual secret/token/PAT/password/CA/cert/key는 Git·채팅·로그·artifact에 기록하지 않습니다.

## image와 GitHub 증거

CI credential은 GitHub Actions `GITHUB_TOKEN`, local pull은 GitHub CLI OAuth `read:packages` → Docker credential store입니다. source-controlled lifecycle gate는 `deploy/github-actions-ghcr-publish-lifecycle.json`입니다.

```txt
preparation: 36e8720a53ef7ff6a8334de6bc99646998d63fc9
authorization: 26a11356e33c978afa8cd8a4881500fa62cdbc5c
immediate closure: 1c4a982b2a35d3d45f59e7d9faefcdecca69e6c5
evidence record: 1f0340ddfcf3c8a74cf14110d5957627d4c5d38a
run ID: 29909291344
artifact IDs: 8525220616 / 8525254543
status/conclusion: completed / success
```

run_attempt=1, repository owner single dispatch, immediate closure, 정확한 `closureCommitSha`, rerun 금지 계약을 사용했습니다. 일반 lifecycle 결과 단계 `review-recorded-workflow-attempt-evidence`는 역사 계약으로 보존합니다. 이전 네 실패와 최종 성공의 상세는 lifecycle JSON과 `docs/CHANGELOG.md`에 있습니다.

Trivy HIGH/CRITICAL 0건, SPDX SBOM, SLSA provenance/SBOM, Cosign sign/verify를 통과했습니다. v333 isolated runtime에서도 non-root, read-only, no host port/volume, health 200을 확인하고 container/network/local image를 제거했습니다. evidence는 `deploy/review/isolated-image-pull-validation-v333.json`입니다.

2026-07-22T12:49:50Z GitHub live 확인에서 selected actions/full SHA, default token read-only, `ghcr-production-publish` main-only는 정상입니다. 개인 비공개 저장소라 native required reviewer는 없고 admins can bypass가 true이므로 exact-SHA owner approval을 유지합니다.

## v334 운영 배포 계획

`docs/current/PRODUCTION_DEPLOYMENT_PLAN.md`와 `deploy/production-deploy-plan.example.json`을 검토 완료했습니다. actual production resource는 변경하지 않았습니다.

미확정 입력:

- production host/provider/region/OS/access
- managed PostgreSQL provider/product/region/endpoint/network
- provider CA PEM과 host mount path
- reverse proxy/ingress, domain, DNS, certificate
- Git 밖의 secret injection
- external edge network
- managed DB backup 상태와 first-deploy traffic rollback 담당

모든 입력을 확정한 실행 준비 commit의 정확한 40자리 SHA를 기호가 별도 승인한 뒤에만 실제 GHCR login/pull, final Compose render, backend start/replace, read-only health, 기존 proxy route 확인을 진행합니다. DB/Alembic mutation, volume 삭제, 자동 deploy/retry는 포함하지 않습니다.

## 폴더 정리 결과

- `docs/` 루트는 index와 단일 changelog만 유지
- `current/`, `guides/`, `contracts/`, `archive/`, `handoff/`로 역할 분리
- 동일한 docs 사본 제거, obsolete root smoke 134개를 `tools/smoke/` canonical 구조로 통합
- 오래된 v316 ZIP과 빈 `.agents` 제거
- `local-backups/`의 PostgreSQL backup과 `local-review-artifacts/`의 Alembic evidence는 보존

## 첫 검사

실행 위치: 프로젝트 루트
Python `.venv` 상태: 셸 활성화는 꺼짐, `backend/.venv/Scripts/python.exe` 직접 사용
새 설치 여부: 없음

```bash
python tools/check_production_deployment_plan.py --strict
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

기대값은 `production-deploy-plan-reviewed-inputs-blocked`, 다음 단계는 `select-production-targets-and-complete-executable-deploy-plan`입니다.

현재 필요한 extension·설치는 없습니다. active GitHub CLI 계정은 `gihohoho`이며 `read:packages`가 있습니다. 비활성 `konghjin`의 만료 token은 건드리지 않았습니다. 서버 재시작은 이번 구조·문서 작업에 필요하지 않습니다.

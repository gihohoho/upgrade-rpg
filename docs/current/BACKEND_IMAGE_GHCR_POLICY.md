# Backend image GHCR policy — v326

## 확정값

```txt
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
namespace: gihohoho
repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility: private
target platform: linux/amd64
production reference: ghcr.io/gihohoho/upgrade-rpg-backend@sha256:<approved-64-hex-digest>
```

`gihohoho`는 기호가 직접 확인한 GitHub repository owner이며 placeholder가 아닙니다.

## 인증정보와 권한

- CI는 실행 중에만 제공되는 ephemeral `GITHUB_TOKEN`을 사용합니다.
- actual token 값은 파일, Git, 채팅, 로그, artifact에 기록하지 않습니다.
- local credential/PAT 전략은 deferred이며 장기 Docker credential을 만들지 않았습니다.
- workflow는 두 번 실행됐습니다. 두 번째 run은 validation을 통과했지만 로컬 image build에서 실패했고 CI login/push는 실행되지 않았습니다.
- repository는 명시한 외부 action 8개와 full-length SHA만 허용합니다.
- 기본 `GITHUB_TOKEN`은 read-only이며 publish job만 `packages: write`, `id-token: write`를 받습니다.
- `ghcr-production-publish` environment는 `main`만 허용하고 secrets/variables는 0/0입니다.
- native required reviewer/prevent self-review가 없으므로 기호가 `owner-only-source-controlled-two-step`을 선택했습니다.

## 현재 실행 상태

```txt
version: v326.dockerfile-bootstrap-fixed-retry-preparation-publish-gated
workflow file/creation approved: yes/yes
workflow execution approved/executed: yes/yes
CI registry login/build/push approved: yes/yes/yes
CI registry login/build/push executed: no/yes/no (build attempted and failed)
publish environment/main-only: yes/yes
required reviewer/prevent self-review: no/no
publish approval model: owner-only-source-controlled-two-step
lifecycle state/gate: attempt-recorded/false
dependency/frontend input lock: complete
prior preparation SHA: 350bbd085f1cf636810d75ddcbb5321e0791256c consumed
bootstrap-fix preparation SHA: 2f77ebf0f60a39c936509df26f903995f0c62967 consumed
container start approved/executed: no/no
```

## lifecycle 게시 정책

- v321 `f4788acf5455b07169320bd29f43ddf92ff1d5ad` 승인은 감사 이력으로만 보존합니다.
- 첫 실패 evidence commit `1f12ea59eb54385337557e9754f86731ec53d253`를 `priorAttemptEvidence`로 보존합니다.
- 두 번째 run `29877813770`과 closure `5479e6b14826b3a0f2b6d0c3beb0e2142ca22c94`를 현재 `attempt-recorded` evidence로 보존합니다.
- 두 번째 run은 Dockerfile bootstrap target 문제로 로컬 build에서 실패했고 publish job은 skipped됐습니다.
- authorization commit은 승인 preparation의 direct child이고 lifecycle JSON만 바꿔야 합니다.
- repository owner, `run_attempt=1`, GitHub API의 single dispatch만 허용합니다.
- run이 접수되면 즉시 closure commit으로 gate를 닫아 `authorization-closed-awaiting-evidence`로 전이합니다. 이 C commit은 `closureCommitSha=null`이며 rerun은 금지합니다.
- run 종료 뒤 별도 evidence commit에서 부모 C commit SHA를 `closureCommitSha`에 넣고 `attempt-recorded`로 전이해 run ID/URL/conclusion/digest/signature 결과를 기록한 뒤 `review-recorded-workflow-attempt-evidence`로 갑니다.
- 실패·취소·시간 초과 conclusion만으로 `registryMutationExecuted=false`나 `signatureVerified=false`를 기록하지 않고 각 job/step, exact digest와 partial evidence를 따로 확인합니다.
- login보다 먼저 lifecycle/ancestry/path를 다시 검사합니다.

## build와 검증 정책

- Python Linux/amd64 dependency와 build toolchain을 exact version/wheel SHA-256으로 잠급니다.
- local OCI build에서 SPDX SBOM과 HIGH/CRITICAL Trivy gate를 먼저 통과합니다.
- push 후 exact digest의 BuildKit provenance/SBOM과 Trivy를 다시 검사합니다.
- 모든 image gate 통과 뒤에만 Cosign keyless sign과 identity/issuer verify를 수행합니다.
- `DOCKER_BUILD_RECORD_UPLOAD=false`로 계획 밖 Docker build record artifact를 만들지 않습니다.
- push 뒤 실패해도 digest가 있다면 존재하는 partial evidence를 14일 보존합니다. 부분 증거는 verified candidate가 아닙니다.
- byte-for-byte deterministic image를 보장한다고 주장하지 않습니다.
- 최종 backend image는 tag가 아니라 검증·승인된 exact `sha256` digest로만 production Compose에 넣습니다.
- 이번 workflow는 production reference 변경이나 자동 deploy를 하지 않습니다.
- authorization-open CI는 v324 정적 checker를 먼저 직접 실행하고 `SKIP_GHCR_HANDOFF_SMOKES=1`로 closed root 전용 세 smoke만 건너뜁니다. application/backend 전체 core smoke는 그대로 유지합니다.

## 다음 안전 단계

run `29877813770`의 evidence를 검토합니다. 기호가 승인하면 `backend/Dockerfile.production`의 bootstrap `--python-version 3` 한 곳만 `3.11`로 수정해 새 preparation을 준비합니다. 그 새 정확한 SHA의 별도 승인 전에는 다음 workflow나 GHCR login/push를 실행하지 않습니다.

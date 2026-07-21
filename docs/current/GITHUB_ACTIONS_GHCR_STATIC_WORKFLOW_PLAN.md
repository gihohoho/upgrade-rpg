# GitHub Actions / GHCR workflow plan — v325

```txt
version: v325.second-owner-only-attempt-recorded-failed-pre-registry-image-build
preparation version: v324.bootstrap-fixed-retry-preparation-publish-gated
base plan version: v322.owner-only-single-run-lifecycle-hardened-publish-gated
result: github-actions-ghcr-owner-only-attempt-recorded-publish-gated
repository: gihohoho/upgrade-rpg
image: ghcr.io/gihohoho/upgrade-rpg-backend
workflow: .github/workflows/publish-backend-ghcr.yml
lifecycle: deploy/github-actions-ghcr-publish-lifecycle.json
workflow source SHA-256: 245630348d384cc1c862014454cb73b6149a8c3a20d7b114763bc6fe655ef4bd
workflow semantic SHA-256: e08c3788e88da351112bc381d225e418938f7bd74ccec7eb83f9f59eff6f724c
workflow file creation: complete
workflow 파일 생성: 완료
workflow execution: runs 29716038891 and 29877813770 completed/failure
registry login/build/push: no/attempted-failed/no
next safe stage: review-recorded-workflow-attempt-evidence
```

정적 문서 잠금 표식: `workflow_dispatch`, `pull_request_target` 금지, `contents: read`, `actions: read`, `packages: write`, `id-token: write`, Docker BuildKit, `HIGH,CRITICAL`, Sigstore Cosign keyless, `approved_preparation_commit`, `DOCKER_BUILD_RECORD_UPLOAD`, required reviewer 제약.

## 첫 실행 결과와 focused fix 후보

run `29716038891`은 validate job의 `Install backend validation dependencies`에서 실패했습니다. bootstrap pip wheel 다운로드가 `--python-version 3`을 사용해 Python `>=3.10`을 요구하는 `pip==26.1.2`를 제외한 것이 직접 원인입니다. 기호의 focused fix 승인 뒤 해당 값을 `--python-version 3.11`로 수정하고 workflow source/semantic hash, checker와 정책 문서를 함께 갱신했습니다. 첫 실패는 `priorAttemptEvidence.recordCommitSha=1f12ea59eb54385337557e9754f86731ec53d253`로 보존하며 새 preparation gate는 `false`입니다.

## 두 번째 실행 결과와 focused fix 후보

run `29877813770`은 workflow bootstrap과 repository checks를 통과한 뒤 `Build local linux/amd64 image without registry mutation`에서 실패했습니다. 직접 원인은 `backend/Dockerfile.production:22`에 같은 bootstrap target `--python-version 3`이 남아 있던 것입니다. SBOM/Trivy와 publish job은 미실행 또는 skipped였고 artifact/digest는 없으며 GHCR login/push와 registry mutation도 없었습니다. 다음 후보는 Dockerfile의 해당 한 곳만 `3.11`로 고치는 focused fix이며 아직 사용자 승인 전입니다.

## v322가 필요한 이유

기호는 v321 준비 commit `f4788acf5455b07169320bd29f43ddf92ff1d5ad`를 정확히 승인했습니다. 이 human checkpoint는 선택한 `owner-only-source-controlled-two-step` 모델의 핵심이어서 필요했습니다. 그러나 실행 직전 추가 감사에서 다음 문제를 발견했습니다.

1. v321 checker가 `PUBLISH_REVIEWER_GATE_READY=false`만 허용해 authorization에서 gate를 열면 CI가 실패했습니다.
2. 같은 authorization SHA의 rerun 또는 여러 dispatch를 차단하지 않았습니다.
3. authorization commit과 승인한 preparation commit의 직접 parent 연결 및 변경 파일 제한이 없었습니다.
4. Docker build action이 계획에 없는 build record artifact를 자동 생성할 수 있었습니다.
5. image push 이후 단계가 실패하면 이미 생성된 digest와 부분 증거가 보존되지 않았습니다.

따라서 `f4788acf...` 승인은 역사적 `priorApprovedPreparationSha`로만 보존합니다. 보안 계약과 workflow가 바뀐 v322 preparation-fix commit의 정확한 새 SHA는 다시 승인받습니다. 현재는 아무 workflow도 실행하지 않았고 registry mutation도 없습니다.

## 2026-07-20 GitHub live 설정

로그인된 repository 설정을 live 재확인하고 다음 상태로 맞췄습니다.

- 허용 action: `gihohoho` 소유 action + 아래 명시한 외부 action 8개만
- 외부 action full-length SHA 강제: 켜짐
- GitHub-owned action blanket allow: 꺼짐
- verified creator blanket allow: 꺼짐
- 기본 `GITHUB_TOKEN`: contents/packages read-only
- Actions의 PR 생성·승인: 꺼짐
- 점검 중 켜져 있던 fork write token과 fork secret 전달: 모두 `false`로 복원
- `ghcr-production-publish`: 존재, deployment branch `main` only
- environment secrets/variables: 0/0
- native required reviewer/prevent self-review: 없음

live 기록 시각은 `2026-07-20T03:04:15Z`입니다. authorization workflow는 이 기록이 실행 시점 기준 4시간을 넘으면 거부합니다. 따라서 새 SHA 승인 뒤 gate 변경 직전에 다시 확인합니다.

## trigger와 입력

trigger는 `workflow_dispatch` 하나뿐입니다. `push`, `pull_request`, `pull_request_target`, `schedule`, `release`, `repository_dispatch`, `workflow_run`은 허용하지 않습니다.

수동 입력:

- `source_commit`: authorization commit의 소문자 40자리 SHA이며 `github.sha`와 같아야 함
- `approved_preparation_commit`: 기호가 별도 메시지로 승인한 직전 preparation-fix commit의 소문자 40자리 SHA
- `approval_reason`: 공백 제거 후 10자 이상, secret 입력 금지
- `confirm_publish`: 명시적 `true`

실행 ref는 `refs/heads/main`이어야 하고 실행 actor와 repository owner가 같아야 합니다.

## 최소 permissions

```yaml
workflow default:
  contents: read

validate:
  actions: read
  contents: read

build_scan:
  contents: read

publish_sign_verify:
  contents: read
  packages: write
  id-token: write
```

`actions: read`는 동일 authorization SHA의 workflow run 목록을 GitHub API로 확인할 때만 사용합니다. `checks`, `deployments`, `issues`, `pull-requests`, `security-events`, `statuses` write는 주지 않습니다. 현재 private repository에서 Artifact Attestations API를 사용하지 않으므로 `attestations: write`도 주지 않습니다.

## full-SHA action allowlist

```txt
actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0
actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405
docker/setup-buildx-action@bb05f3f5519dd87d3ba754cc423b652a5edd6d2c
docker/login-action@af1e73f918a031802d376d3c8bbc3fe56130a9b0
docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a
anchore/sbom-action@e22c389904149dbc22b58101806040fa8d37a610
sigstore/cosign-installer@6f9f17788090df1f26f669e9d70d6ae9567deba6
actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a
```

## source-controlled lifecycle

gate는 workflow 문자열 하나가 아니라 `deploy/github-actions-ghcr-publish-lifecycle.json`의 상태 전이로 관리합니다.

### 1. preparation-closed

```txt
state: preparation-closed
publishReviewerGateReady: false
approvedPreparationSha: null
ownerApproval.recorded: false
observedAttempt.status: not-dispatched
```

현재 상태입니다. `priorApprovedPreparationSha`에는 `f4788acf...`가 역사적 증거로만 있고 새 authorization 권한을 주지 않습니다.

### 2. authorization-open

새 v322 preparation-fix SHA를 기호가 명시 승인한 뒤에만 만들 수 있습니다.

- authorization commit은 승인 preparation commit의 direct child
- 변경 경로는 lifecycle JSON 한 파일만
- `approvedPreparationSha`는 사용자 입력과 정확히 같음
- `ownerApproval.recorded=true` 및 UTC 시각 기록
- live GitHub 설정 증거는 4시간 이내
- `state=authorization-open`, `publishReviewerGateReady=true`

workflow와 정적 checker가 closed/open 두 상태를 모두 명시적으로 이해합니다. open은 임의 편집이 아니라 위 전이를 모두 만족할 때만 합법입니다.

### 3. single-run 검증

- `github.run_attempt`은 반드시 `1`
- rerun은 어떤 이유로도 허용하지 않음
- `actions: read` API로 같은 workflow, head SHA, main branch의 `workflow_dispatch`가 하나 이하인지 조회
- 보이는 run이 하나면 현재 run ID, actor, `run_attempt=1`과 일치해야 함
- API 오류, 두 개 이상 run, 다른 run ID는 fail-closed

### 4. immediate closure와 authorization-closed-awaiting-evidence

dispatch 뒤 GitHub가 run ID를 접수하면 실행 결론을 기다리며 open gate를 남겨 두지 않습니다. 별도 closure commit으로 lifecycle을 즉시 `authorization-closed-awaiting-evidence`로 전이하고 gate를 `false`로 되돌립니다. 이 C commit은 자기 SHA를 스스로 기록할 수 없으므로 `closureCommitSha=null`이어야 합니다. 실행 성공·실패·취소에 관계없이 닫습니다. run은 authorization commit의 snapshot을 사용하므로 main의 closure commit이 이미 접수된 run의 코드를 바꾸지는 않습니다.

closure와 최종 결과 기록은 authorization SHA, run ID/URL, run attempt, status/conclusion, 가능한 image digest와 signature 확인 여부를 남기되 actual secret은 저장하지 않습니다.

### 5. attempt-recorded

run이 종료되면 immediate closure commit을 다시 고치는 대신 별도 evidence commit에서 `attempt-recorded`로 전이합니다. 이 R commit이 direct parent인 C commit의 정확한 SHA를 `closureCommitSha`에 기록하고, run ID/URL, `run_attempt=1`, 실제 status/conclusion, 확인 가능한 exact image digest, signature 검증 여부를 함께 기록합니다. 지원 lifecycle은 P `preparation-closed` → A `authorization-open` → C `authorization-closed-awaiting-evidence` → R `attempt-recorded` 네 상태이며 R의 next stage는 `review-recorded-workflow-attempt-evidence`입니다.

허용되는 완료 conclusion은 `success`, `failure`, `neutral`, `cancelled`, `skipped`, `timed_out`, `action_required`, `stale`, `startup_failure`이며 실제 관찰값을 보존합니다. non-success conclusion은 `registryMutationExecuted=false`나 `signatureVerified=false`를 뜻하지 않습니다. image push 또는 signature verify 뒤 artifact upload/final summary에서 실패했을 수 있으므로 각 job/step conclusion, digest output과 partial evidence artifact를 별도로 확인해 기록합니다. signature 검증까지 끝나고 전체 evidence가 확인된 digest만 verified candidate가 될 수 있습니다.

## fail-closed build/publish 순서

게시 전:

1. exact source, owner, input, first attempt, unique dispatch 확인
2. authorization direct parent와 lifecycle-only diff 확인
3. repository 정적 검사, Python compileall, 전체 core smoke
4. registry에 올리지 않는 로컬 `linux/amd64` OCI build
5. SPDX JSON SBOM 생성과 구조 검사
6. 공식 Trivy `0.70.0` Linux asset을 SHA-256 `8b4376d5d6befe5c24d503f10ff136d9e0c49f9127a4279fd110b727929a5aa9`로 검증
7. local image HIGH/CRITICAL vulnerability gate (`ignore-unfixed=false`, `exit-code=1`)

3번에서 authorization-open lifecycle은 정상 상태이지만 root handoff 문서는 준비 commit 기준 closed 상태이므로, closed 전용 smoke를 그대로 다시 실행하면 오탐 실패합니다. workflow는 정적 checker를 `python tools/check_github_actions_ghcr_static_plan.py --strict`로 먼저 직접 실행하고, 이어서 `SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh`를 실행합니다. `tools/run_smoke_core.sh`는 이 플래그일 때 아래 세 개만 건너뜁니다.

- `tools/smoke/backend/smoke_github_actions_ghcr_static_plan.py`
- `tools/smoke/backend/smoke_codex_handoff_readiness.py`
- `tools/smoke/game/smoke_next_chat_handoff.py`

이 세 smoke는 모두 closed root/handoff 상태를 검증하는 용도입니다. application, backend, game의 나머지 core smoke는 전부 계속 실행하므로 보안·기능 검증 범위를 줄이는 우회가 아닙니다.

게시 단계:

1. publish job 첫 단계에서 같은 direct-parent/lifecycle gate를 다시 확인
2. ephemeral `GITHUB_TOKEN`으로 GHCR login
3. `linux/amd64` image push와 BuildKit `provenance: mode=max`, `sbom: true`
4. exact `sha256:` digest 기록
5. registry exact digest의 provenance와 SPDX SBOM 확인
6. exact digest HIGH/CRITICAL Trivy 재검사
7. 모든 image gate 통과 후 Cosign keyless OIDC sign
8. 고정 workflow identity와 GitHub OIDC issuer로 signature verify
9. 모든 검사가 끝난 digest만 verified candidate로 summary에 출력

production reference 자동 갱신과 deploy는 하지 않습니다.

## artifact와 post-push 실패 증거

- `DOCKER_BUILD_RECORD_UPLOAD="false"`로 `docker/build-push-action`의 자동 build record artifact를 끕니다.
- 계획한 SBOM/Trivy artifact만 14일 보존합니다.
- publish step에서 digest가 만들어졌다면 후속 실패 시에도 `if: always()` evidence upload를 실행합니다.
- 존재하는 파일만 부분 증거가 될 수 있으며 digest, provenance, SBOM, Trivy, Cosign 결과 중 실패 지점 뒤의 파일은 없을 수 있습니다.
- partial evidence artifact가 있다고 성공으로 처리하지 않습니다. Cosign 검증까지 끝나고 final summary가 나온 경우만 verified candidate입니다.

## dependency/frontend 입력 잠금

- CPython 3.11 Linux/amd64 application/build dependency: exact version + 선택 wheel SHA-256, binary-only
- pip `26.1.2`
- setuptools `80.10.2`
- wheel `0.46.3`
- Dockerfile frontend: `docker/dockerfile:1.21.0@sha256:27f9262d43452075f3c410287a2c43f5ef1bf7ec2bb06e8c9eeb1b8d453087bc`

이 잠금은 알려진 dependency/frontend 입력을 고정하지만 timestamp, builder 구현 등 모든 원인을 없애 byte-for-byte 같은 image를 보장한다고 주장하지 않습니다. 실제 결과는 exact digest와 SBOM/Trivy/provenance/Cosign으로 확인합니다.

## secret 및 build context

- GHCR login password 경로는 `${{ secrets.GITHUB_TOKEN }}` 하나만 허용합니다.
- 실제 secret 값을 파일, Git, 로그, 채팅, artifact에 넣지 않습니다.
- root `.dockerignore`는 `.env`, `.env.*`, `**/.env`, `**/.env.*`, `*.env`, `*.env.*`, `.envrc`, `**/.envrc`를 모두 제외합니다.
- env 파일 broad re-include와 `backend/Dockerfile.production.dockerignore`를 금지합니다.

## 현재와 다음 단계

현재 lifecycle은 `attempt-recorded`이고 gate는 `false`입니다. 두 번째 workflow는 로컬 image build에서 실패했고 login/push는 미실행입니다. evidence 검토와 Dockerfile focused fix 승인 전에는 새 preparation이나 workflow dispatch를 하지 않습니다.

```txt
result: github-actions-ghcr-owner-only-attempt-recorded-publish-gated
next safe stage: review-recorded-workflow-attempt-evidence
```

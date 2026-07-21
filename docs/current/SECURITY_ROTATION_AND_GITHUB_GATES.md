# Security rotation and GitHub gates — v325

이 문서는 기호가 허용한 GitHub·숨김 파일·`.env` 작업 범위와 나중에 재확인하거나 교체할 보안 항목을 기록합니다. 실제 secret 값은 적지 않습니다.

## 계속 적용하는 권한과 제한

- Codex는 VS Code/Codex 터미널과 정상 개발 서버를 재사용할 수 있습니다.
- repository Actions, workflow, action SHA, environment, variables와 필요한 설정을 작업 범위 안에서 구성할 수 있습니다.
- 숨김 파일과 `.env`를 점검·수정할 수 있지만 actual secret/token/PAT/credential/CA/cert/key를 Git·채팅·로그·artifact에 노출하지 않습니다.
- root Docker context의 env 계열을 `.dockerignore`로 제외하고, 우선순위를 덮을 수 있는 `backend/Dockerfile.production.dockerignore`를 만들지 않습니다.
- 사용자 계정 선택, 재로그인, 결제/플랜처럼 Codex가 대신할 수 없는 작업만 기호에게 요청합니다.

## 2026-07-22 live GitHub 보호 상태

```txt
Actions allowlist: gihohoho + 명시한 외부 action 8개
full-length action SHA required: yes
GitHub-owned action blanket: off
verified creator blanket: off
default GITHUB_TOKEN: contents/packages read-only
Actions PR create/approve: off
fork write token: off
fork secrets: off
environment: ghcr-production-publish
deployment branch: main only
environment secrets/variables: 0/0
native required reviewer: unavailable/not configured
prevent self-review: unavailable/not configured
live evidence UTC: 2026-07-21T23:34:53Z
```

재확인 중 fork workflow에 write token과 secret을 보내는 설정이 켜진 drift를 발견했고 둘 다 `false`로 복원했습니다. 이는 secret 값을 읽거나 새로 만든 작업이 아니라 repository 정책을 다시 닫은 작업입니다.

private personal repository에서는 native required reviewer를 구성하지 못하므로 `owner-only-source-controlled-two-step`은 독립 reviewer와 동등하지 않습니다. 기호가 이 잔여 위험을 알고 2026-07-20에 선택했습니다.

## v321 승인과 재승인이 필요한 이유

기호는 `f4788acf5455b07169320bd29f43ddf92ff1d5ad`를 정확히 승인했습니다. 이 사람의 별도 확인은 owner-only 2단계 모델에 꼭 필요했습니다. 하지만 실행 전에 아래 결함이 발견되어 workflow/checker 계약을 고쳤습니다.

- open gate를 checker가 합법 상태로 처리하지 못함
- rerun 및 duplicate dispatch 방어 없음
- authorization commit의 direct-parent/link 및 lifecycle-only diff 강제 없음
- 계획 밖 Docker build record artifact 가능
- push 뒤 실패 시 digest/부분 증거 미보존

따라서 과거 SHA는 `priorApprovedPreparationSha`로만 남기며 v322 preparation-fix commit에는 새 명시 승인이 필요합니다. 기존 승인을 자동 확장하지 않습니다.

## 현재 source-controlled gate

```txt
file: deploy/github-actions-ghcr-publish-lifecycle.json
state: attempt-recorded
publishReviewerGateReady: false
priorApprovedPreparationSha: 350bbd085f1cf636810d75ddcbb5321e0791256c
priorAttemptEvidence.recordCommitSha: 1f12ea59eb54385337557e9754f86731ec53d253
approvedPreparationSha: 2f77ebf0f60a39c936509df26f903995f0c62967
ownerApproval.recorded: true
authorization/closure: 7e69555b8b653c406b322fb5c8f23e550751d72c / 5479e6b14826b3a0f2b6d0c3beb0e2142ca22c94
workflow run: prior 29716038891 completed/failure; current 29877813770 completed/failure
```

첫 실행은 dependency 설치에서 실패해 build와 publish jobs가 skipped됐습니다. GHCR login/build/push, artifact, digest, signature는 발생하지 않았으며 동일 실행의 rerun은 금지합니다. 로컬 `gh` keyring의 `konghjin`, `gihohoho` 토큰은 2026-07-20 확인 시 만료 상태였지만 연결된 GitHub 앱으로 로그를 안전하게 조회해 이번 작업에는 재로그인이 필요하지 않았습니다. 향후 `gh` 전용 작업이 꼭 필요할 때만 기호에게 `gh auth login`을 요청합니다.

두 번째 run `29877813770`은 validation을 통과한 뒤 `backend/Dockerfile.production`의 남은 bootstrap `--python-version 3` 때문에 로컬 image build에서 실패했습니다. publish job은 skipped됐고 GHCR login/push, digest, signature, registry mutation은 없었습니다. artifact도 0개였으며 같은 run의 rerun은 금지합니다.

새 SHA 승인 뒤에도 다음 조건이 모두 맞아야 authorization을 열 수 있습니다.

- authorization commit은 승인 SHA의 direct child
- 바뀐 경로는 lifecycle JSON 한 파일뿐
- repository owner가 실행
- live GitHub 설정 증거는 실행 기준 4시간 이내
- authorization은 설정 값은 바꾸지 않고 실제 재확인 뒤 `recheckedAtUtc`만 preparation보다 새로운 시각으로 갱신
- `run_attempt=1`; rerun 금지
- API에서 같은 authorization SHA의 single dispatch 확인
- run 접수 직후 결과와 무관하게 immediate closure commit으로 `authorization-closed-awaiting-evidence` 전이; C commit은 `closureCommitSha=null`
- run 종료 후 별도 evidence commit으로 `attempt-recorded` 전이, 부모 C commit SHA를 `closureCommitSha`에 넣고 run ID/URL/conclusion/digest/signature 실제 결과 기록; 다음 `review-recorded-workflow-attempt-evidence`
- non-success conclusion만으로 `registryMutationExecuted=false`나 `signatureVerified=false`를 기록하지 않고 각 job/step, digest, artifact 확인

gate 검사는 publish job의 GHCR login보다 먼저 다시 수행됩니다.

## artifact와 실패 증거 정책

- `DOCKER_BUILD_RECORD_UPLOAD=false`로 Docker build record 자동 artifact를 끕니다.
- 계획한 SBOM/Trivy/evidence artifact만 14일 보존합니다.
- image digest가 생성된 뒤 후속 단계에서 실패하면 존재하는 digest/provenance/SBOM/Trivy/Cosign 파일을 부분 증거로 업로드합니다.
- 부분 증거에는 secret이나 raw environment가 들어가면 안 됩니다.
- partial evidence는 성공 또는 배포 승인 증거가 아닙니다. 모든 gate와 Cosign verify가 끝난 exact digest만 verified candidate입니다.

authorization-open CI는 closed root 전용 handoff smoke가 lifecycle 전이를 오류로 판단하지 않도록 정적 checker를 직접 먼저 실행한 뒤 `SKIP_GHCR_HANDOFF_SMOKES=1`로 그 세 smoke만 제외합니다. 앱·백엔드 전체 core smoke는 계속 실행되므로 이 플래그를 일반 검증 생략 용도로 사용하지 않습니다.

## 사용자에게 지금 필요한 작업

현재 필요한 설치, extension, 추가 GitHub 권한은 없습니다. 다음 단계에는 Dockerfile bootstrap target 한 곳을 `3.11`로 바꾸는 focused fix에 대한 기호의 승인이 필요합니다. 수정·검증·push 뒤에는 새 정확한 preparation SHA를 다시 별도 승인받아야 합니다.

## 나중에 회전·폐기·재설정할 항목

이번 v325 작업에서는 실제 secret, PAT, registry credential, production `.env`, CA/cert/key를 생성하거나 읽지 않았으므로 즉시 회전할 값은 없습니다.

- [ ] owner-only 모델의 잔여 위험과 계정/environment 보호를 주기적으로 재검토
- [ ] authorization 직전 Actions allowlist/full SHA와 environment main-only를 live 재확인
- [ ] fork write token/secret 설정이 다시 켜지지 않았는지 확인
- [ ] 새 preparation-fix SHA를 기호가 별도 메시지로 승인했는지 확인
- [ ] authorization commit이 승인 SHA의 direct child이며 lifecycle 파일만 바꿨는지 확인
- [ ] 같은 authorization SHA의 중복 dispatch나 rerun이 없는지 확인
- [ ] run 접수 직후 immediate closure commit이 push됐는지 확인
- [ ] 실패 run의 partial evidence에 secret/raw environment가 없는지 확인
- [ ] GHCR package visibility와 접근 주체 재검토
- [ ] production 배포 때 생성될 JWT/Admin/DB credential 회전 주기 기록
- [ ] managed PostgreSQL credential/provider CA 교체 절차 확인
- [ ] reverse proxy TLS key/certificate 갱신 절차 확인
- [ ] 더 이상 필요 없는 PAT/token/credential 즉시 폐기

## 로컬 GitHub CLI 상태

브라우저 기반 GitHub 연결은 정상입니다. 로컬 `gh` CLI에 저장된 예전 token은 이번 확인에서도 만료 상태였으므로 필요 시에만 기호에게 재인증을 요청합니다. 현재 v325 evidence 검토 단계에는 새 로그인이나 설치가 필요 없습니다.

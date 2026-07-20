# Current Status — v322

## 현재 기준

- 최신 작업: `v322.owner-only-single-run-lifecycle-hardened-publish-gated`
- strict result: `github-actions-ghcr-owner-only-single-run-lifecycle-ready-publish-gated`
- next safe stage: `review-and-approve-exact-preparation-fix-sha`
- workflow source/semantic SHA-256: `8b3bde807cb241e14104272a13f1e4c5a857753716e5a2a7e13b710df55ae61e` / `f91419160e34e1ea5c16342b8d346e9b295d502131980eeb084b2da9aa2683fa`
- handoff: current repository + Git `main`; ZIP 기본 생성 없음
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`
- 개발 서버: 마지막 확인 기준 중지 상태; 이번 정적 변경에는 서버 재시작 불필요
- 새 설치/extension/추가 권한: 현재 없음

## 고정 PostgreSQL/Alembic 상태

```txt
classification: alembic-managed-baseline-complete
source DB: rpg_game
source public tables/rows: 23/749
source application tables/rows: 22/748
current revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
next revision required: no
```

## 운영 방향

```txt
managed PostgreSQL + provider CA verify-full
external reverse proxy HTTPS
backend replicas/workers: 1/1
max_connections review candidate: 40
Compose config render: 기호 PC 통과
```

## GitHub Actions / GHCR

```txt
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
namespace: gihohoho
repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility: private
target platform: linux/amd64
base image digest approved: yes
CI credential strategy: github-actions-github-token
local credential strategy: deferred
workflow file/creation approved: yes/yes
workflow execution approved/executed: yes/no
CI workflow/login/build/push approved: yes/yes/yes/yes
CI login/build/push executed: no/no/no
repository Actions allowlist/full SHA: configured/configured
publish environment/main-only: present/configured
environment secrets/variables: 0/0
required reviewer/prevent self-review: missing/missing
publish approval model: owner-only-source-controlled-two-step
source-controlled lifecycle gate: preparation-closed / publishReviewerGateReady=false
dependency/frontend input lock: complete
run_attempt=1: required
single dispatch: required by Actions API
immediate closure: required after run acceptance
exact preparation-fix SHA approval: pending
```

아직 workflow run, GHCR login, image build, push, sign은 한 번도 실행하지 않았습니다. production image reference와 자동 deploy도 바꾸지 않았습니다.

## v321 승인 이후 발견한 감사 문제

기호는 `f4788acf5455b07169320bd29f43ddf92ff1d5ad`를 정확히 승인했습니다. 이 승인은 역사적 prior approval로 유효하게 기록하지만, 실행 전 추가 감사에서 아래 결함을 찾아 새 v322 preparation-fix SHA 승인이 필요합니다.

1. checker가 gate `true` authorization 상태를 허용하지 않아 합법적인 실행 준비 commit이 CI에서 실패할 수 있었습니다.
2. `run_attempt=1`, 동일 SHA rerun 금지, API 기반 single dispatch 방어가 없었습니다.
3. authorization commit의 direct-parent 승인 SHA 연결과 변경 경로 제한이 없었습니다.
4. Docker build record가 정적 계획에 없는 artifact를 만들 수 있었습니다.
5. image push 뒤 실패할 경우 digest와 부분 증거를 남기지 못했습니다.

`f4788acf...` 이후 workflow와 checker가 보안상 중요한 범위로 바뀌므로 과거 승인을 새 commit에 자동 이전하지 않습니다.

## v322 lifecycle 결과

- 새 파일: `deploy/github-actions-ghcr-publish-lifecycle.json`
- 현재 lifecycle: `preparation-closed`
- 현재 gate: `publishReviewerGateReady=false`
- 과거 승인: `priorApprovedPreparationSha=f4788acf5455b07169320bd29f43ddf92ff1d5ad`
- 새 승인 대상: 아직 commit 전이므로 `approvedPreparationSha=null`
- authorization commit: 새 승인 SHA의 direct child, lifecycle 파일 하나만 변경
- 실행자: repository owner만 허용
- rerun: `run_attempt=1`이 아니면 차단
- 중복 실행: GitHub Actions API로 같은 authorization SHA의 single dispatch만 허용
- closure: run ID가 접수되면 결과를 기다리기 전에 immediate closure commit으로 gate를 닫고 `authorization-closed-awaiting-evidence`로 전이; C commit의 `closureCommitSha=null`
- evidence: run 종료 뒤 별도 `attempt-recorded` commit에서 부모 C commit SHA를 `closureCommitSha`에 넣고 run ID/URL/status/conclusion/digest/signature 실제 결과 기록; next `review-recorded-workflow-attempt-evidence`
- non-success conclusion: `registryMutationExecuted=false`나 `signatureVerified=false`와 동의어가 아님; 각 job/step, digest, artifact로 실제 결과 확인
- Docker build record: `DOCKER_BUILD_RECORD_UPLOAD=false`
- post-push failure: digest가 생겼으면 존재하는 partial evidence artifact를 14일 보존; 검증 완료 후보로 표기 금지
- authorization-open CI smoke: 정적 checker를 직접 먼저 실행하고 `SKIP_GHCR_HANDOFF_SMOKES=1`로 closed 전용 handoff smoke 세 개만 제외; 앱·백엔드 전체 smoke는 유지

## 2026-07-20 GitHub live 설정

- 외부 action allowlist 8개와 full-length SHA 강제 확인
- GitHub-owned/verified creator blanket allow 꺼짐 확인
- 기본 `GITHUB_TOKEN` contents/packages read-only, PR create/approve 꺼짐 확인
- 점검 중 발견한 fork write token 및 fork secret 전달 drift를 둘 다 `false`로 복원
- `ghcr-production-publish` 존재, `main` only, secrets/variables 0/0 확인
- native required reviewer/prevent self-review는 비공개 개인 저장소 제약으로 계속 없음
- 기록 시각: `2026-07-20T03:04:15Z`; authorization 시점에 4시간 이내 live 재확인 필요

## 공급망 잠금

- Python application/build dependency: CPython 3.11 Linux/amd64 exact versions + 선택 wheel SHA-256, binary-only
- pip `26.1.2`, setuptools `80.10.2`, wheel `0.46.3`
- Dockerfile frontend: exact digest
- action: 검토한 외부 action 8개 전체 40자리 SHA
- Trivy: 공식 `0.70.0` Linux asset checksum 검증
- local OCI/SBOM/Trivy → pushed digest provenance/SBOM/Trivy → Cosign keyless sign/verify 순서
- byte-for-byte 동일 image를 보장한다고 주장하지 않음

## 현재 안전 경계

현재 lifecycle은 P `preparation-closed`로 닫혀 있어 registry 접근 전 fail-closed입니다. 이후 지원 전이는 A `authorization-open` → C `authorization-closed-awaiting-evidence` → R `attempt-recorded`입니다. v322 준비 수정 commit을 검증·push한 뒤 기호가 그 새 정확한 40자 SHA를 별도 메시지로 승인해야 합니다. 이전 `f4788acf...` 승인을 재사용하지 않습니다. 새 승인 전에는 authorization을 열거나 workflow를 실행하지 않습니다.

DB/Alembic mutation, 인증·write API, Vue Preview/Apply/write, 게임 콘텐츠·밸런스, production container/network/volume, Compose up/down, production reference 갱신과 자동 deploy는 이번 범위 밖입니다.

정상 strict 결과:

```txt
result: github-actions-ghcr-owner-only-single-run-lifecycle-ready-publish-gated
next safe stage: review-and-approve-exact-preparation-fix-sha
```

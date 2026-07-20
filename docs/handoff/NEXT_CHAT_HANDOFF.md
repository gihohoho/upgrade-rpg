# Upgrade RPG Codex handoff — v322

## 먼저 읽을 것

1. `AGENTS.md`
2. 이 문서
3. `docs/current/CURRENT_STATUS.md`
4. `docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md`
5. `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`

## 현재 기준

- latest: `v322.owner-only-single-run-lifecycle-hardened-publish-gated`
- strict result: `github-actions-ghcr-owner-only-single-run-lifecycle-ready-publish-gated`
- next safe stage: `review-and-approve-exact-preparation-fix-sha`
- workflow source/semantic SHA-256: `8b3bde807cb241e14104272a13f1e4c5a857753716e5a2a7e13b710df55ae61e` / `f91419160e34e1ea5c16342b8d346e9b295d502131980eeb084b2da9aa2683fa`
- 기준: 현재 repository + Git `main`; ZIP은 기본 생성하지 않음
- 사용자: 코딩을 거의 모르는 기호, 한국어로 쉽고 자세하게 설명
- remote: `https://github.com/gihohoho/upgrade-rpg.git`
- GHCR: `ghcr.io/gihohoho/upgrade-rpg-backend` (private, `linux/amd64`)
- 운영 구조: managed PostgreSQL + provider CA `verify-full` + external reverse proxy HTTPS + backend 1 replica/1 worker
- backend venv: `backend/.venv`
- Alembic current revision: `v295_initial_schema`; 새 revision 필요 `no`
- Vue: GET read-only 범위까지만, Preview/Apply/write/인증 금지
- 게임 콘텐츠/밸런스: 보류
- 현재 서버: 마지막 확인 기준 backend/frontend 모두 중지 상태; 이번 정적 작업에는 재시작 불필요
- 새 설치/extension/추가 권한 요청: 현재 없음

## 계속 적용할 작업 방식

- 모든 터미널 명령 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적습니다.
- 정상 개발 서버는 재사용하고 설정상 필요한 경우에만 재시작합니다.
- GitHub Actions/workflow/action SHA/environment/variables/repository 설정은 작업 범위 안에서 Codex가 처리할 수 있습니다.
- 숨김 파일과 `.env` 점검·수정 권한이 있지만 실제 secret/token/PAT/credential/CA/cert/key를 Git·채팅·로그·artifact에 노출하지 않습니다.
- root `.dockerignore`에서 `.env`/`*.env`/`.envrc` 계열을 제외하고 `backend/Dockerfile.production.dockerignore`를 만들지 않습니다.
- 변경·검증 후 Codex가 직접 status/add/commit/push합니다. 사용자에게 Git 명령을 주지 않고 ZIP도 만들지 않습니다.
- 매 작업에서 root NEXT_CHAT 두 파일과 `docs/handoff/` mirror를 바이트 단위로 같게 갱신합니다.

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

DB write/restore/reset/seed와 Alembic revision/autogenerate/stamp/upgrade/downgrade는 이번 범위가 아닙니다.

## GitHub/GHCR 승인과 실행 상태

```txt
workflow file/creation approved: yes/yes
workflow execution approved/executed: yes/no
CI workflow/login/build/push approved: yes/yes/yes/yes
CI login/build/push executed: no/no/no
CI credential strategy: github-actions-github-token
local credential/PAT: deferred
repository Actions allowlist/full SHA: configured/configured
publish environment/main-only: present/configured
environment secrets/variables: 0/0
required reviewer/prevent self-review: missing/missing
publish approval model: owner-only-source-controlled-two-step
source-controlled lifecycle gate: preparation-closed / publishReviewerGateReady=false
run_attempt=1: required
single dispatch: required
immediate closure: required
exact preparation-fix SHA approval: pending
```

native required reviewer가 없는 비공개 개인 저장소이므로 이 owner-only 절차는 독립 reviewer와 동등하지 않습니다. 기호가 이 잔여 위험을 이해하고 2026-07-20에 선택했습니다.

## v321 정확한 SHA 승인과 v322 재감사

기호는 다음 준비 commit을 정확히 승인했습니다.

```txt
f4788acf5455b07169320bd29f43ddf92ff1d5ad
```

이 승인은 실제로 필요한 인간 확인이었습니다. Codex가 준비와 승인을 모두 대신하면 선택한 owner-only 2단계가 사실상 한 단계가 되기 때문입니다. 다만 승인 직후, 아직 workflow를 실행하기 전에 방어 구조를 다시 감사했고 다음 결함을 찾았습니다.

1. v321 checker는 workflow gate가 항상 `false`이길 요구해 합법적인 authorization-open commit도 CI에서 실패시켰습니다.
2. 동일 authorization SHA의 rerun과 중복 dispatch를 막지 못했습니다.
3. authorization commit이 승인 preparation의 직접 자식인지, 승인용 변경이 한 파일뿐인지 강제하지 않았습니다.
4. `docker/build-push-action`의 자동 build record가 계획에 없는 artifact를 만들 수 있었습니다.
5. image push 뒤 provenance/SBOM/Trivy/Cosign에서 실패하면 이미 push된 digest의 부분 증거를 보존하지 못했습니다.

따라서 `f4788acf...`는 lifecycle의 `priorApprovedPreparationSha`에 역사적 prior approval로만 남깁니다. v322 workflow/checker/lifecycle 수정이 포함된 새 preparation-fix commit은 범위가 달라졌으므로 그 새 40자 SHA를 다시 승인받아야 합니다. 기존 승인을 새 SHA에 재사용하지 않습니다.

## v322 lifecycle 안전 계약

새 source-controlled lifecycle gate는 `deploy/github-actions-ghcr-publish-lifecycle.json`입니다. 현재 값은 다음처럼 닫혀 있습니다.

```txt
schemaVersion: v322.owner-only-publish-lifecycle
state: preparation-closed
publishReviewerGateReady: false
approvedPreparationSha: null
ownerApproval.recorded: false
observedAttempt.status: not-dispatched
```

새 preparation-fix SHA가 승인된 뒤의 authorization contract:

1. authorization commit은 승인된 preparation-fix commit의 **직접 자식**이어야 합니다.
2. 변경 경로는 lifecycle JSON **한 파일만** 허용합니다.
3. lifecycle을 `authorization-open`, gate `true`, 승인 preparation SHA, owner 승인 시각으로 전이합니다.
4. 실행자는 repository owner여야 하고 `github.sha == source_commit`이어야 합니다.
5. workflow는 `run_attempt=1`만 허용하며 rerun은 항상 실패합니다.
6. `actions: read` 권한과 GitHub Actions API로 같은 authorization SHA의 single dispatch만 존재하는지 확인합니다.
7. run ID가 생성되어 GitHub에 접수되면 결과를 기다리며 gate를 열어 두지 않고 별도 immediate closure commit을 즉시 push해 `authorization-closed-awaiting-evidence`로 전이합니다. 이 C commit에서는 자기 SHA를 쓸 수 없어 `closureCommitSha=null`입니다.
8. closure는 실행 성공·실패·취소와 관계없이 필요합니다.
9. run 종료 뒤 별도 evidence commit에서 부모 C commit의 정확한 SHA를 `closureCommitSha`에 기록하고 `attempt-recorded`로 전이합니다. run ID/URL/attempt/status/conclusion과 실제 image digest/signature 결과를 함께 기록하며 next stage는 `review-recorded-workflow-attempt-evidence`입니다.
10. `failure`, `cancelled`, `timed_out` 등 성공이 아닌 conclusion도 image push나 signature verify 뒤에 발생할 수 있습니다. 전체 conclusion만으로 `registryMutationExecuted=false` 또는 `signatureVerified=false`라고 판단하지 않고 각 job/step, digest, artifact 증거를 따로 확인합니다.

authorization commit이 workflow 자체나 application/dependency를 바꾸면 ancestry/path 검사가 실패합니다. run 접수 전에 main이 이동하거나 같은 SHA로 두 번째 dispatch가 있으면 실패합니다.

## 2026-07-20 GitHub live 재확인

로그인된 GitHub 화면에서 다음을 재확인했습니다.

- 허용 정책: `gihohoho` 소유 action + 명시한 외부 action 8개
- 외부 action: 모두 전체 40자리 SHA
- full-length action SHA 강제: 켜짐
- GitHub-owned action blanket 및 verified creator blanket: 꺼짐
- 기본 `GITHUB_TOKEN`: contents/packages read-only
- Actions의 PR 생성·승인: 꺼짐
- 점검 중 drift로 켜져 있던 fork write token과 fork secret 전달: 둘 다 `false`로 복원
- `ghcr-production-publish`: 존재, deployment branch `main` only
- environment secrets/variables: 0/0
- native required reviewer/prevent self-review: 계속 없음

lifecycle에 저장된 live recheck는 `2026-07-20T03:04:15Z`입니다. workflow는 authorization 시점 기준 4시간이 넘은 증거를 거부하므로 실제 gate 전환 직전에 다시 확인하고 시각을 갱신해야 합니다.

## workflow 방어와 증거

- trigger는 `workflow_dispatch`만 허용합니다.
- 입력은 `source_commit`, `approved_preparation_commit`, `approval_reason`, `confirm_publish=true`입니다.
- validate job만 `actions: read`, `contents: read`; publish job만 `packages: write`, `id-token: write`입니다.
- action 8개는 repository allowlist와 workflow 모두 검토한 full SHA로 고정합니다.
- Python 3.11 Linux/amd64 dependency, pip `26.1.2`, setuptools `80.10.2`, wheel `0.46.3`, Dockerfile frontend digest가 exact version/SHA-256으로 잠겼습니다.
- byte-for-byte 동일 image를 보장한다고 주장하지 않습니다. 실제 결과는 digest, SBOM, Trivy, provenance, Cosign으로 검증합니다.
- `DOCKER_BUILD_RECORD_UPLOAD="false"`로 Docker build record 자동 artifact를 비활성화합니다.
- local OCI build → SPDX SBOM → checksum-pinned Trivy HIGH/CRITICAL gate가 먼저 통과해야 publish job으로 갑니다.
- push된 exact digest에서 provenance/SBOM과 Trivy를 다시 검사한 뒤 Cosign keyless sign/verify를 수행합니다.
- digest가 생성된 뒤 후속 단계가 실패해도 `if: always()` artifact가 존재하는 부분 증거를 14일 보존합니다. partial evidence는 검증 완료 후보가 아닙니다.
- production reference 갱신이나 자동 deploy는 하지 않습니다.
- authorization-open CI에서는 `python tools/check_github_actions_ghcr_static_plan.py --strict`를 먼저 직접 실행한 뒤 `SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh`를 실행합니다. 이 플래그는 closed root를 전제로 하는 `smoke_github_actions_ghcr_static_plan.py`, `smoke_codex_handoff_readiness.py`, `smoke_next_chat_handoff.py`만 제외합니다. application/backend를 포함한 나머지 전체 core smoke는 그대로 실행되므로 검증 범위를 축소하지 않습니다.

## 현재 변경 핵심 파일

- `.github/workflows/publish-backend-ghcr.yml`
- `deploy/github-actions-ghcr-publish-lifecycle.json`
- `deploy/github-actions-ghcr-static-plan.example.json`
- `deploy/github-actions-ghcr-backend-policy.example.json`
- `tools/check_github_actions_ghcr_static_plan.py`
- `tools/smoke_github_actions_ghcr_static_plan.py`
- `tools/check_codex_handoff_readiness.py`
- root/handoff/current 문서

## 첫 검증

실행 위치: `backend` 폴더
Python `.venv` 상태: 꺼져 있을 때
새 설치: 없음

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트
Python `.venv` 상태: `backend/.venv`가 켜진 상태
새 설치: 없음

```bash
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

정상 기대 결과:

```txt
result: github-actions-ghcr-owner-only-single-run-lifecycle-ready-publish-gated
next safe stage: review-and-approve-exact-preparation-fix-sha
```

코드/구조 변경이므로 관련 전용 smoke, compileall, JavaScript 문법, `bash tools/run_smoke_core.sh`까지 통과해야 합니다. 단, authorization-open CI에서는 위의 closed 전용 세 smoke만 플래그로 건너뜁니다. Vue 변경이 없으므로 `npm ci`/`npm run build`는 불필요합니다.

## 다음 안전 단계

1. v322 변경 전체 검증
2. 준비 수정 commit을 `main`에 commit/push
3. 새 exact 40-character preparation-fix SHA와 변경 범위를 기호에게 제시
4. 기호의 새 SHA 명시 승인 대기
5. 승인 후 GitHub live 설정을 다시 확인
6. lifecycle JSON만 바꾸는 direct-child authorization commit을 만들고 검증·push
7. 정확히 한 번 dispatch하고 run ID 접수 즉시 closure commit으로 gate 닫기
8. run 결과를 모니터링하고 성공/실패 및 부분 증거를 `attempt-recorded` evidence commit으로 기록

현재는 4번 전 단계입니다. 새 SHA 승인 없이 lifecycle을 열거나 workflow를 실행하지 않습니다.

## 계속 금지되는 범위

- DB 생성·삭제·복원·reset·seed·write
- Alembic revision/autogenerate/stamp/upgrade/downgrade
- 인증/API route/response body/write logic/Write Guard
- Vue Preview/Apply/write
- 게임 콘텐츠/장비/스킬/보스/드랍률/밸런스
- production container/network/volume, Compose up/down
- production image reference 자동 갱신 또는 자동 deploy

## 완료 답변 기준

- 한 일과 검증 결과
- 서버 재시작 필요 여부 (`이번 단계는 서버 재시작 불필요`)
- commit/push 결과
- 다음 추천 단계
- 필요한 extension/권한/설치 (`현재 없음`이면 명시)

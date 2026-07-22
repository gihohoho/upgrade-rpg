# Upgrade RPG Codex working rules — v327

이 파일은 저장소 전체에 적용됩니다. Codex는 작업을 시작할 때 이 파일과 `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽습니다.

## 사용자와 설명 방식

- 사용자는 코딩을 거의 모르는 **기호**입니다. 항상 쉽고 자세한 한국어로 설명합니다.
- 터미널 명령 바로 위에 **실행 위치**, **Python `.venv` 상태**, **새 설치 여부**를 반드시 적습니다.
- backend 가상환경은 프로젝트 루트가 아니라 `backend/.venv`입니다. Git Bash에서 `backend` 폴더에서 `source .venv/Scripts/activate`로 켭니다.
- Vue/npm 명령은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.
- 필요한 extension, GitHub/repository/app 권한, 로컬 설치가 있으면 기호에게 요청합니다. 해결되지 않으면 다음 작업에서도 다시 요청하고 `NEXT_CHAT_PROMPT.md`, `NEXT_CHAT_HANDOFF.md`에 계속 기록합니다.
- 매 작업에서 root `NEXT_CHAT_PROMPT.md`, `NEXT_CHAT_HANDOFF.md`와 `docs/handoff/` mirror를 최신 상태로 갱신합니다.
- 변경과 검증이 끝나면 Codex가 프로젝트 루트에서 `git status`, `git add .`, `git commit`, `git push`를 직접 실행합니다. 기호에게 Git 한 줄 명령을 다시 제공하지 않습니다.
- Codex 작업에서는 ZIP을 만들거나 제공하지 않습니다. 기호가 별도로 요청한 경우에만 secret·가상환경·node_modules 등을 제외해 만듭니다.

## 개발 서버와 터미널의 계속 적용 권한

- Codex는 VS Code/Codex 터미널을 자유롭게 사용하고 실행 중인 개발 서버를 재사용할 수 있습니다.
- 백엔드 `127.0.0.1:8000`과 프론트엔드 `127.0.0.1:5173`이 정상이라면 작업마다 종료·재시작하지 않습니다.
- 소스 변경은 Uvicorn `--reload`와 Vite HMR에 맡기고, 프로세스가 죽었거나 설정 변경 때문에 필요한 경우에만 재시작합니다.
- 서버를 재시작하지 않은 작업은 완료 답변에 “서버 재시작 불필요”라고 명확히 적습니다.

## GitHub와 보안 파일의 계속 적용 권한

- 기호는 repository의 Actions, workflow, action SHA, environment, variables와 필요한 GitHub 설정을 Codex가 작업 목적 안에서 구성하도록 허용했습니다.
- 숨김 파일과 `.env`도 필요한 경우 Codex가 점검·수정할 수 있습니다.
- 이 권한은 실제 secret 값을 Git, 채팅, 로그, artifact에 노출하거나 커밋하는 권한이 아닙니다. secret은 최소 노출 원칙으로 처리하고 `.gitignore`와 Git index를 계속 검사합니다.
- root Docker build context의 `.dockerignore`는 `.env`/`*.env`/`.envrc` 계열을 모두 제외하며 env 파일 재포함 규칙을 허용하지 않습니다.
- `backend/Dockerfile.production.dockerignore`는 root `.dockerignore`를 우선 덮어쓸 수 있으므로 생성하지 않습니다.
- 나중에 회전·폐기·재설정할 보안 항목은 `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`에 누적합니다.
- 사용자 계정 선택, 추가 로그인, 결제/플랜 변경처럼 Codex가 정책상 또는 기술상 대신할 수 없는 일만 기호에게 요청합니다.

## 현재 고정 상태

- latest: `v327.third-owner-only-attempt-recorded-vulnerability-gated`
- strict result: `github-actions-ghcr-owner-only-attempt-recorded-publish-gated`
- next safe stage: `review-recorded-vulnerability-gate-evidence`
- GitHub remote: `https://github.com/gihohoho/upgrade-rpg.git`
- GHCR namespace: `gihohoho`
- backend image repository: `ghcr.io/gihohoho/upgrade-rpg-backend` (private)
- target: `linux/amd64`
- 운영 구조: managed PostgreSQL + provider CA `verify-full` + external reverse proxy HTTPS + backend 1 replica/1 worker
- Vue는 GET read-only까지만 연결하며 Preview/Apply/write/인증은 연결하지 않습니다.
- 게임 콘텐츠와 밸런스 개발은 계속 보류합니다.
- Alembic current revision은 `v295_initial_schema`; 새 revision 필요 상태는 `no`입니다.
- CI credential strategy: GitHub Actions `GITHUB_TOKEN` 우선 (`github-actions-github-token`)
- workflow file/creation approved: yes/yes
- workflow execution approved/executed: yes/yes
- CI workflow/login/build/push approved: yes/yes/yes/yes
- CI login/build/push executed: no/yes/no (build attempted and failed)
- repository Actions allowlist/full SHA enforcement: configured/configured
- `ghcr-production-publish` environment/main-only: present/configured
- required reviewer/prevent self-review: missing/missing
- publish approval model: `owner-only-source-controlled-two-step` (기호가 2026-07-20 선택)
- source-controlled lifecycle gate: `attempt-recorded` / `publishReviewerGateReady=false`
- dependency/frontend input lock: complete (exact version + SHA-256, binary wheel only)
- byte-for-byte deterministic image: 보장한다고 주장하지 않음
- prior preparation SHA: `350bbd085f1cf636810d75ddcbb5321e0791256c` approved and consumed
- bootstrap-fix preparation SHA: `2f77ebf0f60a39c936509df26f903995f0c62967` approved and consumed
- Dockerfile-fix preparation SHA: `b35dfacf427162b348a6bd29eb030778edc7741c` approved and consumed
- workflow run/login/build/push: three failed runs / no / yes / no
- reviewed workflow source/semantic SHA-256: `245630348d384cc1c862014454cb73b6149a8c3a20d7b114763bc6fe655ef4bd` / `e08c3788e88da351112bc381d225e418938f7bd74ccec7eb83f9f59eff6f724c`

## v321 승인과 v322 감사 결과

기호는 `f4788acf5455b07169320bd29f43ddf92ff1d5ad`를 정확히 승인했습니다. 이 승인은 유효한 역사적 prior approval로 보존하지만, 그 뒤 실행 전 감사에서 다음 결함을 발견했으므로 v322 준비 수정 commit의 새 SHA를 다시 승인받아야 합니다.

1. 정적 checker가 authorization의 `true` gate를 허용하지 않아 승인 commit 자체가 CI에서 실패할 수 있었습니다.
2. 같은 authorization commit의 rerun을 막는 `run_attempt=1` 및 API 기반 중복 실행 검사가 없었습니다.
3. authorization commit이 승인된 preparation commit의 직접 자식인지, lifecycle 파일만 바꿨는지 강제하지 않았습니다.
4. Docker build record가 계획하지 않은 artifact로 자동 업로드될 수 있었습니다.
5. push 뒤 provenance·Trivy·Cosign 단계에서 실패할 때 이미 생성된 digest와 부분 증거를 보존하지 못했습니다.

v322는 `deploy/github-actions-ghcr-publish-lifecycle.json`을 source-controlled lifecycle gate로 사용합니다. 지원 상태는 현재 P `preparation-closed`, 승인 A `authorization-open`, 접수 즉시 닫힌 C `authorization-closed-awaiting-evidence`, 실제 결과를 기록한 R `attempt-recorded`입니다. authorization commit은 lifecycle 파일 하나만 변경해야 하고 승인된 새 preparation SHA의 직접 자식이어야 합니다. workflow는 repository owner만, `run_attempt=1`만, API에서 확인된 single dispatch만 허용합니다. run이 GitHub에 접수되면 성공·실패와 관계없이 immediate closure commit으로 C 상태를 먼저 만듭니다. C commit은 자기 SHA를 스스로 기록할 수 없어 `closureCommitSha=null`을 유지하고, 별도 R evidence commit에서 부모 C commit의 정확한 SHA를 `closureCommitSha`에 기록하면서 run ID/URL/conclusion/digest/signature 실제 결과와 다음 단계 `review-recorded-workflow-attempt-evidence`를 확정합니다. workflow rerun은 금지합니다. 전체 failure·취소·시간 초과 conclusion만으로 `registryMutationExecuted=false` 또는 `signatureVerified=false`라고 단정하지 않고 job/step 증거를 각각 확인합니다. Docker build record 자동 artifact는 끄고, digest가 생긴 뒤 실패해도 available partial evidence를 14일 artifact로 보존하되 검증 완료 후보로 간주하지 않습니다.

## 2026-07-22 GitHub live 재확인

- 외부 action allowlist와 full-length SHA 강제: 정상
- GitHub-owned/verified creator blanket allow: 꺼짐
- 기본 `GITHUB_TOKEN`: contents/packages read-only; PR 생성·승인 꺼짐
- 점검 중 켜져 있던 fork write token/secret 전달 drift: 둘 다 `false`로 복원
- `ghcr-production-publish`: 존재, `main` only, secrets/variables 0/0
- native required reviewer/prevent self-review: 비공개 개인 저장소 제약으로 계속 없음

live 증거는 authorization 실행 시점 기준 4시간 이내여야 하므로 새 SHA 승인 후 gate를 열기 직전에 다시 확인합니다.

## 2026-07-20 첫 owner-only 게시 시도 결과

- authorization commit: `32e5102877851ace06e1c0ed3bcb48310b8d65b6`
- immediate closure commit: `362f5f1901d234b5b86f2a7cefdabd28ac61f896`
- GitHub Actions run: `29716038891` / `https://github.com/gihohoho/upgrade-rpg/actions/runs/29716038891`
- 결론: `failure`; `Install backend validation dependencies` 단계에서 종료
- 원인: bootstrap pip wheel 다운로드의 `--python-version 3`이 `pip==26.1.2`의 Python `>=3.10` 조건과 맞지 않아 배포 후보를 찾지 못함
- 미실행: repository checks 이후 단계, Docker build, SBOM/Trivy, GHCR login/push, provenance, Cosign
- artifact/image digest/signature: 0개 / 없음 / 미검증
- rerun: 금지되며 실행하지 않음
- focused fix: 기호가 승인했으며 workflow bootstrap pip download를 `--python-version 3.11`로 수정 완료
- retry preparation: `priorAttemptEvidence.recordCommitSha=1f12ea59eb54385337557e9754f86731ec53d253`로 첫 실패를 보존하고 새 gate는 `false`

## 2026-07-22 두 번째 owner-only 게시 시도 결과

- preparation commit: `2f77ebf0f60a39c936509df26f903995f0c62967`
- authorization commit: `7e69555b8b653c406b322fb5c8f23e550751d72c`
- immediate closure commit: `5479e6b14826b3a0f2b6d0c3beb0e2142ca22c94`
- GitHub Actions run: `29877813770` / `https://github.com/gihohoho/upgrade-rpg/actions/runs/29877813770`
- 결론: `failure`; workflow bootstrap과 repository checks는 통과했지만 `Build local linux/amd64 image without registry mutation`에서 종료
- 원인: `backend/Dockerfile.production`의 bootstrap pip download에 `--python-version 3`이 남아 `pip==26.1.2`를 찾지 못함
- 미실행: SBOM/Trivy, GHCR login/push, provenance, Cosign
- artifact/image digest/signature: 0개 / 없음 / 미검증
- registry mutation: 없음; publish job 전체 `skipped`
- artifact 보존 단계 실패는 build 실패로 `sbom.spdx.json`과 `trivy-results.json`이 생성되지 않은 후속 결과
- rerun: 금지되며 실행하지 않음
- focused fix: 기호가 승인했으며 Dockerfile bootstrap target을 `--python-version 3.11`로 수정 완료
- evidence 보존: `attemptHistory`에 첫 run `29716038891`과 두 번째 run `29877813770`을 모두 보존

## 2026-07-22 세 번째 owner-only 게시 시도 결과

- preparation/authorization/closure/evidence: `b35dfacf427162b348a6bd29eb030778edc7741c` / `04e002060e576f19f4d8687b33635a414486206d` / `64e5ae0f5e5385ba00df16bb10ac33789ca3760a` / `303a2ed01c69c29894efdcde4ead6c2291c3d8bc`
- GitHub Actions run: `29883012957` / `https://github.com/gihohoho/upgrade-rpg/actions/runs/29883012957`, `run_attempt=1`, conclusion `failure`
- validation, repository checks, local linux/amd64 image build, SPDX SBOM 생성은 성공했습니다.
- Trivy HIGH/CRITICAL gate가 27건(Debian 24, Python 3)을 발견해 게시를 차단했습니다. 2건은 Trivy 기준 fixed version이 있고 25건은 아직 없습니다.
- artifact `8515504259`에 `sbom.spdx.json`, `trivy-results.json`을 14일 보존합니다. artifact SHA-256은 `6a5dfd4cd96754fd365323c7c6a7d1edf18542b5e5729e44220d7bf21ace4c50`입니다.
- publish job은 skipped됐으므로 GHCR login/push/provenance/Cosign은 미실행, image digest는 없고 signature는 미검증입니다.
- `--ignore-unfixed=false` 정책은 의도대로 작동했습니다. 다음 단계는 base image/runtime 구성/Python dependency를 검토하는 것이며, 자동으로 gate를 약화하지 않습니다.

## 현재 안전 경계

현재 lifecycle은 `attempt-recorded`이고 gate는 닫혀 있습니다. 세 실행 모두 rerun 금지입니다. 3차 실행은 로컬 이미지를 만들고 SPDX SBOM을 생성한 뒤 Trivy HIGH/CRITICAL gate에서 차단됐으며, publish job 전체가 skipped되어 GHCR login/push/provenance/Cosign은 실행되지 않았습니다. 취약점 정책을 자동 완화하거나 새 workflow를 실행하지 않습니다.

다음 항목은 이번 GitHub 권한 확대와 별개이므로 기호의 구체적인 작업 요청 전에는 변경·실행하지 않습니다.

- DB 생성·삭제·복원·reset·seed·write
- Alembic revision/autogenerate/stamp/upgrade/downgrade
- 인증, API route path/response body, write logic/Write Guard
- Vue Preview/Apply/write 연결
- 게임 콘텐츠/장비/스킬/보스/드랍률/밸런스 변경
- production container/network/volume 생성·삭제, Compose up/down
- production image reference 자동 갱신 또는 자동 deploy

## 현재 다음 단계

프로젝트 루트에서 `backend/.venv`를 켠 상태로 아래 검사를 먼저 실행합니다.

```bash
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

현재 정상 결과는 `github-actions-ghcr-owner-only-attempt-recorded-publish-gated`, 다음 안전 단계는 `review-recorded-vulnerability-gate-evidence`입니다. 다음 preparation과 workflow 실행에는 별도 사용자 승인이 필요합니다.

## 변경과 검증

- 현재 판단 문서는 `docs/current/`를 우선합니다. 과거 단계 기록은 `docs/archive/`와 `deploy/review/`에 있습니다.
- legacy 게임 `index.html`, 관리자 `admin.html`, `src/`는 Vue 이식 전까지 이동하거나 대규모 재작성하지 않습니다.
- 코드나 구조를 바꾸면 관련 전용 smoke, `python -m compileall -q backend/app backend/scripts backend/alembic tools`, JavaScript 문법, `bash tools/run_smoke_core.sh`를 확인합니다.
- authorization-open workflow에서는 정적 checker를 먼저 직접 실행한 뒤 `SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh`를 실행합니다. 이 플래그는 closed root 상태만 전제로 하는 `smoke_github_actions_ghcr_static_plan.py`, `smoke_codex_handoff_readiness.py`, `smoke_next_chat_handoff.py` 세 개만 건너뛰며 앱·백엔드 전체 smoke는 그대로 실행합니다.
- Vue 변경 시에만 `frontend/vue-app`에서 Python `.venv` 없이 `npm ci`와 `npm run build`를 실행합니다.
- 현재 v327 문서·검사기 정적 변경에는 서버 재시작이 필요 없고 새 설치도 없습니다.
- 완료 답변에는 한 일, 검증, 서버 재시작 필요 여부, commit/push 결과, 다음 추천 단계, 필요한 extension/권한/설치 요청을 포함합니다.

기호의 Upgrade RPG 프로젝트를 Codex에서 이어서 진행합니다.

ZIP은 기준으로 작업하지 않습니다. 현재 프로젝트 루트의 Git `main` 최신 commit을 기준으로 하고, `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 가장 먼저 읽어 계속 지켜주세요.

사용자는 코딩을 거의 모르는 기호입니다. 항상 한국어로 쉽고 자세하게 설명하고, 모든 터미널 명령 바로 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적어주세요. backend 가상환경은 `backend/.venv`이고 Git Bash에서 `backend` 폴더에서 `source .venv/Scripts/activate`로 켭니다. Vue/npm은 `frontend/vue-app`에서 Python `.venv` 없이 실행합니다.

Codex는 VS Code/Codex 터미널을 자유롭게 사용하고 정상인 백엔드 `127.0.0.1:8000`과 프론트엔드 `127.0.0.1:5173` 서버를 재사용할 수 있습니다. 프로세스가 죽었거나 설정 때문에 꼭 필요한 경우에만 재시작하세요.

GitHub Actions, workflow, action SHA, environment, variables와 필요한 repository 설정은 작업 목적 안에서 Codex가 처리할 수 있습니다. 숨김 파일과 `.env`도 필요한 경우 점검·수정할 수 있지만 실제 secret, token, PAT, Docker credential, production `.env`, CA/cert/key는 Git·채팅·로그·artifact에 노출하거나 커밋하지 마세요. 나중에 회전하거나 재설정할 보안 항목은 `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`에 기록하세요.

필요한 extension, 권한, 설치 또는 사용자만 할 수 있는 계정 작업이 있으면 기호에게 요청하고, 해결 전에는 다음 handoff에도 반복 기록하세요. 변경과 검증 후에는 Codex가 프로젝트 루트에서 직접 git status/add/commit/push까지 합니다. 기호에게 Git 명령을 제공하지 않고 ZIP도 만들지 않습니다. root `NEXT_CHAT_PROMPT.md`, `NEXT_CHAT_HANDOFF.md`와 `docs/handoff/` mirror는 매 작업마다 바이트 단위로 같게 갱신합니다.

현재 고정값:

```txt
latest: v326.dockerfile-bootstrap-fixed-retry-preparation-publish-gated
strict result: github-actions-ghcr-owner-only-retry-preparation-ready-publish-gated
next safe stage: review-and-approve-exact-dockerfile-bootstrap-fix-preparation-sha
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
GHCR namespace: gihohoho
backend repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility: private
target platform: linux/amd64
managed PostgreSQL + provider CA verify-full
external reverse proxy HTTPS
backend replicas/workers: 1/1
Compose config render: 기호 PC 실제 통과
base image exact digest: approved
CI credential strategy: GitHub Actions GITHUB_TOKEN 우선
local credential/PAT: deferred
workflow file/creation approved: yes/yes
workflow execution approved/executed: yes/yes
CI workflow/login/build/push approved: yes/yes/yes/yes
CI login/build/push executed: no/yes/no (build attempted and failed)
repository Actions allowlist/full SHA enforcement: configured/configured
publish environment/main-only: present/configured
required reviewer/prevent self-review: missing/missing
publish approval model: owner-only-source-controlled-two-step
source-controlled lifecycle gate: preparation-closed / publishReviewerGateReady=false
dependency/frontend input lock: complete (exact versions + SHA-256)
workflow source SHA-256: 245630348d384cc1c862014454cb73b6149a8c3a20d7b114763bc6fe655ef4bd
workflow semantic SHA-256: e08c3788e88da351112bc381d225e418938f7bd74ccec7eb83f9f59eff6f724c
run_attempt=1: required
single dispatch: required by GitHub Actions API check
immediate closure: required immediately after a run is accepted
prior preparation SHA: 350bbd085f1cf636810d75ddcbb5321e0791256c approved and consumed
bootstrap-fix preparation SHA: 2f77ebf0f60a39c936509df26f903995f0c62967 approved and consumed
```

`gihohoho`는 기호가 직접 확인한 고정 namespace입니다. placeholder로 되돌리거나 다른 이름을 추측하지 마세요. repository 주소는 `ghcr.io/gihohoho/upgrade-rpg-backend`로 고정합니다.

중요한 감사 이력:

- 기호는 `f4788acf5455b07169320bd29f43ddf92ff1d5ad` 준비 commit을 정확히 승인했습니다.
- 그러나 승인 후 실행 전 감사에서 checker의 open gate 불허, rerun 방어 없음, authorization-parent 연결 없음, 계획 밖 Docker build record artifact, post-push 실패 증거 미보존을 발견했습니다.
- 따라서 그 승인은 역사적 `priorApprovedPreparationSha`로만 보존합니다. workflow는 두 번 실행됐지만 GHCR login/push는 아직 한 번도 실행되지 않았습니다.
- v322는 `deploy/github-actions-ghcr-publish-lifecycle.json`을 기본 closed인 source-controlled lifecycle gate로 사용합니다.
- authorization commit은 승인받은 새 preparation commit의 직접 자식이어야 하며 lifecycle JSON 하나만 변경할 수 있습니다.
- workflow는 repository owner, `run_attempt=1`, API에서 확인한 single dispatch만 허용하고 rerun을 금지합니다.
- run이 접수되면 결론을 기다리며 gate를 열어 두지 말고 immediate closure commit을 먼저 push해 `authorization-closed-awaiting-evidence`로 전이합니다. 이 commit에서는 자기 SHA를 기록할 수 없어 `closureCommitSha=null`입니다.
- run 종료 뒤 별도 evidence commit에서 부모 closure commit의 정확한 SHA를 `closureCommitSha`에 넣고 run ID/URL/conclusion과 실제 digest/signature 결과를 `attempt-recorded`로 기록한 뒤 `review-recorded-workflow-attempt-evidence`로 갑니다. 전체 failure·취소·시간 초과 결론만으로 `registryMutationExecuted=false` 또는 `signatureVerified=false`라고 단정하지 말고 job/step 증거를 각각 확인하세요.
- `DOCKER_BUILD_RECORD_UPLOAD=false`로 계획 밖 build record artifact를 끕니다.
- push 뒤 실패해도 digest가 생겼다면 가능한 partial evidence를 보존하지만, 모든 gate와 Cosign 검증이 끝나기 전에는 검증 완료 후보로 취급하지 않습니다.

2026-07-20 첫 실행 결과:

- authorization SHA `32e5102877851ace06e1c0ed3bcb48310b8d65b6`, closure SHA `362f5f1901d234b5b86f2a7cefdabd28ac61f896`
- run `29716038891`: `https://github.com/gihohoho/upgrade-rpg/actions/runs/29716038891`
- `Install backend validation dependencies`에서 실패; bootstrap pip download의 `--python-version 3`이 `pip==26.1.2`의 Python `>=3.10` 조건과 충돌
- build/publish jobs는 skipped, GHCR login/build/push 미실행, artifact 0개, digest 없음, signature 미검증
- 기호가 focused fix를 승인해 workflow의 해당 값을 `--python-version 3.11`로 수정 완료
- 첫 실패는 `priorAttemptEvidence.recordCommitSha=1f12ea59eb54385337557e9754f86731ec53d253`로 보존
- 첫 실패는 `priorAttemptEvidence`에 보존

2026-07-22 두 번째 실행 결과:

- preparation `2f77ebf0f60a39c936509df26f903995f0c62967`, authorization `7e69555b8b653c406b322fb5c8f23e550751d72c`, closure `5479e6b14826b3a0f2b6d0c3beb0e2142ca22c94`
- run `29877813770`: `https://github.com/gihohoho/upgrade-rpg/actions/runs/29877813770`
- workflow bootstrap dependency와 repository checks는 통과
- `Build local linux/amd64 image without registry mutation`에서 실패
- 원인: `backend/Dockerfile.production:22`의 bootstrap pip download에 `--python-version 3`이 남아 `pip==26.1.2`를 찾지 못함
- SBOM/Trivy와 publish job은 미실행 또는 skipped, GHCR login/push 미실행
- artifact 0개, digest 없음, signature 미검증, registry mutation 없음
- Dockerfile bootstrap target 한 곳을 `3.11`로 수정 완료
- lifecycle은 `preparation-closed`, gate는 `false`; 두 실패는 `attemptHistory`에 보존되고 동일 run rerun 금지

2026-07-22 GitHub live 재확인에서 allowlist/full SHA/default read-only/environment main-only/secrets·variables 0/0을 확인했습니다. fork write token과 fork secret 전달은 모두 `false`였습니다. native required reviewer와 prevent self-review는 비공개 개인 저장소 제약으로 계속 없습니다. 다음 authorization 직전에도 4시간 이내 live 상태를 다시 확인해야 합니다.

첫 작업은 읽기 전용 v326 preparation 검사입니다.

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
result: github-actions-ghcr-owner-only-retry-preparation-ready-publish-gated
next safe stage: review-and-approve-exact-dockerfile-bootstrap-fix-preparation-sha
```

Dockerfile focused fix와 v326 preparation을 확인한 뒤 새 preparation commit의 정확한 40자 SHA 승인을 기호에게 요청하세요. 별도 승인 전에는 authorization/workflow를 실행하지 말고 기존 두 run도 rerun하지 마세요.

사용자 별도 작업 요청 전에는 DB write/restore/reset/seed, Alembic revision/autogenerate/stamp/upgrade/downgrade, 인증/API route·response body/write logic, Vue Preview/Apply/write, 게임 콘텐츠·밸런스, production container/network/volume, Compose up/down, 자동 deploy/production image reference를 변경하거나 실행하지 마세요.

코드나 구조를 변경했다면 관련 smoke, Python compileall, JavaScript 문법, `bash tools/run_smoke_core.sh`를 검증하세요. authorization-open workflow에서는 정적 checker를 먼저 직접 실행하고 `SKIP_GHCR_HANDOFF_SMOKES=1 bash tools/run_smoke_core.sh`를 사용합니다. 이 플래그는 closed root 전용 handoff smoke 세 개만 건너뛰며 앱·백엔드 전체 smoke는 계속 실행합니다. Vue 변경 시에만 `frontend/vue-app`에서 Python `.venv` 없이 `npm ci`와 `npm run build`를 실행하세요. 현재 정적 workflow/문서 작업은 서버 재시작이 필요 없고 새 설치도 없습니다. 완료 시 한 일, 검증, 서버 재시작 여부, commit/push 결과, 다음 단계, 필요한 extension/권한/설치를 알려주세요.

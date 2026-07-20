기호의 Upgrade RPG 프로젝트를 Codex에서 이어서 진행합니다.

ZIP을 기준으로 작업하지 않습니다. 현재 프로젝트 루트의 Git `main` 최신 commit을 기준으로 하고, `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 가장 먼저 읽어 계속 지켜주세요.

사용자는 코딩을 거의 모르는 기호입니다. 항상 한국어로 쉽고 자세하게 설명하고, 모든 터미널 명령 바로 위에 실행 위치, Python `.venv` 상태, 새 설치 여부를 적어주세요. backend 가상환경은 `backend/.venv`이고 Git Bash에서 `backend` 폴더에서 `source .venv/Scripts/activate`로 켭니다. Vue/npm은 `frontend/vue-app`에서 Python `.venv` 없이 실행합니다.

Codex는 VS Code/Codex 터미널을 자유롭게 사용하고 이미 실행 중인 백엔드 `127.0.0.1:8000`과 프론트엔드 `127.0.0.1:5173` 서버를 재사용할 수 있습니다. 정상 서버를 작업마다 종료·재시작하지 말고, 프로세스가 죽었거나 설정상 꼭 필요한 경우에만 재시작해주세요.

기호는 GitHub Actions, workflow, action SHA, environment, variables와 필요한 repository 설정을 Codex가 작업 목적 안에서 처리하는 것을 계속 허용했습니다. 숨김 파일과 `.env`도 필요하면 점검·수정할 수 있습니다. 다만 실제 secret 값은 Git, 파일 예제, 로그, 채팅, artifact에 노출하거나 커밋하지 말고, 나중에 회전·폐기·재설정할 항목은 `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`에 계속 적어주세요. 필요한 extension, 권한, 설치 또는 사용자만 할 수 있는 계정 작업이 생기면 기호에게 요청하고, 해결되지 않으면 다음 handoff에도 반복해서 기록해주세요.

코드나 문서를 바꾸고 검증이 끝나면 Codex가 프로젝트 루트에서 직접 `git status`, `git add .`, `git commit`, `git push`까지 합니다. 기호에게 Git 한 줄 명령을 주지 않고 ZIP도 만들지 않습니다. root `NEXT_CHAT_PROMPT.md`, `NEXT_CHAT_HANDOFF.md`와 `docs/handoff/` mirror는 매 작업마다 갱신합니다.

현재 고정값:

```txt
latest: v321.owner-only-reproducibility-locked-publish-gated
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
workflow execution approved/executed: yes/no
CI workflow/login/build/push approved: yes/yes/yes/yes
CI login/build/push executed: no/no/no
repository Actions allowlist/full SHA enforcement: configured/configured
publish environment/main-only: present/configured
required reviewer/prevent self-review: missing/missing
publish approval model: owner-only-source-controlled-two-step
PUBLISH_REVIEWER_GATE_READY: source-controlled false
dependency/frontend input lock: complete (exact versions + SHA-256)
exact preparation SHA approval: pending
GitHub settings evidence: 2026-07-15 browser snapshot; live recheck required before gate change
```

`gihohoho`는 기호가 직접 확인한 고정 namespace입니다. placeholder로 되돌리거나 다른 이름을 추측하지 마세요. repository 주소는 `ghcr.io/gihohoho/upgrade-rpg-backend`로 고정합니다. 실제 token, PAT, Docker credential, production secret 값은 파일·Git·채팅에 넣지 마세요.

첫 작업은 읽기 전용 v321 검사입니다.

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
result: github-actions-ghcr-owner-only-reproducibility-ready-publish-gated
next safe stage: review-and-approve-exact-preparation-sha
```

`.github/workflows/publish-backend-ghcr.yml`은 이미 준비됐고 `workflow_dispatch` 전용입니다. `main`과 40자리 source SHA, 확인 입력, 정적 검사, 로컬 OCI build, SPDX SBOM, checksum-pinned Trivy `HIGH,CRITICAL`, push된 exact digest 재검사, Docker BuildKit provenance/SBOM, Sigstore Cosign keyless 서명·검증을 fail-closed로 설계했습니다.

정적 검사기는 workflow 전체 UTF-8 소스와 파싱된 실행 의미 구조를 별도 SHA-256으로 잠그고 exact step 순서를 확인합니다. `|| true`, 추가 secret 전송 step, step 삭제·재배열 같은 우회를 통과시키지 마세요. 의도적인 workflow 변경은 별도 보안 검토와 두 승인 해시 갱신을 함께 해야 합니다.

action/run step별 잠금과 parsed secret 경로 allowlist도 유지하세요. root Docker build context에서 `.env`/`*.env`/`.envrc`를 제외하는 `.dockerignore` 규칙을 약화하거나 env 파일을 재포함하지 마세요.

Python application/build dependency는 CPython 3.11 Linux/amd64 exact version과 선택 wheel SHA-256으로 잠겼습니다. pip `26.1.2`, `setuptools 80.10.2`, `wheel 0.46.3`, Dockerfile frontend exact digest도 고정됐고 source distribution은 금지됩니다. byte-for-byte 동일 image를 보장한다고 과장하지 말고 실제 결과 digest의 SBOM/Trivy/provenance/Cosign 검증을 계속 유지하세요.

현재 `ghcr-production-publish`에 required reviewer와 prevent self-review가 없습니다. 기호는 이 잔여 위험을 알고 2026-07-20에 `owner-only-source-controlled-two-step`을 선택했습니다. source-controlled `PUBLISH_REVIEWER_GATE_READY`는 리터럴 `"false"`로 고정되어 GHCR login 전에 실패하며 repository/environment variable로 우회할 수 없습니다. v321 preparation commit의 정확한 40자 SHA와 범위를 기호가 명시적으로 승인하기 전에는 이 값을 바꾸거나 workflow를 실행하지 마세요. 승인 뒤에도 GitHub 설정을 live 재확인하고 별도 authorization commit에서만 gate를 열며, 한 번의 실행 뒤 성공·실패와 관계없이 즉시 다시 닫으세요.

DB write/restore/reset/seed, Alembic revision/autogenerate/stamp/upgrade/downgrade, 인증/API route·response body/write logic, Vue Preview/Apply/write, 게임 콘텐츠·밸런스, production container/network/volume, Compose up/down, 자동 deploy와 production image reference 갱신은 구체적인 다음 요청 전에는 변경하거나 실행하지 마세요.

코드나 구조를 변경했다면 관련 smoke, `python -m compileall -q backend/app backend/scripts backend/alembic tools`, JavaScript 문법, `bash tools/run_smoke_core.sh`를 검증합니다. Vue 변경 시에만 `frontend/vue-app`에서 Python `.venv` 없이 `npm ci`와 `npm run build`를 실행합니다. 작업 후에는 NEXT_CHAT 문서와 mirror를 갱신하고 Codex가 직접 commit/push한 뒤, 한 일·검증·서버 재시작 필요 여부·Git 결과·다음 단계·필요한 extension/권한/설치를 알려주세요.

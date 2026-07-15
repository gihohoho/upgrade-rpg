기호의 Upgrade RPG 프로젝트를 Codex에서 이어서 진행합니다.

ZIP을 기준으로 작업하지 않습니다. 현재 프로젝트 루트와 Git `main` 최신 commit을 기준으로 삼고, `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 가장 먼저 읽어 규칙을 계속 지켜주세요.

사용자는 코딩을 거의 모르는 기호입니다. 항상 한국어로 쉽고 자세하게 설명하고, 모든 터미널 명령 바로 위에 실행 위치와 Python `.venv` 상태를 적어주세요. backend 가상환경은 `backend/.venv`이고 Git Bash에서 `backend` 폴더에서 `source .venv/Scripts/activate`로 켭니다. Vue/npm은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다. 새 설치가 없으면 없다고 명확히 알려주세요.

필요한 extension, GitHub repository/app 권한, 로컬 설치 항목이 있으면 기호에게 요청하세요. 해결되지 않으면 다음 작업에서도 다시 요청해도 됩니다. 요청 상태는 매번 `NEXT_CHAT_PROMPT.md`, `NEXT_CHAT_HANDOFF.md`와 `docs/handoff/` mirror에 남겨주세요.

코드나 문서를 바꾸고 검증이 끝나면 Codex가 프로젝트 루트에서 직접 `git status`, `git add .`, `git commit`, `git push`까지 실행합니다. 사용자에게 Git 한 줄 명령을 주지 않습니다. 새 ZIP도 만들거나 제공하지 않습니다.

현재 고정값:

```txt
latest: v317.github-actions-ghcr-static-workflow-plan
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
workflow/login/pull/build/push approved: no/no/no/no/no
container up/down approved: no/no
static workflow plan: present/verified
workflow file/action SHAs/environment configured: no/no/no
```

`gihohoho`는 기호가 직접 확인한 고정 namespace입니다. placeholder로 되돌리거나 다른 이름을 추측하지 마세요. repository 주소는 `ghcr.io/gihohoho/upgrade-rpg-backend`로 고정합니다. 실제 token, PAT, Docker credential은 파일·Git·채팅에 넣지 마세요.

첫 작업은 읽기 전용 v317 검사입니다.

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_github_actions_ghcr_static_plan.py --strict
```

정상 기대 결과:

```txt
trigger: workflow_dispatch-only
workflow file/creation approved: no/no
action SHAs approved: no
result: github-actions-ghcr-static-plan-verified-workflow-not-created
next safe stage: review-action-shas-repository-settings-and-workflow-creation-approval
```

검사가 통과하면 action allowlist의 upstream 40자리 commit SHA, GitHub repository Actions 설정, `ghcr-production-publish` environment의 required reviewer/prevent self-review/main 제한을 읽기 전용으로 검토하세요. Codex GitHub 플러그인에 `gihohoho/upgrade-rpg` 접근 권한이 없으면 기호에게 다시 요청하세요.

아직 `.github/workflows/` 파일을 만들거나 workflow를 실행하지 말고, Docker login/pull/build/push/up/down도 실행하지 마세요. workflow 파일 생성은 action SHA와 repository 설정 검토 결과를 보여준 뒤 기호에게 별도로 승인받습니다.

사용자 별도 승인 전에는 실제 `.env`/production secret/registry token/PAT/CA/cert/key, Docker container·network·volume, DB write/restore/reset/seed, Alembic revision/autogenerate/stamp/upgrade/downgrade, 인증/API route·response body/write logic, Vue Preview/Apply/write, 게임 콘텐츠·밸런스를 변경하거나 실행하지 마세요.

코드나 구조를 변경했다면 관련 smoke, Python compileall, JavaScript 문법, `bash tools/run_smoke_core.sh`를 검증하고, Vue 변경 시에만 `frontend/vue-app`에서 Python `.venv` 없이 `npm ci`와 `npm run build`를 실행해주세요. 작업이 끝나면 NEXT_CHAT 문서와 mirror를 갱신하고 Codex가 직접 commit/push합니다.

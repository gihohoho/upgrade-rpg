기호의 Upgrade RPG 프로젝트를 Codex에서 이어서 진행합니다.

이번에 첨부하는 최신 ZIP `rpg_v316_codex_handoff_audit_fix.zip`을 반드시 기준으로 작업해주세요. 압축을 푼 프로젝트 루트의 `AGENTS.md`, `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 가장 먼저 읽고 그 규칙을 계속 지켜주세요.

사용자는 코딩을 거의 모르는 기호입니다. 항상 한국어로 쉽고 자세하게 설명하고, 모든 터미널 명령 바로 위에 실행 위치와 Python `.venv` 상태를 적어주세요. backend 가상환경은 `backend/.venv`이고 Git Bash에서 `backend` 폴더에서 `source .venv/Scripts/activate`로 켭니다. Vue/npm은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다. 새 설치가 없으면 없다고 명확히 알려주세요. Git 명령은 프로젝트 루트에서 `git status && git add . && git commit -m "..." && git push` 형태의 한 줄 블록으로 주세요.

현재 고정값:

```txt
latest: v316.codex-handoff-audit-fix
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
workflow/login/pull/build/push/up/down approved: no
```

`gihohoho`는 기호가 직접 확인한 고정 namespace입니다. placeholder로 되돌리거나 다른 이름을 추측하지 마세요. repository 주소는 `ghcr.io/gihohoho/upgrade-rpg-backend`로 고정합니다. 실제 token, PAT, Docker credential은 파일·Git·ZIP·채팅에 넣지 마세요.

첫 작업은 읽기 전용 v316 검사입니다.

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_codex_handoff_readiness.py --strict
```

정상 기대 결과:

```txt
namespace/repository: gihohoho / ghcr.io/gihohoho/upgrade-rpg-backend
credential strategy: github-actions-github-token / local=deferred
workflow/login/pull/build/push approved: no/no/no/no/no
result: codex-ghcr-namespace-handoff-verified-workflow-plan-only
next safe stage: review-github-actions-permissions-and-static-workflow-plan
```

검사가 통과하면 다음 단계로 GitHub Actions 최소 permissions, 안전한 trigger, SBOM/provenance/signature/vulnerability gate를 **문서와 fail-closed 정적 검사로만** 설계해주세요. 아직 `.github/workflows/` 파일을 만들거나 workflow를 실행하지 말고, Docker login/pull/build/push/up/down도 실행하지 마세요.

사용자 별도 승인 전에는 실제 `.env`/production secret/registry token/PAT/CA/cert/key, Docker container·network·volume, DB write/restore/reset/seed, Alembic revision/autogenerate/stamp/upgrade/downgrade, 인증/API route·response body/write logic, Vue Preview/Apply/write, 게임 콘텐츠·밸런스를 변경하거나 실행하지 마세요.

코드나 구조를 변경했다면 관련 smoke, Python compileall, JavaScript 문법, `bash tools/run_smoke_core.sh`를 검증하고, Vue 변경 시에만 `frontend/vue-app`에서 Python `.venv` 없이 `npm ci`와 `npm run build`를 실행해주세요. 작업 후에는 한 일, 검증, 서버 재실행 명령, Git 한 줄 명령, 다음 추천 단계, 변경 시 새 ZIP을 함께 주세요.

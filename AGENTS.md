# Upgrade RPG Codex working rules — v319

이 파일은 저장소 전체에 적용됩니다. Codex는 작업을 시작할 때 이 파일과 `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽습니다.

## 사용자와 설명 방식

- 사용자는 코딩을 거의 모르는 **기호**입니다. 항상 쉽고 자세한 한국어로 설명합니다.
- 터미널 명령 바로 위에 **실행 위치**와 **Python `.venv` 상태**를 반드시 적습니다.
- backend 가상환경은 프로젝트 루트가 아니라 `backend/.venv`입니다. Git Bash에서 `backend` 폴더에서 `source .venv/Scripts/activate`로 켭니다.
- Vue/npm 명령은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.
- 새 설치가 있으면 설치 항목과 이유를 알리고, 없으면 “새 설치 없음”이라고 명확히 적습니다.
- 필요한 extension, repository/app 권한, 로컬 설치가 있으면 사용자에게 요청합니다. 해결되지 않으면 다음 작업에서도 다시 요청할 수 있으며 요청 상태를 `NEXT_CHAT_PROMPT.md`와 `NEXT_CHAT_HANDOFF.md`에 기록합니다.
- 매 작업에서 root `NEXT_CHAT_PROMPT.md`, `NEXT_CHAT_HANDOFF.md`와 `docs/handoff/` mirror를 최신 상태로 갱신합니다.
- 변경과 검증이 끝나면 Codex가 프로젝트 루트에서 `git status`, `git add .`, `git commit`, `git push`를 직접 실행합니다. 사용자에게 Git 한 줄 명령을 다시 제공하지 않습니다.
- Codex 작업에서는 새 ZIP을 만들거나 제공하지 않습니다. 사용자가 별도로 요청한 경우에만 안전 제외 규칙을 적용해 생성합니다.

## 현재 고정 상태

- latest: `v319.github-connector-actions-settings-reviewed`
- GitHub remote: `https://github.com/gihohoho/upgrade-rpg.git`
- GHCR namespace: `gihohoho`
- backend image repository: `ghcr.io/gihohoho/upgrade-rpg-backend` (private)
- target: `linux/amd64`
- 운영 구조: managed PostgreSQL + provider CA `verify-full` + external reverse proxy HTTPS + backend 1 replica/1 worker
- Vue는 GET read-only까지만 연결하며 Preview/Apply/write/인증은 연결하지 않습니다.
- 게임 콘텐츠와 밸런스 개발은 계속 보류합니다.
- Alembic current revision은 `v295_initial_schema`; 새 revision 필요 상태는 `no`입니다.
- CI credential strategy: GitHub Actions `GITHUB_TOKEN` 우선 (`github-actions-github-token`)
- workflow/login/pull/build/push approved: no/no/no/no/no
- Codex GitHub App access: `gihohoho/upgrade-rpg` selected repository only, verified
- repository Actions settings reviewed/changed: yes/no
- `ghcr-production-publish` environment reviewed/configured: yes/no

## 안전 승인 경계

사용자 별도 승인 전에는 다음을 실행하거나 변경하지 않습니다.

- 실제 `backend/.env`, production env, JWT/Admin secret
- 실제 registry token/PAT, Docker credential, CA/cert/key 생성·입력·커밋
- `.github/workflows/` 생성, GitHub Actions settings/environment 변경, workflow 실행
- `docker login`, `pull`, `build`, `push`, `compose up/down`
- container/network/volume 생성·삭제·변경
- DB 생성·삭제·복원·reset·seed·write
- Alembic revision/autogenerate/stamp/upgrade/downgrade
- 인증, API route path/response body, write logic/Write Guard
- Vue Preview/Apply/write 연결
- 게임 콘텐츠/장비/스킬/보스/드랍률/밸런스 변경

DB/env/seed/인증/API body/route/write/migration/Docker/secret/TLS 작업은 작은 승인 경계로 나누고, 각 단계의 실제 결과를 확인한 뒤 다음 단계로 진행합니다.

## 현재 허용된 다음 단계

Codex GitHub App은 `gihohoho/upgrade-rpg` 저장소 하나에만 연결되었고 repository Actions 설정과 environment 존재 여부를 v319에서 읽기 전용으로 검토했습니다. 현재 Actions는 외부 action 전체 허용이며 full-length SHA 강제가 꺼져 있고, 기본 `GITHUB_TOKEN`은 contents/packages read-only이며, `ghcr-production-publish` environment는 없습니다. 다음 단계는 외부 action 허용 범위를 v318 allowlist로 제한하고 full-length SHA 강제를 켜는 repository Actions settings 변경 승인을 사용자에게 별도로 묻는 것입니다. Environment 생성과 `.github/workflows/` 생성·실행은 이후 각각 별도 승인 경계로 유지합니다.

첫 검사는 프로젝트 루트에서 `backend/.venv`를 켠 상태로 실행합니다.

```bash
python tools/check_github_actions_ghcr_static_plan.py --strict
```

정상 결과: `github-connector-actions-settings-verified-workflow-not-created`

## 변경과 검증

- 현재 판단 문서는 `docs/current/`를 우선합니다. 과거 단계 기록은 `docs/archive/`와 `deploy/review/`에 있습니다.
- legacy 게임 `index.html`, 관리자 `admin.html`, `src/`는 Vue 이식 전까지 이동하거나 대규모 재작성하지 않습니다.
- 코드나 구조를 바꾸면 관련 전용 smoke, `python -m compileall -q backend/app backend/scripts backend/alembic tools`, JavaScript 문법, `bash tools/run_smoke_core.sh`를 확인합니다.
- Vue 변경 시 `frontend/vue-app`에서 Python `.venv` 없이 `npm ci`와 `npm run build`를 실행합니다.
- ZIP은 기본 생성하지 않습니다. 사용자가 별도 요청하면 `.git`, `backend/.env`, `backend/.venv`, `node_modules`, `local-backups`, `local-review-artifacts`, 실제 secret/cert/token을 제외합니다.
- 작업 완료 답변에는 ① 한 일 ② 검증 ③ 서버 재실행 필요 여부 ④ commit/push 결과 ⑤ 다음 추천 단계 ⑥ 필요한 extension/권한/설치 요청을 포함합니다.

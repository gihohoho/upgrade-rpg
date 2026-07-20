# Upgrade RPG Codex working rules — v321

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

- latest: `v321.owner-only-reproducibility-locked-publish-gated`
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
- workflow execution approved/executed: yes/no
- CI workflow/login/build/push approved: yes/yes/yes/yes
- CI login/build/push executed: no/no/no
- repository Actions allowlist/full SHA enforcement: configured/configured
- `ghcr-production-publish` environment/main-only: present/configured
- required reviewer/prevent self-review: missing/missing
- publish approval model: `owner-only-source-controlled-two-step` (기호가 2026-07-20 선택)
- `PUBLISH_REVIEWER_GATE_READY`: source-controlled `"false"`; GHCR login 전에 fail-closed
- dependency/frontend input lock: complete (exact version + SHA-256, binary wheel only)
- byte-for-byte deterministic image: 보장한다고 주장하지 않음
- exact preparation SHA approval: pending
- GitHub Actions/environment 설정 증거: 2026-07-15 browser snapshot; gate 변경 직전 live 재확인 필수

## 현재 안전 경계

GitHub workflow 작성과 CI GHCR 작업은 사용자가 승인했습니다. 기호는 비공개 개인 저장소의 native required reviewer가 없다는 위험을 이해하고 `owner-only-source-controlled-two-step`을 선택했습니다. Python application/build dependency, pip, Dockerfile frontend 입력은 exact version과 SHA-256으로 잠겼습니다. 다만 publish job은 source-controlled `PUBLISH_REVIEWER_GATE_READY`가 현재 리터럴 `"false"`로 고정되어 GHCR login 전에 실패해야 합니다. 기호가 준비 commit의 정확한 40자 SHA를 별도로 승인하고, GitHub live 설정을 재확인하고, 별도 authorization commit을 검토하기 전에는 이 값을 바꾸거나 workflow를 실행하지 않습니다. authorization을 열었다면 성공·실패와 관계없이 한 번의 실행 뒤 즉시 다시 닫아야 합니다.

다음 항목은 이번 GitHub 권한 확대와 별개이므로 기호의 구체적인 작업 요청 전에는 변경·실행하지 않습니다.

- DB 생성·삭제·복원·reset·seed·write
- Alembic revision/autogenerate/stamp/upgrade/downgrade
- 인증, API route path/response body, write logic/Write Guard
- Vue Preview/Apply/write 연결
- 게임 콘텐츠/장비/스킬/보스/드랍률/밸런스 변경
- production container/network/volume 생성·삭제, Compose up/down
- production image reference 자동 갱신 또는 자동 deploy

## 현재 다음 단계

워크플로 파일은 준비됐고 실행하지 않았습니다. 첫 검사는 프로젝트 루트에서 `backend/.venv`를 켠 상태로 실행합니다.

```bash
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

정상 결과: `github-actions-ghcr-owner-only-reproducibility-ready-publish-gated`

그다음 안전 단계는 현재 v321 준비 commit이 push된 뒤 Codex가 정확한 40자 commit SHA와 검토 범위를 기호에게 설명하고, 기호가 그 SHA를 명시적으로 승인하는 것입니다. 승인을 받기 전에는 gate를 바꾸지 않습니다. 승인 뒤에도 GitHub Actions allowlist/full SHA/environment main-only 설정을 live 재확인한 다음, gate 변경만 다루는 별도 authorization commit과 한 번의 수동 실행을 준비합니다. 실행 성공·실패 후에는 별도 commit으로 gate를 즉시 `false`로 되돌립니다.

## 변경과 검증

- 현재 판단 문서는 `docs/current/`를 우선합니다. 과거 단계 기록은 `docs/archive/`와 `deploy/review/`에 있습니다.
- legacy 게임 `index.html`, 관리자 `admin.html`, `src/`는 Vue 이식 전까지 이동하거나 대규모 재작성하지 않습니다.
- 코드나 구조를 바꾸면 관련 전용 smoke, `python -m compileall -q backend/app backend/scripts backend/alembic tools`, JavaScript 문법, `bash tools/run_smoke_core.sh`를 확인합니다.
- Vue 변경 시에만 `frontend/vue-app`에서 Python `.venv` 없이 `npm ci`와 `npm run build`를 실행합니다.
- 완료 답변에는 한 일, 검증, 서버 재시작 필요 여부, commit/push 결과, 다음 추천 단계, 필요한 extension/권한/설치 요청을 포함합니다.

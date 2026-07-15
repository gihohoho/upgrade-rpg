# Upgrade RPG Codex working rules — v315

이 파일은 저장소 전체에 적용됩니다. Codex는 작업을 시작할 때 이 파일과 `NEXT_CHAT_HANDOFF.md`, `docs/current/CURRENT_STATUS.md`를 먼저 읽습니다.

## 사용자와 설명 방식

- 사용자는 코딩을 거의 모르는 **기호**입니다. 항상 쉽고 자세한 한국어로 설명합니다.
- 터미널 명령 바로 위에 **실행 위치**와 **Python `.venv` 상태**를 반드시 적습니다.
- backend 가상환경은 프로젝트 루트가 아니라 `backend/.venv`입니다. Git Bash에서 `backend` 폴더에서 `source .venv/Scripts/activate`로 켭니다.
- Vue/npm 명령은 `frontend/vue-app`에서 실행하며 Python `.venv`가 필요 없습니다.
- 새 설치가 있으면 설치 항목과 이유를 알리고, 없으면 “새 설치 없음”이라고 명확히 적습니다.
- Git 명령은 프로젝트 루트에서 다음 형태의 한 줄 블록으로 제공합니다: `git status && git add . && git commit -m "..." && git push`.

## 현재 고정 상태

- latest: `v315.codex-ghcr-namespace-handoff-ready`
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

## 안전 승인 경계

사용자 별도 승인 전에는 다음을 실행하거나 변경하지 않습니다.

- 실제 `backend/.env`, production env, JWT/Admin secret
- 실제 registry token/PAT, Docker credential, CA/cert/key 생성·입력·커밋
- `docker login`, `pull`, `build`, `push`, `compose up/down`
- container/network/volume 생성·삭제·변경
- DB 생성·삭제·복원·reset·seed·write
- Alembic revision/autogenerate/stamp/upgrade/downgrade
- 인증, API route path/response body, write logic/Write Guard
- Vue Preview/Apply/write 연결
- 게임 콘텐츠/장비/스킬/보스/드랍률/밸런스 변경

DB/env/seed/인증/API body/route/write/migration/Docker/secret/TLS 작업은 작은 승인 경계로 나누고, 각 단계의 실제 결과를 확인한 뒤 다음 단계로 진행합니다.

## 현재 허용된 다음 단계

현재는 파일 읽기, 정적 검사, 문서·검사기 개선만 허용됩니다. 다음 단계는 GitHub Actions의 최소 권한과 GHCR workflow를 **설계 문서로만** 준비하는 것입니다. `.github/workflows/` 생성과 workflow 실행은 아직 승인되지 않았습니다.

첫 검사는 프로젝트 루트에서 `backend/.venv`를 켠 상태로 실행합니다.

```bash
python tools/check_codex_handoff_readiness.py --strict
```

정상 결과: `codex-ghcr-namespace-handoff-verified-workflow-plan-only`

## 변경과 검증

- 현재 판단 문서는 `docs/current/`를 우선합니다. 과거 단계 기록은 `docs/archive/`와 `deploy/review/`에 있습니다.
- legacy 게임 `index.html`, 관리자 `admin.html`, `src/`는 Vue 이식 전까지 이동하거나 대규모 재작성하지 않습니다.
- 코드나 구조를 바꾸면 관련 전용 smoke, `python -m compileall -q backend/app backend/scripts backend/alembic tools`, JavaScript 문법, `bash tools/run_smoke_core.sh`를 확인합니다.
- Vue 변경 시 `frontend/vue-app`에서 Python `.venv` 없이 `npm ci`와 `npm run build`를 실행합니다.
- ZIP에는 `.git`, `backend/.env`, `backend/.venv`, `node_modules`, `local-backups`, `local-review-artifacts`, 실제 secret/cert/token을 넣지 않습니다.
- 작업 완료 답변에는 ① 한 일 ② 검증 ③ 서버 재실행 명령 ④ Git 한 줄 명령 ⑤ 다음 추천 단계 ⑥ 코드/문서 변경 시 새 ZIP을 포함합니다.

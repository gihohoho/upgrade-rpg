# Upgrade RPG Codex handoff — v319

## 기준

- handoff mode: current repository + Git `main` (ZIP 없음)
- latest: `v319.github-connector-actions-settings-reviewed`
- Codex 규칙: `AGENTS.md`
- backend virtualenv: `backend/.venv`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- change delivery: Codex가 검증 후 직접 add/commit/push

## 고정 PostgreSQL/Alembic 증거

```txt
source rpg_game: public 23/749, application 22/748
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
next revision required: no
```

## 운영/이미지 고정값

```txt
managed PostgreSQL + provider CA verify-full
external reverse proxy HTTPS
backend replicas/workers: 1/1
max_connections review candidate: 40
Compose config render approved/executed: yes/yes
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
namespace: gihohoho
repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility: private
target platform: linux/amd64
base image digest approved: yes
CI credential strategy: github-actions-github-token
local credential strategy: deferred
workflow/login/pull/build/push approved: no/no/no/no/no
```

`gihohoho`는 사용자 확인 완료 값이며 앞으로 고정합니다.

## v319 GitHub Actions 정적 plan과 repository 검토

```txt
trigger: workflow_dispatch only
required ref/source: refs/heads/main / exact 40-char github.sha
environment: ghcr-production-publish, required reviewers, prevent self-review, main only
workflow default/validate/build-scan permissions: contents read only
publish permissions: contents read + packages/attestations/id-token write
action pinning: reviewed full 40-char commit SHA required
action SHA candidates reviewed: yes (9개 최신 정식 release, 2026-07-15 upstream tag commit 대조)
action SHAs approved: no
pre-push: static checks -> local OCI -> SPDX SBOM -> HIGH/CRITICAL Trivy gate
post-push: exact digest -> provenance -> SBOM attestation -> keyless signature -> verify
automatic deploy/production reference update: no/no
workflow file present/creation approved/executed: no/no/no
```

```txt
GitHub App owner/scope: gihohoho / selected repositories only
selected repository/access: gihohoho/upgrade-rpg / verified
repository Actions settings reviewed/changed: yes/no
allowed actions / full-length SHA enforcement: all / off
default GITHUB_TOKEN: read contents and packages
Actions create/approve PR: off
publish environment reviewed/configured: yes/no
ghcr-production-publish environment: absent
```

정적 기준 파일:

- `deploy/github-actions-ghcr-static-plan.example.json`
- `docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md`
- `tools/check_github_actions_ghcr_static_plan.py`
- `tools/smoke/backend/smoke_github_actions_ghcr_static_plan.py`

## v319 검증 상태

```txt
GitHub connector/Actions settings strict checker: passed
GitHub connector/Actions settings fail-closed smoke: passed
Codex handoff strict/synchronization smoke: passed
docs index/archive smoke: passed
Python 3.11.4 / backend/.venv / SQLAlchemy-FastAPI-Pydantic imports: passed
full core smoke: passed
Python compileall / JavaScript / Bash / JSON syntax: passed
Windows cp949 guard output / source stamp smoke isolation / fake Docker smoke compatibility: fixed and passed
Vue files changed: no (npm ci/build not required)
workflow/Docker/registry/DB/Alembic mutation: none
repository settings/environment mutation: none
```

## 필요한 extension/권한/설치 요청

- GitHub App 연결과 repository 읽기 권한은 해결됨: `gihohoho/upgrade-rpg` 하나만 허용됐고 Codex repository 조회가 통과했습니다.
- 다음 단계의 repository Actions settings 변경은 기호의 별도 승인이 필요합니다.
- `ghcr-production-publish` environment 생성, action SHA 승인, workflow 파일 생성도 이후 각각 별도 승인이 필요합니다.
- Python 3.11.4와 `backend/.venv`는 정상 확인되어 추가 설치가 필요하지 않습니다.
- 필요한 요청이 해결되지 않으면 다음 채팅에서도 다시 요청합니다.

## 다음 첫 작업

```bash
python tools/check_github_actions_ghcr_static_plan.py --strict
```

기대 결과: `github-connector-actions-settings-verified-workflow-not-created`

다음 안전 단계는 외부 action 허용 범위를 v318에서 검토한 9개 repository로 제한하고 full-length SHA 강제를 켜는 repository Actions settings 변경 승인을 기호에게 묻는 것입니다. Environment 생성과 workflow 파일 생성은 각각 이후의 별도 승인 경계입니다.

## 계속 금지

- `.github/workflows/` 생성과 workflow 실행
- 실제 registry token/PAT/credential 및 production secret
- Docker login/pull/build/push/up/down
- container/network/volume mutation
- DB/Alembic mutation
- API/auth/write/Vue write
- 게임 콘텐츠/밸런스 변경
- 자동 deploy와 production image reference 갱신

# Upgrade RPG Codex handoff — v317

## 기준

- handoff mode: current repository + Git `main` (ZIP 없음)
- latest: `v317.github-actions-ghcr-static-workflow-plan`
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

## v317 GitHub Actions 정적 plan

```txt
trigger: workflow_dispatch only
required ref/source: refs/heads/main / exact 40-char github.sha
environment: ghcr-production-publish, required reviewers, prevent self-review, main only
workflow default/validate/build-scan permissions: contents read only
publish permissions: contents read + packages/attestations/id-token write
action pinning: reviewed full 40-char commit SHA required
action SHAs approved: no
pre-push: static checks -> local OCI -> SPDX SBOM -> HIGH/CRITICAL Trivy gate
post-push: exact digest -> provenance -> SBOM attestation -> keyless signature -> verify
automatic deploy/production reference update: no/no
workflow file present/creation approved/executed: no/no/no
```

정적 기준 파일:

- `deploy/github-actions-ghcr-static-plan.example.json`
- `docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md`
- `tools/check_github_actions_ghcr_static_plan.py`
- `tools/smoke/backend/smoke_github_actions_ghcr_static_plan.py`

## v317 검증 상태

```txt
GitHub Actions static plan strict checker: passed
GitHub Actions fail-closed smoke: passed
Codex handoff strict/synchronization smoke: passed
docs index/archive smoke: passed
Python compileall / JavaScript 238 / Bash 3 / JSON 23: passed
core smoke: dependency-free prefix passed; full run stopped at SQLAlchemy import because backend/.venv Python 3.11 base is broken
Vue files changed: no (npm ci/build not required)
workflow/Docker/registry/DB/Alembic mutation: none
```

## 필요한 extension/권한/설치 요청

- GitHub 플러그인은 로그인 `gihohoho`가 확인됐지만 `gihohoho/upgrade-rpg` repository 설치 접근 권한이 아직 필요합니다. 다음 원격 검토 전에 기호에게 다시 요청합니다.
- repository Actions settings와 environment를 읽거나 설정할 권한이 다음 단계에 필요합니다.
- action upstream SHA 검토 후 workflow 파일 생성은 기호의 별도 승인이 필요합니다.
- 현재 Codex 실행 계정의 `backend/.venv`는 존재하지 않는 Python 3.11 원본을 가리킵니다. 전체 backend core smoke가 필요할 때 Python 3.11/가상환경 복구 설치 권한을 기호에게 요청합니다.
- 필요한 요청이 해결되지 않으면 다음 채팅에서도 다시 요청합니다.

## 다음 첫 작업

```bash
python tools/check_github_actions_ghcr_static_plan.py --strict
```

기대 결과: `github-actions-ghcr-static-plan-verified-workflow-not-created`

다음 안전 단계는 action별 upstream 40자리 SHA, repository Actions 설정, `ghcr-production-publish` environment를 읽기 전용으로 검토하고 workflow 파일 생성 승인 여부를 기호에게 묻는 것입니다.

## 계속 금지

- `.github/workflows/` 생성과 workflow 실행
- 실제 registry token/PAT/credential 및 production secret
- Docker login/pull/build/push/up/down
- container/network/volume mutation
- DB/Alembic mutation
- API/auth/write/Vue write
- 게임 콘텐츠/밸런스 변경
- 자동 deploy와 production image reference 갱신

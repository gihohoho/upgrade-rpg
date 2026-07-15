# Upgrade RPG Codex handoff — v320

## 기준

- handoff mode: current repository + Git `main` (ZIP 없음)
- latest: `v320.github-actions-ghcr-workflow-prepared-gated`
- Codex 규칙: `AGENTS.md`
- backend virtualenv: `backend/.venv`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- change delivery: Codex가 검증 후 직접 add/commit/push
- 개발 서버: backend `127.0.0.1:8000` PID 32476, frontend `127.0.0.1:5173` PID 12064, HTTP 200 확인 후 계속 재사용

## 계속 적용되는 기호의 권한

- VS Code/Codex 터미널 사용과 실행 중인 개발 서버 재사용 허용
- GitHub Actions, workflow, action SHA, environment, variables와 필요한 repository 설정 작업 허용
- 숨김 파일과 `.env` 점검·수정 허용
- 실제 secret의 Git·로그·채팅·artifact 노출과 커밋은 계속 금지
- 나중에 교체할 보안 항목은 `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`에 기록
- 필요한 extension, 권한, 설치, 사용자 계정 작업은 기호에게 요청하고 미해결 시 다음 handoff에도 반복
- ZIP과 사용자용 Git 명령은 기본 제공하지 않음

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
```

`gihohoho`는 기호가 직접 확인한 고정 namespace입니다.

## v320 GitHub repository 설정

```txt
GitHub App/Connector scope: gihohoho/upgrade-rpg selected repository only
GitHub App 연결과 repository 읽기 권한은 해결됨
Actions policy: gihohoho + selected external actions
full-length action SHA required: yes
GitHub-owned actions blanket: off
Marketplace verified creators blanket: off
default GITHUB_TOKEN: read contents and packages
Actions create/approve PR: off
fork write tokens/secrets: off/off
workflow file/creation approved: yes/yes
workflow execution approved/executed: yes/no
CI workflow/login/build/push approved: yes/yes/yes/yes
CI login/build/push executed: no/no/no
publish environment: ghcr-production-publish
environment branch rule: main only
environment secrets/variables: 0/0
owner 외 collaborators: 0
required reviewer/prevent self-review: missing/missing
PUBLISH_REVIEWER_GATE_READY: source-controlled false
deterministic dependency/toolchain lock: incomplete (required before first publish)
GitHub settings evidence: 2026-07-15 browser snapshot; live recheck required before gate change
publish allowed now: no
```

repository Actions 설정은 실제 변경됐고, 승인한 8개 외부 action만 전체 SHA로 허용합니다. `ghcr-production-publish` environment도 만들고 `main` branch rule을 적용했습니다.

## v320 workflow

파일: `.github/workflows/publish-backend-ghcr.yml`

```txt
trigger: workflow_dispatch only
reviewed workflow source SHA-256: 83393cb875cf43ce1bc30d245c100482818af96cd7b5417d81b9cb45ce62a993
reviewed workflow semantic SHA-256: 2f1b1baf3f7db363f2f175b98623ec97e59a785592ae32d023f4b5123f2bd4c0
required ref/source: refs/heads/main / exact 40-char github.sha
required inputs: source_commit, approval_reason, confirm_publish
default/validate/build-scan permissions: contents read only
publish permissions: contents read + packages write + id-token write
pre-push: static checks -> local OCI -> SPDX SBOM -> checksum-pinned HIGH/CRITICAL Trivy gate
post-push: exact digest -> Docker BuildKit mode=max provenance/SBOM -> inspect -> exact-digest Trivy -> Cosign keyless sign/verify
root Docker context env files: excluded by enforced .dockerignore patterns
deterministic dependency/toolchain lock: incomplete; first publish blocked until resolved
automatic deploy/production reference update: no/no
```

개인 비공개 저장소에서는 GitHub Artifact Attestations API를 사용할 수 없어 `actions/attest`와 `attestations: write`는 제거했습니다.

publish job의 첫 단계는 source-controlled `PUBLISH_REVIEWER_GATE_READY`가 정확히 `true`인지 확인합니다. 이 값은 현재 workflow에 리터럴 `"false"`로 고정됐고 repository/environment variable을 참조하지 않습니다. 검사는 GHCR login보다 앞에 있어 workflow가 실수로 수동 실행돼도 registry 접근 전에 실패합니다.

## 현재 판단 파일

- `.github/workflows/publish-backend-ghcr.yml`
- `deploy/github-actions-ghcr-static-plan.example.json`
- `deploy/backend-image-ghcr-policy.example.json`
- `docs/current/GITHUB_ACTIONS_GHCR_STATIC_WORKFLOW_PLAN.md`
- `docs/current/BACKEND_IMAGE_GHCR_POLICY.md`
- `docs/current/SECURITY_ROTATION_AND_GITHUB_GATES.md`
- `tools/check_github_actions_ghcr_static_plan.py`
- `tools/check_codex_handoff_readiness.py`

## v320 검증 기준

```txt
GitHub Actions/GHCR strict checker: passed
GitHub Actions fail-closed mutation smoke: passed
workflow source + semantic lock bypass audit (extra secret step / || true / step reorder): blocked
per-step lock / parsed secret path / Docker env-context mutation smoke: passed
Codex handoff strict/synchronization smoke: passed
Python compileall / JavaScript / Bash / JSON syntax: passed
full core smoke: passed (101.6s with backend/.venv)
Vue files changed: no (npm ci/build not required)
workflow/Docker/registry/DB/Alembic execution: none
backend/frontend reused without restart: HTTP 200/200
```

정상 결과:

```txt
result: github-actions-ghcr-workflow-prepared-publish-gated
next safe stage: choose-private-repository-publish-approval-model
```

## 필요한 extension/권한/설치/사용자 작업

- 새 extension/패키지 설치: 없음
- GitHub Connector와 브라우저 repository 접근: 해결됨
- 로컬 `gh` CLI의 저장된 기존 계정 token은 401로 만료됐지만 현재 작업은 로그인된 GitHub 브라우저/Connector로 처리되어 막히지 않음
- GitHub Free/Pro/Team의 required reviewer는 공개 저장소 전용이어서 현재 비공개 저장소에서는 collaborator 추가만으로 해결되지 않음
- 기호가 `Enterprise Cloud required reviewer`, `owner-only source-controlled 2단계 승인`, `게시 계속 비활성화` 중 하나를 선택해야 함
- 승인 모델을 선택하기 전에는 source-controlled `PUBLISH_REVIEWER_GATE_READY`를 바꾸지 않음
- 게시 허용 모델을 선택해도 dependency/toolchain hash lock과 GitHub live 설정 재확인 전에는 gate를 바꾸지 않음

## 다음 첫 작업

프로젝트 루트에서 `backend/.venv`를 켠 상태로 다음 읽기 전용 검사를 먼저 실행합니다.

```bash
python tools/check_github_actions_ghcr_static_plan.py --strict
python tools/check_codex_handoff_readiness.py --strict
```

검사가 통과하면 기호에게 비공개 저장소 게시 승인 모델을 선택해달라고 요청합니다. Enterprise Cloud를 선택한 경우에만 collaborator/required reviewer/prevent self-review를 구성합니다. owner-only 모델을 선택하면 독립 reviewer가 없다는 위험을 문서로 승인받습니다. 어느 게시 허용 모델이든 dependency/toolchain hash lock과 GitHub live 설정 재확인까지 끝난 별도 commit에서만 gate 변경을 검토합니다. 게시 비활성화를 선택하면 현재 hard gate를 유지합니다.

## 계속 별도 요청이 필요한 범위

- DB write/restore/reset/seed와 Alembic mutation
- 인증/API route·response body/write logic
- Vue Preview/Apply/write
- 게임 콘텐츠와 밸런스
- production container/network/volume과 Compose up/down
- 자동 deploy와 production image reference 변경

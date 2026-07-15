# Current Status — v319

## 현재 기준

- 최신 작업: `v319.github-connector-actions-settings-reviewed`
- handoff: current repository + Git `main` (ZIP 기본 생성 안 함)
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 고정 PostgreSQL/Alembic 상태

```txt
classification: alembic-managed-baseline-complete
source DB: rpg_game
source public tables/rows: 23/749
source application tables/rows: 22/748
current revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
next revision required: no
```

## 운영 방향

```txt
managed PostgreSQL + provider CA verify-full
external reverse proxy HTTPS
backend replicas/workers: 1/1
max_connections review candidate: 40
Compose config render: 기호 PC 통과
```

## GHCR와 Codex 인수인계

```txt
GitHub remote: https://github.com/gihohoho/upgrade-rpg.git
namespace: gihohoho
repository: ghcr.io/gihohoho/upgrade-rpg-backend
visibility: private
target platform: linux/amd64
base image digest approved: yes
CI credential strategy: GitHub Actions GITHUB_TOKEN 우선
local credential strategy: deferred
workflow/login/pull/build/push approved: no/no/no/no/no
GitHub Actions static plan present/verified: yes/yes
workflow file/action SHA candidates reviewed/action SHAs approved/environment configured: no/yes/no/no
GitHub connector selected repository access: gihohoho/upgrade-rpg only / verified
repository Actions settings reviewed/changed: yes/no
publish environment reviewed/configured: yes/no
```

## GitHub Actions / GHCR 정적 설계

```txt
trigger: workflow_dispatch only
ref/source: refs/heads/main / exact 40-char github.sha
default/validate/build-scan permissions: contents read only
publish permissions: contents read + packages/attestations/id-token write
pre-push: local OCI + SPDX SBOM + Trivy HIGH/CRITICAL fail-closed
post-push: exact digest + provenance + SBOM attestation + Sigstore keyless signature + verify
automatic deploy/production reference update: no/no
action SHA candidates: 9개 최신 정식 release tag와 upstream 40자리 commit 대조 완료
action SHA approval: no
```

## v319 GitHub repository 읽기 전용 검토

```txt
ChatGPT Codex Connector owner/scope: gihohoho / selected repositories only
selected repository: gihohoho/upgrade-rpg
Actions allowed policy: allow all actions and reusable workflows
require full-length action SHA: off
artifact/log retention: 90 days
fork workflows: run=yes, write tokens=no, secrets=no, approval=yes
default GITHUB_TOKEN: read contents and packages
Actions create/approve PR: off
private reusable workflow access: not accessible
ghcr-production-publish environment: absent
```

연결과 읽기 권한은 해결됐지만 repository 설정은 바꾸지 않았습니다. 다음 승인 경계는 외부 action을 검토한 9개 repository로 제한하고 full-length SHA 강제를 켜는 Actions settings 변경입니다. Environment 생성과 workflow 파일 생성은 아직 별도 승인 전입니다.

Codex는 루트 `AGENTS.md`를 우선 읽습니다. 첫 검사는 `python tools/check_github_actions_ghcr_static_plan.py --strict`입니다.

## 계속 보류

- 실제 secret/credential/TLS 적용
- Docker runtime 및 registry mutation
- DB/Alembic mutation
- Vue write/인증 연결
- 게임 콘텐츠와 밸런스 개발

## 필요한 권한/설치

- GitHub App 연결과 `gihohoho/upgrade-rpg` repository 읽기 권한은 해결됨
- 다음 단계의 repository Actions settings 변경은 기호의 별도 승인 필요
- `ghcr-production-publish` environment 생성과 workflow 파일 생성도 이후 각각 별도 승인 필요
- Python 3.11.4와 `backend/.venv`는 정상 확인되어 추가 설치가 필요하지 않음
- 해결되지 않은 요청은 다음 작업에서도 다시 요청

## v319 검증

- GitHub connector/Actions settings review strict/fail-closed smoke 통과
- Codex handoff strict/synchronization smoke와 docs index/archive smoke 통과
- Python compileall, 전체 JavaScript/Bash/JSON 문법 검사 통과
- `backend/.venv` 활성화 상태 전체 core smoke 통과
- Windows cp949 실행 차단 안내, 실제 보고서와 smoke 격리, 가짜 Docker 실행 호환성 수정 및 전용 smoke 통과
- Vue 변경 없음, Docker/registry/DB/Alembic mutation 없음
- `.github/workflows/` 없음, workflow 실행 없음
- GitHub App은 `gihohoho/upgrade-rpg` 하나만 허용, repository settings/environment 변경 없음

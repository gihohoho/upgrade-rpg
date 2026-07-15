# Upgrade RPG Codex handoff — v315

## 기준

- ZIP: `rpg_v315_codex_ghcr_namespace_handoff_ready.zip`
- latest: `v315.codex-ghcr-namespace-handoff-ready`
- Codex 규칙: `AGENTS.md`
- backend virtualenv: `backend/.venv`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

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

## v315 검증 완료

```txt
Codex handoff strict checker: passed
Codex/GHCR fail-closed smoke: passed
handoff/document synchronization: passed
docs index/archive smoke: passed
Python compileall: passed
JavaScript node --check: passed
Bash syntax: passed
JSON parse: passed
core smoke: 전체 명령을 환경 제한 때문에 구간별 실행, 모두 passed
Vue files changed: no (npm ci/build not required)
Docker/registry/DB/Alembic mutation: none
```

## 다음 첫 작업

```bash
python tools/check_codex_handoff_readiness.py --strict
```

기대 결과: `codex-ghcr-namespace-handoff-verified-workflow-plan-only`

다음 안전 단계는 GitHub Actions permissions/trigger/supply-chain gate의 정적 설계입니다. `.github/workflows/` 생성과 registry/Docker 실행은 아직 승인되지 않았습니다.

## 계속 금지

- 실제 registry token/PAT/credential 및 production secret
- Docker login/pull/build/push/up/down
- container/network/volume mutation
- DB/Alembic mutation
- API/auth/write/Vue write
- 게임 콘텐츠/밸런스 변경

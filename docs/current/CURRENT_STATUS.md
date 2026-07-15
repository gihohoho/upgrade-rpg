# Current Status — v316

## 현재 기준

- 최신 작업: `v316.codex-handoff-audit-fix`
- 기준 ZIP: `rpg_v316_codex_handoff_audit_fix.zip`
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
```

Codex는 루트 `AGENTS.md`를 우선 읽습니다. 첫 검사는 `python tools/check_codex_handoff_readiness.py --strict`입니다.

## 계속 보류

- 실제 secret/credential/TLS 적용
- Docker runtime 및 registry mutation
- DB/Alembic mutation
- Vue write/인증 연결
- 게임 콘텐츠와 밸런스 개발

## v316 검증

- strict checker와 fail-closed smoke 통과 (`git-index` workspace / `filesystem-absence` ZIP)
- Python/JavaScript/Bash/JSON 문법 통과
- 관련 v316 전용 smoke와 정적 구간 통과; 전체 core는 깨진 `backend/.venv` 기반 Python 때문에 SQLAlchemy import에서 중단
- Vue 변경 없음, Docker/registry/DB/Alembic mutation 없음
- v315에서 남은 superseded 활성 파일과 실행되지 않는 옛 smoke 제거

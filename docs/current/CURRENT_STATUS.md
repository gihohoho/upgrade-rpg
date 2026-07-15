# Current Status — v308

## 현재 기준

- 최신 작업: `v308.runtime-config-hardening-ready`
- 기준 ZIP: `rpg_v308_runtime_config_hardening_ready.zip`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 PostgreSQL/Alembic 상태

```txt
classification: alembic-managed-baseline-complete
source rpg_game: 23/749
application: 22/748
current revision: v295_initial_schema
restore rehearsal: 23/749 / verified
migration test DB: 23/1 / differences=0
v306 candidate operations: 0 / next revision required no
v307 runtime readiness + live health: passed
v307 production hardening warnings: 12
```

## v308 준비 내용

```txt
explicit pool policy: 5 options
FastAPI shutdown: await engine.dispose()
production unsafe defaults: fail closed
backend Dockerfile: non-root / no automatic Alembic
deploy/docker-compose.production.yml: separate review template
local docker-compose.yml: preserved
actual backend/.env: unchanged
```

## 다음 첫 작업

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
```

정상 예상 분류:

```txt
result: runtime-config-hardening-verified-local-runtime-preserved
next safe stage: separate-production-secrets-tls-and-container-validation
```

## 계속 금지

- 실제 `.env` 및 운영 secret 입력
- production Compose build/up/pull
- Docker container/volume 변경 또는 삭제
- source/rehearsal stamp 재실행
- revision/autogenerate/upgrade/downgrade
- seed/인증/API body/route/write 변경
- 게임 콘텐츠/밸런스 변경

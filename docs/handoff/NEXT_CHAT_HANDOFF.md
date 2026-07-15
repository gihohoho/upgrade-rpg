# NEXT CHAT HANDOFF — Upgrade RPG v308

## 기준 ZIP

- `rpg_v308_runtime_config_hardening_ready.zip`

## 현재 버전

- 최신 작업: `v308.runtime-config-hardening-ready`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 DB 상태

```txt
source rpg_game:
  public tables/rows 23/749
  application tables/rows 22/748
  current revision v295_initial_schema
  classification alembic-managed-baseline-complete
  v304 execution report verified

restore rehearsal rpg_game_restore_rehearsal_v290:
  public tables/rows 23/749
  application tables/rows 22/748
  current revision v295_initial_schema
  v302 execution report verified

migration rpg_game_migration_empty_v290:
  public tables/rows 23/1
  current revision v295_initial_schema
  differences=0
```

## 고정 증거

```txt
backup: local-backups/postgres/rpg_game_20260714_130403_KST_v290.custom.dump
backup SHA-256: b103d71370815478a6b3900854e7959b7d6c037c5f46c42da154855a24eff481
revision: v295_initial_schema
revision SHA-256: 24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa
schema digest: 7cd69d4f4ee1a4b71c999d518379c1e6b782cb73f90adbf467d0b9b26846c921
data digest: ecb19e57283dc6b780426339bfc46f2bac14da63a618249808f30132508f9244
```

로컬 backup과 review evidence는 Git/ZIP/채팅에 포함하지 않습니다.

## 사용자 PC에서 실제 완료

```txt
v298 first upgrade: passed
v299 downgrade base: passed
v300 second upgrade: passed
first/second upgrade signatures: identical
v301 source preflight: passed
v302 rehearsal stamp: passed
v303 rehearsal post-check: restore-rehearsal-stamp-current-state-verified
v304 source post-check: source-baseline-stamp-current-state-verified
v305 completion check: postgres-baseline-completion-state-verified
v306 next revision preflight: next-revision-not-required-current-schema-equivalent
v306 Alembic candidate operations: 0
v307 strict + require-health: passed
v307 exact runtime DB/driver: rpg_game / postgresql+asyncpg
v307 Docker PostgreSQL: running/healthy
v307 production hardening warnings: 12
```

## v308 추가 내용

```txt
backend/app/core/config.py
backend/app/db/session.py
backend/app/main.py
backend/.env.example
backend/Dockerfile
deploy/docker-compose.production.yml
deploy/README.md
tools/check_runtime_config_hardening.py
tools/smoke/backend/smoke_runtime_config_hardening.py
docs/current/POSTGRES_RUNTIME_CONFIG_HARDENING.md
docs/current/POSTGRES_PRODUCTION_DEPLOYMENT_TEMPLATE.md
```

v308에서 보강한 경계:

- `pool_pre_ping`, pool size, overflow, timeout, recycle 명시
- local 기본 pool: true / 5 / 10 / 30 / 1800
- FastAPI lifespan 종료 시 `await engine.dispose()`
- lifespan에는 create_all/Alembic/schema reset 없음
- production에서 DEBUG=true, 로컬 기본 secret, 32자 미만 secret 차단
- non-root FastAPI Dockerfile
- Dockerfile command에 자동 Alembic 없음
- 별도 production Compose template
- production template에 Adminer와 PostgreSQL host port 없음
- actual `backend/.env`와 local `docker-compose.yml` 미변경

## 다음 첫 작업

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
```

정상 기대 핵심:

```txt
explicit SQLAlchemy pool options: 5
FastAPI shutdown engine.dispose lifecycle: True
unsafe production defaults blocked: True
safe production settings accepted: True
production Compose: Adminer=False / PostgreSQL host port=False
local docker-compose behavior preserved: True
result: runtime-config-hardening-verified-local-runtime-preserved
next safe stage: separate-production-secrets-tls-and-container-validation
```

## 다음 안전 순서

1. v308 실제 strict + health 결과 확인
2. local runtime과 DB health 회귀 없음 확인
3. 남은 warning을 secret/TLS/image/reverse proxy로 분류
4. production Compose는 실행하지 않고 정적 검증부터 보강
5. 실제 운영 secret/TLS/Docker build는 별도 승인 전 금지
6. worker/pool/max_connections 계산과 container health 설계
7. 이후 isolated deployment candidate smoke로 이동

## 절대 변경/실행 금지

- actual `.env`와 production secret
- production Compose build/up/pull/down
- Docker container/volume 변경 또는 삭제
- source/rehearsal `stamp` 재실행
- 새 Alembic revision/autogenerate
- source/rehearsal/migration `upgrade`/`downgrade`
- DB 생성/삭제/복원
- seed
- 인증
- 기존 API route path/response body
- 실제 write 로직/Write Guard
- Preview/Apply request body
- 게임 콘텐츠/밸런스 변경

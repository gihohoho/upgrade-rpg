# NEXT CHAT HANDOFF — Upgrade RPG v309

## 기준 ZIP

- `rpg_v309_runtime_engine_source_binding_inspector_fix_ready.zip`

## 현재 버전

- 최신 작업: `v309.runtime-engine-source-binding-inspector-fix`
- readiness: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- backend virtualenv: `backend/.venv`

## 실제 DB 상태

```txt
source rpg_game:
  public tables/rows 23/749
  application tables/rows 22/748
  current revision v295_initial_schema
  v304 source post-check source-baseline-stamp-current-state-verified
restore rehearsal rpg_game_restore_rehearsal_v290:
  public tables/rows 23/749
  application tables/rows 22/748
  v302 report verified
migration rpg_game_migration_empty_v290:
  public tables/rows 23/1
  differences=0
classification: alembic-managed-baseline-complete
v306 candidate operations: 0
v307 strict + require-health: passed
v307 Docker PostgreSQL: running/healthy
```

## v308 적용 상태

```txt
pool policy: pre_ping/size/overflow/timeout/recycle
shutdown: await engine.dispose()
production unsafe defaults: fail closed
backend Dockerfile: non-root / no automatic Alembic
production Compose: no Adminer / no PostgreSQL host port
actual backend/.env and local docker-compose.yml: unchanged
```

## 사용자 PC에서 발생한 v308 검사 결과

```txt
result: blocked-or-failed
reason: DeploymentRuntimeReadinessError: runtime engine bypasses settings.database_url
```

원인: 실제 `backend/app/db/session.py`는 계속 `settings.database_url`을 사용했지만, 검사기가 `create_async_engine(settings.database_url`이 한 줄에 붙어 있는 경우만 찾았습니다. v308 pool 옵션으로 호출이 여러 줄이 되면서 오탐이 발생했습니다.

## v309 수정

```txt
AST-based create_async_engine binding inspection
multiline positional settings.database_url: allowed
url=settings.database_url: allowed
literal URL / other settings attribute: blocked
runtime/DB/.env/Docker/Alembic mutation: none
```

추가 파일:

```txt
tools/smoke/backend/smoke_runtime_engine_source_binding_inspector.py
docs/current/POSTGRES_RUNTIME_ENGINE_BINDING_INSPECTOR_FIX.md
```

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

정상 기대:

```txt
result: runtime-config-hardening-verified-local-runtime-preserved
next safe stage: separate-production-secrets-tls-and-container-validation
```

## 다음 안전 순서

1. v309 strict + health 결과 확인
2. 남은 production warnings 재수집
3. production secret/TLS/image/reverse proxy 정적 검증 준비
4. worker/pool/max_connections 계산
5. 실제 production Compose/build/secret 입력은 별도 승인

## 절대 변경/실행 금지

- actual `.env`와 production secret
- production Compose build/up/pull/down
- Docker container/volume 변경 또는 삭제
- source/rehearsal `stamp` 재실행
- 새 Alembic revision/autogenerate/upgrade/downgrade
- DB 생성/삭제/복원
- seed/인증/API route/body/write
- 게임 콘텐츠/밸런스 변경

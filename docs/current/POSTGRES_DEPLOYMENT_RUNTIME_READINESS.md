# PostgreSQL/FastAPI 운영·배포 runtime readiness — v307

## 목적

v307은 완료된 PostgreSQL baseline을 유지하면서 실제 배포 전에 필요한 runtime 경계를 읽기 전용으로 점검합니다.
DB, `.env`, Docker container/volume, Alembic history는 변경하지 않습니다.

v371 현재 local source graph head는 `v371_email_identity_lifecycle`이지만 local/live/Neon
DB current는 계속 `v295_initial_schema`입니다. 아래 v306 equivalent 판정은 v307 당시
역사이며, v371 source는 아직 적용하지 않았습니다. runtime startup 자동 migration 금지는
그대로 유지됩니다.

## 추가 파일

```txt
tools/check_postgres_deployment_runtime_readiness.py
tools/smoke/backend/smoke_postgres_deployment_runtime_readiness.py
docs/current/POSTGRES_DEPLOYMENT_RUNTIME_READINESS.md
docs/current/POSTGRES_DEPLOYMENT_MIGRATION_RUNBOOK.md
```

## 점검 범위

### PostgreSQL/Alembic

- v305 baseline completion 유지
- v306 당시 `next-revision-not-required-current-schema-equivalent` 역사 보존
- local source graph head `v371_email_identity_lifecycle` / applied DB current v295 분리
- runtime `DATABASE_URL`이 `postgresql+asyncpg`인지
- runtime DB가 exact `rpg_game`인지
- rehearsal/migration DB가 runtime URL로 사용되지 않는지
- live current revision이 `v295_initial_schema`인지
- DB identity와 `SELECT 1`을 read-only transaction에서 확인

### FastAPI

- `create_async_engine(settings.database_url)` 사용
- `AsyncSession` dependency lifecycle 유지
- startup/lifespan에 `create_all`, `upgrade`, `stamp`, schema reset이 없는지
- `GET /api/v1/health/db`가 `SELECT 1`만 실행하고 commit/비밀값 노출이 없는지
- Alembic online env가 동일한 settings URL과 `NullPool`을 사용하는지
- 위험한 `setup_dev_db.py --reset`이 앱 runtime 밖 CLI로 분리되어 있는지

### 환경 설정

- `backend/.env.example` 필수 키 존재
- 실제 `backend/.env`는 값이 아니라 **키 이름만** 확인
- DB 비밀번호, JWT secret, 관리자 쓰기 키는 출력하지 않음
- production일 때 `DEBUG=false`와 로컬 기본 secret 미사용을 필수로 검사
- v371 production은 `EMAIL_PROVIDER=brevo`, `BREVO_API_KEY`, 인증된 sender,
  `EMAIL_TOKEN_SECRET`, exact HTTPS `PUBLIC_FRONTEND_ORIGIN`을 추가로 요구하며 값은
  secret-safe inventory로만 확인
- `EMAIL_TOKEN_SECRET`은 32자 이상이고 `JWT_SECRET_KEY`와 달라야 하며 owner bootstrap
  password는 startup runtime이 사용하지 않음

### Docker

읽기 전용 명령만 실행합니다.

```txt
docker compose ps --format json
docker compose config --format json
```

확인 항목:

- PostgreSQL 16 service
- `restart: unless-stopped`
- `pg_isready` healthcheck
- named volume `rpg_postgres_data`
- 실제 container running/healthy

다음은 로컬에서는 허용되지만 운영 전 보강 경고입니다.

- compose 안의 로컬 고정 비밀번호
- PostgreSQL host port 55432 공개
- Adminer 8081 공개
- image digest 미고정
- DB TLS 미설정
- FastAPI Dockerfile 부재
- 명시적 connection pool 옵션 부재
- app shutdown의 `engine.dispose()` lifecycle 부재

## 실행 방법

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 Git Bash

```bash
source .venv/Scripts/activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_postgres_deployment_runtime_readiness.py --strict
```

FastAPI 서버까지 켜져 있는 상태에서 live health를 필수로 확인할 때만:

```bash
python tools/check_postgres_deployment_runtime_readiness.py --strict --require-health
```

`--require-health`를 사용하지 않으면 서버가 꺼져 있어도 health GET은 경고로만 표시합니다.

## 예상 분류

현재 로컬 개발 구성을 유지한 상태에서는 다음 결과가 정상입니다.

```txt
result: local-runtime-readiness-verified-production-hardening-required
next safe stage: separate-runtime-config-hardening-without-db-mutation
```

이 결과는 DB baseline/runtime 경계는 정상이나, 운영 배포용 secret, pool, TLS, container image 구성이 아직 별도 보강되어야 한다는 의미입니다.

## 절대 실행하지 않는 것

```txt
.env 수정
docker compose up/down/restart
docker volume rm
docker compose down -v
alembic revision/autogenerate
alembic stamp/upgrade/downgrade
DB create/drop/restore
setup_dev_db.py --reset
row write
```

## v308 후속 반영

v307에서 경고였던 명시적 pool 정책, `engine.dispose()` lifecycle, FastAPI Dockerfile 부재는 v308에서 보강했습니다.
로컬 secret, 로컬 Compose 공개 포트, 운영 TLS/digest/secret 실제 입력은 아직 별도 승인 대상입니다.

## v309 검사기 오탐 수정

`create_async_engine()`의 여러 줄 호출을 한 줄 문자열로만 검사하던 v307 정적 판정을 Python AST 기반으로 교체했습니다. 실제 runtime은 계속 `settings.database_url`을 사용하며, DB·`.env`·Docker·Alembic·pool 동작은 변경하지 않았습니다. 전용 회귀 smoke는 여러 줄/keyword 호출을 허용하고 literal 또는 다른 settings 속성은 차단합니다.

## 사용자 PC 실제 완료 상태

v307 `--strict --require-health`가 실제 통과했고, v308/v309 보강 후 runtime hardening 검사도 통과했습니다. 현재 로컬 runtime은 유지하며 남은 9개 경고는 production secret/TLS/digest/로컬 공개 포트 분리 항목입니다.

v310에서는 실제 Docker 명령이나 secret 입력 없이 production template만 정적으로 검증합니다.

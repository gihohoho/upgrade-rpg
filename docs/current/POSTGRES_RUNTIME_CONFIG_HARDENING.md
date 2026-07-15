# FastAPI/PostgreSQL runtime config hardening — v308

## 목적

v308은 v307에서 확인된 로컬 runtime 정상 상태를 유지하면서 DB schema/data를 변경하지 않고 FastAPI runtime 설정을 보강합니다.
실제 `backend/.env`, Docker container/volume, Alembic history는 변경하지 않습니다.

## 적용한 안전 보강

### SQLAlchemy async pool

`backend/app/core/config.py`와 `backend/app/db/session.py`에 다음 환경변수 기반 정책을 추가했습니다.

```txt
DB_POOL_PRE_PING=true
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT_SECONDS=30
DB_POOL_RECYCLE_SECONDS=1800
```

`pool_pre_ping`은 끊어진 연결을 재사용하기 전에 확인합니다. 나머지 값은 로컬 기본값이며 운영 worker 수와 PostgreSQL `max_connections`를 계산한 뒤 환경변수로 조정합니다.

### FastAPI shutdown lifecycle

`backend/app/main.py`의 lifespan 종료 경계에서 `await engine.dispose()`를 실행합니다.
이 lifecycle은 pooled connection을 정리할 뿐이며 다음을 실행하지 않습니다.

```txt
create_all
revision/autogenerate
stamp
upgrade
downgrade
schema reset
row write
```

### production fail-closed guard

`ENVIRONMENT=production` 또는 `prod`일 때 다음 조건을 만족하지 않으면 Settings 로딩 단계에서 차단합니다.

- `DEBUG=false`
- `JWT_SECRET_KEY`가 로컬 기본값이 아님
- `ADMIN_WRITE_DEV_KEY`가 로컬 기본값이 아님
- 두 secret 모두 32자 이상

실제 비밀값은 프로젝트 파일이나 검사 결과에 저장하지 않습니다.

## 읽기 전용 확인 도구

```txt
tools/check_runtime_config_hardening.py
tools/smoke/backend/smoke_runtime_config_hardening.py
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_runtime_config_hardening.py --strict --require-health
```

정상 결과:

```txt
result: runtime-config-hardening-verified-local-runtime-preserved
next safe stage: separate-production-secrets-tls-and-container-validation
```

## 유지한 경계

- 실제 `.env` 미변경
- 로컬 `docker-compose.yml` 동작 유지
- DB schema/data 미변경
- Alembic revision 1개 유지
- API route path/response body 미변경
- seed/auth/write/game content 미변경
- Docker build/up/down/restart/remove 미실행

## v309 검사기 오탐 수정

`create_async_engine()`의 여러 줄 호출을 한 줄 문자열로만 검사하던 v307 정적 판정을 Python AST 기반으로 교체했습니다. 실제 runtime은 계속 `settings.database_url`을 사용하며, DB·`.env`·Docker·Alembic·pool 동작은 변경하지 않았습니다. 전용 회귀 smoke는 여러 줄/keyword 호출을 허용하고 literal 또는 다른 settings 속성은 차단합니다.

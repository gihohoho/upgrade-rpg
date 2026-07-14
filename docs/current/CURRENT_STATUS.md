# Current Status — v284

## 현재 기준

- 최신 작업: `v284.alembic-async-env-fix`
- 기준 ZIP: `rpg_v284_alembic_async_env_fix.zip`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- 실제 backend 가상환경: `backend/.venv`

## v284 완료

- 기호 컴퓨터의 `python -m alembic current` 실제 결과에서 `MissingGreenlet` 확인
- 원인: `postgresql+asyncpg` URL을 sync `engine_from_config()`로 연결
- `backend/alembic/env.py`를 async engine 구조로 수정
- `tools/check_alembic_readonly_state.py` 추가
- `tools/smoke/backend/smoke_backend_alembic_async_env.py` 추가
- PostgreSQL/Alembic 보고서와 로컬 체크리스트 갱신

## 현재 Alembic 상태

- `alembic.ini`, `env.py` 존재
- asyncpg 호환 online env 적용
- `versions/` 없음
- revision 0개
- `script.py.mako` 없음
- 실제 schema 기준은 아직 `Base.metadata.create_all()`

## 변경하지 않은 것

- DB schema 및 데이터
- Docker volume
- `.env`
- seed
- Alembic revision 생성
- upgrade/downgrade/stamp
- API route path/response body
- 인증/Write Guard/write 로직
- Vue GET 화면
- 게임 콘텐츠

## 다음 확인

v284 ZIP 적용 후 아래 읽기 전용 결과를 수집합니다.

```bash
python tools/check_alembic_readonly_state.py
```

그다음 Docker container/volume, `/api/v1/health/db`, 보존할 DB 데이터 존재 여부를 확인합니다.

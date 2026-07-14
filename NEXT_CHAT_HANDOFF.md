# NEXT CHAT HANDOFF — Upgrade RPG v284

## 최신 ZIP

- `rpg_v284_alembic_async_env_fix.zip`

## 현재 기준

- 최신 작업: `v284.alembic-async-env-fix`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`
- 실제 backend 가상환경: `backend/.venv`

## 사용자 응답 규칙

- 한국어로 쉽고 자세하게 설명
- 모든 명령 앞에 실행 위치 표시
- npm/Vue 명령은 `.venv` 불필요 여부 표시
- Python/FastAPI/Alembic 명령은 `backend/.venv` 활성 여부 표시
- 설치 파일/라이브러리/프레임워크와 사용자 확인 항목 안내
- git 명령은 프로젝트 루트에서 한 줄

## v284 완료

- 사용자 실제 `python -m alembic current` 결과에서 `MissingGreenlet` 확인
- 원인: asyncpg URL + sync `engine_from_config()`
- `backend/alembic/env.py`를 async engine 구조로 수정
- `async_engine_from_config()` + `connection.run_sync()` 적용
- 읽기 전용 `tools/check_alembic_readonly_state.py` 추가
- 전용 `smoke_backend_alembic_async_env.py` 추가 및 core smoke 등록
- PostgreSQL/Alembic readiness 문서 갱신

## 변경 금지/보류

- DB schema/data/volume
- `.env`/seed
- Alembic revision/upgrade/downgrade/stamp
- 인증
- route path/API response body
- Write Guard/실제 write
- Preview/Apply 요청 body
- 기존 smoke/contract 의미
- 게임 콘텐츠

## 다음 추천 작업

`v285 로컬 PostgreSQL 비파괴 런타임 상태 확인`

먼저 v284 적용 후 아래 결과를 받습니다.

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때

```bash
.venv\Scripts\activate
```

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_alembic_readonly_state.py
```

그다음 container/volume, `/health/db`, 보존 데이터 여부를 삭제 없이 확인합니다.

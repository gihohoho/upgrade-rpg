# Backend Ready

현재 안정 readiness: `v250.backend-admin-rollback-snapshot`

Backend splitStatus: `admin-schema-field-constraint-contract-v238`

현재 프로젝트 작업 버전: `v284.alembic-async-env-fix`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- backend/frontend contract parity 유지
- apply route Write Guard 유지
- 기존 route path/API response body/write 의미 유지
- DB schema/data/env/seed/revision 변경 없음

## v284 Alembic 수정

- 사용자 실제 `MissingGreenlet` 결과 확인
- sync `engine_from_config()` 제거
- `async_engine_from_config()` + `connection.run_sync()` 적용
- 읽기 전용 `history/heads/current` 수집 도구 추가
- 전용 async env smoke 추가

## backend 가상환경

실행 위치: `backend` 폴더  
`.venv` 상태: 꺼져 있을 때 실행

```bash
.venv\Scripts\activate
```

의존성 누락 시에만:

실행 위치: `backend` 폴더  
`.venv` 상태: 켜진 상태

```bash
python -m pip install -e ".[dev]"
```

## 읽기 전용 Alembic 확인

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태

```bash
python tools/check_alembic_readonly_state.py
```

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
bash tools/run_smoke_core.sh && python -m compileall -q backend/app backend/scripts backend/alembic tools
```

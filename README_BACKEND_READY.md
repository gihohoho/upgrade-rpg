# Backend Ready — v298

현재 안정 readiness: `v250.backend-admin-rollback-snapshot`  
Backend splitStatus: `admin-schema-field-constraint-contract-v238`  
현재 프로젝트 작업 버전: `v298.postgres-initial-alembic-manual-review-upgrade-ready`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- backend/frontend contract parity 유지
- apply route Write Guard 유지
- 기존 route path/API response body/write 의미 유지
- 실제 backend virtualenv: `backend/.venv`

## PostgreSQL / Alembic 상태

- source: 22 tables / 748 rows / schema differences=0
- verified backup과 restore rehearsal 완료
- migration test DB: `alembic_version` 1 table / 0 rows / revision row 없음
- 최초 revision `v295_initial_schema` 생성 완료
- revision SHA-256: `24a30adb216e3a9809cb38c7b844be3020415978fd1e1dcb8b5f6482f85eabfa`
- 수동 검토: 22 tables / 209 columns / 42 indexes, model schema와 일치
- isolated migration DB의 `upgrade head` 실행 도구만 준비
- 원본 DB upgrade/stamp와 migration DB downgrade는 아직 승인 전

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

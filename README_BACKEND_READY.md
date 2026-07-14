# Backend Ready — v300

현재 안정 readiness: `v250.backend-admin-rollback-snapshot`  
Backend splitStatus: `admin-schema-field-constraint-contract-v238`  
현재 프로젝트 작업 버전: `v300.postgres-migration-roundtrip-reupgrade-ready`

## 핵심 보장

- 관리자 runtime route/OpenAPI/request/response/schema 계약 유지
- backend/frontend contract parity 유지
- apply route Write Guard 유지
- 기존 route path/API response body/write 의미 유지
- 실제 backend virtualenv: `backend/.venv`

## PostgreSQL / Alembic 상태

- source: 22 tables / 748 rows / schema differences=0
- verified backup과 restore rehearsal 완료
- 최초 revision `v295_initial_schema` 수동 검토 통과
- isolated migration DB 첫 `upgrade head` 실제 성공
- 같은 DB `downgrade base` 실제 성공
- 현재 migration DB: 빈 `alembic_version` placeholder / revision 없음 / differences=22
- v300: 두 번째 `upgrade head`와 첫 upgrade 결과의 exact signature 비교 가드 준비
- 원본 DB upgrade/stamp와 DB 삭제는 아직 승인하지 않음

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: `backend/.venv`가 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts backend/alembic tools
bash tools/run_smoke_core.sh
```

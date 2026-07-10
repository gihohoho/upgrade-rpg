# Upgrade RPG

현재 안정 버전: **v246.backend-admin-write-replay-safety-contract**

Backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 현재 상태

- 관리자 프론트 thin entry/helper 분리 완료
- `AdminService` facade 및 backend service split 유지
- 관리자 route module/facade 분리 완료
- runtime/OpenAPI/response/request/schema 계약 완료
- request payload·422·Content-Type·encoding·transport header 계약 완료
- preview 반복 parsing과 apply write guard 계약 완료
- backend/frontend 계약 목록과 routeContract 전체 parity 검사 적용
- DB, env, seed, API 주소, 응답 body 변경 없음

## 먼저 볼 파일

1. `NEXT_CHAT_PROMPT.md`
2. `NEXT_CHAT_HANDOFF.md`
3. `docs/CURRENT_STATUS.md`
4. `docs/NEXT_STEPS.md`
5. `docs/PROJECT_WORKING_RULES.md`
6. `docs/PROJECT_STRUCTURE.md`

## 핵심 검증

실행 위치: 프로젝트 루트

```bash
python tools/smoke_backend_admin_write_replay_safety_contract.py && python tools/smoke_backend_admin_frontend_contract_parity.py && node tools/smoke_admin_readonly_page.js && python tools/smoke_backend_admin_runtime_route_contract.py && python tools/smoke_backend_admin_request_metadata_contract.py && python tools/smoke_backend_admin_schema_model_contract.py && python tools/smoke_backend_admin_schema_field_constraint_contract.py && python -m compileall -q backend/app backend/scripts tools
```

## 서버 실행

실행 위치: backend 폴더

```bash
uvicorn app.main:app --reload
```

DB reset과 seed 재실행은 필요 없습니다.

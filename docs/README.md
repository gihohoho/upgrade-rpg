# Docs Index

## 새 채팅에서 먼저 볼 문서

1. `../NEXT_CHAT_PROMPT.md`
2. `../NEXT_CHAT_HANDOFF.md`
3. `CURRENT_STATUS.md`
4. `NEXT_STEPS.md`
5. `PROJECT_WORKING_RULES.md`
6. `PROJECT_STRUCTURE.md`
7. `../README_BACKEND_READY.md`
8. `CHANGELOG.md`

## 현재 관리자 backend 핵심 문서

- `BACKEND_ADMIN_SERVICE_SPLIT_CONTRACT.md`
- `BACKEND_ADMIN_ROUTE_RESPONSE_HELPER.md`
- `BACKEND_ADMIN_ROUTE_PARAMS_ERROR_HELPERS.md`
- `BACKEND_ADMIN_ROUTE_RESPONSE_DATA_META_HELPERS.md`
- `BACKEND_ADMIN_SCHEMA_MODEL_CONTRACT.md`
- `BACKEND_ADMIN_SCHEMA_FIELD_CONSTRAINT_CONTRACT.md`

v240 이후 request 경계 계약의 실제 기준은 아래 코드와 smoke입니다.

```text
backend/app/api/routes/admin_request_*_contract.py
backend/app/api/routes/admin_write_replay_safety_contract.py
tools/smoke_backend_admin_request_*_contract.py
tools/smoke_backend_admin_write_replay_safety_contract.py
```

## 실행·개발 환경

- `LOCAL_DEV_SETUP.md`
- `DOCKER_POSTGRES_GUIDE.md`
- `GIT_WORKFLOW.md`
- `BACKEND_ARCHITECTURE.md`

## 과거 단계 기록

과거 단계별 문서는 삭제하지 않고 아래에 보관합니다.

```text
docs/archive/stage-notes/
```

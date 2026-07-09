# Next Chat Start Guide

새 채팅에서 이 ZIP을 넘긴 뒤, 아래 순서로 시작하면 됩니다.

## 1. 먼저 현재 상태 확인

읽을 파일:

```txt
NEXT_CHAT_PROMPT.md
NEXT_CHAT_HANDOFF.md
docs/CURRENT_STATUS.md
docs/NEXT_STEPS.md
docs/BACKEND_ADMIN_SERVICE_MAP.md
```

## 2. smoke test 먼저 실행

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

전체 확인이 필요하면 아래도 실행합니다.

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_all.sh
```

## 3. 브라우저에서 관리자 readiness 확인

관리자 페이지 콘솔에서 실행합니다.

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().backendCreateLifecycleServiceSplitReady
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상값:

```txt
v201.backend-admin-create-lifecycle-service-split
true
create-lifecycle-extracted-v201
```

## 4. 다음 작업 시작

다음 추천 작업은 **v202 backend admin change log service split**입니다.

먼저 만들 파일 후보:

```txt
backend/app/services/admin/admin_change_log_service.py
tools/smoke_backend_admin_change_log_service_split.py
docs/BACKEND_ADMIN_CHANGE_LOG_SERVICE_SPLIT.md
```

## 5. v202 작업 원칙

- `AdminService`는 route import 호환을 위해 facade로 유지합니다.
- `backend/app/api/routes/admin.py`는 변경하지 않습니다.
- schema/API 응답 구조를 바꾸지 않습니다.
- DB schema/env를 바꾸지 않습니다.
- create-delete/restore는 v201 `AdminCreateLifecycleService`에 유지합니다.
- change log list/detail/rollback만 새 service로 이동합니다.

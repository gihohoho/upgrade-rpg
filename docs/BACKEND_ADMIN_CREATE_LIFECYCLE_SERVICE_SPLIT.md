# Backend Admin Create Lifecycle Service Split

버전: **v201 backend admin create lifecycle service split**

## 목적

`AdminService`가 너무 커지는 것을 막기 위해 create blueprint / create preview/apply / create-delete / restore 기능을 별도 mixin으로 분리했습니다.

## 추가 파일

- `backend/app/services/admin/admin_create_lifecycle_service.py`
- `tools/smoke_backend_admin_create_lifecycle_service_split.py`

## 유지한 것

- `AdminService` facade 유지
- `backend/app/api/routes/admin.py` 변경 없음
- schema/API 응답 구조 변경 없음
- DB schema 변경 없음

## 확인

```js
checkAdminReadOnlyPageReady().backendCreateLifecycleServiceSplitReady
```

예상: `true`

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상: `create-lifecycle-extracted-v201`

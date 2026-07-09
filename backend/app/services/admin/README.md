# backend/app/services/admin

백엔드 관리자 기능을 `AdminService` facade에서 단계적으로 분리한 mixin 폴더입니다.

`backend/app/api/routes/admin.py`는 계속 아래 facade를 사용합니다.

```txt
backend/app/services/admin_service.py
```

## 현재 분리 완료

- `admin_overview_snapshots_service.py` — overview / save snapshots
- `admin_master_catalog_service.py` — master catalog / detail / relations
- `admin_create_lifecycle_service.py` — create blueprint / create preview/apply / create-delete / restore

## 다음 후보

- `admin_change_log_service.py` — change log list/detail/rollback
- `admin_edit_draft_service.py` — edit preview/apply/stale guard 묶음
- `admin_shared_utils.py` — 여러 service가 같이 쓰는 안전한 serializer/normalizer 후보

## 원칙

- route import 경로는 바꾸지 않습니다.
- `AdminService` facade를 유지합니다.
- DB schema/env 변경 없이 한 묶음씩 분리합니다.
- 각 분리마다 smoke test를 추가합니다.

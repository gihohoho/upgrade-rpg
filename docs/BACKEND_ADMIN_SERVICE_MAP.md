# Backend Admin Service Map

현재 백엔드 admin service 분리 현황과 다음 분리 후보입니다.

## Facade

```txt
backend/app/services/admin_service.py
```

`backend/app/api/routes/admin.py`는 계속 `AdminService`를 import합니다. 따라서 route import 경로를 바꾸지 않고, `AdminService`가 여러 mixin을 상속하는 facade 역할을 유지합니다.

현재 구조:

```py
class AdminService(
    AdminOverviewSnapshotsService,
    AdminMasterCatalogService,
    AdminCreateLifecycleService,
):
    ...
```

## 분리 완료

| 버전 | 파일 | 역할 |
|---|---|---|
| v199.1 | `backend/app/services/admin/admin_overview_snapshots_service.py` | admin overview / save snapshots |
| v200 | `backend/app/services/admin/admin_master_catalog_service.py` | master catalog/detail/relations |
| v201 | `backend/app/services/admin/admin_create_lifecycle_service.py` | create blueprint / create preview/apply / create-delete / restore |

## v202 추천: change log service split

새 파일 후보:

```txt
backend/app/services/admin/admin_change_log_service.py
```

새 class 후보:

```py
class AdminChangeLogService:
    ...
```

`AdminService` 상속 후보:

```py
class AdminService(
    AdminOverviewSnapshotsService,
    AdminMasterCatalogService,
    AdminCreateLifecycleService,
    AdminChangeLogService,
):
    ...
```

## v202 이동 후보 public 메서드

- `list_admin_change_logs`
- `get_admin_change_log_detail`
- `preview_admin_change_log_rollback`
- `apply_admin_change_log_rollback`

## v202 이동 후보 helper

- `_clean_admin_change_log_filters`
- `_build_admin_change_log_where_clauses`
- `_admin_change_log_order_by`
- `_is_safe_admin_change_key`
- `_get_admin_change_log`
- `_empty_change_log_detail`
- `_empty_rollback_preview`
- `_serialize_admin_change_log_detail`
- `_build_change_log_changes`
- `_build_change_log_changes_with_relations`
- `_enrich_rollback_mismatches_with_relations`
- `_describe_change_log_relation_value`
- `_extract_master_change_target`
- `_count_admin_change_logs`
- `_serialize_admin_change_log`

## 헷갈리면 안 되는 경계

`create_delete`와 `create_delete_restore` action은 change log 테이블에 기록되지만, create lifecycle 기능 자체는 v201 `AdminCreateLifecycleService`에 유지합니다.

즉 v202에서 이동하는 것은 **change log 조회/상세/rollback 표시와 일반 update rollback** 중심입니다.

## v202 smoke에서 확인할 것

- 새 파일과 새 class 존재
- `AdminService` facade에 새 mixin 연결
- 기존 public API 응답 키 유지
- `routes/admin.py` 변경 없음
- schema/DB/env 변경 없음
- `create_delete`/`create_delete_restore` lifecycle 메서드가 새 change log service로 섞이지 않음

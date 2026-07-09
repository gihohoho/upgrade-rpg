# Backend Admin Change Log Service Split — v202

## 목표

`AdminService`가 너무 커지는 것을 막기 위해 관리자 변경 이력 목록/상세/rollback 관련 백엔드 구현을 별도 mixin으로 분리했습니다.

## 변경 파일

- 추가: `backend/app/services/admin/admin_change_log_service.py`
- 수정: `backend/app/services/admin_service.py`
- 수정: `backend/app/services/admin_service_split_contract.py`
- 수정: `src/api/admin-page-readonly.js`
- 추가: `tools/smoke_backend_admin_change_log_service_split.py`

## 분리된 기능

`AdminChangeLogService`로 이동한 public 메서드:

- `list_admin_change_logs`
- `get_admin_change_log_detail`
- `preview_admin_change_log_rollback`
- `apply_admin_change_log_rollback`

함께 이동한 helper:

- `_clean_admin_change_log_filters`
- `_build_admin_change_log_where_clauses`
- `_admin_change_log_order_by`
- `_get_admin_change_log`
- `_empty_change_log_detail`
- `_empty_rollback_preview`
- `_serialize_admin_change_log_detail`
- `_build_change_log_changes`
- `_build_change_log_changes_with_relations`
- `_enrich_rollback_mismatches_with_relations`
- `_describe_change_log_relation_value`
- `_extract_master_change_target`
- `_current_master_values`
- `_count_admin_change_logs`
- `_serialize_admin_change_log`

## 유지한 것

- `AdminService`는 계속 route가 import하는 facade입니다.
- `backend/app/api/routes/admin.py`의 URL/path는 변경하지 않았습니다.
- `backend/app/schemas/admin.py`의 요청/응답 계약은 변경하지 않았습니다.
- DB schema/env 변경은 없습니다.
- 기존 create-delete/restore 흐름은 `AdminCreateLifecycleService`에 유지했습니다.

## 추가 보강

기존 `apply_admin_change_log_rollback()`의 마지막 성공 경로에서 업데이트된 preview payload를 명시적으로 `return preview` 하도록 보강했습니다.

## 브라우저 확인

관리자 페이지 콘솔에서:

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v202.backend-admin-change-log-service-split
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
change-logs-extracted-v202
```

```js
checkAdminReadOnlyPageReady().backendChangeLogServiceSplitReady
```

예상:

```txt
true
```

## 검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_change_log_service_split.py
python -m compileall -q backend/app backend/scripts tools
```

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- `.env`, `.gitignore` 변경 없음

# Backend Admin Shared Utils Service Split — v204

## 목적

`AdminService` facade와 여러 split service에 흩어져 있던 공용 helper를 `backend/app/services/admin/admin_shared_utils.py`로 분리했습니다.

## 변경 파일

- `backend/app/services/admin/admin_shared_utils.py` 추가
- `backend/app/services/admin_service.py` inheritance에 `AdminSharedUtilsService` 추가
- `backend/app/services/admin_service_split_contract.py`의 `splitStatus`를 `shared-utils-extracted-v204`로 갱신
- `src/api/admin-page-readonly.js` readiness 버전을 `v204.backend-admin-shared-utils-service-split`으로 갱신
- `tools/smoke/contracts/smoke_backend_admin_shared_utils_service_split.py` 추가
- `tools/run_smoke_core.sh`에 v204 smoke 추가

## 이동한 helper

- `AdminService` facade에서 이동
  - `_get_master_row`
  - `_count`
- master catalog 쪽에서 이동
  - `_clean_filter_text`
  - `_is_safe_slot_key`
  - `_fetch_relation_code_options`
  - `_serialize_relation_option`
  - `_count_where`
  - `_is_asset_field`
  - `_serialize_asset_field`
  - `_safe_detail_scalar_value`
  - `_sanitize_json_preview`
  - `_sanitize_json_value`
  - `_humanize_field_name`
  - `_join_json_keys`
- overview snapshots 쪽에서 이동
  - `_count_filled_items`
- edit draft 쪽에서 이동
  - `_exists_by_code`
  - `_fetch_code_name`
  - `_exists_duplicate_combo`
- change logs 쪽에서 이동
  - `_is_safe_admin_change_key`

## 유지한 계약

- route path 변경 없음
- schema 변경 없음
- API 응답 구조 변경 없음
- DB/env 변경 없음
- `backend/app/api/routes/admin.py`는 계속 `AdminService` facade만 import
- 기존 public method 이름 유지

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
// v204.backend-admin-shared-utils-service-split

checkAdminReadOnlyPageReady().backendSharedUtilsServiceSplitReady
// true

getAdminBackendServiceSplitContractReadiness().splitStatus
// shared-utils-extracted-v204
```

## 검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke/contracts/smoke_backend_admin_shared_utils_service_split.py
python -m compileall -q backend/app backend/scripts tools
```

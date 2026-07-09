# NEXT CHAT HANDOFF — v203

기호는 코딩/터미널/경로에 익숙하지 않으므로, 명령어는 항상 실행 위치를 먼저 적습니다.

## 현재 안정 버전

**v203 backend admin edit draft service split**

## 현재 ZIP

**rpg_v203_backend_admin_edit_draft_service_split_ready.zip**

## v203 완료

- `backend/app/services/admin/admin_edit_draft_service.py` 추가
- `AdminEditDraftService` mixin 추가
- `AdminService(AdminOverviewSnapshotsService, AdminMasterCatalogService, AdminEditDraftService, AdminChangeLogService, AdminCreateLifecycleService)` 구조로 변경
- `preview_master_data_edit`, `apply_master_data_edit` 이동
- edit draft / relation edit / stale guard / normalize helper 이동
- route/schema/API 응답 구조 변경 없음
- DB/env 변경 없음
- `tools/smoke_backend_admin_edit_draft_service_split.py` 추가
- core smoke에 새 백엔드 split smoke 포함
- 기존 static smoke는 legacy marker로 유지

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v203.backend-admin-edit-draft-service-split
```

```js
checkAdminReadOnlyPageReady().backendEditDraftServiceSplitReady
```

예상:

```txt
true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
edit-draft-extracted-v203
```

## 다음 추천 단계

v204는 **backend admin shared utils 실제 분리 1단계**가 좋습니다.

추천 방향:

- `backend/app/services/admin/admin_shared_utils.py` 생성
- 여러 split service가 같이 쓰는 helper 이동
- 후보 helper:
  - `_get_master_row`
  - `_count`
  - `_count_where`
  - `_clean_filter_text`
  - `_is_asset_field`
  - `_serialize_asset_field`
  - `_safe_detail_scalar_value`
  - `_sanitize_json_preview`
  - `_sanitize_json_value`
  - `_humanize_field_name`
  - `_join_json_keys`
  - `_count_filled_items`
- `AdminService`는 facade로 유지
- `backend/app/api/routes/admin.py` 변경하지 않기
- schema/DB/env 변경 없이 전용 smoke 추가

## 주의

v203은 DB schema/env 변경이 없습니다. DB reset/seed 재실행도 필요 없습니다.

## 적용 명령 안내 원칙

명령어를 줄 때는 반드시 아래처럼 실행 위치를 먼저 적습니다.

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

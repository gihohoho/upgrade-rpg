# Backend Admin Edit Draft Service Split — v203

## 목표

`AdminService`에 남아 있던 마스터 데이터 편집 초안 검증/적용 로직을 별도 mixin 서비스로 분리했습니다.
라우터가 import하는 facade는 그대로 `AdminService`를 유지합니다.

## 변경 파일

- `backend/app/services/admin/admin_edit_draft_service.py` 추가
- `backend/app/services/admin_service.py`에서 edit draft 메서드 제거 후 `AdminEditDraftService` 상속 추가
- `backend/app/services/admin_service_split_contract.py`의 `splitStatus`를 `edit-draft-extracted-v203`으로 갱신
- `src/api/admin-page-readonly.js` 브라우저 readiness 버전을 `v203.backend-admin-edit-draft-service-split`으로 갱신
- `tools/smoke/contracts/smoke_backend_admin_edit_draft_service_split.py` 추가
- `tools/run_smoke_core.sh`에 v203 smoke 추가

## 이동된 public 메서드

- `preview_master_data_edit`
- `apply_master_data_edit`

## 이동된 주요 helper

- `_empty_edit_preview`
- `_master_edit_column_map`
- `_master_edit_field_is_readonly`
- `_master_edit_field_is_allowed`
- `_master_relation_edit_field_is_open`
- `_validate_master_relation_edit_value`
- `_describe_master_relation_edit_value`
- `_build_proposed_combo_values`
- `_exists_by_code`
- `_fetch_code_name`
- `_exists_duplicate_combo`
- `_normalize_master_edit_value`
- `_master_edit_column_type`

## 유지한 계약

- API route 변경 없음
- schema 변경 없음
- DB/env 변경 없음
- `AdminService` facade 유지
- guarded apply 확인 문구 유지: `APPLY MASTER DATA EDIT`
- stale guard 유지
- `admin_change_logs` 기록 유지

## 브라우저 확인

관리자 페이지 콘솔:

```js
checkAdminReadOnlyPageReady().version
// v203.backend-admin-edit-draft-service-split

checkAdminReadOnlyPageReady().backendEditDraftServiceSplitReady
// true

getAdminBackendServiceSplitContractReadiness().splitStatus
// edit-draft-extracted-v203
```

## 검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

실행 위치: 프로젝트 루트

```bash
python tools/smoke/contracts/smoke_backend_admin_edit_draft_service_split.py
python tools/smoke/contracts/smoke_backend_admin_service_split_contract.py
python -m compileall -q backend/app backend/scripts tools
```

## 다음 추천 단계

v204는 `backend/app/services/admin/admin_shared_utils.py`를 만들어 공유 helper를 분리하는 단계가 좋습니다.

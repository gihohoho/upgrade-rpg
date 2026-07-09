# Current Status — v203

현재 기준: **v203 backend admin edit draft service split**

이 패키지 기준 ZIP: **rpg_v203_backend_admin_edit_draft_service_split_ready.zip**

## 완료 흐름

- v198: backend admin service split contract 고정
- v199.1: overview/save snapshots service 분리 + hotfix
- v200: master catalog/detail/relations service 분리
- v201: create lifecycle service 분리
- v202: change logs/detail/rollback service 분리
- v203: edit draft preview/apply service 분리

## v203 완료 내용

- `backend/app/services/admin/admin_edit_draft_service.py` 추가
- `AdminEditDraftService` mixin 추가
- `preview_master_data_edit`, `apply_master_data_edit` 이동
- edit draft / relation edit / stale guard / normalize helper 이동
- route/schema/API 응답 구조 변경 없음
- DB/env 변경 없음
- 전용 smoke 추가 및 core smoke 포함

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().backendEditDraftServiceSplitReady
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
v203.backend-admin-edit-draft-service-split
true
edit-draft-extracted-v203
```

## 다음 추천

v204: `backend/app/services/admin/admin_shared_utils.py` 생성 후 공유 helper 분리.

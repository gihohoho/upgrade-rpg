# Next Steps

## 현재 완료: v204 backend admin shared utils service split

v204까지 backend admin service 분리 작업은 아래 순서까지 완료되었습니다.

1. overview/save snapshots service 분리
2. master catalog/detail/relations service 분리
3. create lifecycle service 분리
4. change logs/detail/rollback service 분리
5. edit draft preview/apply service 분리
6. shared utils service 분리

## 다음 추천: v205 backend admin config split

`AdminService` facade에는 이제 public API 구현보다는 상수/설정 데이터가 많이 남아 있습니다. 다음에는 route/schema/API/DB를 건드리지 않고 아래 설정 묶음을 별도 파일로 빼는 것이 좋습니다.

후보 파일:

- `backend/app/services/admin/admin_config.py`

후보 내용:

- `MASTER_DATA_MODELS`
- `MASTER_EDIT_ALLOWED_FIELDS`
- `MASTER_RELATION_EDIT_FIELDS`
- `MASTER_COMBO_GUARDED_FIELDS`
- `MASTER_CATALOG_DOMAINS`
- `MASTER_CREATE_BLUEPRINT_FIELDS`
- confirm text 상수
- create/delete allowed domain set
- change log action filters

유지할 것:

- `AdminService` facade는 그대로 유지
- `backend/app/api/routes/admin.py` 변경 없음
- `backend/app/schemas/admin.py` 변경 없음
- API 응답 구조 변경 없음
- DB/env 변경 없음

검증 목표:

- `checkAdminReadOnlyPageReady().version` → v205 계열
- `getAdminBackendServiceSplitContractReadiness().splitStatus` → config-extracted-v205
- core smoke 통과

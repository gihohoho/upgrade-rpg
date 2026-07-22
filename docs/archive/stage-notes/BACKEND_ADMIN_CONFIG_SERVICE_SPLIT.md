# Backend Admin Config Service Split — v205

## 목적

`AdminService` facade에 남아 있던 큰 설정/상수 묶음을 `backend/app/services/admin/admin_config.py`로 분리했습니다.

## 변경 파일

- `backend/app/services/admin/admin_config.py` 추가
- `backend/app/services/admin_service.py` inheritance에 `AdminConfigService` 추가
- `backend/app/services/admin/__init__.py` export 정리
- `backend/app/services/admin_service_split_contract.py` extracted files에 config service 추가

## 이동한 설정

- `MASTER_DATA_MODELS`
- `MASTER_EDIT_APPLY_CONFIRM_TEXT`
- `MASTER_EDIT_ROLLBACK_CONFIRM_TEXT`
- `MASTER_CREATE_APPLY_CONFIRM_TEXT`
- `MASTER_CREATE_DELETE_CONFIRM_TEXT`
- `MASTER_CREATE_DELETE_RESTORE_CONFIRM_TEXT`
- `MASTER_CREATE_APPLY_ALLOWED_DOMAINS`
- `MASTER_CREATE_DELETE_ALLOWED_DOMAINS`
- `ADMIN_CHANGE_LOG_ACTION_FILTERS`
- `MASTER_EDIT_ALLOWED_FIELDS`
- `MASTER_RELATION_EDIT_FIELDS`
- `MASTER_COMBO_GUARDED_FIELDS`
- `MASTER_CATALOG_DOMAINS`
- `MASTER_CREATE_BLUEPRINT_FIELDS`

## 유지한 계약

- route path 변경 없음
- schema 변경 없음
- API 응답 구조 변경 없음
- DB/env 변경 없음
- `backend/app/api/routes/admin.py`는 계속 `AdminService` facade만 import
- 모든 기존 public method 이름 유지

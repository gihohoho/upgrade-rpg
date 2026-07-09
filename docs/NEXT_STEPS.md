# Next Steps

## 현재 완료: v203 backend admin edit draft service split

v203까지 backend admin service 분리 작업은 아래 순서까지 완료되었습니다.

- overview/save snapshots
- master catalog/detail/relations
- create lifecycle
- change logs/detail/rollback
- edit draft preview/apply

## 다음 추천: v204 backend admin shared utils split

`AdminService` facade에 아직 남은 공용 helper들을 `backend/app/services/admin/admin_shared_utils.py`로 이동하는 단계가 좋습니다.

후보 helper:

- `_get_master_row`
- `_build_readiness`
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

## 제약

- route/schema/API 응답 구조 변경하지 않기
- DB/env 변경하지 않기
- `AdminService` facade 유지
- 전용 backend smoke 추가

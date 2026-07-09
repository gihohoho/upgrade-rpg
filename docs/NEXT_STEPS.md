# Next Steps

## 현재 완료: v200 backend admin master catalog/detail service split

백엔드 `AdminService` facade는 유지한 채, 두 번째 실제 분리 대상으로 master catalog/detail/relations 묶음을 `AdminMasterCatalogService`로 이동했습니다.

## 다음 추천: v201 backend admin create lifecycle service split

다음 실제 분리 후보는 **create/delete/restore lifecycle** 묶음입니다.

추천 방향:

1. `backend/app/services/admin/admin_create_lifecycle_service.py` 생성
2. 아래 기능을 이동
   - `get_master_create_blueprint`
   - `preview_master_data_create`
   - `apply_master_data_create`
   - `preview_admin_create_delete_rollback`
   - `apply_admin_create_delete_rollback`
   - `preview_admin_create_delete_restore`
   - `apply_admin_create_delete_restore`
   - create lifecycle helper
3. `AdminService`는 facade로 계속 유지
4. `backend/app/api/routes/admin.py`는 변경하지 않기
5. schema/DB/env 변경 없이 smoke 추가

## 그 다음 후보

v201이 안정적이면 다음 순서가 좋습니다.

1. change logs service 분리
2. edit draft service 분리
3. shared utils 분리

## 주의

다음 단계에서도 DB schema/env 변경은 최대한 피하고, 기존 게임 정상 작동 상태를 유지합니다.

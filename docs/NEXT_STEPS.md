# Next Steps

## 현재 완료: v199.1 backend admin overview/snapshots service hotfix

백엔드 `AdminService` facade는 유지한 채, 첫 실제 분리 대상으로 overview/save snapshots 묶음을 `AdminOverviewSnapshotsService`로 이동했습니다.

## 다음 추천: v200 backend admin master catalog service split

다음 실제 분리 후보는 **master catalog/detail/relations** 묶음입니다.

추천 방향:

1. `backend/app/services/admin/admin_master_catalog_service.py` 생성
2. 아래 기능을 이동
   - `list_master_catalog_domains`
   - `list_master_catalog_rows`
   - `get_master_catalog_detail`
   - `get_master_catalog_relations`
   - master catalog/detail/relation helper
3. `AdminService`는 facade로 계속 유지
4. `backend/app/api/routes/admin.py`는 변경하지 않기
5. schema/DB/env 변경 없이 smoke 추가

## 그 다음 후보

v200이 안정적이면 다음 순서가 좋습니다.

1. create lifecycle service 분리
2. change logs service 분리
3. edit draft service 분리
4. shared utils 분리

## 주의

다음 단계에서도 DB schema/env 변경은 최대한 피하고, 기존 게임 정상 작동 상태를 유지합니다.

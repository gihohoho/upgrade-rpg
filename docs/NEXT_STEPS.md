# Next Steps

## 현재 완료: v198 backend admin service split contract

백엔드 `admin_service.py`를 바로 쪼개지 않고, 먼저 service split 계약과 smoke를 추가했습니다.

## 다음 추천: v199 backend admin overview/snapshots service split

가장 안전한 첫 실제 분리 대상은 **overview/save snapshots** 묶음입니다.

추천 방향:

1. `backend/app/services/admin/` 폴더 생성
2. `backend/app/services/admin/admin_overview_snapshots_service.py` 생성
3. 아래 기능을 먼저 이동
   - `get_readonly_overview`
   - `list_save_snapshot_summaries`
   - snapshot filter/order/count helper
   - overview readiness helper
4. `backend/app/services/admin_service.py`는 facade로 유지
5. `backend/app/api/routes/admin.py`는 변경하지 않기
6. route/schema/DB/env 변경 없이 smoke 추가

## 그 다음 후보

v199가 안정적이면 다음 순서가 좋습니다.

1. master catalog/detail service 분리
2. create lifecycle service 분리
3. change logs service 분리
4. edit draft service 분리
5. shared utils 분리

## 주의

다음 단계에서도 DB schema/env 변경은 최대한 피하고, 기존 게임 정상 작동 상태를 유지합니다.

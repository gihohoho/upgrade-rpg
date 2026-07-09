# Next Steps

## 현재 완료: v202 backend admin change log service split

v201의 create lifecycle 분리 상태를 유지하면서, 관리자 변경 이력 목록/상세/rollback 묶음을 `AdminChangeLogService`로 실제 분리했습니다.

## 다음 추천: v203 backend admin edit draft service split

다음 실제 분리 후보는 **edit draft / guarded apply** 묶음입니다.

추천 방향:

1. `backend/app/services/admin/admin_edit_draft_service.py` 생성
2. 아래 기능을 이동
   - `preview_master_data_edit`
   - `apply_master_data_edit`
   - edit draft helper
   - relation edit validation/description helper
   - normalize/type helper
3. `AdminService`는 facade로 계속 유지
4. `backend/app/api/routes/admin.py`는 변경하지 않기
5. schema/DB/env 변경 없이 전용 smoke 추가

## 그 다음 후보

v203이 안정적이면 다음 순서가 좋습니다.

1. shared utils 분리
2. 백엔드 서비스 파일별 문서 정리
3. 오래된 legacy smoke marker 축소

## 주의

다음 단계에서도 DB schema/env 변경은 최대한 피하고, 기존 게임 정상 작동 상태를 유지합니다.

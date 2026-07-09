이전 채팅에서 이어서 할게. 첨부한 zip은 v203 `backend admin edit draft service split` 완료본이야.

나는 코딩/터미널/경로에 익숙하지 않으니까, 명령어를 줄 때는 항상 실행 위치를 먼저 알려줘.

현재 상태:

- `AdminService` facade는 유지
- `AdminOverviewSnapshotsService` 분리 완료
- `AdminMasterCatalogService` 분리 완료
- `AdminCreateLifecycleService` 분리 완료
- `AdminChangeLogService` 분리 완료
- `AdminEditDraftService` 분리 완료
- route/schema/API 응답 구조 변경 없음
- DB schema/env 변경 없음

브라우저 확인 예상값:

```js
checkAdminReadOnlyPageReady().version
// v203.backend-admin-edit-draft-service-split

checkAdminReadOnlyPageReady().backendEditDraftServiceSplitReady
// true

getAdminBackendServiceSplitContractReadiness().splitStatus
// edit-draft-extracted-v203
```

다음 추천 단계는 v204 `backend admin shared utils service split`이야.

추천 방향:

1. `backend/app/services/admin/admin_shared_utils.py` 생성
2. 여러 backend admin service가 같이 쓰는 helper 이동
3. `AdminService`는 route facade로 유지
4. `backend/app/api/routes/admin.py` 변경하지 않기
5. schema/DB/env 변경 없이 smoke 추가

이 흐름으로 다음 단계 진행해줘.

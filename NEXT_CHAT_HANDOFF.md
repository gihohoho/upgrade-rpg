# NEXT CHAT HANDOFF — v200

기호는 코딩/터미널/경로에 익숙하지 않으므로, 명령어는 항상 실행 위치를 먼저 적습니다.

## 현재 안정 버전

**v200 backend admin master catalog/detail service split**

## 현재 ZIP

**rpg_v200_backend_admin_master_catalog_service_split_ready.zip**

## v200 완료

- `backend/app/services/admin/admin_master_catalog_service.py` 추가
- `AdminMasterCatalogService` mixin 추가
- `AdminService(AdminOverviewSnapshotsService, AdminMasterCatalogService)` 구조로 변경
- master catalog/detail/relations 관련 public/helper 메서드 외부 서비스로 이동
- route/schema/API 응답 구조 변경 없음
- `tools/smoke_backend_admin_master_catalog_service_split.py` 추가
- core smoke에 새 백엔드 split smoke 포함
- 기존 static smoke를 분리 구조에 맞게 갱신

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v200.backend-admin-master-catalog-service-split
```

```js
checkAdminReadOnlyPageReady().backendMasterCatalogServiceSplitReady
```

예상:

```txt
true
```

```js
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
master-catalog-extracted-v200
```

## 다음 추천 단계

v201은 **backend admin create lifecycle service 실제 분리 1단계**가 좋습니다.

추천 방향:

- `backend/app/services/admin/admin_create_lifecycle_service.py` 생성
- create blueprint / create preview/apply / create-delete / restore 관련 public/helper 메서드 이동
- `AdminService`는 facade로 유지
- `backend/app/api/routes/admin.py` 변경하지 않기
- schema/DB/env 변경 없이 전용 smoke 추가

## 주의

v200은 DB schema/env 변경이 없습니다. DB reset/seed 재실행도 필요 없습니다.

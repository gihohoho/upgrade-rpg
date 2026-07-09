# NEXT CHAT HANDOFF — v204

기호는 코딩/터미널/경로에 익숙하지 않으므로, 명령어는 항상 실행 위치를 먼저 적습니다. git 명령은 가능하면 한 번에 복사 가능한 한 코드 블록으로 묶습니다.

## 현재 안정 버전

**v204 backend admin shared utils service split**

## 현재 ZIP

**rpg_v204_backend_admin_shared_utils_service_split_ready.zip**

## v204 완료

- `backend/app/services/admin/admin_shared_utils.py` 추가
- `AdminSharedUtilsService` mixin 추가
- `AdminService(AdminSharedUtilsService, AdminOverviewSnapshotsService, AdminMasterCatalogService, AdminEditDraftService, AdminChangeLogService, AdminCreateLifecycleService)` 구조로 변경
- `AdminService` facade에 남아 있던 `_get_master_row`, `_count` 이동
- master catalog / overview snapshots / edit draft / change log 서비스에 있던 공용 helper 이동
- route/schema/API 응답 구조 변경 없음
- DB/env 변경 없음
- `tools/smoke_backend_admin_shared_utils_service_split.py` 추가
- core smoke에 새 백엔드 split smoke 포함
- 기존 v199~v203 static smoke는 v204 구조에 맞게 조정

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v204.backend-admin-shared-utils-service-split
```

```js
checkAdminReadOnlyPageReady().backendSharedUtilsServiceSplitReady
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
shared-utils-extracted-v204
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_shared_utils_service_split.py
python -m compileall -q backend/app backend/scripts tools
```

## git push 명령

실행 위치: 프로젝트 루트

```bash
git status && git add . && git commit -m "Split backend admin shared utils service" && git push
```

## 다음 추천 단계

v205는 **backend admin config split**이 좋습니다.

추천 방향:

- `backend/app/services/admin/admin_config.py` 생성
- `AdminService` facade에 남은 대형 상수/설정 묶음 이동
- 후보:
  - `MASTER_DATA_MODELS`
  - `MASTER_EDIT_ALLOWED_FIELDS`
  - `MASTER_RELATION_EDIT_FIELDS`
  - `MASTER_COMBO_GUARDED_FIELDS`
  - `MASTER_CATALOG_DOMAINS`
  - `MASTER_CREATE_BLUEPRINT_FIELDS`
  - confirm text 상수들
  - create/delete allowed domain set
  - change log action filters
- route/schema/API/DB/env 변경 없이 진행
- v205 전용 smoke 추가

## 주의

v204는 DB schema/env 변경이 없습니다. DB reset/seed 재실행도 필요 없습니다.

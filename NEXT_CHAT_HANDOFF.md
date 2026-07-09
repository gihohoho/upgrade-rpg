# NEXT CHAT HANDOFF — v206

기호는 코딩/터미널/경로에 익숙하지 않으므로, 명령어는 항상 실행 위치를 먼저 적습니다. git 명령은 가능하면 한 번에 복사 가능한 한 코드 블록으로 묶습니다.

## 현재 안정 버전

**v206 backend admin config/readiness service split**

## 현재 ZIP

**rpg_v206_backend_admin_config_readiness_service_split_ready.zip**

## v205~v206 완료

- `backend/app/services/admin/admin_config.py` 추가
- `backend/app/services/admin/admin_readiness_service.py` 추가
- `AdminConfigService` mixin 추가
- `AdminReadinessService` mixin 추가
- `AdminService(AdminConfigService, AdminSharedUtilsService, AdminReadinessService, AdminOverviewSnapshotsService, AdminMasterCatalogService, AdminEditDraftService, AdminChangeLogService, AdminCreateLifecycleService)` 구조로 변경
- `AdminService` facade에 남아 있던 큰 설정/상수 묶음 이동
  - `MASTER_DATA_MODELS`
  - `MASTER_CATALOG_DOMAINS`
  - `MASTER_EDIT_ALLOWED_FIELDS`
  - `MASTER_RELATION_EDIT_FIELDS`
  - `MASTER_COMBO_GUARDED_FIELDS`
  - `MASTER_CREATE_BLUEPRINT_FIELDS`
  - confirm text 상수들
  - create/delete allowed domain set
  - change log action filters
- `preview_change`, `_build_readiness` 이동
- `backend/app/services/admin/__init__.py` export 정리
- route/schema/API 응답 구조 변경 없음
- DB/env 변경 없음
- `tools/smoke_backend_admin_config_readiness_service_split.py` 추가
- core smoke에 새 백엔드 split smoke 포함
- 기존 static smoke는 v206 구조에 맞게 조정

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v206.backend-admin-config-readiness-service-split
```

```js
checkAdminReadOnlyPageReady().backendConfigServiceSplitReady
```

예상:

```txt
true
```

```js
checkAdminReadOnlyPageReady().backendReadinessServiceSplitReady
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
readiness-extracted-v206
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke_backend_admin_config_readiness_service_split.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

## git push 명령

실행 위치: 프로젝트 루트

```bash
git status && git add . && git commit -m "Split backend admin config and readiness services" && git push
```

## 다음 추천 단계

v207은 **backend admin route response helper cleanup** 또는 **legacy smoke marker cleanup**이 좋습니다.

추천 방향 A — route response helper cleanup:

- `backend/app/api/routes/admin.py`의 반복되는 `ApiResponse(...)` wrapper 생성 helper화
- route path/schema/API 응답 구조는 그대로 유지
- v207 전용 smoke 추가

추천 방향 B — legacy smoke marker cleanup:

- `AdminService` facade에 남아 있는 legacy marker 문자열을 테스트/문서 기준으로 줄이기
- static smoke들이 split file을 직접 보도록 조정
- route/schema/API/DB/env 변경 없이 진행

## 주의

v206은 DB schema/env 변경이 없습니다. DB reset/seed 재실행도 필요 없습니다.

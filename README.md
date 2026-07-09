# Upgrade RPG v203 패키지

현재 안정 버전: **v203 backend admin edit draft service split**

새 채팅 인수인계 ZIP: **rpg_v203_backend_admin_edit_draft_service_split_ready.zip**

## 이번 v203에서 정리한 것

v203에서는 백엔드 `AdminService` facade를 유지한 상태로, **마스터 데이터 편집 초안 검증/적용** 묶음을 `AdminEditDraftService` mixin으로 실제 분리했습니다.

- `backend/app/services/admin/admin_edit_draft_service.py` 추가
- `preview_master_data_edit`, `apply_master_data_edit` 이동
- edit draft / relation edit / stale guard / normalize helper 이동
- `AdminService`는 route facade로 유지
- `backend/app/api/routes/admin.py` 변경 없음
- `backend/app/schemas/admin.py` 변경 없음
- DB/env 변경 없음
- v203 전용 smoke test 추가

## 주요 파일

- `admin.html` — 정적 관리자 페이지
- `src/api/admin-page-readonly.js` — 관리자 진입/readiness
- `src/api/admin/admin-edit-draft.js` — 프론트 edit draft 모듈
- `backend/app/services/admin_service.py` — backend facade
- `backend/app/services/admin/admin_edit_draft_service.py` — v203 분리 완료
- `backend/app/services/admin_service_split_contract.py` — backend split contract
- `docs/BACKEND_ADMIN_EDIT_DRAFT_SERVICE_SPLIT.md` — v203 상세 문서

## 브라우저 확인

관리자 페이지 콘솔에서 확인:

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v203.backend-admin-edit-draft-service-split
```

```js
checkAdminReadOnlyPageReady().backendEditDraftServiceSplitReady
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
edit-draft-extracted-v203
```

## 검증 명령

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

실행 위치: 프로젝트 루트

```bash
python tools/smoke_backend_admin_edit_draft_service_split.py
python tools/smoke_backend_admin_service_split_contract.py
python tools/smoke_seed_import_long_asset_columns.py
python tools/smoke_seed_import_structure.py
python -m compileall -q backend/app backend/scripts tools
```

## 적용 후 실행

실행 위치: `backend` 폴더

```bash
uvicorn app.main:app --reload
```

DB schema/env 변경이 없어서 DB reset/seed 재실행은 필요 없습니다.

## 다음 추천 단계

v204는 `backend/app/services/admin/admin_shared_utils.py`를 만들고, 여러 split service가 같이 쓰는 공유 helper를 분리하는 단계가 좋습니다.

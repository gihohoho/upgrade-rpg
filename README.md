# Upgrade RPG v204 패키지

현재 안정 버전: **v204 backend admin shared utils service split**

새 채팅 인수인계 ZIP: **rpg_v204_backend_admin_shared_utils_service_split_ready.zip**

## 이번 v204에서 정리한 것

v204에서는 백엔드 `AdminService` facade를 유지한 상태로, 여러 admin split service가 같이 쓰는 공용 helper를 `AdminSharedUtilsService`로 실제 분리했습니다.

## 핵심 변경

- `backend/app/services/admin/admin_shared_utils.py` 추가
- `AdminService` inheritance에 `AdminSharedUtilsService` 추가
- `_get_master_row`, `_count`, `_count_where` 등 공용 DB helper 이동
- relation option, safe key, asset hiding, JSON preview sanitizer helper 이동
- 기존 route/schema/API 응답 구조 변경 없음
- DB/env 변경 없음
- v204 전용 smoke test 추가

## 주요 파일

- `backend/app/services/admin_service.py` — route facade 유지
- `backend/app/services/admin/admin_shared_utils.py` — v204 신규 shared utils service
- `backend/app/services/admin_service_split_contract.py` — splitStatus 갱신
- `src/api/admin-page-readonly.js` — 브라우저 readiness 버전 갱신
- `docs/BACKEND_ADMIN_SHARED_UTILS_SERVICE_SPLIT.md` — v204 상세 문서
- `tools/smoke_backend_admin_shared_utils_service_split.py` — v204 전용 smoke

## 적용 후 확인

관리자 페이지 콘솔:

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

## 다음 추천

v205는 `backend/app/services/admin_service.py`에 남은 대형 상수/설정 묶음을 `backend/app/services/admin/admin_config.py` 같은 파일로 분리하는 단계가 좋습니다.

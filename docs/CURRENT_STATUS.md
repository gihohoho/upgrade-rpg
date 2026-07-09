# Current Status — v204

현재 기준: **v204 backend admin shared utils service split**

이 패키지 기준 ZIP: **rpg_v204_backend_admin_shared_utils_service_split_ready.zip**

## 완료 흐름

- v198: backend admin service split contract 고정
- v199.1: overview/save snapshots service 분리 + hotfix
- v200: master catalog/detail/relations service 분리
- v201: create lifecycle service 분리
- v202: change logs/detail/rollback service 분리
- v203: edit draft preview/apply service 분리
- v204: shared utils service 분리

## v204 완료 내용

- `backend/app/services/admin/admin_shared_utils.py` 추가
- 여러 split service가 같이 쓰는 count/relation/serialization/helper 이동
- `AdminService`는 route facade로 유지
- route/schema/API 응답 구조 변경 없음
- DB/env 변경 없음
- v204 전용 smoke 추가 및 core smoke 포함

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().backendSharedUtilsServiceSplitReady
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
v204.backend-admin-shared-utils-service-split
true
shared-utils-extracted-v204
```

## 다음 추천

v205: `backend/app/services/admin_service.py`에 남은 대형 상수/설정 묶음을 별도 config 파일로 분리.

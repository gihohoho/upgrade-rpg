# Current Status — v206

현재 기준: **v206 backend admin config/readiness service split**

이 패키지 기준 ZIP: **rpg_v206_backend_admin_config_readiness_service_split_ready.zip**

## 완료 흐름

- v198: backend admin service split contract 고정
- v199.1: overview/save snapshots service 분리 + hotfix
- v200: master catalog/detail/relations service 분리
- v201: create lifecycle service 분리
- v202: change logs/detail/rollback service 분리
- v203: edit draft preview/apply service 분리
- v204: shared utils service 분리
- v205: config service 분리
- v206: readiness service 분리

## v205~v206 완료 내용

- `backend/app/services/admin/admin_config.py` 추가
- `backend/app/services/admin/admin_readiness_service.py` 추가
- `AdminService` facade에 남아 있던 큰 설정/상수 묶음 이동
- `preview_change`, `_build_readiness` 이동
- route/schema/API 응답 구조 변경 없음
- DB/env 변경 없음
- v206 전용 smoke 추가 및 core smoke 포함

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().backendConfigServiceSplitReady
checkAdminReadOnlyPageReady().backendReadinessServiceSplitReady
getAdminBackendServiceSplitContractReadiness().splitStatus
```

예상:

```txt
v206.backend-admin-config-readiness-service-split
true
true
readiness-extracted-v206
```

## 다음 추천

v207: `AdminService` facade의 legacy smoke marker를 테스트 구조 기준으로 정리하거나, admin route 응답 wrapper 중복을 helper로 정리.

# Backend Admin Readiness Service Split — v206

## 목적

`AdminService` facade에 마지막으로 남아 있던 작은 준비/미리보기 helper를 `backend/app/services/admin/admin_readiness_service.py`로 분리했습니다.

## 변경 파일

- `backend/app/services/admin/admin_readiness_service.py` 추가
- `backend/app/services/admin_service.py` inheritance에 `AdminReadinessService` 추가
- `backend/app/services/admin_service_split_contract.py`의 `splitStatus`를 `readiness-extracted-v206`으로 갱신
- `src/api/admin-page-readonly.js` readiness 버전을 `v206.backend-admin-config-readiness-service-split`으로 갱신
- `tools/smoke/contracts/smoke_backend_admin_config_readiness_service_split.py` 추가
- `tools/run_smoke_core.sh`에 v206 smoke 추가

## 이동한 helper

- `preview_change`
- `_build_readiness`

## 유지한 계약

- route path 변경 없음
- schema 변경 없음
- API 응답 구조 변경 없음
- DB/env 변경 없음
- `AdminService`는 route facade로 유지

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
// v206.backend-admin-config-readiness-service-split

checkAdminReadOnlyPageReady().backendConfigServiceSplitReady
// true

checkAdminReadOnlyPageReady().backendReadinessServiceSplitReady
// true

getAdminBackendServiceSplitContractReadiness().splitStatus
// readiness-extracted-v206
```

## 검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
python tools/smoke/contracts/smoke_backend_admin_config_readiness_service_split.py
python -m compileall -q backend/app backend/scripts tools
```

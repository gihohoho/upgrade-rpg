# Current Status

현재 기준: **v198 backend admin service split contract**

이 패키지 기준 ZIP: **rpg_v198_backend_admin_service_split_contract_ready.zip**

## 완료된 관리자 JS 분리/정리

- v185: layout shell 분리
- v187: change logs 분리
- v189.1: create lifecycle 분리 + helper export hotfix
- v191: edit draft 분리
- v192: master catalog/detail 분리
- v193: overview/snapshots 분리
- v194: bootstrap/bindEvents thin entry 계약 고정
- v195: thin entry cleanup
- v196: field help/value hints/equip slot label 분리
- v197: settings helpers/API URL/write key/page URL helper 분리

## v198 완료 내용

- `backend/app/services/admin_service_split_contract.py` 추가
- `tools/smoke_backend_admin_service_split_contract.py` 추가
- `docs/BACKEND_ADMIN_SERVICE_SPLIT_CONTRACT.md` 추가
- 백엔드 `admin_service.py` 실제 분리 전 계약 고정
- route/schema 변경 금지 정책 고정
- `AdminService` facade 유지 정책 고정
- 관리자 JS 분리 준비 카드에 backend service split 계약 표시 추가
- `checkAdminReadOnlyPageReady().backendServiceSplitContractReady` 추가

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().backendServiceSplitContractReady
getAdminBackendServiceSplitContractReadiness().status
```

예상:

```txt
v198.backend-admin-service-split-contract
true
contract-frozen-v198
```

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음

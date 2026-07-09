# Upgrade RPG v198 패키지

현재 안정 버전: **v198 backend admin service split contract**

새 채팅 인수인계 ZIP: **rpg_v198_backend_admin_service_split_contract_ready.zip**

## 요약

v198에서는 프론트 관리자 JS 분리 이후 다음 단계로, 백엔드 `AdminService`를 실제로 쪼개기 전에 **분리 계약과 smoke**를 먼저 추가했습니다.

추가 파일:

- `backend/app/services/admin_service_split_contract.py`
- `tools/smoke_backend_admin_service_split_contract.py`
- `docs/BACKEND_ADMIN_SERVICE_SPLIT_CONTRACT.md`

## v198에서 정리한 것

- `admin_service.py`의 기능 묶음 분리 후보 고정
- route/schema 유지 계약 고정
- `AdminService` facade 유지 정책 고정
- 브라우저 관리자 JS 분리 준비 카드에 backend service 계약 표시 추가
- `checkAdminReadOnlyPageReady().backendServiceSplitContractReady` 추가
- core smoke에 백엔드 service split contract smoke 추가

## 현재 관리자 JS 분리 상태

- `src/api/game-api-client.js` — 기존 외부 API client
- `src/api/admin-layout-shell.js` — v185 분리 완료
- `src/api/admin/admin-field-help.js` — v196 분리 완료
- `src/api/admin/admin-settings-helpers.js` — v197 분리 완료
- `src/api/admin/admin-change-logs.js` — v187 분리 완료
- `src/api/admin/admin-create-lifecycle.js` — v189.1 hotfix 포함 분리 완료
- `src/api/admin/admin-edit-draft.js` — v191 분리 완료
- `src/api/admin/admin-master-catalog.js` — v192 분리 완료
- `src/api/admin/admin-overview-snapshots.js` — v193 분리 완료
- `src/api/admin-page-readonly.js` — thin entry 유지

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v198.backend-admin-service-split-contract
```

```js
checkAdminReadOnlyPageReady().backendServiceSplitContractReady
```

예상값:

```txt
true
```

```js
getAdminBackendServiceSplitContractReadiness().status
```

예상값:

```txt
contract-frozen-v198
```

## 검증

- `bash tools/run_smoke_core.sh` 통과
- `python tools/smoke_backend_admin_service_split_contract.py` 통과
- `node --check src/api/admin-page-readonly.js` 통과
- `python -m compileall -q backend/app` 통과

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음

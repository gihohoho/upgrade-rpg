# Upgrade RPG v194 패키지

현재 안정 버전: **v194 admin bootstrap/bindEvents readiness**

새 채팅 인수인계 ZIP: **rpg_v194_admin_bootstrap_bindings_readiness_ready.zip**

## 요약

v194에서는 `admin-page-readonly.js`를 바로 더 크게 분리하지 않고, 마지막 entry 파일에 남아 있는 **bootstrap / bindEvents / window export** 역할을 계약으로 고정했습니다.

새 파일 분리는 없습니다.

## 현재 관리자 JS 분리 상태

- `src/api/game-api-client.js` — 기존 외부 API client
- `src/api/admin-layout-shell.js` — v185 분리 완료
- `src/api/admin/admin-change-logs.js` — v187 분리 완료
- `src/api/admin/admin-create-lifecycle.js` — v189.1 hotfix 포함 분리 완료
- `src/api/admin/admin-edit-draft.js` — v191 분리 완료
- `src/api/admin/admin-master-catalog.js` — v192 분리 완료
- `src/api/admin/admin-overview-snapshots.js` — v193 분리 완료
- `src/api/admin-page-readonly.js` — v194 기준 bootstrap/bindEvents/window wrapper 중심 thin entry 계약 고정

## v194에서 고정한 것

- boot 순서
- delegated event action map
- window export 호환 목록
- 외부 모듈 configure 순서
- readiness aggregation 진단

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v194.admin-bootstrap-bindings-readiness
```

```js
checkAdminReadOnlyPageReady().bootstrapBindingReady
```

예상값:

```txt
true
```

```js
getAdminBootstrapBindingReadiness().status
```

예상값:

```txt
contract-frozen-v194
```

## 검증

- `bash tools/run_smoke_core.sh` 통과
- `bash tools/run_smoke_all.sh` 통과
- `node --check src/api/admin-page-readonly.js` 통과
- `python -m compileall -q backend/app` 통과

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음

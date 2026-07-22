# Admin Change Log Split Contract

v186 admin change log split contract

## 목적

`change logs` 묶음을 바로 외부 파일로 옮기기 전에, 분리 후에도 반드시 유지해야 할 API/window/DOM 계약을 먼저 고정했습니다.

이번 단계에서는 실제 파일 분리를 하지 않습니다.

## 고정한 다음 분리 후보

- 현재 파일: `src/api/admin-page-readonly.js`
- 다음 후보 파일: `src/api/admin/admin-change-logs.js`
- 상태: `contract-frozen-v186`

## 고정한 기능 범위

- 변경 이력 필터 읽기/초기화/설명
- 변경 이력 목록 조회와 렌더링
- 변경 이력 상세 조회와 렌더링
- rollback preview/apply
- create row delete preview/apply
- create_delete row restore preview/apply
- `create`, `create_delete`, `create_delete_restore` action shortcut

## 고정한 백엔드 API 함수

- `listAdminChangeLogs`
- `fetchAdminChangeLogDetail`
- `previewAdminChangeLogRollback`
- `applyAdminChangeLogRollback`
- `previewAdminCreateDeleteRollback`
- `applyAdminCreateDeleteRollback`
- `previewAdminCreateDeleteRestore`
- `applyAdminCreateDeleteRestore`

## 브라우저 확인

관리자 페이지 Console에서 확인합니다.

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v186.admin-change-log-split-contract
```

추가 확인:

```js
checkAdminReadOnlyPageReady().changeLogSplitContractReady
```

예상값:

```txt
true
```

상세 계약 확인:

```js
getAdminChangeLogSplitContractReadiness()
```

## 검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
bash tools/run_smoke_all.sh
python -m compileall -q backend/app
node --check src/api/admin-layout-shell.js
node --check src/api/admin-page-readonly.js
```

## DB reset / seed

필요 없습니다.

- DB schema 변경 없음
- seed 재실행 필요 없음
- `.env` 변경 없음
- `.gitignore` 변경 없음

## 다음 추천 단계

v187에서는 이 계약을 유지한 상태에서 실제 `src/api/admin/admin-change-logs.js` 파일을 만들고, 변경 이력 관련 함수만 1차 분리하는 것이 좋습니다.

`admin-page-readonly.js`에는 기존 window export 호환 wrapper를 남겨서 브라우저와 smoke가 같은 방식으로 동작하게 유지하는 방향이 안전합니다.

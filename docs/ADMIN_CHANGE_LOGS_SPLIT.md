# Admin Change Logs Split

v187 admin change logs split

## 목적

v186에서 고정한 change logs API/window/DOM 계약을 유지한 상태로, 관리자 변경 이력 관련 구현을 외부 파일로 1차 분리했습니다.

## 이번 단계에서 분리한 파일

- 새 파일: `src/api/admin/admin-change-logs.js`
- 유지 파일: `src/api/admin-page-readonly.js`

`admin-page-readonly.js`에는 기존 window export 호환을 위한 얇은 wrapper만 남겼습니다.

## 분리한 기능

- 변경 이력 필터 읽기/초기화/설명
- 변경 이력 목록 렌더링
- 변경 이력 상세 렌더링
- rollback preview/apply
- 생성 row 삭제 preview/apply
- 삭제 row 복원 preview/apply
- `create`, `create_delete`, `create_delete_restore` action shortcut

## script 로드 순서

`admin.html`은 아래 순서로 로드됩니다.

```html
<script src="src/api/game-api-client.js"></script>
<script src="src/api/admin-layout-shell.js"></script>
<script src="src/api/admin/admin-change-logs.js"></script>
<script src="src/api/admin-page-readonly.js"></script>
```

`admin-page-readonly.js`가 `RpgAdminChangeLogs` wrapper를 호출하므로 `admin-change-logs.js`가 먼저 로드되어야 합니다.

## 브라우저 확인

관리자 페이지 Console에서 확인합니다.

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v187.admin-change-logs-split
```

추가 확인:

```js
checkAdminReadOnlyPageReady().changeLogsExternalReady
```

예상값:

```txt
true
```

그리고:

```js
window.RpgAdminChangeLogs.VERSION
```

예상값:

```txt
v187.admin-change-logs-split
```

상세 확인:

```js
getAdminChangeLogsReadiness()
```

## 검증

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
bash tools/run_smoke_all.sh
python -m compileall -q backend/app
node --check src/api/admin-layout-shell.js
node --check src/api/admin/admin-change-logs.js
node --check src/api/admin-page-readonly.js
```

## DB reset / seed

필요 없습니다.

- DB schema 변경 없음
- seed 재실행 필요 없음
- `.env` 변경 없음
- `.gitignore` 변경 없음

## 다음 추천 단계

change logs 분리가 안정적이면 다음은 `create lifecycle` 분리 전 계약 smoke를 추가하는 것이 좋습니다.

바로 기능을 뜯어내기보다 `runAdminCreateLifecycleBatchCheck`, 생성 초안, 생성/삭제/복원 결과 렌더링, 확인 문구, DOM target 목록을 먼저 고정하면 다음 분리 단계가 안전합니다.

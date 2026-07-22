# Admin Layout Shell Split

v185 admin layout shell split

## 목적

관리자 페이지의 거대한 `admin-page-readonly.js`를 한 번에 나누지 않고, DB 쓰기와 직접 관련 없는 layout shell부터 안전하게 외부 파일로 분리했습니다.

## 이번 단계에서 분리한 파일

- 새 파일: `src/api/admin-layout-shell.js`
- 유지 파일: `src/api/admin-page-readonly.js`

`admin-page-readonly.js`에는 기존 window export 호환을 위한 얇은 wrapper만 남겼습니다.

## 분리한 기능

- sidebar active navigation
- sticky header offset 계산
- 섹션 접기/펼치기 버튼 생성
- 기본 접힘 섹션 관리
- layout shell readiness 계산

## script 로드 순서

`admin.html`은 아래 순서로 로드됩니다.

```html
<script src="src/api/game-api-client.js"></script>
<script src="src/api/admin-layout-shell.js"></script>
<script src="src/api/admin-page-readonly.js"></script>
```

`admin-page-readonly.js`가 layout shell wrapper를 호출하므로 `admin-layout-shell.js`가 먼저 로드되어야 합니다.

## 브라우저 확인

관리자 페이지 Console에서 확인합니다.

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v185.admin-layout-shell-split
```

추가 확인:

```js
checkAdminReadOnlyPageReady().adminJsSplitReadiness.layoutShellExternalReady
```

예상값:

```txt
true
```

그리고:

```js
window.RpgAdminLayoutShell.VERSION
```

예상값:

```txt
v185.admin-layout-shell-split
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

layout shell 분리가 안정적이면 다음은 `change logs` 묶음 분리 전 readiness/contract smoke를 추가하는 것이 좋습니다. 변경 이력은 rollback/create-delete 흐름이 포함되어 있으므로, 바로 큰 분리보다는 이력 관련 함수 목록과 window export 계약을 먼저 고정하는 방향이 안전합니다.

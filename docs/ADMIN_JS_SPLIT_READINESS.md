# Admin JS Split Readiness

## 버전

v184 admin JS split readiness

## 목적

`admin-page-readonly.js`가 계속 커지고 있어서, 실제 파일 분리를 시작하기 전에 안전하게 나눌 수 있는지 먼저 확인하는 단계입니다.

이번 단계에서는 **실제 파일 분리는 하지 않았습니다.**

기존 게임 런타임, 관리자 쓰기 API, 생성→삭제→복원 일괄 점검 동작은 그대로 유지합니다.

## 추가된 관리자 UI

관리자 페이지에 아래 섹션을 추가했습니다.

```txt
관리자 JS 분리 준비
```

이 섹션은 다음 정보를 표시합니다.

- script 로드 순서
- 필수 global 누락 여부
- `window.RpgAdminReadOnlyPage` export 개수
- 분리 후보 묶음
- 다음 안전 분리 순서

## 분리 후보 순서

첫 실제 분리는 DB 쓰기와 무관한 영역부터 시작하는 것이 안전합니다.

권장 순서:

1. layout shell
2. change logs
3. create lifecycle
4. edit draft
5. bootstrap entry 유지/정리

`layout shell`은 sidebar, sticky header, section collapse 기능이라 DB apply와 직접 연결되지 않습니다.
따라서 다음 단계에서 가장 안전한 첫 분리 후보입니다.

## readiness 확인

브라우저 개발자도구 Console에서 아래 값을 확인합니다.

```js
checkAdminReadOnlyPageReady().version
```

예상값:

```txt
v184.admin-js-split-readiness
```

추가 확인:

```js
checkAdminReadOnlyPageReady().adminJsSplitReadinessReady
```

예상값:

```txt
true
```

자세한 진단값:

```js
getAdminJsSplitReadiness()
```

## smoke

새 smoke를 추가했습니다.

```txt
tools/smoke_admin_js_split_readiness.js
```

`run_smoke_core.sh`에도 포함했습니다.

## DB reset / seed

- DB schema 변경 없음.
- DB reset 필요 없음.
- seed 재실행 필요 없음.
- `.env`, `.gitignore` 변경 없음.


## v185 업데이트

- `layout shell`은 `src/api/admin-layout-shell.js`로 실제 분리되었습니다.
- `admin-page-readonly.js`에는 기존 window export 호환 wrapper가 남아 있습니다.
- 다음 단계는 change logs 분리 전 contract smoke 고정입니다.

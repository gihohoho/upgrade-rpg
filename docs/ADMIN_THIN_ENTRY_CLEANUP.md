# Admin Thin Entry Cleanup

버전: **v195 admin thin entry cleanup**

## 목적

`admin-page-readonly.js`를 관리자 페이지의 마지막 연결 파일처럼 유지하면서, 내부 흐름을 더 읽기 쉽게 정리했습니다.

## 변경 내용

- click action 처리 중앙화
- `getAdminClickActionHandlers()` 추가
- `handleAdminClickAction()` 추가
- window export 등록을 `registerAdminReadOnlyPageExports()`로 묶음
- 외부 모듈 configure 호출을 `configureAdminExternalModules()`로 묶음
- `ADMIN_THIN_ENTRY_CLEANUP_CONTRACT` 추가
- `getAdminThinEntryCleanupReadiness()` 추가
- `renderAdminThinEntryCleanupReadiness()` 추가
- `checkAdminReadOnlyPageReady().thinEntryCleanupReady` 추가

## 유지한 것

- 기존 `data-admin-action` 값 유지
- 기존 window 함수명 유지
- DB 쓰기 정책 변경 없음
- API schema 변경 없음

## 확인

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().thinEntryCleanupReady
getAdminThinEntryCleanupReadiness().status
```

예상:

```txt
v195.admin-thin-entry-cleanup
true
cleaned-v195
```

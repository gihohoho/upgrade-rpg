# Current Status

현재 기준: **v191 admin edit draft split**

이 패키지 기준 ZIP: **rpg_v191_admin_edit_draft_split_ready.zip**

## 완료된 관리자 JS 분리

- v185: layout shell 분리
- v187: change logs 분리
- v189.1: create lifecycle 분리 + helper export hotfix
- v191: edit draft 분리

## v191 완료 내용

- `src/api/admin/admin-edit-draft.js` 추가
- edit draft render/read/reset/review/impact/preview/apply 함수 이동
- relation select 검색/연동 helper 이동
- stale guard 결과 렌더링 이동
- `admin-page-readonly.js`에는 기존 함수명 wrapper 유지
- `admin.html` script 순서 갱신
- edit draft split smoke 추가

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().editDraftExternalReady
window.RpgAdminEditDraft.VERSION
```

예상:

```txt
v191.admin-edit-draft-split
true
v191.admin-edit-draft-split
```

## DB / env

- DB reset 필요 없음
- seed 재실행 필요 없음
- DB schema 변경 없음
- `.env`, `.gitignore` 변경 없음

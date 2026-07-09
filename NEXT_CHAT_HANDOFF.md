# NEXT CHAT HANDOFF — v191

기호는 코딩/터미널/경로에 익숙하지 않으므로, 명령어는 항상 실행 위치를 먼저 적습니다.

## 현재 안정 버전

**v191 admin edit draft split**

## 현재 ZIP

**rpg_v191_admin_edit_draft_split_ready.zip**

## v191 완료

- `src/api/admin/admin-edit-draft.js` 추가
- edit draft 실제 분리 1단계 완료
- 편집 초안/preview/apply/impact/review/relation select/stale guard 렌더링을 외부 파일로 이동
- 기존 window 함수명은 `admin-page-readonly.js` wrapper로 유지
- `admin.html` script 순서에 edit draft 파일 추가
- `tools/smoke_admin_edit_draft_split.js` 추가
- core/all smoke 통과

## 브라우저 확인

```js
checkAdminReadOnlyPageReady().version
```

예상:

```txt
v191.admin-edit-draft-split
```

```js
checkAdminReadOnlyPageReady().editDraftExternalReady
```

예상:

```txt
true
```

```js
window.RpgAdminEditDraft.VERSION
```

예상:

```txt
v191.admin-edit-draft-split
```

## 다음 추천 단계

v192는 **master detail/catalog split contract**를 추천합니다.

실제 분리 전에 아래 계약을 먼저 고정하세요.

- master catalog render/pagination 함수
- master detail open/render 함수
- master relations render 함수
- API verify helper
- window export
- DOM target
- 다음 후보 파일명

후보:

```txt
src/api/admin/admin-master-catalog.js
src/api/admin/admin-master-detail.js
```

## 주의

v189에서 helper 누락 버그가 있었으므로, 앞으로 실제 분리 전에는 contract smoke 또는 runtime smoke를 같이 추가하는 것이 좋습니다.

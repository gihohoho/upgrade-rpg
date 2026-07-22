# Admin Edit Draft Split

Status: v191 admin edit draft split

## Summary

`edit draft` 관리자 기능을 `src/api/admin/admin-edit-draft.js`로 1차 분리했다.

분리 대상:

- 편집 초안 렌더링
- 편집 초안 값 읽기/초기화
- relation select 검색/연동
- impact guide
- draft review
- preview/apply 호출
- stale guard 결과 렌더링

## Compatibility

기존 브라우저 전역 함수명은 `admin-page-readonly.js`의 wrapper로 유지한다.

대표 호환 함수:

- `renderMasterEditDraft`
- `readAdminEditDraftValues`
- `resetAdminEditDraft`
- `previewAdminEditDraft`
- `applyAdminEditDraft`
- `buildAdminEditImpactGuide`
- `renderAdminEditImpactGuide`
- `getAdminEditDraftReadiness`

## Browser checks

```js
checkAdminReadOnlyPageReady().version
checkAdminReadOnlyPageReady().editDraftExternalReady
window.RpgAdminEditDraft.VERSION
```

Expected:

```txt
v191.admin-edit-draft-split
true
v191.admin-edit-draft-split
```

## DB reset / seed

No DB reset is required. No seed rerun is required.

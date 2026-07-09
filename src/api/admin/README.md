# src/api/admin

관리자 페이지 JS 기능을 `src/api/admin-page-readonly.js`에서 단계적으로 분리한 브라우저 모듈 폴더입니다.

`admin-page-readonly.js`는 bootstrap / bindEvents / window wrapper 중심의 thin entry 역할을 유지합니다.

## 현재 주요 모듈

- `admin-change-logs.js` — 변경 이력 조회/상세/rollback UI helper
- `admin-create-lifecycle.js` — 신규 row 생성/삭제/복원 lifecycle helper
- `admin-edit-draft.js` — edit draft / validation / stale guard helper
- `admin-master-catalog.js` — master catalog/detail/relation helper
- `admin-overview-snapshots.js` — overview/save snapshots helper
- `admin-field-help.js` — field help/value hints/equip slot labels
- `admin-settings-helpers.js` — API URL/write key/page URL helper

## 원칙

- `admin-page-readonly.js`가 계속 브라우저 window helper를 안정적으로 노출합니다.
- 기존 콘솔 확인 함수 이름은 가능한 유지합니다.
- 분리 후에는 `tools/smoke_admin_*_split.js`로 static smoke를 추가합니다.

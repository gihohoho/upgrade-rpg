# Next Steps

## 현재 완료: v190 admin edit draft split contract

`edit draft` 실제 분리 전에 필요한 계약을 먼저 고정했습니다.

완료된 항목:

- 다음 후보 파일명 `src/api/admin/admin-edit-draft.js` 고정
- 편집 초안 render/read/reset/preview/apply 함수 목록 고정
- relation select / value hint / impact guide 함수 목록 고정
- `APPLY MASTER DATA EDIT`, `HIGH RISK EDIT` 확인 문구 계약 고정
- DOM target / delegated action 계약 고정
- 새 smoke `tools/smoke_admin_edit_draft_split_contract.js` 추가

## 다음 추천: v191 edit draft 실제 분리 1단계

다음 단계에서는 `src/api/admin/admin-edit-draft.js` 파일을 만들고 edit draft 구현을 외부 파일로 1차 분리하는 것이 좋습니다.

안전한 방향:

1. `src/api/admin/admin-edit-draft.js` 파일 생성.
2. edit draft 렌더/read/reset/review/impact/preview/apply 함수 이동.
3. `admin-page-readonly.js`에는 기존 window export 호환 wrapper 유지.
4. `admin.html` script 순서에 edit draft 파일 추가.
5. v190 contract smoke가 계속 통과하는지 확인.

## 계속 가능한 브라우저 일괄 점검

생성→삭제→복원 일괄 점검은 계속 사용할 수 있습니다. 성공하면 마지막에 row를 다시 복원하므로 테스트 row가 DB에 남습니다.

권장 확인 순서:

1. `skillLevels`
2. `enhancementLevels`
3. `characterSkills`
4. `dropTableItems`

## 아직 미루는 것이 좋은 작업

- Vue 전환.
- 관리자 전체 리디자인.
- 모든 JSON/asset 필드 생성 입력 오픈.
- master-data schema 변경.

## DB reset / seed

- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

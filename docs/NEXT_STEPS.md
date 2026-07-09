# Next Steps

## 현재 완료: v189.1 admin create lifecycle split hotfix

`create lifecycle` 구현을 외부 JS 파일로 1차 분리했습니다.

완료된 항목:

- `src/api/admin/admin-create-lifecycle.js` 신규 추가
- 생성 설계/초안/preview/apply/lifecycle guide/batch check 구현 1차 분리
- `admin-page-readonly.js`에는 호환 wrapper 유지
- `admin.html` script 순서에 create lifecycle 파일 추가
- 새 smoke `tools/smoke_admin_create_lifecycle_split.js` 추가

## 다음 추천: v190 edit draft split contract

다음 단계에서는 `edit draft`를 바로 실제 분리하지 않고, 먼저 분리 전 계약을 고정하는 것이 좋습니다.

권장 고정 항목:

1. 다음 후보 파일명 `src/api/admin/admin-edit-draft.js` 고정.
2. 편집 초안 입력/preview/apply 함수 목록 고정.
3. impact guide / relation select / value hint 함수 목록 고정.
4. window export 목록 고정.
5. DOM target / delegated action 목록 고정.
6. contract smoke를 추가해 다음 실제 분리 전 기준을 만듭니다.

## 계속 가능한 브라우저 일괄 점검

생성→삭제→복원 일괄 점검은 계속 사용할 수 있습니다. 성공하면 마지막에 row를 다시 복원하므로 테스트 row가 DB에 남습니다.

권장 확인 순서:

1. `skillLevels`
2. `enhancementLevels`
3. `characterSkills`
4. `dropTableItems`

부모 도메인인 `skills`, `itemTemplates`, `dropTables`는 연결 데이터가 있을 때 삭제 preview가 차단되는지만 확인하는 편이 안전합니다.

## 그 다음 후보

1. edit draft 기능 분리 전 계약 고정.
2. edit draft 실제 분리 1단계.
3. FastAPI 관리자 라우터/서비스 파일 분리.
4. Vue 전환 전 관리자 기능 목록 정리.

## 아직 미루는 것이 좋은 작업

- Vue 전환.
- 관리자 전체 리디자인.
- 모든 JSON/asset 필드 생성 입력 오픈.
- master-data schema 변경.

## DB reset / seed

- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

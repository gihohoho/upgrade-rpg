# Next Steps

## 현재 완료: v188 admin create lifecycle split contract

`create lifecycle` 실제 분리 전에 API/window/DOM/확인 문구 계약을 고정했습니다.

완료된 항목:

- `ADMIN_CREATE_LIFECYCLE_SPLIT_CONTRACT` 추가
- `contract-frozen-v188` 상태 고정
- 다음 후보 파일명 `src/api/admin/admin-create-lifecycle.js` 고정
- 생성 초안/생성 apply/생성→삭제→복원 batch check 함수 목록 고정
- 확인 문구와 DOM target 목록 고정
- 새 smoke `tools/smoke_admin_create_lifecycle_split_contract.js` 추가

## 다음 추천: v189 create lifecycle 실제 분리 1단계

다음 단계에서는 v188에서 고정한 계약을 유지한 채 `create lifecycle` 구현을 외부 파일로 1차 분리하는 것이 좋습니다.

권장 고정 항목:

1. `src/api/admin/admin-create-lifecycle.js` 파일 생성.
2. 생성 설계/초안/preview/apply 함수 이동.
3. 생성 lifecycle guide / batch check 함수 이동.
4. `admin-page-readonly.js`에는 기존 window export 호환 wrapper 유지.
5. `admin.html` script 순서를 game api → layout shell → change logs → create lifecycle → admin page로 변경.
6. v188 contract smoke가 깨지지 않는지 확인.

## 계속 가능한 브라우저 일괄 점검

생성→삭제→복원 일괄 점검은 계속 사용할 수 있습니다. 성공하면 마지막에 row를 다시 복원하므로 테스트 row가 DB에 남습니다.

권장 확인 순서:

1. `skillLevels`
2. `enhancementLevels`
3. `characterSkills`
4. `dropTableItems`

부모 도메인인 `skills`, `itemTemplates`, `dropTables`는 연결 데이터가 있을 때 삭제 preview가 차단되는지만 확인하는 편이 안전합니다.

## 그 다음 후보

1. create lifecycle 실제 분리.
2. edit draft 기능 분리 전 계약 고정.
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

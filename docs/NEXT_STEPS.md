# Next Steps

## 현재 완료: v186 admin change log split contract

`change logs` 묶음을 실제로 분리하기 전에 필요한 계약을 먼저 고정했습니다.

고정된 항목:

- 변경 이력 백엔드 API 함수
- 변경 이력 window export 함수
- 변경 이력 DOM target
- delegated action 이름
- action filter 값
- 다음 후보 파일명 `src/api/admin/admin-change-logs.js`

## 다음 추천: v187 change logs 실제 분리 1단계

다음 단계에서는 `src/api/admin/admin-change-logs.js` 파일을 새로 만들고, 변경 이력 관련 함수만 외부 파일로 옮기는 것이 좋습니다.

권장 순서:

1. `src/api/admin/` 폴더 생성.
2. `src/api/admin/admin-change-logs.js` 파일 생성.
3. 변경 이력 필터, 목록 렌더, 상세 렌더, rollback/create-delete/restore 관련 함수만 이동.
4. `admin.html` script 순서를 `game-api-client.js` → `admin-layout-shell.js` → `admin/admin-change-logs.js` → `admin-page-readonly.js`로 유지.
5. `admin-page-readonly.js`에는 기존 window export 호환 wrapper를 유지.
6. v186 계약 smoke와 core/all smoke 통과 확인.

## 계속 가능한 브라우저 일괄 점검

생성→삭제→복원 일괄 점검은 계속 사용할 수 있습니다. 성공하면 마지막에 row를 다시 복원하므로 테스트 row가 DB에 남습니다.

권장 확인 순서:

1. `skillLevels`
2. `enhancementLevels`
3. `characterSkills`
4. `dropTableItems`

부모 도메인인 `skills`, `itemTemplates`, `dropTables`는 연결 데이터가 있을 때 삭제 preview가 차단되는지만 확인하는 편이 안전합니다.

## 그 다음 후보

1. create lifecycle 기능 분리.
2. edit draft 기능 분리.
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

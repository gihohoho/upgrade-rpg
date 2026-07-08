# Next Steps

## 현재 완료: v187 admin change logs split

`change logs` 묶음을 `src/api/admin/admin-change-logs.js`로 1차 분리했습니다.

완료된 항목:

- `src/api/admin/` 폴더 생성
- `src/api/admin/admin-change-logs.js` 파일 생성
- 변경 이력 필터/목록/상세 렌더링 이동
- rollback preview/apply 이동
- 생성 row 삭제 preview/apply 이동
- 삭제 row 복원 preview/apply 이동
- `admin-page-readonly.js`에는 호환 wrapper 유지
- `admin.html` script 순서 고정
- 새 smoke `tools/smoke_admin_change_logs_split.js` 추가

## 다음 추천: v188 create lifecycle 분리 계약 고정

다음 단계에서는 바로 `create lifecycle` 구현을 외부 파일로 옮기지 말고, 먼저 분리 전 계약을 고정하는 것이 좋습니다.

권장 고정 항목:

1. 생성 초안 관련 window export 목록.
2. 생성→삭제→복원 batch check 함수 목록.
3. 생성/삭제/복원 결과 렌더링 함수 목록.
4. 확인 문구 상수 목록.
5. DOM target 목록.
6. delegated action 목록.
7. 다음 후보 파일명 `src/api/admin/admin-create-lifecycle.js`.

이 계약이 안정적이면 그 다음 v189에서 실제 `admin-create-lifecycle.js` 분리로 넘어가면 됩니다.

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

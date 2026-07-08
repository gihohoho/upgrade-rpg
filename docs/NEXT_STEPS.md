# Next Steps

## 현재 완료: v183 admin create lifecycle batch check

현재 생성 초안을 기준으로 생성 preview/apply, 삭제 preview/apply, 복원 preview/apply를 한 번에 실행할 수 있는 관리자 일괄 점검 UI를 추가했습니다.

## 다음 추천: leaf row부터 일괄 점검

일괄 점검은 성공하면 마지막에 row를 다시 복원하므로 테스트 row가 DB에 남습니다.
처음에는 하위 연결이 없는 leaf row부터 확인하는 것이 안전합니다.

권장 확인 순서:

1. 관리자 페이지에서 `skillLevels` 생성 blueprint 로드.
2. 기존 스킬을 선택하고 중복되지 않는 `level` 값 입력.
3. 생성 확인 문구에 `CREATE MASTER DATA ROW` 입력.
4. 일괄 점검 확인 문구에 `RUN CREATE DELETE RESTORE CHECK` 입력.
5. `생성→삭제→복원 한 번에 점검` 실행.
6. 단계별 결과가 6단계 모두 ok인지 확인.
7. 같은 흐름을 `enhancementLevels`, `characterSkills`에 반복.
8. 이후 `dropTableItems`처럼 id 기반 leaf row도 확인.
9. 부모 도메인(`skills`, `itemTemplates`, `dropTables`)은 연결 데이터가 있을 때 삭제 preview가 차단되는지만 확인.

## 그 다음 후보

브라우저 일괄 점검까지 안정적이면 다음은 아래 순서가 좋습니다.

1. 관리자 페이지 코드 분리 준비.
2. 관리자 페이지 JS를 기능별 파일로 나누기 전 smoke 범위 고정.
3. `admin-page-readonly.js`를 create/edit/change-log/save 쪽으로 나누는 계획 문서 작성.
4. FastAPI 관리자 라우터/서비스 파일 분리.
5. Vue 전환 전 관리자 기능 목록 정리.

## 아직 미루는 것이 좋은 작업

- Vue 전환.
- 관리자 전체 리디자인.
- 모든 JSON/asset 필드 생성 입력 오픈.
- master-data schema 변경.

## v183 DB reset / seed 결과

- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

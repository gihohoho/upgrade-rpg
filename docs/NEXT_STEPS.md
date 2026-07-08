# Next Steps

## 현재 완료: v185 admin layout shell split

관리자 페이지 JS를 실제로 나누기 전에 script 순서, 필수 global, export 계약, 분리 후보 묶음을 브라우저에서 확인할 수 있는 readiness UI를 추가했습니다. 실제 파일 분리는 아직 하지 않았습니다.

## 다음 추천: change logs 분리 전 readiness/contract smoke

다음 v186에서는 변경 이력 묶음을 바로 분리하기 전에, change logs 함수 목록과 window export 계약을 smoke로 고정하는 것이 좋습니다.

권장 순서:

1. `src/api/admin-layout-shell.js` 후보 파일 생성.
2. sidebar, sticky header, section collapse 관련 함수만 이동.
3. `admin.html` script 순서를 `game-api-client.js` → 분리 파일 → `admin-page-readonly.js`로 유지.
4. 기존 `checkAdminReadOnlyPageReady().layoutShellReady`와 `adminJsSplitReadinessReady`가 true인지 확인.
5. core/all smoke 통과 확인.

## 계속 가능한 브라우저 일괄 점검

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

layout shell 분리가 안정적이면 다음은 아래 순서가 좋습니다.

1. change log 기능 분리.
2. create lifecycle 기능 분리.
3. edit draft 기능 분리.
4. FastAPI 관리자 라우터/서비스 파일 분리.
5. Vue 전환 전 관리자 기능 목록 정리.

## 아직 미루는 것이 좋은 작업

- Vue 전환.
- 관리자 전체 리디자인.
- 모든 JSON/asset 필드 생성 입력 오픈.
- master-data schema 변경.

## v184 DB reset / seed 결과

- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.


## v185 이후 주의

`layout shell`은 이미 `src/api/admin-layout-shell.js`로 분리되었습니다. 다음 분리는 rollback/create-delete 흐름과 연결되므로, 실제 이동 전에 contract smoke를 먼저 추가하는 것이 안전합니다.

# Next Steps

## 현재 완료: v182 admin create lifecycle result summary

신규 row 생성 apply 도메인을 더 열지 않고, 이미 열린 생성→삭제→복원 흐름의 결과 화면을 더 안전하게 읽을 수 있도록 요약 카드를 추가했습니다.

## 다음 추천: 브라우저 실제 검증

이제 다음은 코드 변경보다 브라우저 실제 확인이 안전합니다.

권장 확인 순서:

1. 관리자 페이지에서 `skillLevels` 생성 blueprint 로드.
2. `신규 row 생성·삭제·복원 점검` 섹션에서 삭제 preview 차단 기준이 보이는지 확인.
3. `create` 이력 보기 버튼으로 변경 이력 필터가 바로 적용되는지 확인.
4. `skillLevels` 생성 preview/apply 확인.
5. 변경 이력에서 create 이력을 열고 id 기반 삭제 preview를 눌러 결과 요약 카드가 보이는지 확인.
6. 삭제 apply 후 `create_delete` 이력에서 복원 preview를 눌러 결과 요약 카드가 보이는지 확인.
7. 같은 흐름을 `enhancementLevels`, `characterSkills`에 반복.
8. 부모 도메인(`skills`, `itemTemplates`, `dropTables`)은 연결 데이터가 있을 때 삭제 preview가 차단되는지만 확인.

## 그 다음 후보

브라우저 확인까지 안정적이면 다음은 아래 순서가 좋습니다.

1. 관리자 페이지 코드 분리 준비.
2. 관리자 페이지 JS를 도메인별/기능별 파일로 나누기 전 smoke 고정.
3. 관리자 페이지 JS 파일 분리 전 smoke 범위 고정.
4. FastAPI 관리자 라우터/서비스 파일 분리.
5. Vue 전환 전 관리자 기능 목록 정리.

## 아직 미루는 것이 좋은 작업

- Vue 전환.
- 관리자 전체 리디자인.
- 모든 JSON/asset 필드 생성 입력 오픈.
- master-data schema 변경.

## v182 DB reset / seed 결과

- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

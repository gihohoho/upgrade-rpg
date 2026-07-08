# Next Steps

## 현재 완료: v176 create apply bosses

`bosses` 신규 row 생성 apply를 제한적으로 열었고, 생성 row 삭제/복원 guard도 같은 제한 범위에 맞춰 확장했습니다.

## 다음 추천: 생성/삭제/복원 실제 브라우저 검증

다음 단계는 새 도메인을 더 여는 것보다, 지금 열린 도메인의 실제 흐름을 브라우저에서 확인하는 것이 안전합니다.

권장 확인 순서:

1. 관리자 페이지에서 `bosses` 생성 blueprint 로드.
2. `bosses` 생성 preview/apply 확인.
3. 생성된 `bosses` row 삭제 preview 확인.
4. `dropTables.owner_type=boss + owner_code` blocker 표시 확인.
5. 삭제/복원 apply까지 확인.

## 그 다음 후보

브라우저 확인까지 안정적이면 다음은 아래 순서가 좋습니다.

1. create/delete/restore UI에서 위험도와 dependency 표시 강화.
2. 관리자 페이지 코드 분리 준비.
3. `admin.html` 내부 script/css가 너무 커지면 기능별 JS/CSS 파일 분리.
4. 이후 `skills` create apply는 별도 검토.

## 아직 미루는 것이 좋은 작업

- Vue 전환.
- 관리자 전체 리디자인.
- 모든 도메인 create apply 일괄 오픈.
- `itemTemplates` 신규 생성 apply.
- `dropTables` 신규 생성 apply.
- `dropTableItems` 신규 생성 apply.
- `skills` 신규 생성 apply.

## v176 DB reset / seed 결과

- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

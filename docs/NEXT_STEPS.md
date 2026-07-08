# Next Steps

## 현재 완료: v178 create apply itemTemplates/dropTableItems

`itemTemplates`와 `dropTableItems` 신규 row 생성 apply를 제한적으로 열었고, 생성 row 삭제/복원 guard도 같은 제한 범위에 맞춰 확장했습니다.

## 다음 추천: 브라우저 실제 검증

다음 단계는 새 도메인을 더 여는 것보다, 이번에 열린 `itemTemplates`, `dropTableItems` 실제 흐름을 브라우저에서 확인하는 것이 안전합니다.

권장 확인 순서:

1. 관리자 페이지에서 `itemTemplates` 생성 blueprint 로드.
2. `base_stats_json`, `options_json`, asset 계열 필드가 생성 입력에서 잠긴 상태인지 확인.
3. `itemTemplates` 생성 preview/apply 확인.
4. 생성된 `itemTemplates` row 삭제 preview에서 `dropTableItems.item_template_code`, `itemInstances.template_code` blocker 표시 확인.
5. 삭제/복원 apply까지 확인.
6. 관리자 페이지에서 `dropTableItems` 생성 blueprint 로드.
7. `drop_table_code`, `item_template_code` relation select 후보가 보이는지 확인.
8. `rate`, `min_quantity`, `max_quantity` 검증이 동작하는지 확인.
9. `dropTableItems` 생성 preview/apply 확인.
10. 생성된 `dropTableItems` row가 id 기반으로 삭제/복원되는지 확인.

## 그 다음 후보

브라우저 확인까지 안정적이면 다음은 아래 순서가 좋습니다.

1. `skillLevels` create apply를 열기 전 combo unique/삭제 정책 재확인.
2. `enhancementLevels` create apply를 열기 전 강화 그룹 max_level과 단계 연결 정책 재확인.
3. `characterSkills` create apply를 열기 전 기본 스킬 연결 중복/정렬 정책 재확인.
4. create/delete/restore UI에서 dependency 표시를 더 직관적으로 강화.
5. 관리자 페이지 코드 분리 준비.

## 아직 미루는 것이 좋은 작업

- Vue 전환.
- 관리자 전체 리디자인.
- 모든 도메인 create apply 일괄 오픈.
- `skillLevels`, `enhancementLevels`, `characterSkills` 신규 생성 apply 일괄 오픈.

## v178 DB reset / seed 결과

- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

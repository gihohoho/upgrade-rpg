# Next Steps

## 현재 완료: v177 create apply skills/dropTables

`skills`와 `dropTables` 신규 row 생성 apply를 제한적으로 열었고, 생성 row 삭제/복원 guard도 같은 제한 범위에 맞춰 확장했습니다.

## 다음 추천: 브라우저 실제 검증

다음 단계는 새 도메인을 더 여는 것보다, 이번에 열린 `skills`, `dropTables` 실제 흐름을 브라우저에서 확인하는 것이 안전합니다.

권장 확인 순서:

1. 관리자 페이지에서 `skills` 생성 blueprint 로드.
2. `skills` 생성 preview/apply 확인.
3. 생성된 `skills` row 삭제 preview 확인.
4. `skillLevels.skill_code`, `characterSkills.skill_code`, `userCharacterSkills.skill_code` blocker 표시 확인.
5. 삭제/복원 apply까지 확인.
6. 관리자 페이지에서 `dropTables` 생성 blueprint 로드.
7. `owner_type` 변경 시 `owner_code` 후보가 보스/필드로 전환되는지 확인.
8. `dropTables` 생성 preview/apply 확인.
9. 생성된 `dropTables` row 삭제 preview에서 `dropTableItems.drop_table_code` blocker 표시 확인.
10. 삭제/복원 apply까지 확인.

## 그 다음 후보

브라우저 확인까지 안정적이면 다음은 아래 순서가 좋습니다.

1. create/delete/restore UI에서 dependency 표시를 더 직관적으로 강화.
2. `dropTableItems` create apply를 열기 전에 id 기반 생성 row 삭제/복원 지원 검토.
3. `itemTemplates` create apply를 열기 전에 JSON/asset/base_stats/options 입력 정책 정리.
4. 관리자 페이지 코드 분리 준비.

## 아직 미루는 것이 좋은 작업

- Vue 전환.
- 관리자 전체 리디자인.
- 모든 도메인 create apply 일괄 오픈.
- `itemTemplates` 신규 생성 apply.
- `dropTableItems` 신규 생성 apply.
- `skillLevels`, `enhancementLevels`, `characterSkills` 신규 생성 apply.

## v177 DB reset / seed 결과

- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

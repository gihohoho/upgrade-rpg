# Next Steps

## 현재 완료: v179 create apply level/link tables

`skillLevels`, `enhancementLevels`, `characterSkills` 신규 row 생성 apply를 제한적으로 열었고, 생성 row 삭제/복원 guard도 id 기반으로 확장했습니다.

## 다음 추천: 브라우저 실제 검증

다음 단계는 새 도메인을 더 여는 것보다, 이번에 열린 level/link 계열 row의 실제 흐름을 브라우저에서 확인하는 것이 안전합니다.

권장 확인 순서:

1. 관리자 페이지에서 `skillLevels` 생성 blueprint 로드.
2. `skill_code` relation select 후보가 보이는지 확인.
3. `skill_code + level` 중복 검증이 동작하는지 확인.
4. `skillLevels` 생성 preview/apply 확인.
5. 생성된 `skillLevels` row가 id 기반으로 삭제/복원되는지 확인.
6. 관리자 페이지에서 `enhancementLevels` 생성 blueprint 로드.
7. `group_code` relation select 후보가 보이는지 확인.
8. `group_code + from_level`, `to_level > from_level`, 확률/비용 검증이 동작하는지 확인.
9. `enhancementLevels` 생성 preview/apply/delete/restore 확인.
10. 관리자 페이지에서 `characterSkills` 생성 blueprint 로드.
11. `character_code`, `skill_code` relation select 후보가 보이는지 확인.
12. `character_code + skill_code` 중복 검증이 동작하는지 확인.
13. `characterSkills` 생성 preview/apply/delete/restore 확인.

## 그 다음 후보

브라우저 확인까지 안정적이면 다음은 아래 순서가 좋습니다.

1. 관리자 페이지 코드 분리 준비.
2. create/delete/restore UI에서 dependency와 combo guard 표시를 더 직관적으로 강화.
3. 관리자 relation select 성능/검색 UX 개선.
4. FastAPI 관리자 라우터/서비스 파일 분리.
5. Vue 전환 전 관리자 기능 목록 정리.

## 아직 미루는 것이 좋은 작업

- Vue 전환.
- 관리자 전체 리디자인.
- 모든 JSON/asset 필드 생성 입력 오픈.
- master-data schema 변경.

## v179 DB reset / seed 결과

- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.

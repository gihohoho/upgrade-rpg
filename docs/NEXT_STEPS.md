# Next Steps

## 1순위 추천: 관리자 allow-list 추가 확장 후보 검토

v138에서 적용 직전 비교 UI와 high risk 추가 확인을 넣었기 때문에, 다음에는 조금 더 과감하게 실제 수정 가능한 필드를 늘릴 수 있습니다.

우선 검토 후보:

- `dropTables.owner_type`
- `dropTables.owner_code`
- `dropTableItems.item_template_code`
- `itemTemplates.enhance_group_code`
- `skillLevels.level`
- `enhancementLevels.from_level`

단, 위 필드는 대부분 관계/연결 필드라 잘못 바꾸면 드랍, 강화, 스킬 레벨 연결이 깨질 수 있습니다. 그래서 바로 전부 열기보다는 select 후보를 만들고, 관계 대상이 실제 존재하는지 백엔드 검증을 붙인 뒤 여는 편이 안전합니다.

DB reset/seed는 필요 없을 가능성이 높지만, 관계 검증 API를 추가하면 백엔드 smoke를 같이 늘리는 것이 좋습니다.

## 2순위: 관리자 변경 전 영향 시뮬레이션 강화

현재는 영향 안내와 before/after 비교까지 있습니다. 다음에는 변경하려는 값이 실제로 연결된 대상에 어떤 영향을 주는지 더 구체적으로 보여줄 수 있습니다.

예시:

- 특정 장비의 `equip_slot` 변경 전 연결 강화 그룹 표시
- 특정 드랍 아이템의 드랍 테이블/소유자 표시
- 특정 스킬의 characterSkills 연결 표시
- 특정 강화 레벨의 그룹/이전 단계/다음 단계 표시

## 3순위: 정식 인증/권한 설계 준비

현재 `local-admin-dev-key`는 개발용 안전장치입니다. 실서비스 구조로 가려면 로그인, 권한, 관리자 계정 설계를 준비해야 합니다.

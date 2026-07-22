# Admin Change Log Relation Tools

v154~v156에서는 이미 저장된 관리자 변경 이력과 rollback preview에서도 relation 값이 코드만 보이지 않도록 표시를 강화했습니다.

## 목표

- 변경 이력 상세의 before/after relation 값에 대상 이름을 함께 표시합니다.
- rollback preview의 되돌릴 값과 현재값 안전 검사 표에서도 relation label을 표시합니다.
- relation 값 옆에서 대상 상세를 바로 열 수 있게 유지합니다.
- 변경 이력 목록/상세/rollback summary에 relation 변경 개수를 표시합니다.

## 적용 범위

- `itemTemplates.enhance_group_code`
- `dropTables.owner_type`
- `dropTables.owner_code`
- `dropTableItems.drop_table_code`
- `dropTableItems.item_template_code`
- `skillLevels.skill_code`
- `enhancementLevels.group_code`
- `characterSkills.character_code`
- `characterSkills.skill_code`

## 안전장치

- 변경 이력 list endpoint는 before/after 원본 JSON을 계속 숨깁니다.
- 상세 endpoint는 안전한 scalar change row만 반환합니다.
- rollback은 기존처럼 현재 DB 값이 변경 이력의 after 값과 일치할 때만 가능합니다.
- 기존 dev key, rollback 확인 문구, stale guard, post-write verify를 유지합니다.

## DB reset / seed

필요 없습니다. schema와 seed 데이터는 변경하지 않았습니다.

# Admin Create Apply ItemTemplates and DropTableItems

v178에서는 신규 row 생성 apply 제한 도메인에 `itemTemplates`와 `dropTableItems`를 추가했다.

## 열린 범위

실제 DB insert가 가능한 도메인은 아래 여덟 개다.

- `characters`
- `enhancementGroups`
- `fieldZones`
- `bosses`
- `skills`
- `dropTables`
- `itemTemplates`
- `dropTableItems`

## itemTemplates 생성 정책

`itemTemplates`는 장비/재료/강화권 등 아이템 기준 데이터라 런타임 영향이 크다. 그래서 v178에서는 아래 scalar/relation 필드만 생성 apply에 사용한다.

- `code`
- `name`
- `item_type`
- `grade`
- `description`
- `stackable`
- `equip_slot`
- `enhance_group_code`
- `admin_note`

아래 필드는 계속 잠근다.

- `base_stats_json`
- `options_json`
- `icon_url` 같은 asset 계열 필드

`enhance_group_code`는 비워둘 수 있고, 값을 넣으면 `enhancementGroups.code`에 실제 존재해야 한다.

## dropTableItems 생성 정책

`dropTableItems`는 특정 드랍 테이블에 어떤 아이템이 어떤 확률로 떨어지는지 연결하는 leaf row다. v178에서는 아래 scalar/relation 필드만 생성 apply에 사용한다.

- `drop_table_code`
- `item_template_code`
- `rate`
- `min_quantity`
- `max_quantity`

아래 필드는 계속 잠근다.

- `conditions_json`

`drop_table_code`는 `dropTables.code`에 실제 존재해야 하고, `item_template_code`는 `itemTemplates.code`에 실제 존재해야 한다.

## dropTableItems 추가 검증

생성 preview/apply에서 아래 값을 검사한다.

- `rate`는 0 이상이어야 한다.
- `min_quantity`는 1 이상이어야 한다.
- `max_quantity`는 1 이상이어야 한다.
- `max_quantity`는 `min_quantity`보다 작을 수 없다.

## 생성 row 삭제 guard

`itemTemplates` 생성 row를 삭제 되돌리기할 때는 아래 연결을 검사한다.

- `dropTableItems.item_template_code`
- `itemInstances.template_code`

연결된 드랍 아이템이나 유저 아이템 인스턴스가 있으면 `dependencyBlockerCount`가 올라가고 삭제 apply를 차단한다.

`dropTableItems`는 하위 연결이 없는 leaf row라 `code`가 없어도 id 기반으로 삭제/복원할 수 있게 열었다. 그래도 현재값이 생성 당시 값과 달라졌으면 삭제 apply는 차단된다.

## 복원 guard

`create_delete` 이력으로 삭제된 `itemTemplates` 또는 `dropTableItems` row는 아래 조건을 통과할 때만 복원할 수 있다.

- 원래 id가 현재 DB에 없음
- `itemTemplates`는 원래 code가 다른 row에서 재사용되지 않음
- 저장된 삭제 전 값이 생성 blueprint 검증을 다시 통과함
- `itemTemplates.enhance_group_code` relation 검증을 다시 통과함
- `dropTableItems.drop_table_code` / `item_template_code` relation 검증을 다시 통과함

## 계속 잠긴 범위

아래 도메인은 계속 preview-only다.

- `skillLevels`
- `enhancementLevels`
- `characterSkills`

이 세 도메인은 combo unique 성격이 강하고 게임 성장/기본 스킬 연결에 직접 영향을 주므로 별도 단계에서 여는 것이 안전하다.

## DB reset / seed

필요 없음.

DB schema 변경도 없다.

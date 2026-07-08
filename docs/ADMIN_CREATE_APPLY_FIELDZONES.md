# Admin Create Apply FieldZones

v175에서는 신규 row 생성 apply 제한 도메인에 `fieldZones`를 추가했다.

## 열린 범위

실제 DB insert가 가능한 도메인은 아래 세 개다.

- `characters`
- `enhancementGroups`
- `fieldZones`

`fieldZones`는 필드 구역 기준 데이터이며, JSON 필드(`entry_rules_json`, `farm_rules_json`)와 asset 필드는 여전히 생성 입력에서 잠근다. 생성 apply는 scalar 필드만 받는다.

## 계속 잠긴 범위

아래 도메인은 계속 preview-only다.

- `itemTemplates`
- `skills`
- `dropTables`
- `dropTableItems`
- `skillLevels`
- `bosses`
- `enhancementLevels`
- `characterSkills`

## fieldZones 생성 필드

생성 초안에서 입력 가능한 필드는 아래와 같다.

- `code`
- `name`
- `sort_order`
- `enemy_hp`
- `gold_reward`
- `description`
- `is_enabled`

`code`는 unique 중복 검사를 거친다.

## 삭제 dependency guard

`fieldZones` 생성 row를 삭제 되돌리기할 때는 아래 연결을 검사한다.

- `dropTables.owner_type = field`
- `dropTables.owner_code = fieldZones.code`

연결된 드랍 테이블이 하나라도 있으면 `dependencyBlockerCount`가 올라가고 삭제 apply를 차단한다.

## 복원 guard

`create_delete` 이력으로 삭제된 `fieldZones` row는 아래 조건을 통과할 때만 복원할 수 있다.

- 원래 id가 현재 DB에 없음
- 원래 code가 다른 row에서 재사용되지 않음
- 저장된 삭제 전 값이 생성 blueprint 검증을 다시 통과함

## DB reset / seed

필요 없음.

DB schema 변경도 없다.

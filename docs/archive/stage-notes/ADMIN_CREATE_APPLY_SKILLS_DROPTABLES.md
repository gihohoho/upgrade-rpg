# Admin Create Apply Skills and DropTables

v177에서는 신규 row 생성 apply 제한 도메인에 `skills`와 `dropTables`를 추가했다.

## 열린 범위

실제 DB insert가 가능한 도메인은 아래 여섯 개다.

- `characters`
- `enhancementGroups`
- `fieldZones`
- `bosses`
- `skills`
- `dropTables`

`skills`는 스킬 기준 데이터이고, `options_json`과 이미지/asset 필드는 생성 입력에서 잠근다. 생성 apply는 `code`, `name`, `slot_key`, `description`, `proc_rate`, `cooldown_seconds` 같은 scalar 필드만 받는다.

`dropTables`는 보스/필드별 드랍 묶음 데이터이고, `rules_json`은 생성 입력에서 잠근다. `owner_type`과 `owner_code`는 기존 relation select 검증을 그대로 사용한다.

## 계속 잠긴 범위

아래 도메인은 계속 preview-only다.

- `itemTemplates`
- `dropTableItems`
- `skillLevels`
- `enhancementLevels`
- `characterSkills`

## skills 생성 필드

생성 초안에서 입력 가능한 필드는 아래와 같다.

- `code`
- `name`
- `slot_key`
- `description`
- `proc_rate`
- `cooldown_seconds`

`code`는 unique 중복 검사를 거친다.

## dropTables 생성 필드

생성 초안에서 입력 가능한 필드는 아래와 같다.

- `code`
- `owner_type`
- `owner_code`
- `description`
- `is_enabled`

`code`는 unique 중복 검사를 거친다. `owner_code`는 `owner_type`에 따라 `bosses.code` 또는 `fieldZones.code`에 실제 존재해야 한다.

## 삭제 dependency guard

`skills` 생성 row를 삭제 되돌리기할 때는 아래 연결을 검사한다.

- `skillLevels.skill_code`
- `characterSkills.skill_code`
- `userCharacterSkills.skill_code`

연결된 스킬 레벨, 캐릭터 스킬 연결, 유저 스킬 데이터가 하나라도 있으면 `dependencyBlockerCount`가 올라가고 삭제 apply를 차단한다.

`dropTables` 생성 row를 삭제 되돌리기할 때는 아래 연결을 검사한다.

- `dropTableItems.drop_table_code`

연결된 드랍 아이템이 하나라도 있으면 삭제 apply를 차단한다.

## 복원 guard

`create_delete` 이력으로 삭제된 `skills` 또는 `dropTables` row는 아래 조건을 통과할 때만 복원할 수 있다.

- 원래 id가 현재 DB에 없음
- 원래 code가 다른 row에서 재사용되지 않음
- 저장된 삭제 전 값이 생성 blueprint 검증을 다시 통과함
- `dropTables`는 `owner_type + owner_code` relation 검증을 다시 통과함

## 이번 단계에서 열지 않은 도메인

v178에서 `itemTemplates`와 `dropTableItems`는 JSON/asset 필드 잠금과 id 기반 삭제/복원 guard를 추가한 뒤 열었다. 아래 도메인은 아직 create apply를 열지 않는다.

- `skillLevels`
- `enhancementLevels`
- `characterSkills`

## DB reset / seed

필요 없음.

DB schema 변경도 없다.

# Admin Create Apply Bosses

v176에서는 신규 row 생성 apply 제한 도메인에 `bosses`를 추가했다.

## 열린 범위

v176 당시 실제 DB insert가 가능한 도메인은 아래 네 개였다.

- `characters`
- `enhancementGroups`
- `fieldZones`
- `bosses`

`bosses`는 보스 기준 데이터이며, `summon_rules_json`과 이미지/asset 필드는 생성 입력에서 잠근다. 생성 apply는 scalar 필드만 받는다.

## 계속 잠긴 범위

v176 당시 아래 도메인은 계속 preview-only였다.

- `itemTemplates`
- `skills`
- `dropTables`
- `dropTableItems`
- `skillLevels`
- `enhancementLevels`
- `characterSkills`

## bosses 생성 필드

생성 초안에서 입력 가능한 필드는 아래와 같다.

- `code`
- `name`
- `tier`
- `boss_type`
- `hp`
- `description`
- `cooldown_seconds`
- `is_enabled`

`code`는 unique 중복 검사를 거친다.

## 삭제 dependency guard

`bosses` 생성 row를 삭제 되돌리기할 때는 아래 연결을 검사한다.

- `dropTables.owner_type = boss`
- `dropTables.owner_code = bosses.code`

연결된 드랍 테이블이 하나라도 있으면 `dependencyBlockerCount`가 올라가고 삭제 apply를 차단한다.

## 복원 guard

`create_delete` 이력으로 삭제된 `bosses` row는 아래 조건을 통과할 때만 복원할 수 있다.

- 원래 id가 현재 DB에 없음
- 원래 code가 다른 row에서 재사용되지 않음
- 저장된 삭제 전 값이 생성 blueprint 검증을 다시 통과함

## 이번 단계에서 열지 않은 도메인

v177에서 `skills`와 `dropTables`는 별도 guard를 추가한 뒤 열었다. 아래 도메인은 아직 create apply를 열지 않는다.

- `itemTemplates`
- `dropTableItems`

## DB reset / seed

필요 없음.

DB schema 변경도 없다.

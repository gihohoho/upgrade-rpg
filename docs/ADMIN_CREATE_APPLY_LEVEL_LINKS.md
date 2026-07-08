# Admin Create Apply Level and Link Tables

## 버전

- v179: create apply level/link tables

## 목적

`skillLevels`, `enhancementLevels`, `characterSkills` 신규 row 생성 apply를 제한적으로 열었습니다.

기존 게임 동작을 유지하기 위해 JSON 계열 필드는 계속 생성 입력에서 잠그고, 관계/조합 검증을 통과한 scalar 필드만 DB insert 대상에 포함합니다.

## 이번에 열린 도메인

- `skillLevels`
- `enhancementLevels`
- `characterSkills`

## 현재 생성 apply 열린 전체 도메인

- `characters`
- `enhancementGroups`
- `fieldZones`
- `bosses`
- `skills`
- `dropTables`
- `itemTemplates`
- `dropTableItems`
- `skillLevels`
- `enhancementLevels`
- `characterSkills`

## 검증 정책

### skillLevels

- `skill_code`는 실제 `skills.code`에 존재해야 합니다.
- `level`은 0 이상이어야 합니다.
- `skill_code + level` 조합이 이미 있으면 생성 apply를 차단합니다.
- `options_json`은 생성 입력에서 잠금 상태입니다.

### enhancementLevels

- `group_code`는 실제 `enhancementGroups.code`에 존재해야 합니다.
- `from_level`은 0 이상이어야 합니다.
- `to_level`은 `from_level`보다 커야 합니다.
- `success_rate`는 0 이상이어야 합니다.
- `gold_cost`는 0 이상이어야 합니다.
- `group_code + from_level` 조합이 이미 있으면 생성 apply를 차단합니다.
- `material_rules_json`, `result_stats_json`, `fail_rules_json`은 생성 입력에서 잠금 상태입니다.

### characterSkills

- `character_code`는 실제 `characters.code`에 존재해야 합니다.
- `skill_code`는 실제 `skills.code`에 존재해야 합니다.
- `character_code + skill_code` 조합이 이미 있으면 생성 apply를 차단합니다.
- `sort_order`는 0 이상이어야 합니다.

## 생성 row 삭제/복원

이번 3개 도메인은 `code`가 없는 relation/level row라 id 기반 삭제/복원을 사용합니다.

- `skillLevels`: `skill_levels.id` 기준
- `enhancementLevels`: `enhancement_levels.id` 기준
- `characterSkills`: `character_skills.id` 기준

삭제 preview는 생성 당시 값과 현재 DB 값이 같을 때만 통과합니다. 복원 preview는 같은 id 충돌과 조합 중복 검증을 다시 통과해야 합니다.

## 안전성 메모

- DB schema 변경 없음.
- DB reset / seed 필요 없음.
- `.env`, `.gitignore` 변경 없음.
- 기존 v178의 `itemTemplates`, `dropTableItems` 생성 apply 정책은 유지합니다.

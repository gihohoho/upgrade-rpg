# Admin Combo Relation Guard

기준 버전: **v144 admin combo relation guard**

## 목적

v141에서 단일 관계 필드 select를 열었고, v144에서는 조합으로 묶여야 안전한 관계 필드를 추가로 열었습니다. 텍스트 직접 입력은 계속 막고, 실제 DB 대상 목록 기반 select와 백엔드 중복 조합 검증을 함께 사용합니다.

## 새로 실제 적용 가능해진 관계/조합 필드

| 도메인 | 필드 | 검증 |
|---|---|---|
| `dropTableItems` | `drop_table_code` | 선택한 `dropTables.code`가 실제 존재해야 함 |
| `skillLevels` | `skill_code`, `level` | `skill_code`가 실제 존재해야 하고 `skill_code + level` 조합이 중복되면 차단 |
| `enhancementLevels` | `group_code`, `from_level` | `group_code`가 실제 존재해야 하고 `group_code + from_level` 조합이 중복되면 차단 |
| `characterSkills` | `character_code`, `skill_code` | 캐릭터/스킬 코드가 실제 존재해야 하고 `character_code + skill_code` 조합이 중복되면 차단 |

## 유지되는 안전장치

- dev key guard 유지
- `APPLY MASTER DATA EDIT` 확인 문구 유지
- high risk 변경 시 `HIGH RISK EDIT` 추가 확인 유지
- stale guard 유지
- change log / rollback 유지
- relation select는 실제 대상 목록 기반
- preview/apply 공통으로 관계 존재 여부와 중복 조합 검사

## 아직 잠근 필드

아래 필드는 여전히 바로 열지 않았습니다.

- `dropTables.owner_code`
- JSON 원본 필드
- 이미지/asset URL 필드
- id/code 식별자 자체

`dropTables.owner_code`는 owner_type과 함께 움직여야 해서, 다음 단계에서 boss/field 대상 목록 기반 select로 묶어 여는 것이 안전합니다.

## DB reset / seed

DB reset / seed는 필요 없습니다. 기존 DB 스키마와 데이터 위에서 관리자 UI/API 검증만 확장했습니다.

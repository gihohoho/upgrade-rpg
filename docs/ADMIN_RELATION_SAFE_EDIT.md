# Admin Relation Safe Edit

현재 기준: **v141 admin relation safe edit**

관리자 편집 초안에서 일부 관계 필드를 바로 텍스트로 입력하지 않고, 실제 DB에 존재하는 대상 목록 기반 `relation select`로 고르게 했습니다. 관계 필드는 잘못 바꾸면 드랍/강화 연결이 깨질 수 있으므로, 프론트에서 선택지를 제한하고 백엔드가 적용 직전에 다시 존재 여부를 검증합니다.

## 이번에 연 관계 필드

- `itemTemplates.enhance_group_code`
  - 대상: `enhancementGroups.code`
  - 빈 값 허용
  - 장비가 어떤 강화 그룹을 사용할지 연결합니다.
- `dropTableItems.item_template_code`
  - 대상: `itemTemplates.code`
  - 빈 값 불가
  - 드랍 테이블에서 실제로 떨어지는 아이템을 연결합니다.
- `dropTables.owner_type`
  - 선택값: `boss`, `field`
  - `owner_code`는 아직 잠금입니다.
  - 선택한 `owner_type` 기준으로 현재 `owner_code`가 실제 보스/필드 코드에 존재해야 통과합니다.

## 안전장치

- 관계 필드는 `relation select`로 표시합니다.
- 현재 상세 응답에 `relationEditOptions`를 내려줍니다.
- 백엔드 preview/apply 공통 검증에서 대상 존재 여부를 다시 검사합니다.
- 존재하지 않는 대상 코드는 reject 처리합니다.
- high risk 필드는 기존처럼 `APPLY MASTER DATA EDIT`와 `HIGH RISK EDIT` 확인을 거쳐야 합니다.
- stale guard와 change log/rollback 구조는 그대로 유지합니다.

## 아직 잠금 유지

아래는 아직 열지 않았습니다.

- `dropTables.owner_code`
- `dropTableItems.drop_table_code`
- `skillLevels.skill_code`
- `skillLevels.level`
- `enhancementLevels.group_code`
- `enhancementLevels.from_level`
- `characterSkills.character_code`
- `characterSkills.skill_code`

이 필드들은 조합 유니크 제약이나 대량 연결 변경 위험이 있어 다음 단계에서 별도 안전 UI를 붙이는 편이 좋습니다.

## DB reset / seed

DB reset / seed는 필요 없습니다.

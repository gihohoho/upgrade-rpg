# Admin Safe Selects + Allow-list Expansion

현재 기준: **v134 admin safe selects**

v134에서는 관리자 마스터 데이터 편집 초안에서 enum 성격의 문자열 필드를 자유 텍스트가 아니라 프리셋 select로 고르게 했습니다.
실수로 오타를 넣어 런타임 분류가 깨지는 일을 줄이기 위한 단계입니다.

## 새로 실제 적용까지 연 필드

백엔드 allow-list와 관리자 UI allow-list를 같이 확장했습니다.

- `itemTemplates.item_type`
- `itemTemplates.equip_slot`
- `skills.slot_key`

기존에 열려 있던 필드는 그대로 유지합니다.

## preset select 대상

- `item_type`
  - `normal`
  - `skill_book`
  - `special_equip`
  - `abyss`
  - `avatar`
  - `material`
  - `consumable`
  - `unknown`
- `equip_slot`
  - 빈 값
  - `skill_all`
  - `skill_dmg`
  - `skill_chance`
  - `atk_inc`
  - `normal_dmg`
  - `normal_crit`
  - `all_dmg`
  - `6` ~ `14` 특수 슬롯
- `boss_type`
  - `normal`
  - `special`
- `slot_key`
  - `Q`, `W`, `E`, `R`, `T`, `F`, `D`, `M`
  - `SQ`, `SW`, `SE`, `SR`, `ST`, `SF`, `SD`, `SM`

현재 DB 값이 프리셋에 없으면 select 맨 위에 “현재 DB 값”으로 보이게 했습니다.
이렇게 하면 기존 데이터를 숨기지 않고, 새 값은 안전한 프리셋에서 고를 수 있습니다.

## 위험도 표시

편집 초안 필드 제목 오른쪽에 위험도 배지를 추가했습니다.

- `risk high`: 인게임 동작, 전투, 드랍, 장착, 슬롯 배치에 직접 영향을 줄 수 있는 필드
- `risk medium`: 표시, 정렬, 구간 정보에 영향을 줄 수 있는 필드
- `risk low`: 관리자 메모나 설명처럼 비교적 안전한 필드

## 유지한 잠금 정책

아래 필드는 계속 잠금입니다.

- `id`
- `code`
- `*_id`
- `*_code`
- `*_json`
- `created_at`
- `updated_at`
- asset/image/icon 계열

관계 필드와 JSON 필드는 아직 직접 편집하지 않는 것이 안전합니다.

## DB reset / seed

필드 추가나 schema 변경이 아니라 allow-list와 관리자 UI만 바꾼 단계입니다.

**DB reset / seed는 필요 없습니다.**

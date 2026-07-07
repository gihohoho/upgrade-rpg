# Next Steps

## 1순위 추천: 관리자 allow-list 확장

v133에서 관리자 편집 초안 입력 UI 타입을 정리했으므로, 다음 단계에서는 실제로 수정 가능한 필드를 조금씩 늘리는 것이 좋습니다.

추천 후보:

- skills: `name`, `description`, `cooldown_seconds`, `proc_rate`
- dropTableItems: `rate`, `min_quantity`, `max_quantity`
- enhancementLevels: `success_rate`, `gold_cost`
- fieldZones: `enemy_hp`, `gold_reward`, `is_enabled`

관계 필드(`*_id`, `*_code`)는 아직 잠금 유지가 안전합니다.

DB reset/seed는 필요 없을 가능성이 높지만, allow-list만 늘리는지 DB 컬럼을 새로 추가하는지에 따라 다시 확인해야 합니다.

## 2순위: 관리자 변경 전후 비교 UI 강화

실제 적용 전에 “바뀌는 필드만” 더 크게 보여주고, 위험도가 높은 변경은 상단에 한 번 더 강조할 수 있습니다.

## 3순위: 정식 인증/권한 설계 준비

현재 `local-admin-dev-key`는 개발용 안전장치입니다.
실서비스 구조로 가려면 로그인/권한/관리자 계정 설계가 필요합니다.

# Next Steps

## 1순위 추천: 관리자 변경 전후 비교 UI 강화

v134에서 preset select와 allow-list 확장을 적용했으므로, 다음 단계에서는 실제 적용 직전에 “바뀌는 필드만” 더 크게 보여주는 UI를 강화하는 것이 좋습니다.

추천 작업:

- 적용 직전 diff summary 상단 고정
- high risk 변경이 있으면 한 번 더 눈에 띄게 표시
- item_type / equip_slot / slot_key 변경 시 별도 경고 문구 표시
- 적용 후 “게임 새로고침 필요” 안내를 더 명확히 표시

DB reset/seed는 필요 없을 가능성이 높습니다.

## 2순위: 관리자 allow-list 추가 확장 후보 검토

아래 필드는 아직 조심해서 검토하는 편이 좋습니다.

- `dropTables.owner_type`
- `skillLevels.level`
- `enhancementLevels.from_level`
- `itemTemplates.enhance_group_code`

관계 필드(`*_id`, `*_code`)와 JSON 필드는 아직 잠금 유지가 안전합니다.

## 3순위: 정식 인증/권한 설계 준비

현재 `local-admin-dev-key`는 개발용 안전장치입니다.
실서비스 구조로 가려면 로그인/권한/관리자 계정 설계가 필요합니다.

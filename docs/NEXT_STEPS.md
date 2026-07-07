# Next Steps

## 1순위 추천: 조합 관계 필드 안전 편집 준비

v141에서 단일 대상 관계 select와 백엔드 존재 검증을 붙였으므로, 다음에는 조합 관계 필드를 열기 전에 더 강한 검증이 필요합니다.

우선 검토 후보:

- `dropTableItems.drop_table_code`
- `skillLevels.skill_code`
- `skillLevels.level`
- `enhancementLevels.group_code`
- `enhancementLevels.from_level`
- `characterSkills.character_code`
- `characterSkills.skill_code`

주의점:

- `skillLevels.skill_code + level`은 유니크 조합입니다.
- `enhancementLevels.group_code + from_level`은 유니크 조합입니다.
- `characterSkills.character_code + skill_code`는 유니크 조합입니다.
- 그래서 둘 중 하나만 바꾸더라도 변경 후 조합이 이미 존재하는지 백엔드에서 검사해야 합니다.

DB reset/seed는 필요 없을 가능성이 높습니다.

## 2순위: 관계 변경 영향 시뮬레이션 강화

현재는 relation select와 존재 검증까지 들어갔습니다. 다음에는 변경하려는 연결값이 실제로 어떤 대상에 영향을 주는지 더 구체적으로 보여줄 수 있습니다.

예시:

- 아이템의 강화 그룹 변경 전/후 강화 단계 수 표시
- 드랍 아이템 변경 전/후 아이템 이름과 장착 슬롯 표시
- 드랍 테이블 owner_type 변경 전/후 연결 대상 표시

## 3순위: 정식 인증/권한 설계 준비

현재 `local-admin-dev-key`는 개발용 안전장치입니다. 실서비스 구조로 가려면 로그인, 권한, 관리자 계정 설계를 준비해야 합니다.

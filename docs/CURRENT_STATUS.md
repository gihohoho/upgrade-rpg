# Current Status

현재 기준: **v144 admin combo relation guard**

v144에서는 v141의 relation select를 확장해서 조합 관계 필드를 안전하게 편집할 수 있게 했습니다. `skill_code + level`, `group_code + from_level`, `character_code + skill_code` 조합은 중복될 경우 백엔드 preview/apply 단계에서 차단됩니다.

DB schema, seed 데이터, localStorage 저장 구조는 변경하지 않았습니다.

## 정상 확인된 흐름

- 백엔드 master-data 연동 정상.
- master-data 실패 시 static JS fallback 정상.
- localStorage 저장 유지 정상.
- 수동 저장 시 DB save snapshot dual write 정상.
- save preview / restore / backup rollback 정상.
- save restore reload lock 정상.
- 관리자 페이지 열기 정상.
- 관리자 overview, save snapshot 필터, 마스터 데이터 목록/상세/관계 조회 정상.
- 관리자 allow-list 필드 실제 적용 정상.
- 보스 hp 수정 후 게임 새로고침 시 인게임 반영 확인됨.
- 변경 이력 rollback 정상.
- 관리자 write dev key guard 정상.
- 관리자 edit stale guard 정상.
- 관리자 편집 초안 입력 UI 타입 개선 정상.
  - boolean: true/false select
  - preset enum: preset select
  - relation field: relation select
  - number: number input
  - description/admin_note: textarea
  - 읽기 전용/잠금 필드 카드 표시
  - 필드 위험도 배지 표시
- 실제 적용 가능 필드 정상.
  - itemTemplates.item_type
  - itemTemplates.equip_slot
  - itemTemplates.enhance_group_code
  - skills.slot_key
  - dropTables.owner_type
  - dropTableItems.drop_table_code
  - dropTableItems.item_template_code
  - skillLevels.skill_code
  - skillLevels.level
  - enhancementLevels.group_code
  - enhancementLevels.from_level
  - characterSkills.character_code
  - characterSkills.skill_code
- 관계 필드 안전 검증 정상.
  - itemTemplates.enhance_group_code는 enhancementGroups.code 존재 여부 검사
  - dropTableItems.item_template_code는 itemTemplates.code 존재 여부 검사
  - dropTableItems.drop_table_code는 dropTables.code 존재 여부 검사
  - dropTables.owner_type은 현재 owner_code가 해당 타입의 보스/필드 코드에 존재하는지 검사
  - skillLevels는 skill_code + level 중복 조합 검사
  - enhancementLevels는 group_code + from_level 중복 조합 검사
  - characterSkills는 character_code + skill_code 중복 조합 검사
- 마스터 데이터 카탈로그 페이지네이션 정상.
  - 기본 표시 개수 20개
  - 기본 정렬 ID순
  - equip_slot 숫자 값 6~14를 인게임 특수 장비 슬롯 이름으로 표시
- 관리자 적용 직전 비교 UI 정상.
  - 변경된 필드만 before/after로 표시
  - risk high / medium / low 순서로 표시
  - high risk 변경 시 `HIGH RISK EDIT` 추가 확인 필요
  - 초안 검증 결과에도 위험도 컬럼 표시
  - 카탈로그 현재 선택 행 강조 표시
- itemTemplates.stackable=true 신규 획득 아이템 겹치기 반영 정상.
- 겹친 장비 강화 시 빈 칸 없으면 강화 차단 정상.

## 현재 주의점

- 이미 열려 있는 게임 화면은 master-data를 자동 실시간 반영하지 않습니다. 새로고침이 필요합니다.
- 기존 세이브에 이미 따로 들어간 stackable 아이템은 자동 병합하지 않습니다.
- skills.slot_key는 스킬 버튼 배치에 직접 영향을 줄 수 있으므로 변경 후 게임 화면에서 버튼 중복/배치를 확인해야 합니다.
- itemTemplates.item_type / equip_slot은 아이템 분류와 장착 위치에 영향을 줄 수 있으므로 신규 획득/장착/툴팁 확인이 필요합니다.
- itemTemplates.enhance_group_code는 강화 규칙 연결에 직접 영향을 줍니다.
- dropTableItems.item_template_code는 실제 드랍 아이템을 바꿉니다.
- dropTableItems.drop_table_code는 드랍 아이템이 어느 드랍 묶음에 속하는지 바꿉니다.
- dropTables.owner_type은 owner_code의 의미를 보스/필드 중 어디로 볼지 바꿉니다.
- skillLevels.skill_code/level, enhancementLevels.group_code/from_level, characterSkills.character_code/skill_code는 조합 관계를 바꾸므로 적용 후 연결 관계를 확인해야 합니다.
- high risk 변경은 기존 `APPLY MASTER DATA EDIT` 외에 `HIGH RISK EDIT` 추가 확인 문구도 필요합니다.
- 관리자 dev key는 정식 인증이 아니라 로컬 개발용 잠금장치입니다.
- `.env`, `.gitignore`는 현재 로컬에 있으므로 변경되지 않았다면 zip에 없어도 됩니다.
- v144는 관리자 UI/API 안전장치 중심 변경이라 **DB reset/seed가 필요 없습니다.**

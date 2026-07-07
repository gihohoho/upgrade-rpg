# Current Status

현재 기준: **v134 admin safe selects**

v134에서는 관리자 마스터 데이터 편집 초안에서 enum 성격 필드를 preset select로 고르게 하고, 일부 안전한 allow-list 필드를 추가로 열었습니다.
DB schema, seed 데이터, localStorage 저장 구조는 변경하지 않았습니다.

## 정상 확인된 흐름

- 백엔드 master-data 연동 정상.
- master-data 실패 시 static JS fallback 정상.
- localStorage 저장 유지 정상.
- 수동 저장 시 DB save snapshot dual write 정상.
- save preview / restore / backup rollback 정상.
- save restore reload lock 정상.
- 관리자 페이지 열기 정상.
- 관리자 마스터 데이터 목록/상세/관계 조회 정상.
- 관리자 allow-list 필드 실제 적용 정상.
- 보스 hp 수정 후 게임 새로고침 시 인게임 반영 확인됨.
- 변경 이력 rollback 정상.
- 관리자 write dev key guard 정상.
- 관리자 edit stale guard 정상.
- 관리자 편집 초안 입력 UI 타입 개선 정상.
  - boolean: true/false select
  - preset enum: preset select
  - number: number input
  - description/admin_note: textarea
  - 읽기 전용/잠금 필드 카드 표시
  - 필드 위험도 배지 표시
- v134에서 추가로 실제 적용까지 연 필드 정상.
  - itemTemplates.item_type
  - itemTemplates.equip_slot
  - skills.slot_key
- itemTemplates.stackable=true 신규 획득 아이템 겹치기 반영 정상.
- 겹친 장비 강화 시 빈 칸 없으면 강화 차단 정상.

## 현재 주의점

- 이미 열려 있는 게임 화면은 master-data를 자동 실시간 반영하지 않습니다. 새로고침이 필요합니다.
- 기존 세이브에 이미 따로 들어간 stackable 아이템은 자동 병합하지 않습니다.
- skills.slot_key는 스킬 버튼 배치에 직접 영향을 줄 수 있으므로 변경 후 게임 화면에서 버튼 중복/배치를 확인해야 합니다.
- itemTemplates.item_type / equip_slot은 아이템 분류와 장착 위치에 영향을 줄 수 있으므로 신규 획득/장착/툴팁 확인이 필요합니다.
- 관리자 dev key는 정식 인증이 아니라 로컬 개발용 잠금장치입니다.
- `.env`, `.gitignore`는 현재 로컬에 있으므로 변경되지 않았다면 zip에 없어도 됩니다.
- v134는 allow-list + 관리자 UI 중심 변경이라 **DB reset/seed가 필요 없습니다.**

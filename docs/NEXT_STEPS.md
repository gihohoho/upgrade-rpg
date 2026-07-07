# Next Steps

현재 기준: **v144 admin combo relation guard**

v144에서 조합 관계 필드 안전 편집과 백엔드 중복 조합 검증을 완료했습니다.

## 다음 추천 단계

### v145 관리자 dropTables owner_code 안전 편집

`dropTables.owner_type`은 이미 열려 있지만 `owner_code`는 아직 잠겨 있습니다. 다음에는 owner_type에 따라 실제 대상 목록을 바꾸는 select를 붙이는 것이 좋습니다.

- owner_type이 `boss`이면 bosses 목록에서 owner_code 선택
- owner_type이 `field`이면 fieldZones 목록에서 owner_code 선택
- owner_type + owner_code 조합이 실제 대상에 존재하는지 preview/apply 공통 검증
- owner_type을 바꿨을 때 owner_code 후보 목록도 함께 바뀌는 UI 보강

이 단계도 DB reset/seed 없이 진행 가능합니다.

## 이후 후보

- relation select 검색/필터 UI
- 변경 preview 표에 relation target label 표시 강화
- 관리자 마스터 데이터 신규 생성 기능 준비
- JSON 편집기 미리보기 전용 UI 준비

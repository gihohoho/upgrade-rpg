# Next Steps

현재 기준: **v147 admin owner code relation tools**

v147에서 `dropTables.owner_code` 안전 편집, owner_type 연동 select, relation target label 표시를 완료했습니다.

## 다음 추천 단계

### v148 relation select 검색/필터 UI

관계 대상 목록이 길어질수록 select에서 원하는 대상을 찾기 어려워질 수 있습니다. 다음에는 relation select 주변에 작은 검색 입력 또는 빠른 필터를 붙이는 것이 좋습니다.

- relation select 후보를 코드/이름으로 필터링
- 현재 선택값은 필터와 상관없이 항상 유지
- 검색은 프론트 UI 안에서만 동작하고 DB를 수정하지 않음
- preview/apply 백엔드 검증은 기존처럼 유지

이 단계도 DB reset/seed 없이 진행 가능합니다.

## 이후 후보

- 변경 preview 표에 relation before label 표시 강화
- 관리자 마스터 데이터 신규 생성 기능 준비
- JSON 편집기 미리보기 전용 UI 준비
- 관리자 변경 이력에서 relation label 표시 강화

# Admin Owner Code Relation Tools

기준 버전: **v147 admin owner code relation tools**

## 목적

`dropTables.owner_code`는 어느 보스/필드가 해당 드랍 테이블을 쓰는지 결정하는 연결 필드입니다. 직접 텍스트 입력으로 열면 오타나 타입 불일치로 드랍 연결이 깨질 수 있으므로, 실제 존재하는 대상 목록 기반 select와 백엔드 검증을 붙였습니다.

## 완료 내용

### v145 - dropTables.owner_code 안전 편집

- `dropTables.owner_code`를 관리자 allow-list에 추가했습니다.
- `owner_code`는 text input이 아니라 relation select로만 편집합니다.
- `owner_type=boss`이면 bosses 목록에서만 선택합니다.
- `owner_type=field`이면 fieldZones 목록에서만 선택합니다.
- preview/apply 공통으로 `owner_type + owner_code`가 실제 대상에 존재하는지 검사합니다.
- 존재하지 않는 조합은 `owner_code_not_found_for_owner_type`으로 차단합니다.

### v146 - owner_type 연동 select

- 관리자 편집 초안에서 `owner_type`을 바꾸면 `owner_code` 후보 목록도 자동으로 바뀝니다.
- boss → field로 바꾸면 owner_code select가 fieldZones 후보로 전환됩니다.
- field → boss로 바꾸면 owner_code select가 bosses 후보로 전환됩니다.
- 기존 owner_code가 새 타입 후보 목록에 없으면 첫 번째 안전 후보로 자동 선택됩니다.

### v147 - relation label 표시 강화

- 백엔드 preview/apply 응답의 relation 변경 정보에 대상 라벨을 붙입니다.
- 관리자 초안 검증 결과의 적용/초안 값에 relation target label을 같이 표시합니다.
- 예: `boss_001 · 슬라임 왕`, `field_001 · 초보자의 숲`처럼 볼 수 있습니다.

## 유지되는 안전장치

- 관리자 쓰기 dev key 필요.
- 실제 적용 확인 문구 `APPLY MASTER DATA EDIT` 유지.
- high risk 변경 시 추가 확인 문구 `HIGH RISK EDIT` 유지.
- stale guard 유지.
- change log / rollback 유지.
- post-edit master-data API verify 유지.

## DB reset / seed

필요 없습니다.

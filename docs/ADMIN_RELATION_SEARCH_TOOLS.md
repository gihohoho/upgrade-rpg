# Admin Relation Search Tools

기준 버전: **v153 admin relation preview tools**

## 목적

관계 필드 select 후보가 길어질 때 관리자에서 원하는 대상을 코드/이름으로 빠르게 찾을 수 있게 했습니다.

## 변경 내용

- relation select 입력칸 위에 후보 검색 input을 추가했습니다.
- 검색어는 코드와 이름 label을 대상으로 프론트에서만 필터링합니다.
- 검색 결과가 현재 선택값을 숨기더라도 현재 선택값은 유지됩니다.
- owner_type 변경 시 owner_code 후보 목록과 검색 상태가 함께 안전하게 갱신됩니다.
- 마스터 데이터 카탈로그 검색/페이지 입력에서 Enter를 누르면 바로 조회됩니다.
- 카탈로그 domain, 표시 개수, 활성 상태, 정렬을 바꾸면 페이지가 1로 돌아갑니다.

## 안전성

- 검색/필터는 관리자 UI 안에서만 동작합니다.
- DB 값은 초안 검증/실제 적용 버튼을 누르기 전까지 바뀌지 않습니다.
- 기존 preview/apply 백엔드 관계 검증은 그대로 유지됩니다.
- dev key, 확인 문구, high risk 추가 확인, stale guard, change log/rollback을 유지합니다.

## DB reset / seed

필요 없습니다.

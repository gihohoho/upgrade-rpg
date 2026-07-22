# Admin Relation Preview Tools

기준 버전: **v153 admin relation preview tools**

## 목적

관리자 편집 초안과 백엔드 preview 결과에서 relation 필드 변경을 코드만 보지 않고 대상 이름까지 함께 확인할 수 있게 합니다.

## 완료 내용

- 적용 직전 before/after 표에서 relation 값에 대상 이름 label을 함께 표시합니다.
- 초안 검증 결과의 적용/초안 값에서도 relation label을 함께 표시합니다.
- relation 변경 행에는 `relation` 배지를 표시합니다.
- 변경 요약 배너에 relation 변경 개수를 표시합니다.
- relation 대상이 열 수 있는 도메인이면 `대상 열기` 버튼을 표시합니다.
- `대상 열기`는 code로 카탈로그를 조회한 뒤 해당 상세를 엽니다.

## 안전성

- DB 값은 이 기능만으로 바뀌지 않습니다.
- 기존 preview/apply 백엔드 검증을 그대로 유지합니다.
- 기존 dev key guard, 확인 문구, high risk 추가 확인, stale guard를 유지합니다.
- DB reset / seed는 필요 없습니다.

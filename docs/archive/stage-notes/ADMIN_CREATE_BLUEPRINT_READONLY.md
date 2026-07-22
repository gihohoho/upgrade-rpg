# Admin Create Blueprint Read-only

## 목적

v159는 관리자 신규 row 생성 기능을 바로 열기 전에, 도메인별 생성 설계를 read-only로 확인하는 단계입니다.

실제 DB insert API는 아직 만들지 않았고, 관리자 화면은 필수 필드/기본값/relation 후보/중복 검사 힌트만 보여줍니다.

## 완료 내용

- `GET /api/v1/admin/master-data/create-blueprint` 추가.
- 관리자 페이지에 `신규 row 생성 준비` 섹션 추가.
- 도메인별 필수 필드, unique 필드, combo guard 표시.
- 생성 기본값 draft JSON 미리보기 표시.
- relation 필드 후보 목록 개수 표시.
- JSON 필드는 생성 적용 전까지 잠금으로 표시.
- 실제 생성 적용은 `insert API locked`로 계속 차단.

## 안전 원칙

- DB reset / seed 필요 없음.
- schema 변경 없음.
- 기존 edit apply / rollback / change log는 그대로 유지.
- localStorage 저장 구조는 변경 없음.
- 신규 row 생성은 아직 실제 적용되지 않음.

## 다음 단계 후보

- 생성 draft 입력 UI를 read-only에서 초안 입력 단계로 확장.
- 생성 preview API 추가.
- unique code 중복 검사와 combo guard를 생성 preview에서 검증.
- 실제 insert apply는 dev key, 확인 문구, change log를 붙인 뒤 마지막에 열기.

# Admin Create Draft Preview

## 목적

v162는 v159의 신규 row 생성 blueprint를 바탕으로 관리자 페이지에 생성 초안 입력 UI와 preview-only 백엔드 검증을 추가한 단계입니다.

실제 DB insert는 아직 열지 않았습니다.

## 추가된 기능

- blueprint 기반 생성 초안 입력 UI
- boolean 필드는 true/false select
- number 필드는 number input
- description/admin_note는 textarea
- preset 필드는 select
- relation 필드는 실제 후보 목록 기반 select
- relation 후보 검색/필터
- owner_type 변경 시 owner_code 후보 목록 자동 전환
- 생성 초안 preview-only 검증 API
- code unique 중복 검사
- relation 대상 존재 검사
- combo guard 중복 검사

## 추가된 API

```txt
POST /api/v1/admin/master-data/create-preview
```

이 API는 초안을 검증만 합니다.

- DB insert 없음
- commit 없음
- change log 없음
- rollback 없음
- raw JSON 반환 없음
- asset 반환 없음

## 아직 잠근 기능

- 실제 신규 row 생성 apply
- 생성 확인 문구
- 생성 change log
- 생성 rollback
- JSON 필드 직접 편집

## DB reset / seed

필요 없습니다.

schema 변경도 없습니다.

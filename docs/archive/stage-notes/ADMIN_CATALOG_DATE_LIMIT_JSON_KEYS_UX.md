# Admin Catalog Date/Limit/JSON Keys UX

## 목적

`마스터 데이터 카탈로그` 목록을 더 짧고 읽기 쉽게 만들기 위한 UI 정리입니다.

## 변경 사항

- `수정`/`updated_at` 계열 카탈로그 셀은 화면에 `YYYY-MM-DD` 일자만 표시합니다.
- 값 옆 `?` tooltip에는 원본 timestamp의 초 단위 상세 시각을 유지합니다.
- `표시 개수` 선택지는 `10`, `30`, `50`, `100` 네 개로 제한했습니다.
- `표시 개수` 기본값은 `10`입니다.
- `JSON 키` 셀은 앞 3개 키만 chip으로 표시하고, 나머지는 `외 N개`로 접습니다.
- JSON 키 전체 목록은 셀 옆 `?` tooltip에서 확인합니다.

## 변경하지 않은 것

- DB
- env
- seed
- 인증
- 기존 route
- API 응답 body
- Write Guard
- 실제 write 로직

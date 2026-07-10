# Backend Admin Schema Field Constraint Contract — v238

## 목적

Admin request schema의 이름과 필드가 남아 있어도 길이 제한, 기본값, required 여부, alias 입력 방식이 바뀌면 API 동작은 달라질 수 있습니다. 이 계약은 그런 조용한 drift를 smoke 단계에서 차단합니다.

## 검증 범위

- 11개 OpenAPI request schema의 required 목록
- `domain`: 최소 1자, 최대 80자
- `reason`: 최대 500자
- `confirmText`: 최대 80자
- 편집 `id`: 1 이상
- preview/apply `dryRun` 기본값
- `populate_by_name`, `str_strip_whitespace`, alias/name validation
- 공백 제거와 잘못된 값 거절을 실제 Pydantic validation으로 확인

## 변경하지 않은 범위

- route path
- API 응답 body
- DB schema/data
- env
- 실제 쓰기 service 로직

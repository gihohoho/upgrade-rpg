# Admin Catalog Compact Help UX

## 목적

기존 관리자 카탈로그는 값 아래에 설명문까지 붙어 목록이 길고 난잡해 보였다. v259에서는 목록은 핵심값만 보여주고, 설명은 `?` 도움말로 분리한다.

## 변경 사항

- `마스터 데이터 카탈로그` 필터 영역과 결과 표 영역을 하나의 섹션으로 합쳤다.
- 별도 `section-master-catalog-table` 섹션을 제거하고, `section-master-catalog` 안에 필터/메타/페이지네이션/표를 모두 배치했다.
- 카탈로그 표와 relation 표는 `formatCatalogCellValue()`를 사용한다.
- `formatCatalogCellValue()`는 긴 설명문 대신 `normal · 일반 장비` 같은 compact label만 시각적으로 표시한다.
- 자세한 설명은 열 제목 `?`와 값 tooltip에 남긴다.

## 안전 기준

이 작업은 프론트엔드 표시 구조만 바꾼다.

- DB 변경 없음
- env 변경 없음
- seed 변경 없음
- API route 변경 없음
- API 응답 body 변경 없음
- 인증 변경 없음
- Write Guard 변경 없음
- 실제 write 로직 변경 없음

## 검증

추가 Smoke:

```bash
node tools/smoke/frontend/smoke_admin_catalog_help_compact_ux.js
```

전체 Smoke에도 포함했다.

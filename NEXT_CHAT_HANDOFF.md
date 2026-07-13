# NEXT CHAT HANDOFF — Upgrade RPG v279

## 최신 ZIP

- `rpg_v279_vue_admin_catalog_controls_detail.zip`

## 현재 기준

- 최신 작업: `v279.vue-admin-readonly-detail-panel`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 사용자 응답 규칙

- 한국어로 쉽고 자세하게 설명합니다.
- 모든 명령 앞에 실행 위치를 적습니다.
- npm/Vue 명령은 `.venv` 불필요 여부를 적습니다.
- Python/FastAPI 명령은 `.venv` 활성 여부를 적습니다.
- 설치 파일/라이브러리/프레임워크와 사용자 확인 항목을 빠짐없이 알립니다.
- git 명령은 프로젝트 루트에서 한 줄로 제공합니다.

## v278~v279 완료

v278:

- 검색어 query
- 활성/비활성 enabled
- 정렬 sort
- 이전/다음 page
- 도메인 변경 시 필터/page 초기화
- stale 요청 취소

v279:

- `AdminMasterDetailPanel.vue`
- `GET /admin/master-data/detail?domain=...&id=...`
- scalar fields
- relation hints
- sanitized JSON preview
- asset 숨김 상태
- `/requirements`를 `준비 완료`로 의미 있게 표시

## 현재 Vue `/admin` GET

- `/health`
- `/admin/requirements`
- `/admin/master-data/domains`
- `/admin/master-data/catalog`
- `/admin/master-data/detail`

## 변경 금지/보류

- DB/env/seed/인증
- route path/API response body
- Write Guard/실제 write
- Preview/Apply 요청 body
- 기존 smoke/contract 의미
- 게임 콘텐츠
- relations GET

## 사용자 확인

`http://127.0.0.1:5173/admin`에서:

1. requirements가 `준비 완료`인지
2. 검색/초기화가 동작하는지
3. 활성 필터가 지원 도메인에서만 활성인지
4. 이전/다음 페이지가 동작하는지
5. 상세 보기와 선택 해제가 동작하는지
6. JSON 미리보기가 표시되는지
7. 콘솔 오류가 없는지

## 다음 추천 작업

`v280 Vue admin read-only relations panel`

실제 relations 응답 구조를 먼저 확인하고 GET 목록만 표시합니다. Preview/Apply/write는 계속 보류합니다.

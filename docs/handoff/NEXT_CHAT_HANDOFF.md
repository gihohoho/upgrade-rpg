# NEXT CHAT HANDOFF — Upgrade RPG v281

## 최신 ZIP

- `rpg_v281_vue_admin_readonly_relations_navigation.zip`

## 현재 기준

- 최신 작업: `v281.vue-admin-related-detail-navigation`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 사용자 응답 규칙

- 한국어로 쉽고 자세하게 설명
- 모든 명령 앞에 실행 위치 표시
- npm/Vue 명령은 `.venv` 불필요 여부 표시
- Python/FastAPI 명령은 `.venv` 활성 여부 표시
- 설치 파일/라이브러리/프레임워크와 사용자 확인 항목 안내
- git 명령은 프로젝트 루트에서 한 줄

## v280~v281 완료

- `AdminMasterRelationsPanel.vue`
- `GET /admin/master-data/relations?domain=...&id=...&limit=20`
- relation groups/columns/rows/count/shown/limited 표시
- loading/error/empty/success
- stale 요청 취소
- 연관 row GET 상세 이동
- 로컬 `selectionHistory`와 `이전 상세로`
- 관계 편집 및 모든 mutation 미연결

## 현재 Vue `/admin` GET

- `/health`
- `/admin/requirements`
- `/admin/master-data/domains`
- `/admin/master-data/catalog`
- `/admin/master-data/detail`
- `/admin/master-data/relations`

## 변경 금지/보류

- DB/env/seed/인증
- route path/API response body
- Write Guard/실제 write
- Preview/Apply 요청 body
- 기존 smoke/contract 의미
- 게임 콘텐츠
- 관계 편집

## 다음 추천 작업

`v282 PostgreSQL/Alembic 도입 준비 상세 계획`

현재 model/session/config/alembic 구조를 분석하고 실제 DB/env를 변경하지 않은 채 전환 순서, 위험 지점, rollback, 사전 검증을 문서/report/smoke로 고정합니다.

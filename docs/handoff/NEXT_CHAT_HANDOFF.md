# NEXT CHAT HANDOFF — Upgrade RPG v277

## 최신 ZIP

- `rpg_v277_vue_admin_readonly_catalog_mini_panel.zip`

## 현재 기준

- 최신 작업: `v277.vue-admin-readonly-catalog-mini-panel`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 사용자 응답 규칙

- 사용자는 코딩을 거의 모릅니다.
- 한국어로 쉽고 자세하게 설명합니다.
- 모든 명령 앞에 실행 위치를 적습니다.
- npm/Vue 명령은 `.venv` 불필요 여부를 반드시 적습니다.
- Python/FastAPI 명령은 `.venv` 활성 여부를 반드시 적습니다.
- 설치 파일/라이브러리/프레임워크와 사용자가 확인할 항목을 빠짐없이 알립니다.
- git 명령은 프로젝트 루트에서 한 줄로 제공합니다.

## v276~v277 완료

추가:

- `frontend/vue-app/src/components/AdminMasterDomainPanel.vue`
- `frontend/vue-app/src/components/AdminMasterCatalogMiniPanel.vue`
- `docs/current/VUE_ADMIN_READONLY_CATALOG.md`
- `tools/smoke/frontend/smoke_vue_admin_readonly_catalog_panel.py`

현재 Vue `/admin` 자동 GET:

- `/health`
- `/admin/requirements`
- `/admin/master-data/domains`
- `/admin/master-data/catalog?domain=...&limit=20&page=1&sort=id_asc`

도메인 목록은 `response.payload.domains`를 사용합니다.
카탈로그는 `response.payload.columns`, `response.payload.rows`를 사용합니다.

## 변경 금지/보류

- DB/env/seed/인증
- route path/API response body
- Write Guard/실제 write 로직
- Preview/Apply 요청 body
- 기존 smoke/contract 의미
- 게임 콘텐츠

아직 Vue에 연결하지 않음:

- detail/relations
- 모든 Preview/Apply/write
- 검색/필터/페이지네이션

## 사용자 확인

FastAPI와 Vue를 실행한 뒤:

```txt
http://127.0.0.1:5173/admin
```

확인:

1. 상태 패널 성공
2. 도메인 카드 표시
3. 기본 도메인 선택
4. 첫 20개 표 표시
5. 도메인 변경 시 표 변경
6. 콘솔 오류 없음

## 다음 추천 작업

`v278 Vue admin catalog query controls`

- 검색어
- 활성/비활성 필터
- 이전/다음 페이지
- GET query만 사용
- detail/relations/Preview/Apply/write는 계속 보류

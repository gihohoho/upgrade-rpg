# Current Status — v279

## 현재 기준

- 최신 작업: `v279.vue-admin-readonly-detail-panel`
- 기준 ZIP: `rpg_v279_vue_admin_catalog_controls_detail.zip`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## v276~v279 완료

Vue 관리자 shell의 read-only 이식을 네 단계 진행했습니다.

- v276: 도메인 목록
- v277: 선택 도메인의 첫 카탈로그
- v278: 검색·활성 상태·정렬·페이지네이션
- v279: 선택 row의 안전한 상세 조회

추가/변경된 핵심 Vue 파일:

- `AdminMasterDomainPanel.vue`
- `AdminMasterCatalogMiniPanel.vue`
- `AdminMasterDetailPanel.vue`
- `ReadOnlyApiStatusPanel.vue`
- `AdminShell.vue`

## 현재 Vue `/admin` 연결 범위

실제 호출:

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`
- `GET /api/v1/admin/master-data/domains`
- `GET /api/v1/admin/master-data/catalog`
- `GET /api/v1/admin/master-data/detail`

아직 연결하지 않음:

- `GET /api/v1/admin/master-data/relations`
- 모든 Preview/Apply/write
- 인증/token/interceptor

## 이번 상태의 안전 경계

- 목록/상세 모두 GET만 사용
- 검색어 최대 80자
- page size 20 고정
- 도메인/필터/page 변경 시 stale 요청 취소
- 목록 재조회 시 이전 상세 선택 해제
- JSON은 backend의 sanitized preview만 표시
- asset 원본을 요청하거나 표시하지 않음

## 변경하지 않은 것

- DB 구조
- `.env`
- seed
- 인증
- 기존 route path
- 기존 API 응답 body
- Write Guard
- 실제 write 로직
- 관리자 Preview/Apply 요청 body
- 기존 smoke/contract 의미
- 게임 콘텐츠

## 설치

v278~v279에서 새 라이브러리나 프레임워크는 추가하지 않았습니다.

`frontend/vue-app/node_modules`가 없는 경우에만:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

## 실행

FastAPI 가상환경:

실행 위치: 프로젝트 루트  
`.venv` 상태: 꺼져 있다면 켜야 함

```bash
.venv\Scripts\activate
```

FastAPI 서버:

실행 위치: `backend` 폴더  
`.venv` 상태: 켜진 상태

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Vue 서버:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음

```bash
npm run dev
```

## 사용자 확인

`http://127.0.0.1:5173/admin`에서 검색, 활성 필터, 페이지 이동, 상세 보기, 상세 선택 해제, 콘솔 오류 여부를 확인합니다.

## 다음 추천 단계

`v280 Vue admin read-only relations panel`

관계 GET 응답만 별도 패널로 연결하고 Preview/Apply/write는 계속 보류합니다.

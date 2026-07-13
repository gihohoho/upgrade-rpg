# Current Status — v277

## 현재 기준

- 최신 작업: `v277.vue-admin-readonly-catalog-mini-panel`
- 기준 ZIP: `rpg_v277_vue_admin_readonly_catalog_mini_panel.zip`
- 직전 기준: `v275.backend-route-map-report`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## v276~v277 완료

Vue 관리자 shell의 read-only 이식을 두 단계 진행했습니다.

### v276 — 도메인 목록

- `AdminMasterDomainPanel.vue` 추가
- `GET /api/v1/admin/master-data/domains` 자동 호출
- `response.payload.domains` 기준 표시
- loading/error/empty/success 상태
- 기본 도메인 선택
- 전체/활성/비활성 개수 표시

### v277 — 첫 카탈로그 페이지

- `AdminMasterCatalogMiniPanel.vue` 추가
- 선택된 도메인의 `GET /api/v1/admin/master-data/catalog` 자동 호출
- 고정 query: `limit=20`, `page=1`, `sort=id_asc`
- `response.payload.columns`, `response.payload.rows` 일반 표 렌더링
- 도메인 변경 시 이전 요청 취소
- loading/error/empty/success 상태

## 현재 Vue `/admin` 연결 범위

자동 호출:

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`
- `GET /api/v1/admin/master-data/domains`
- `GET /api/v1/admin/master-data/catalog`

아직 연결하지 않음:

- 검색/필터/페이지네이션
- detail/relations
- Preview/Apply/write
- 인증/token/interceptor

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

## 실제 화면 기준

| 화면 | 현재 기준 |
|---|---|
| 게임 운영/검증 화면 | 루트 `index.html` |
| 관리자 운영/검증 화면 | 루트 `admin.html` |
| Vue 이식 준비 화면 | `frontend/vue-app/` |

Vue 경로:

- `http://127.0.0.1:5173/game`
- `http://127.0.0.1:5173/admin`

## 설치/실행

v276~v277에서 새 라이브러리나 프레임워크는 추가하지 않았습니다.

Vue 의존성을 아직 설치하지 않은 경우에만:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

FastAPI 실행:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜야 함

```bash
.venv\Scripts\activate
```

실행 위치: `backend` 폴더  
`.venv` 상태: 켜진 상태

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Vue 실행:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

## 사용자가 확인할 것

`http://127.0.0.1:5173/admin`에서 다음을 확인합니다.

1. API 상태 2개가 성공인지
2. 도메인 카드가 표시되는지
3. 기본 도메인이 선택되는지
4. 아래 표에 첫 20개 row가 표시되는지
5. 다른 도메인을 선택하면 표가 바뀌는지
6. 브라우저 콘솔 오류가 없는지

## 다음 추천 단계

`v278 Vue admin catalog query controls`

- 검색
- 활성/비활성 필터
- 페이지네이션
- GET query만 사용
- detail/relations와 Preview/Apply/write는 계속 보류

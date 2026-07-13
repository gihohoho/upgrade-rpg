# Current Status — v275

## 현재 기준

- 최신 작업: `v275.backend-route-map-report`
- 기준 ZIP: `rpg_v275_backend_route_map_report.zip`
- 직전 기준: `v274.backend-structure-plan`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## v275 완료

v275에서는 FastAPI 실제 route 목록을 정적으로 분석해서 자동 보고서로 만들고, Vue에서 다음에 연결 가능한 read-only `GET` route 후보와 아직 보류해야 하는 route를 분리했습니다.

추가/변경한 것:

- `tools/report_backend_route_map.py`
  - `app.main`을 import하지 않고 route 파일의 `@router.get/post(...)` decorator를 분석합니다.
  - `docs/current/BACKEND_ROUTE_MAP.md`를 생성/검사합니다.
  - 단순 문서 생성이 `asyncpg` 같은 로컬 DB 의존성 설치 상태에 막히지 않도록 설계했습니다.
- `docs/current/BACKEND_ROUTE_MAP.md`
  - 전체 route 27개를 정리했습니다.
  - GET 15개, POST 12개를 분류했습니다.
  - Vue 자동 smoke 화면에 이미 쓰는 route와 다음 read-only 후보를 분리했습니다.
  - Preview/Apply/write route는 보류 목록으로 고정했습니다.
- `tools/smoke/backend/smoke_backend_route_map_report.py`
  - route map 보고서 최신 여부와 핵심 보호 문구를 검사합니다.
  - Vue read-only wrapper가 상세/관계 조회에서 `rowId`를 backend query `id`로 변환하는지도 검사합니다.
- `frontend/vue-app/src/api/adminReadOnlyApi.js`
  - `fetchMasterDetail({ rowId })` → 실제 query `id`로 변환
  - `fetchMasterRelations({ rowId })` → 실제 query `id`로 변환

## v275 route map 요약

| 구분 | 수 |
|---|---:|
| 전체 route | 27 |
| GET | 15 |
| POST | 12 |
| admin group | 21 |
| game group | 4 |
| health group | 2 |
| 중복 method/path | 0 |

현재 Vue 화면에서 실제 자동 호출 중인 route:

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`

다음 연결 후보:

- `GET /api/v1/admin/master-data/domains`
- 그다음에 catalog/detail/relations 등 단계적 연결

보류:

- 관리자 Preview 계열 POST
- 관리자 Apply/write 계열 POST
- `POST /api/v1/game/save`
- 인증/권한/Write Guard 설계가 필요한 route

## v275에서 변경하지 않은 것

- DB 구조
- env
- seed
- 인증
- 기존 route path
- 기존 API 응답 body
- 기존 write 로직
- Write Guard
- 관리자 Preview/Apply 요청 body
- 기존 smoke/contract 의미
- 게임 콘텐츠

## 현재 실제 실행 기준

| 화면 | 실제 기준 |
|---|---|
| 게임 | 루트 `index.html` |
| 관리자 | 루트 `admin.html` |
| Vue 준비 shell | `frontend/vue-app/` |

Vue route:

| 경로 | 의미 |
|---|---|
| `/game` | 게임 이식 준비 shell + 안전 GET 상태 확인 |
| `/admin` | 관리자 이식 준비 shell + 안전 GET 상태 확인 |

## 사용자가 설치/확인해야 할 것

v275에서 새 라이브러리/프레임워크는 추가하지 않았습니다.

Vue 앱을 처음 실행한다면 기존 Vue 의존성 설치가 필요합니다. 이미 `frontend/vue-app/node_modules`가 있다면 다시 설치하지 않아도 됩니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

FastAPI 서버 실행:

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

Vue 개발 서버 실행:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

확인 주소:

```txt
http://127.0.0.1:5173/game
http://127.0.0.1:5173/admin
```

## 다음 추천 단계

`v276 Vue admin read-only catalog mini panel`

추천 목표:

- Vue 관리자 shell에서 `GET /api/v1/admin/master-data/domains`만 먼저 호출합니다.
- 성공/오류/빈 데이터 상태를 작게 보여줍니다.
- catalog row 목록, detail, relations는 아직 자동 호출하지 않습니다.
- Preview/Apply/write route는 계속 보류합니다.
- DB/Alembic/인증/env/seed는 변경하지 않습니다.

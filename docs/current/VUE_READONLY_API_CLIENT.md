# Vue Read-only API Client — v275

## 한 줄 요약

v271에서는 Vue 앱 내부에 `GET` 전용 API client 구조를 만들었고, v272에서는 그 client를 이용해 Vue shell 화면에서 안전한 GET API를 실제로 작게 호출하도록 연결했습니다. v273에서는 Vue 개발 서버에서 FastAPI를 호출할 때 발생한 local CORS 오류를 수정했습니다. v275에서는 backend route map 자동 보고서를 기준으로 read-only 후보와 보류 route를 다시 정리했고, 상세/관계 조회 query 이름을 backend 기준에 맞췄습니다.

## v272에서 실제 화면에 연결한 API

| 화면 | 실제 호출 | 이유 |
|---|---|---|
| `/game` | `GET /health` | DB 없이 백엔드 서버 응답만 확인하기 위한 가장 안전한 API |
| `/admin` | `GET /health` | 백엔드 서버 응답 확인 |
| `/admin` | `GET /admin/requirements` | 관리자 read-only 화면의 기본 요구사항 확인 |

`/game/master-data`, `/game/load`, `/game/save-slots`는 아직 화면 자동 호출에 넣지 않았습니다. 이 경로들은 조회용이지만 DB 상태에 영향을 받을 수 있으므로, v272에서는 공통 `/health`만 먼저 연결했습니다.

## v275 route map 기준

자동 보고서:

```txt
docs/current/BACKEND_ROUTE_MAP.md
```

현재 Vue 자동 smoke 화면에 쓰는 route:

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`

다음 연결 후보:

- `GET /api/v1/admin/master-data/domains`

아직 보류:

- 관리자 Preview 계열 POST
- 관리자 Apply/write 계열 POST
- `POST /api/v1/game/save`
- 인증/권한/Write Guard가 필요한 route

## v275 query 이름 수정

백엔드의 관리자 상세/관계 조회 route는 row 식별자 query 이름으로 `id`를 사용합니다.

| Vue wrapper 입력 | 실제 backend query |
|---|---|
| `fetchMasterDetail({ domain, rowId })` | `?domain=...&id=...` |
| `fetchMasterRelations({ domain, rowId })` | `?domain=...&id=...` |

즉 Vue 코드에서는 사람이 이해하기 쉬운 `rowId`를 받되, 실제 요청은 `id`로 변환합니다.

## 추가/변경 위치

```txt
frontend/vue-app/src/api/adminReadOnlyApi.js
tools/report_backend_route_map.py
tools/smoke/backend/smoke_backend_route_map_report.py
docs/current/BACKEND_ROUTE_MAP.md
```

## 상태 표시 구조

`ReadOnlyApiStatusPanel.vue`는 아래 상태를 화면에 표시합니다.

| 상태 | 의미 |
|---|---|
| `idle` | 아직 확인 전 |
| `loading` | API 확인 중 |
| `success` | GET 응답 성공 |
| `error` | 서버 꺼짐, HTTP 오류 등. v273 이후 local CORS 기본값은 보강됨 |

실패해도 Vue shell 전체가 깨지지 않고 오류 문구만 표시됩니다.

## 기본 API 주소

기본값:

```txt
http://127.0.0.1:8000/api/v1
```

`.env` 파일은 만들거나 수정하지 않았습니다. v273에서는 오래된 로컬 `.env`에 `5173` origin이 빠져 있어도 local/debug 환경에서 기본 개발 origin을 자동 포함합니다. 나중에 실제 개발/배포 주소 분리가 필요해지면 `VITE_API_BASE_URL` 도입을 별도 단계에서 검토합니다.

## 현재 준비된 관리자 GET 경로

| 이름 | 경로 | v275 자동 화면 확인 여부 |
|---|---|---|
| requirements | `/admin/requirements` | 사용 |
| overview | `/admin/overview` | 아직 미사용 |
| saveSnapshots | `/admin/save-snapshots` | 아직 미사용 |
| masterDomains | `/admin/master-data/domains` | 다음 후보 |
| masterCatalog | `/admin/master-data/catalog` | 아직 미사용 |
| masterCreateBlueprint | `/admin/master-data/create-blueprint` | 아직 미사용 |
| masterDetail | `/admin/master-data/detail` | 아직 미사용 |
| masterRelations | `/admin/master-data/relations` | 아직 미사용 |
| changeLogs | `/admin/change-logs` | 아직 미사용 |
| changeLogDetail | `/admin/change-logs/{changeLogId}` | 아직 미사용 |

## 현재 준비된 게임 GET 경로

| 이름 | 경로 | v275 자동 화면 확인 여부 |
|---|---|---|
| masterData | `/game/master-data` | 아직 미사용 |
| load | `/game/load` | 아직 미사용 |
| saveSlots | `/game/save-slots` | 아직 미사용 |

## 일부러 제외한 것

Preview/Apply/write 계열은 아직 Vue 화면에 실제 연결하지 않습니다.

- `POST /game/save`
- 관리자 Preview 계열 POST
- 관리자 Apply 계열 POST
- Rollback Preview/Apply 계열 POST
- 생성 row 삭제/복원 Preview/Apply 계열 POST
- 인증 interceptor
- access token 처리
- Write Guard 처리
- `.env` 생성/수정
- DB 구조 변경
- 기존 API 응답 body 변경

## 사용자가 확인해야 할 것

### Vue 의존성 설치

처음 한 번만 필요합니다. 이미 `frontend/vue-app/node_modules`가 있다면 다시 하지 않아도 됩니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

### FastAPI 서버 실행

Vue 화면에서 API 상태가 `성공`으로 뜨려면 FastAPI 서버가 켜져 있어야 합니다. v273 CORS 수정은 서버를 재시작해야 반영됩니다.

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

### Vue 개발 서버 실행

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

## 검증 명령

Vue shell/API 구조 검증:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
bash tools/run_smoke_vue_shell.sh
```

Backend route map 검사:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python tools/report_backend_route_map.py --check
```

Vue build 검증:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run build
```

## v276~v277 실제 연결 확장

Vue `/admin`에서 아래 GET이 추가로 실제 호출됩니다.

- `GET /admin/master-data/domains`
- `GET /admin/master-data/catalog`

도메인 목록은 `response.payload.domains`, 카탈로그는 `response.payload.columns`와 `response.payload.rows`를 사용합니다.
카탈로그는 현재 `limit=20`, `page=1`, `sort=id_asc`로 고정했습니다.
검색/필터/페이지네이션/detail/relations/Preview/Apply/write는 아직 연결하지 않습니다.


## v278~v281 실제 연결 확장

Vue `/admin`은 기존 read-only client를 사용해 카탈로그의 `query`, `enabled`, `sort`, `page`를 GET query로 전송합니다.
선택 row 상세는 `fetchMasterDetail({ domain, rowId })`를 사용하며 wrapper가 backend query 이름 `id`로 변환합니다.

상세는 `payload.fields`, `payload.jsonFields`, `payload.assetFields`, `payload.relationHints`를 표시합니다.
관계는 `fetchMasterRelations({ domain, rowId, limit: 20 })`로 조회하고 `payload.groups[].columns/rows`를 표시합니다. 연관 row 이동은 다시 GET detail/relations만 호출합니다. Preview/Apply/write는 호출하지 않습니다.

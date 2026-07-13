# NEXT CHAT HANDOFF — Upgrade RPG v275

## 최신 ZIP

- `rpg_v275_backend_route_map_report.zip`

## 현재 기준

- 현재 작업 기준: `v275.backend-route-map-report`
- 직전 기준: `v274.backend-structure-plan`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 사용자/응답 방식

- 사용자는 코딩을 거의 모릅니다.
- 설명은 한국어로 쉽고 자세하게 합니다.
- 터미널 명령은 반드시 실행 위치를 먼저 씁니다.
- `npm install`, `npm run dev`, `npm run build` 같은 Vue/npm 명령은 `.venv`가 필요 없다고 함께 설명합니다.
- FastAPI/Python 명령은 `.venv`를 켠 상태 기준으로 안내합니다.
- 새로 설치해야 하는 파일/라이브러리/프레임워크가 있으면 사용자가 확인할 사항과 함께 반드시 알려줍니다.
- git 명령은 반드시 아래처럼 한 줄 블록으로 줍니다.

```bash
git status && git add . && git commit -m "..." && git push
```

## v270~v273 완료 내용

기존 legacy 화면을 건드리지 않고 `frontend/vue-app/`에 Vue shell을 추가했습니다.

현재 Vue route:

- `/game`
- `/admin`

Vue shell에 실제 연결한 안전 GET API:

- `/game` → `GET /health`
- `/admin` → `GET /health`
- `/admin` → `GET /admin/requirements`

v273에서는 Vue 개발 서버 `http://127.0.0.1:5173`에서 FastAPI `http://127.0.0.1:8000` 호출이 CORS로 막히는 문제를 local/debug 환경 기본 CORS origin 보강으로 해결했습니다.

## v274 완료 내용

v274에서는 FastAPI 구조를 실제 파일 기준으로 분석하고, Vue/FastAPI/DB 전환 전에 유지해야 할 backend 경계를 문서화했습니다.

추가:

- `tools/report_backend_structure_plan.py`
- `tools/smoke/backend/smoke_backend_structure_plan.py`
- `docs/current/BACKEND_STRUCTURE_PLAN.md`

핵심 결론:

- `backend/app/api/routes/`는 route path/contract 보호 대상으로 유지합니다.
- `backend/app/services/admin_service.py` facade는 유지합니다.
- `backend/app/services/admin/`은 당장 이동하지 않습니다.
- `backend/app/schemas/`, `backend/app/models/`, `backend/app/db/`는 PostgreSQL/Alembic 준비 전까지 구조 변경하지 않습니다.
- Vue에서는 당분간 안전한 `GET` read-only API만 연결합니다.
- Preview/Apply/write API는 인증/권한/Write Guard 설계 전까지 Vue에서 확장하지 않습니다.

## v275 완료 내용

v275에서는 FastAPI route map 자동 보고서를 만들고, Vue read-only 연결 후보와 보류 route를 분리했습니다.

추가/변경:

- `tools/report_backend_route_map.py`
- `tools/smoke/backend/smoke_backend_route_map_report.py`
- `docs/current/BACKEND_ROUTE_MAP.md`
- `frontend/vue-app/src/api/adminReadOnlyApi.js`

route map 요약:

| 구분 | 수 |
|---|---:|
| 전체 route | 27 |
| GET | 15 |
| POST | 12 |
| admin group | 21 |
| game group | 4 |
| health group | 2 |
| 중복 method/path | 0 |

현재 Vue 자동 smoke 화면에 연결된 route:

- `GET /api/v1/health`
- `GET /api/v1/admin/requirements`

다음 연결 후보:

- `GET /api/v1/admin/master-data/domains`

보류:

- 관리자 Preview 계열 POST
- 관리자 Apply/write 계열 POST
- `POST /api/v1/game/save`
- 인증/권한/Write Guard가 필요한 route

v275에서 함께 고친 것:

- Vue wrapper는 `rowId`를 받을 수 있지만 backend query 이름은 `id`입니다.
- `fetchMasterDetail({ rowId })`, `fetchMasterRelations({ rowId })`가 실제 요청에서는 `id`로 보내도록 맞췄습니다.

## v275에서 변경하지 않은 것

- DB 구조
- `.env` 파일
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

브라우저 확인:

```txt
http://127.0.0.1:5173/game
http://127.0.0.1:5173/admin
```

## 검증 기준

v275에서 확인한 검증:

- backend route map report smoke
- backend route map report `--check`
- backend structure plan smoke
- backend structure report `--check`
- backend local CORS smoke
- Vue shell/API smoke
- Vue read-only API status panel smoke
- JS 문법 검사
- legacy 경로 의존성 보고서 검사
- Python compileall
- core smoke 분할 실행
- ZIP 무결성 검사

## 다음 추천 작업

`v276 Vue admin read-only catalog mini panel`

목표:

- Vue 관리자 shell에 작은 read-only 카탈로그 점검 패널을 추가합니다.
- 첫 연결은 `GET /api/v1/admin/master-data/domains`만 사용합니다.
- 성공/오류/빈 데이터 상태를 표시합니다.
- catalog row 목록/detail/relations는 아직 자동 호출하지 않습니다.
- Preview/Apply/write route는 계속 보류합니다.
- route path/API response body는 변경하지 않습니다.
- DB/Alembic/인증/env/seed는 실제 변경하지 않습니다.

## 주의

다음은 사용자 승인 전 변경하지 않습니다.

- DB
- env
- seed
- 인증
- route path
- API 응답 body
- Write Guard
- 실제 write 로직
- 관리자 Preview/Apply 요청 body
- 기존 Smoke/Contract 의미

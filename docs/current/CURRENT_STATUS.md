# Current Status — v271

## 현재 기준

- 최신 작업: `v271.vue-readonly-api-client`
- 기준 ZIP: `rpg_v271_vue_readonly_api_client.zip`
- 직전 기준: `v270.vue-app-basic-shell`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## v271 완료

v271에서는 기존 legacy 화면을 건드리지 않고, Vue 앱에 읽기 전용 API client 준비 구조만 추가했습니다.

추가한 것:

- `frontend/vue-app/src/api/config.js`
- `frontend/vue-app/src/api/readOnlyRoutes.js`
- `frontend/vue-app/src/api/readOnlyClient.js`
- `frontend/vue-app/src/api/adminReadOnlyApi.js`
- `frontend/vue-app/src/api/gameReadOnlyApi.js`
- `frontend/vue-app/src/api/index.js`
- `docs/current/VUE_READONLY_API_CLIENT.md`
- `tools/smoke/frontend/smoke_vue_readonly_api_client.py`

Vue shell 변경:

- `AdminShell.vue`에 관리자 GET route 목록 표시
- `GameShell.vue`에 게임 GET route 목록 표시
- 아직 자동 API 호출은 하지 않음

## v271에서 변경하지 않은 것

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
| `/game` | 게임 이식 준비 shell |
| `/admin` | 관리자 이식 준비 shell |

## 사용자가 설치/확인해야 할 것

v271에서 새 라이브러리는 추가하지 않았습니다.

Vue 앱을 처음 실행한다면 기존 Vue 의존성 설치가 필요합니다.
이미 `frontend/vue-app/node_modules`가 있다면 다시 설치하지 않아도 됩니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

Vue 개발 서버 실행:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

FastAPI 서버 실행:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜야 함

```bash
.venv\\Scripts\\activate
```

실행 위치: `backend` 폴더  
`.venv` 상태: 켜진 상태

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 다음 추천 단계

`v272 Vue read-only API smoke 화면 연결`

추천 목표:

- Vue shell에서 실제 GET API 호출을 아주 작게 연결합니다.
- 처음에는 `/admin/requirements` 또는 `/health`처럼 안전한 조회 API만 사용합니다.
- 실패 시 화면이 깨지지 않도록 loading/error 상태를 먼저 만듭니다.
- Preview/Apply/write 요청은 계속 제외합니다.

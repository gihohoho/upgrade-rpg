# Current Status — v273

## 현재 기준

- 최신 작업: `v273.local-dev-cors-vue-fix`
- 기준 ZIP: `rpg_v273_local_dev_cors_vue_fix.zip`
- 직전 기준: `v272.vue-readonly-api-smoke-screen`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## v273 완료

v272에서는 기존 legacy 화면을 건드리지 않고, Vue shell에서 안전한 GET API를 실제로 작게 호출하는 화면 상태 패널을 추가했습니다.

v273에서는 사용자가 실제 브라우저에서 확인한 CORS 오류를 수정했습니다. Vue 개발 서버 `http://127.0.0.1:5173`에서 FastAPI `http://127.0.0.1:8000`의 read-only API를 호출할 수 있도록 local/debug CORS origin을 보강했습니다.

v272 추가/변경한 것:

- `frontend/vue-app/src/api/healthReadOnlyApi.js`
- `frontend/vue-app/src/components/ReadOnlyApiStatusPanel.vue`
- `frontend/vue-app/src/pages/AdminShell.vue`
- `frontend/vue-app/src/pages/GameShell.vue`
- `frontend/vue-app/src/styles/base.css`
- `tools/smoke/frontend/smoke_vue_readonly_api_status_panel.py`

v273 추가/변경한 것:

- `backend/app/core/config.py`
- `tools/smoke/backend/smoke_backend_local_cors.py`
- `docs/current/LOCAL_DEV_CORS.md`

Vue shell 변경:

- `/game`에서 `GET /health` 상태 확인
- `/admin`에서 `GET /health` 상태 확인
- `/admin`에서 `GET /admin/requirements` 상태 확인
- loading/error/success 상태 표시
- API 재확인 버튼 추가

## v273에서 변경하지 않은 것

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

v273에서 새 라이브러리는 추가하지 않았습니다.

Vue 앱을 처음 실행한다면 기존 Vue 의존성 설치가 필요합니다. 이미 `frontend/vue-app/node_modules`가 있다면 다시 설치하지 않아도 됩니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

FastAPI 서버 실행:

주의: v273 CORS 수정은 서버 재시작 후 반영됩니다. 기존 서버가 켜져 있다면 끄고 다시 실행합니다.

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

확인할 것:

- FastAPI 서버가 켜져 있으면 API 상태가 `성공`으로 표시됩니다.
- FastAPI 서버가 꺼져 있으면 API 상태가 `오류`로 표시됩니다. 이 경우도 정상이며, 화면 전체가 깨지지 않으면 됩니다.

## 다음 추천 단계

`v274 FastAPI 구조 정리 계획 구체화`

추천 목표:

- route/service/schema/model 책임을 현재 실제 파일 기준으로 다시 정리합니다.
- Vue에서 앞으로 읽을 API와 기존 legacy가 읽는 API를 분리해서 문서화합니다.
- route path/API response body는 바꾸지 않습니다.
- DB/Alembic/인증은 아직 실제 변경하지 않고 설계 문서부터 준비합니다.

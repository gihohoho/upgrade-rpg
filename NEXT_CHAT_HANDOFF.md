# NEXT CHAT HANDOFF — Upgrade RPG v273

## 최신 ZIP

- `rpg_v273_local_dev_cors_vue_fix.zip`

## 현재 기준

- 현재 작업 기준: `v273.local-dev-cors-vue-fix`
- 직전 기준: `v272.vue-readonly-api-smoke-screen`
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

## v270~v272 완료 내용

기존 legacy 화면을 건드리지 않고 `frontend/vue-app/`에 Vue shell을 추가했습니다.

현재 Vue route:

- `/game`
- `/admin`

v272에서 Vue shell에 실제 연결한 안전 GET API:

- `/game` → `GET /health`
- `/admin` → `GET /health`
- `/admin` → `GET /admin/requirements`

## v273 완료 내용

사용자가 Vue 화면에서 아래 CORS 오류를 확인했습니다.

```txt
Access to fetch at 'http://127.0.0.1:8000/api/v1/health' from origin 'http://127.0.0.1:5173' has been blocked by CORS policy
```

v273에서는 이 문제를 수정했습니다.

변경:

- `backend/app/core/config.py`
  - local/debug 환경에서 기본 개발 CORS origin을 자동 포함
  - 오래된 로컬 `.env`의 `CORS_ORIGINS`에 `5173`이 빠져 있어도 Vue 개발 서버 호출 허용
  - production/debug-false에서는 명시 origin만 사용
- `tools/smoke/backend/smoke_backend_local_cors.py`
  - 오래된 CORS 설정 fallback 검증
  - production 비자동 추가 검증
  - 실제 FastAPI app CORS preflight header 검증
- `tools/run_smoke_core.sh`
  - CORS smoke 포함
- `docs/current/LOCAL_DEV_CORS.md`

## v273에서 변경하지 않은 것

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

v273에서 새 라이브러리/프레임워크는 추가하지 않았습니다.

Vue 앱을 처음 실행한다면 기존 Vue 의존성 설치가 필요합니다. 이미 `frontend/vue-app/node_modules`가 있다면 다시 설치하지 않아도 됩니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

FastAPI 서버 실행:

주의: v273 CORS 수정은 서버를 재시작해야 반영됩니다. 기존 서버가 켜져 있다면 끄고 다시 실행합니다.

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

확인 기준:

- FastAPI 서버가 켜져 있으면 API 상태가 `성공`으로 표시됩니다.
- CORS 수정 후에도 오류가 남으면 FastAPI 서버가 완전히 재시작되었는지 먼저 확인합니다.
- FastAPI 서버가 꺼져 있으면 API 상태가 `오류`로 표시됩니다. 이 경우도 정상이며, 화면 전체가 깨지지 않으면 됩니다.

## 검증 기준

v273에서 확인한 검증:

- backend local CORS smoke
- Vue shell/API smoke
- Vue read-only API status panel smoke
- JS 문법 검사
- legacy 경로 의존성 보고서 검사
- Python compileall
- core smoke 분할 실행
- ZIP 무결성 검사

## 다음 추천 작업

`v274 FastAPI 구조 정리 계획 구체화`

목표:

- 현재 `backend/app/api/routes`, `backend/app/services`, `backend/app/schemas`, `backend/app/models` 역할을 실제 파일 기준으로 정리합니다.
- Vue에서 앞으로 사용할 read-only API와 legacy 유지 API를 구분합니다.
- route path/API response body는 변경하지 않습니다.
- DB/Alembic/인증은 실제 변경하지 않고 계획만 문서화합니다.
- 기존 smoke/contract 의미를 깨지 않는지 영향 범위를 확인합니다.

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

# Vue API Layer — v272

이 폴더는 Vue 앱에서 FastAPI를 호출할 때 사용할 API client 준비 공간입니다.

v272 기준 원칙:

- 읽기 전용 `GET` API만 연결합니다.
- `POST`, `PUT`, `PATCH`, `DELETE` 요청은 아직 추가하지 않습니다.
- 관리자 Preview/Apply/write 요청 body는 아직 Vue로 옮기지 않습니다.
- 인증 interceptor는 아직 만들지 않습니다.
- `.env` 파일은 만들거나 수정하지 않았습니다.

## 파일 역할

| 파일 | 역할 |
|---|---|
| `config.js` | API 기본 주소 관리. 기본값은 `http://127.0.0.1:8000/api/v1` |
| `readOnlyRoutes.js` | 읽기 전용 route 상수 목록 |
| `readOnlyClient.js` | `fetch` 기반 GET 전용 요청 함수 |
| `healthReadOnlyApi.js` | `/health` 계열 조회 API 함수 묶음 |
| `adminReadOnlyApi.js` | 관리자 읽기 전용 API 함수 묶음 |
| `gameReadOnlyApi.js` | 게임 읽기 전용 API 함수 묶음 |
| `index.js` | API layer export 모음 |

## v272에서 화면에 실제 연결한 것

- `/game`: `GET /health`
- `/admin`: `GET /health`
- `/admin`: `GET /admin/requirements`

## 사용자가 설치해야 하는 것

v272에서 새 라이브러리는 추가하지 않았습니다.

다만 Vue 앱을 처음 실행한다면 기존 v270에서 추가된 Vue 의존성을 한 번 설치해야 합니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

## Vue 개발 서버 실행

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

## FastAPI 서버 실행

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

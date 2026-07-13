# Local Dev CORS — v273

## 한 줄 요약

v273에서는 Vue 개발 서버(`http://127.0.0.1:5173`)에서 FastAPI(`http://127.0.0.1:8000`)를 호출할 때 브라우저 CORS 오류가 나지 않도록, local/debug 환경의 기본 CORS 허용 origin을 보강했습니다.

## 사용자가 본 오류

브라우저 콘솔 예시:

```txt
Access to fetch at 'http://127.0.0.1:8000/api/v1/health' from origin 'http://127.0.0.1:5173' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## 원인

Vue 개발 서버와 FastAPI 서버는 포트가 다릅니다.

| 서버 | 주소 |
|---|---|
| Vue 개발 서버 | `http://127.0.0.1:5173` |
| FastAPI 서버 | `http://127.0.0.1:8000` |

브라우저는 포트가 다르면 다른 출처(origin)로 판단합니다. 그래서 FastAPI가 `http://127.0.0.1:5173`을 허용하지 않으면 Vue에서 API 호출이 차단됩니다.

## v273 수정 내용

수정 파일:

```txt
backend/app/core/config.py
```

추가/보강한 것:

- local/debug 환경에서 기본 개발 origin을 자동 포함
- 오래된 로컬 `.env`의 `CORS_ORIGINS` 값에 `5173` 포트가 빠져 있어도 Vue 개발 서버 호출 허용
- production 환경에서는 `CORS_ORIGINS`에 명시한 값만 사용

local/debug 기본 허용 origin:

```txt
http://localhost:5500
http://127.0.0.1:5500
http://localhost:5173
http://127.0.0.1:5173
http://localhost:3000
http://127.0.0.1:3000
```

## 변경하지 않은 것

- `.env` 파일은 수정하지 않았습니다.
- DB 구조는 수정하지 않았습니다.
- seed는 수정하지 않았습니다.
- 인증은 수정하지 않았습니다.
- API route path는 수정하지 않았습니다.
- API 응답 body는 수정하지 않았습니다.
- Preview/Apply/write 요청 body는 수정하지 않았습니다.
- Write Guard와 실제 write 로직은 수정하지 않았습니다.

## 사용자가 해야 할 것

FastAPI 서버는 CORS 설정을 서버 시작 시점에 읽습니다. 따라서 v273 ZIP을 적용한 뒤에는 백엔드 서버를 껐다가 다시 켜야 합니다.

### FastAPI 서버 재실행

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

## 검증

추가한 전용 smoke:

```txt
tools/smoke/backend/smoke_backend_local_cors.py
```

확인하는 것:

- 오래된 `CORS_ORIGINS` 값에 `5173`이 없어도 local 설정에서는 `5173`을 자동 포함하는지
- production 설정에서는 local 개발 origin을 자동 추가하지 않는지
- 실제 FastAPI app이 `Origin: http://127.0.0.1:5173` 요청에 CORS header를 반환하는지

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python tools/smoke/backend/smoke_backend_local_cors.py
```

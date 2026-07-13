# Upgrade RPG Vue App Shell — v277

이 폴더는 기존 게임/관리자 화면을 바로 대체하지 않는 Vue 준비 앱입니다.

현재 실제 화면:

- 게임: 루트 `index.html`
- 관리자: 루트 `admin.html`
- legacy JS/CSS: 루트 `src/`

## 현재 Vue 연결 범위

`/game`:

- `GET /health`

`/admin`:

- `GET /health`
- `GET /admin/requirements`
- `GET /admin/master-data/domains`
- `GET /admin/master-data/catalog` 첫 페이지

v276에서는 도메인 목록을 연결했고, v277에서는 선택 도메인의 첫 20개 row를 표로 연결했습니다.

아직 연결하지 않은 것:

- 검색/필터/페이지네이션
- detail/relations
- Preview/Apply/write
- 인증/token/interceptor

## 설치

v277에서 새 라이브러리나 프레임워크는 추가하지 않았습니다.

처음 실행하는 경우에만:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

## Vue 실행

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

## FastAPI 실행

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

확인 주소:

```txt
http://127.0.0.1:5173/game
http://127.0.0.1:5173/admin
```

## 빌드 확인

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run build
```

## 변경하지 않은 것

- DB/env/seed/auth
- route path/API response body
- Write Guard/실제 write
- Preview/Apply 요청 body
- 기존 smoke/contract 의미

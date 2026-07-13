# Upgrade RPG Vue App Shell — v279

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
- `GET /admin/master-data/catalog`
- `GET /admin/master-data/detail`

지원 기능:

- 도메인 선택
- 검색어
- 활성/비활성 필터
- 정렬
- 이전/다음 페이지
- 선택 row 상세
- scalar 필드
- 관계 힌트
- 안전한 JSON 미리보기

아직 연결하지 않은 것:

- relations GET
- Preview/Apply/write
- 인증/token/interceptor

## 설치

v278~v279에서 새 라이브러리나 프레임워크는 추가하지 않았습니다.

처음 실행하는 경우에만:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음

```bash
npm install
```

## Vue 실행

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음

```bash
npm run dev
```

## FastAPI 실행

실행 위치: 프로젝트 루트  
`.venv` 상태: 꺼져 있다면 켜야 함

```bash
.venv\Scripts\activate
```

실행 위치: `backend` 폴더  
`.venv` 상태: 켜진 상태

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 빌드 확인

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음

```bash
npm run build
```

## 변경하지 않은 것

- DB/env/seed/auth
- route path/API response body
- Write Guard/실제 write
- Preview/Apply 요청 body
- 기존 smoke/contract 의미

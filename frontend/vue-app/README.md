# Upgrade RPG Vue App Shell — v281

이 폴더는 기존 게임/관리자 화면을 바로 대체하지 않는 Vue 준비 앱입니다.

실제 화면은 계속 루트 `index.html`, `admin.html`, legacy `src/`를 사용합니다.

## 현재 Vue 연결 범위

`/game`은 `GET /health`를 사용합니다.

`/admin`은 아래 GET을 사용합니다.

- `/health`
- `/admin/requirements`
- `/admin/master-data/domains`
- `/admin/master-data/catalog`
- `/admin/master-data/detail`
- `/admin/master-data/relations`

지원 기능:

- 도메인 선택
- 검색, 활성/비활성 필터, 정렬, 페이지네이션
- scalar/JSON 안전 상세
- 관계 그룹 표
- 연관 row 상세 이동
- `이전 상세로`

아직 연결하지 않은 것:

- 관계 편집
- Preview/Apply/write
- 인증/token/interceptor

## 설치

v280~v281에서 새 라이브러리나 프레임워크는 없습니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음 / 꺼져 있어도 됨

```bash
npm install
```

## Vue 실행

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음 / 꺼져 있어도 됨

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

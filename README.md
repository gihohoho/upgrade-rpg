# Upgrade RPG

현재 기준: **v281.vue-admin-related-detail-navigation**

## 현재 상태

- 실제 게임 화면: 루트 `index.html`
- 실제 관리자 화면: 루트 `admin.html`
- legacy JS/CSS: 루트 `src/`
- 새 Vue shell: `frontend/vue-app/`
- FastAPI 백엔드: `backend/`

Vue `/admin`에는 안전한 GET 상태 확인, 도메인, 카탈로그, 상세, 관계 그룹을 연결했습니다. 관계 표의 `이 row 상세`로 연관 row를 조회하고 `이전 상세로`로 돌아갈 수 있습니다.

관계 편집, Preview/Apply/write, DB/env/seed/auth는 변경하거나 연결하지 않았습니다.

## 설치해야 하는 것

v280~v281에서 새 라이브러리나 프레임워크는 추가하지 않았습니다.

`frontend/vue-app/node_modules`가 없다면 한 번만 설치합니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음 / 꺼져 있어도 됨

```bash
npm install
```

## Vue 앱 실행

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 필요 없음 / 꺼져 있어도 됨

```bash
npm run dev
```

확인 주소: `http://127.0.0.1:5173/admin`

## FastAPI 서버 실행

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

## 검증

실행 위치: 프로젝트 루트  
`.venv` 상태: Vue 검사는 무관, Python/core 검사는 켜진 상태 권장

```bash
bash tools/run_smoke_vue_shell.sh
python -m compileall -q backend/app backend/scripts tools
bash tools/run_smoke_core.sh
```

## 다음 방향

다음은 실제 DB를 바꾸지 않고 PostgreSQL/Alembic 도입 계획과 검증 체크리스트를 구체화합니다.

# Upgrade RPG

현재 기준: **v279.vue-admin-readonly-detail-panel**

## 현재 상태

- 기존 실제 게임 화면: `index.html`
- 기존 실제 관리자 화면: `admin.html`
- 기존 legacy JS/CSS: 루트 `src/`
- 새 Vue shell: `frontend/vue-app/`
- FastAPI 백엔드: `backend/`

Vue `/admin`에 현재 연결된 안전한 GET 범위:

- `/health`
- `/admin/requirements`
- `/admin/master-data/domains`
- `/admin/master-data/catalog`
- `/admin/master-data/detail`

v278에서는 카탈로그 검색·활성 상태·정렬·페이지네이션을 추가했습니다.  
v279에서는 선택 row의 scalar 필드, 관계 힌트, 안전한 JSON 미리보기를 표시하는 상세 패널을 추가했습니다.  
`/admin/requirements`는 성공해도 `-`로 보이던 대신 `readOnlyOverviewReady`를 기준으로 `준비 완료`를 표시합니다.

기존 게임/관리자 동작, API route, API 응답 body, DB, env, seed, 인증, Write Guard, 실제 write 로직은 변경하지 않았습니다.

## 설치해야 하는 것

v278~v279에서 새 라이브러리나 프레임워크는 추가하지 않았습니다.

`frontend/vue-app/node_modules`가 없다면 한 번만 설치합니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

## Vue 앱 실행

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

확인 주소:

```txt
http://127.0.0.1:5173/admin
```

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

## 검증 명령

Vue shell/API 검사:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜져 있거나 꺼져 있어도 됨

```bash
bash tools/run_smoke_vue_shell.sh
```

기존 core smoke:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
bash tools/run_smoke_core.sh
```

Python compile 검사:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python -m compileall -q backend/app backend/scripts tools
```

보고서 검사:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python tools/report_legacy_path_dependencies.py --check && python tools/report_backend_structure_plan.py --check && python tools/report_backend_route_map.py --check
```

## 현재 개발 방향

당분간 게임 콘텐츠 개발은 하지 않습니다.

다음 추천 작업은 `v280 Vue admin read-only relations panel`입니다. 관계 GET만 연결하고 Preview/Apply/write는 계속 보류합니다.

# Upgrade RPG

현재 기준: **v277.vue-admin-readonly-catalog-mini-panel**

## 현재 상태

- 기존 실제 게임 화면: `index.html`
- 기존 실제 관리자 화면: `admin.html`
- 기존 legacy JS/CSS: 루트 `src/`
- 새 Vue shell: `frontend/vue-app/`
- Vue 읽기 전용 API client 준비 위치: `frontend/vue-app/src/api/`
- FastAPI 백엔드: `backend/`

v272에서는 Vue 앱 안에서 안전한 `GET /health`, `GET /admin/requirements` 상태 확인 패널을 실제 화면에 연결했습니다.  
v273에서는 Vue 개발 서버(`127.0.0.1:5173`)에서 FastAPI(`127.0.0.1:8000`)를 호출할 때 발생한 local CORS 오류를 수정했습니다.  
v274에서는 FastAPI route/service/schema/model/db/core 구조를 실제 파일 기준으로 분석하고, 전환 전 유지해야 할 backend 경계를 문서화했습니다.  
v275에서는 FastAPI route map 자동 보고서를 만들고, Vue read-only 연결 후보와 보류 route를 분리했습니다.
v276에서는 Vue 관리자 shell에 마스터 데이터 도메인 목록을 연결했습니다.
v277에서는 선택 도메인의 첫 20개 카탈로그를 일반 표로 연결했습니다.

기존 게임/관리자 동작, API route, API 응답 body, DB, env, seed, 인증, Write Guard, 실제 write 로직은 변경하지 않았습니다.

## 사용자가 설치해야 하는 것

v276~v277에서 새 라이브러리나 프레임워크는 추가하지 않았습니다.

Vue 앱을 처음 실행할 때만 Node 패키지 설치가 필요합니다. 이미 `frontend/vue-app/node_modules`가 있다면 다시 설치하지 않아도 됩니다.

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

브라우저 주소:

```txt
http://127.0.0.1:5173
```

확인할 화면:

- `http://127.0.0.1:5173/game`
- `http://127.0.0.1:5173/admin`

## Vue API 상태 확인

FastAPI 서버와 Vue 개발 서버를 둘 다 켠 뒤 아래 화면을 확인합니다.

- `http://127.0.0.1:5173/game` → `GET /health` 상태 확인
- `http://127.0.0.1:5173/admin` → `GET /health`, `GET /admin/requirements`, 도메인 목록, 선택 도메인 첫 카탈로그 확인

FastAPI 서버가 꺼져 있으면 `오류`가 표시되는 것이 정상입니다. 중요한 것은 Vue 화면 전체가 깨지지 않는 것입니다.

v273 ZIP 적용 후에도 CORS 오류가 남아 있으면 FastAPI 서버를 완전히 종료한 뒤 다시 실행해야 합니다. CORS 설정은 서버 시작 시점에 반영됩니다.

## FastAPI 서버 실행

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

## 검증 명령

Vue shell/API 구조 검사:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

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

legacy 경로 의존성 검사:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python tools/report_legacy_path_dependencies.py --check
```

Backend 구조 계획 검사:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python tools/report_backend_structure_plan.py --check
```

Backend route map 검사:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python tools/report_backend_route_map.py --check
```

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python tools/smoke/backend/smoke_backend_route_map_report.py
```

## 현재 개발 방향

당분간 게임 콘텐츠 개발은 하지 않습니다.

보류:

- 장비 추가
- 스킬 추가
- 보스 추가
- 필드 추가
- 드랍률/밸런스 조정
- 강화 수치 조정
- 신규 콘텐츠 기획 반영

우선순위:

1. Vue/FastAPI/DB 전환 준비
2. legacy 유지 범위 확정
3. Vue 읽기 전용 API client 연결
4. FastAPI 구조/route map 문서화
5. PostgreSQL/Alembic 준비
6. 인증 설계 준비
7. 관리자 페이지 Vue 이식
8. 게임 화면 Vue 이식
9. 배포 직전 안정화

## 주요 문서

- `docs/current/CURRENT_STATUS.md`
- `docs/current/PROJECT_STRUCTURE.md`
- `docs/current/VUE_APP_SHELL.md`
- `docs/current/VUE_READONLY_API_CLIENT.md`
- `docs/current/VUE_ADMIN_READONLY_CATALOG.md`
- `docs/current/LOCAL_DEV_CORS.md`
- `docs/current/BACKEND_STRUCTURE_PLAN.md`
- `docs/current/BACKEND_ROUTE_MAP.md`
- `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`
- `docs/current/LEGACY_PATH_DEPENDENCIES.md`
- `docs/NEXT_STEPS.md`
- `NEXT_CHAT_HANDOFF.md`
- `NEXT_CHAT_PROMPT.md`

# Upgrade RPG

현재 기준: **v271.vue-readonly-api-client**

## 현재 상태

- 기존 실제 게임 화면: `index.html`
- 기존 실제 관리자 화면: `admin.html`
- 기존 legacy JS/CSS: 루트 `src/`
- 새 Vue shell: `frontend/vue-app/`
- Vue 읽기 전용 API client 준비 위치: `frontend/vue-app/src/api/`
- FastAPI 백엔드: `backend/`

v271에서는 Vue 앱 안에 읽기 전용 `GET` API client 준비 구조를 추가했습니다.
기존 게임/관리자 동작, API route, API 응답 body, DB, env, seed, 인증, Write Guard, 실제 write 로직은 변경하지 않았습니다.

## 사용자가 설치해야 하는 것

v271에서 새 라이브러리는 추가하지 않았습니다.

Vue 앱을 처음 실행할 때만 Node 패키지 설치가 필요합니다.
이미 `frontend/vue-app/node_modules`가 있다면 다시 설치하지 않아도 됩니다.

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
4. FastAPI 구조 정리 계획
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
- `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`
- `docs/current/LEGACY_PATH_DEPENDENCIES.md`
- `docs/NEXT_STEPS.md`
- `NEXT_CHAT_HANDOFF.md`
- `NEXT_CHAT_PROMPT.md`

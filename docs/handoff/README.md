# Upgrade RPG

현재 인계 기준: **v270.vue-app-basic-shell**

직전 작업 기준: `v269.legacy-path-dependency-report`

직전 기능 기준: `v266.admin-practical-ux-polish`

관리자 readiness: `v250.backend-admin-rollback-snapshot`

Backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 현재 상태

- 관리자 HTML 페이지는 임시 운영/검증 도구로 충분히 안정화했습니다.
- 게임 콘텐츠 개발은 당분간 보류합니다.
- v268에서는 프로젝트 구조와 Vue/FastAPI/DB 전환 준비 문서를 갱신했습니다.
- v269에서는 legacy 경로 의존성 자동 목록화 도구와 보고서를 추가했습니다.
- v270에서는 `frontend/vue-app/`에 Vite + Vue 기본 shell을 추가했습니다.
- 기존 `admin.html`, `index.html`, 루트 `src/`는 계속 유지합니다.
- Vue shell은 아직 실제 관리자/게임 기능을 대체하지 않습니다.
- DB, env, seed, 인증, 기존 route, API 응답 body, Write Guard, 실제 write 로직은 유지합니다.

## 사용자가 설치해야 할 것

Vue 앱 실행 전 처음 한 번 설치가 필요합니다.

실행 위치: `frontend/vue-app` 폴더

```bash
npm install
```

개발 서버 실행:

실행 위치: `frontend/vue-app` 폴더

```bash
npm run dev
```

브라우저 확인:

```txt
http://127.0.0.1:5173
```

## 먼저 볼 파일

1. `NEXT_CHAT_PROMPT.md`
2. `NEXT_CHAT_HANDOFF.md`
3. `docs/current/CURRENT_STATUS.md`
4. `docs/current/VUE_APP_SHELL.md`
5. `docs/current/PROJECT_STRUCTURE.md`
6. `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`
7. `docs/current/LEGACY_PATH_DEPENDENCIES.md`

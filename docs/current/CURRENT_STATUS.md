# Current Status — v270

## 현재 최신 작업

- 최신 작업: `v270.vue-app-basic-shell`
- 직전 작업: `v269.legacy-path-dependency-report`
- 직전 기능 기준: `v266.admin-practical-ux-polish`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## 현재 상태 요약

관리자 페이지는 임시 운영/검증 도구로 충분히 안정화된 상태입니다.

당분간 게임 콘텐츠 개발은 하지 않습니다.

우선순위는 Vue + FastAPI + PostgreSQL + 관리자 페이지 + 배포 직전 안정화 구조를 준비하는 것입니다.

## v270 완료

- `frontend/vue-app/`에 Vite + Vue 기본 shell 추가
- Vue Router 기본 구조 추가
- `GameShell.vue` 추가
- `AdminShell.vue` 추가
- `ShellCard.vue` 공통 shell 카드 추가
- Vue shell 기본 CSS 추가
- Vue shell 구조 smoke 추가
- Vue 실행/설치 문서 추가

## v270에서 변경하지 않은 것

- DB
- env
- seed
- 인증
- 기존 route path
- 기존 API 응답 body
- Write Guard
- 실제 write 로직
- 관리자 Preview/Apply 요청 body
- 기존 smoke/contract 의미
- 게임 콘텐츠

## 사용자가 확인해야 할 것

Vue 앱을 실제로 실행하려면 한 번 설치가 필요합니다.

실행 위치: `frontend/vue-app` 폴더

```bash
npm install
```

실행 위치: `frontend/vue-app` 폴더

```bash
npm run dev
```

브라우저 주소:

```txt
http://127.0.0.1:5173
```

확인할 화면:

- `/game`에서 게임 Shell 안내가 보이는지
- `/admin`에서 관리자 Shell 안내가 보이는지
- 기존 루트 `index.html`, `admin.html`은 그대로 열리는지

## 다음 추천

`v271 Vue API client 읽기 전용 설계 + backend route map 연결 준비`

주의:

- 인증/interceptor/write는 아직 넣지 않습니다.
- 먼저 GET 계열 API client와 route 목록 문서화를 진행합니다.

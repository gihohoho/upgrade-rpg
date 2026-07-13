# NEXT CHAT HANDOFF — Upgrade RPG v270

## 현재 최신 ZIP

- `rpg_v270_vue_app_basic_shell.zip`

반드시 이 ZIP을 기준으로 작업합니다.

## 사용자/응답 방식

- 사용자는 코딩을 거의 모릅니다.
- 설명은 항상 한국어로 쉽고 자세하게 합니다.
- 터미널 명령을 줄 때는 반드시 실행 위치를 먼저 적습니다.
- git 명령은 아래처럼 한 줄 블록으로 줍니다.

```bash
git status && git add . && git commit -m "..." && git push
```

- 앞으로 사용자가 확인해야 할 사항, 설치해야 할 파일, 라이브러리, 프레임워크는 빠짐없이 알려줍니다.
- 필요한 라이브러리/파일은 추가해도 됩니다.
- 여러 단계를 한 번에 진행해도 됩니다.
- 위험한 작업은 작게 나누고 검증 후 진행합니다.

## 현재 기준

- 현재 작업 기준: `v270.vue-app-basic-shell`
- 직전 작업 기준: `v269.legacy-path-dependency-report`
- 직전 기능 기준: `v266.admin-practical-ux-polish`
- readiness version: `v250.backend-admin-rollback-snapshot`
- backend splitStatus: `admin-schema-field-constraint-contract-v238`

## v270 완료 내용

- `frontend/vue-app/`에 Vite + Vue 기본 shell 추가
- `package.json`, `vite.config.js`, `index.html` 추가
- `src/main.js`, `src/App.vue` 추가
- Vue Router 기본 구조 추가
- `/game` → `GameShell.vue`
- `/admin` → `AdminShell.vue`
- 공통 `ShellCard.vue` 추가
- Vue 기본 CSS 추가
- `tools/smoke/frontend/smoke_vue_shell_structure.py` 추가
- `tools/run_smoke_vue_shell.sh` 추가
- 관련 문서 갱신

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

## 사용자가 설치해야 할 것

Vue 앱을 실제로 실행하려면 처음 한 번 설치가 필요합니다.

실행 위치: `frontend/vue-app` 폴더

```bash
npm install
```

Vue 개발 서버 실행:

실행 위치: `frontend/vue-app` 폴더

```bash
npm run dev
```

브라우저 확인:

```txt
http://127.0.0.1:5173
```

## 검증 명령

Vue shell 검사:

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_vue_shell.sh
```

기존 core smoke:

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

Python compile:

실행 위치: 프로젝트 루트

```bash
python -m compileall -q backend/app backend/scripts tools
```

## 다음 추천 작업

`v271 Vue API client 읽기 전용 설계 + backend route map 연결 준비`

목표:

- Vue용 API client 폴더/파일을 준비합니다.
- 기존 FastAPI route path 목록을 문서와 연결합니다.
- 처음에는 GET/읽기 전용 API만 대상으로 합니다.
- 인증/interceptor/write는 아직 구현하지 않습니다.
- 관리자 Preview/Apply 요청 body는 변경하지 않습니다.
- 기존 legacy `admin.html`, `index.html`, 루트 `src/`는 유지합니다.

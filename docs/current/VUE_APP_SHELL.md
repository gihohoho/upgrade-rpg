# Vue App Shell — v270

## 한 줄 요약

v270에서는 기존 게임/관리자 화면을 건드리지 않고, `frontend/vue-app/`에 Vue 기본 shell만 추가했습니다.

## 현재 실제 화면

| 화면 | 실제 기준 |
|---|---|
| 게임 | 루트 `index.html` |
| 관리자 | 루트 `admin.html` |
| legacy JS/CSS | 루트 `src/` |

## 새 Vue shell

```txt
frontend/vue-app/
```

현재 Vue route:

| 경로 | 컴포넌트 | 의미 |
|---|---|---|
| `/` | redirect | `/game`으로 이동 |
| `/game` | `GameShell.vue` | 게임 Vue 이식 준비 화면 |
| `/admin` | `AdminShell.vue` | 관리자 Vue 이식 준비 화면 |

## 이번 단계에서 설치한/추가한 파일

추가한 프레임워크 설정:

- Vite 설정: `frontend/vue-app/vite.config.js`
- Vue 앱 진입점: `frontend/vue-app/src/main.js`
- Vue Router 설정: `frontend/vue-app/src/router/index.js`

`package.json` 의존성:

- `vue`
- `vue-router`
- `vite`
- `@vitejs/plugin-vue`

## 사용자가 직접 설치해야 하는 것

ZIP에는 `node_modules`가 없습니다.
처음 실행할 때 한 번만 설치합니다.

실행 위치: `frontend/vue-app` 폴더

```bash
npm install
```

## 실행 방법

실행 위치: `frontend/vue-app` 폴더

```bash
npm run dev
```

브라우저 주소:

```txt
http://127.0.0.1:5173
```

## 검증 방법

Vue shell 구조 검증:

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_vue_shell.sh
```

`npm install` 이후 빌드 검증:

실행 위치: `frontend/vue-app` 폴더

```bash
npm run build
```

## 주의

v270 Vue shell은 아직 실제 기능과 연결하지 않았습니다.

연결하지 않은 것:

- 관리자 catalog API
- 관리자 detail API
- Preview API
- Apply/write API
- 게임 상태
- 전투/아이템/스탯 시스템
- 저장/복구 기능
- 인증

## 다음 단계에서 할 일

v271에서는 Vue API client를 만들 수 있습니다.
단, 처음에는 읽기 전용 GET 계열부터 시작합니다.

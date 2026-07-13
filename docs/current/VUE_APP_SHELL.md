# Vue App Shell — v271

## 한 줄 요약

v270에서 기존 게임/관리자 화면을 건드리지 않고 `frontend/vue-app/`에 Vue 기본 shell을 추가했고, v271에서는 그 shell 안에 읽기 전용 API route 목록을 표시했습니다.

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

## v271에서 화면에 표시하는 것

- `GameShell.vue`: 게임 GET API 준비 목록
- `AdminShell.vue`: 관리자 GET API 준비 목록

아직 실제 API를 자동 호출하지는 않습니다.
다음 단계에서 loading/error/success 구조를 만든 뒤 아주 작은 GET API부터 연결합니다.

## 이번 단계에서 추가된 API 준비 파일

```txt
frontend/vue-app/src/api/
├── README.md
├── adminReadOnlyApi.js
├── config.js
├── gameReadOnlyApi.js
├── index.js
├── readOnlyClient.js
└── readOnlyRoutes.js
```

## 사용자가 직접 설치해야 하는 것

v271에서 새 라이브러리는 추가하지 않았습니다.

ZIP에는 `node_modules`가 없습니다.
Vue 앱을 처음 실행할 때 한 번만 설치합니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

## 실행 방법

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

브라우저 주소:

```txt
http://127.0.0.1:5173
```

## 검증 방법

Vue shell/API 구조 검증:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
bash tools/run_smoke_vue_shell.sh
```

`npm install` 이후 빌드 검증:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run build
```

## 주의

v271 Vue shell은 아직 실제 기능을 대체하지 않았습니다.

연결하지 않은 것:

- 관리자 catalog 실제 화면 이식
- 관리자 detail 실제 화면 이식
- Preview API
- Apply/write API
- 게임 상태
- 전투/아이템/스탯 시스템
- 저장/복구 기능
- 인증

## 다음 단계에서 할 일

v272에서는 Vue shell에서 안전한 GET API를 1~2개만 실제 호출해볼 수 있습니다.
단, Preview/Apply/write는 계속 제외합니다.

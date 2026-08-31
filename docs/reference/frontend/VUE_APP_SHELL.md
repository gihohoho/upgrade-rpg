# Vue App Shell — v273 + v383 admin confirmation boundary

## 한 줄 요약

v270에서 `frontend/vue-app/`에 Vue 기본 shell을 추가했고, v271에서 읽기 전용 API route/client를 준비했으며, v272에서 안전한 GET API 상태 확인 패널을 실제 화면에 연결했습니다. v273에서는 Vue 개발 서버와 FastAPI 사이의 local CORS 오류를 수정했습니다.

## 현재 실제 화면

| 화면 | 실제 기준 |
|---|---|
| 게임 | 루트 `index.html` |
| 관리자 | 루트 `admin.html` |
| legacy JS/CSS | 루트 `src/` |
| Vue 준비 shell | `frontend/vue-app/` |

## 새 Vue shell route

| 경로 | 컴포넌트 | 의미 |
|---|---|---|
| `/` | redirect | `/game`으로 이동 |
| `/game` | `GameShell.vue` | 게임 Vue 이식 준비 화면 |
| `/admin` | `AdminShell.vue` | 관리자 Vue 이식 준비 화면 |
| `/admin/access` | `AdminAccessPage.vue` | 관리자 로그인·권한 거부·재시도 |

v381부터 `/admin`은 `isAdmin=true` route guard를 통과해야 합니다. 통과 전에는 `AdminShell`과 관리자 GET 패널을 렌더링하지 않으며, 통과한 GET 요청은 Bearer token과 `no-store`를 사용합니다.

v382부터 인증된 관리자 shell 안에 생성·수정·되돌리기 Preview 작업대를 렌더링합니다. 이 작업대의 POST는 `dryRun: true`이고 실제 Apply와 dev key 입력은 없습니다.

v383부터 ready Preview에는 실제 write 없는 확인 modal 진입 버튼이 나타납니다. modal은 동일 Preview 재검증, server exact 문구, 현재 비밀번호·dev key 미전송 입력과 영향 확인을 제공하지만 최종 Apply 버튼은 항상 잠겨 있고 Apply API/header는 연결하지 않습니다.

## v272에서 화면에 표시하는 것

- `GameShell.vue`
  - 게임 Vue 이식 준비 안내
  - `GET /health` 실제 호출 상태
  - 게임 GET API 준비 목록
- `AdminShell.vue`
  - 관리자 Vue 이식 준비 안내
  - `GET /health` 실제 호출 상태
  - `GET /admin/requirements` 실제 호출 상태
  - 관리자 GET API 준비 목록

## 추가된 화면 컴포넌트

```txt
frontend/vue-app/src/components/ReadOnlyApiStatusPanel.vue
```

역할:

- loading/error/success 상태 표시
- API 재확인 버튼 제공
- 실패해도 shell 전체가 깨지지 않도록 오류 문구만 표시

## 사용자가 직접 설치해야 하는 것

v273에서 새 라이브러리는 추가하지 않았습니다.

ZIP에는 `node_modules`가 없습니다. Vue 앱을 처음 실행할 때 한 번만 설치합니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

## 실행 방법

FastAPI 서버 실행:

주의: v273 CORS 수정은 FastAPI 서버 재시작 후 반영됩니다.

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

Vue 개발 서버 실행:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

브라우저 주소:

```txt
http://127.0.0.1:5173/game
http://127.0.0.1:5173/admin
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

v273 Vue shell은 아직 실제 기능을 대체하지 않았습니다.

연결하지 않은 것:

- 관리자 catalog 실제 화면 이식
- 관리자 detail 실제 화면 이식
- Preview API
- Apply/write API
- 게임 상태
- 전투/아이템/스탯 시스템
- 저장/복구 기능
- 인증
- DB 구조 변경

## 다음 단계에서 할 일

v274에서는 FastAPI 구조 정리 계획을 더 구체화하는 것이 안전합니다. 또는 Vue read-only 화면에 `GET /admin/overview`처럼 DB 의존 조회를 붙이기 전에 DB 실행/오류 처리 기준을 먼저 문서화할 수 있습니다.

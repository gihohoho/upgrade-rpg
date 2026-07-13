# Vue Read-only API Client — v271

## 한 줄 요약

v271에서는 기존 legacy 화면과 FastAPI route를 바꾸지 않고, 새 Vue 앱 내부에 `GET` 전용 API client 구조만 추가했습니다.

## 왜 읽기 전용부터 하나?

관리자 Preview/Apply, 저장, 복구 같은 기능은 요청 body와 Write Guard가 중요합니다.
이 기능을 Vue로 성급히 옮기면 기존 contract나 smoke 의미가 깨질 수 있습니다.
그래서 첫 API 연결 단계에서는 아래처럼 안전한 조회용 `GET` 경로만 준비합니다.

## 추가 위치

```txt
frontend/vue-app/src/api/
```

## 파일 역할

| 파일 | 역할 |
|---|---|
| `config.js` | API 기본 주소 관리 |
| `readOnlyRoutes.js` | Vue에서 참조할 읽기 전용 route 상수 |
| `readOnlyClient.js` | `fetch` 기반 GET 전용 client |
| `adminReadOnlyApi.js` | 관리자 조회 API wrapper |
| `gameReadOnlyApi.js` | 게임 조회 API wrapper |
| `index.js` | API export 모음 |

## 기본 API 주소

기본값:

```txt
http://127.0.0.1:8000/api/v1
```

v271에서는 `.env` 파일을 만들거나 수정하지 않았습니다.
나중에 실제 개발 환경별 주소 분리가 필요해지면 `VITE_API_BASE_URL` 도입을 별도 단계에서 검토합니다.

## v271에서 준비한 관리자 GET 경로

| 이름 | 경로 |
|---|---|
| requirements | `/admin/requirements` |
| overview | `/admin/overview` |
| saveSnapshots | `/admin/save-snapshots` |
| masterDomains | `/admin/master-data/domains` |
| masterCatalog | `/admin/master-data/catalog` |
| masterCreateBlueprint | `/admin/master-data/create-blueprint` |
| masterDetail | `/admin/master-data/detail` |
| masterRelations | `/admin/master-data/relations` |
| changeLogs | `/admin/change-logs` |
| changeLogDetail | `/admin/change-logs/{changeLogId}` |

## v271에서 준비한 게임 GET 경로

| 이름 | 경로 |
|---|---|
| masterData | `/game/master-data` |
| load | `/game/load` |
| saveSlots | `/game/save-slots` |

## v271에서 일부러 제외한 것

아래는 아직 Vue API client에 추가하지 않았습니다.

- `POST /game/save`
- 관리자 Preview 계열 POST
- 관리자 Apply 계열 POST
- Rollback Preview/Apply 계열 POST
- 생성 row 삭제/복원 Preview/Apply 계열 POST
- 인증 interceptor
- access token 처리
- Write Guard 처리
- `.env` 생성/수정

## 사용자가 확인해야 할 것

### Vue 의존성 설치

처음 한 번만 필요합니다.
이미 `frontend/vue-app/node_modules`가 있다면 다시 하지 않아도 됩니다.

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

### FastAPI 서버 실행

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

### Vue 개발 서버 실행

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

확인 주소:

```txt
http://127.0.0.1:5173/game
http://127.0.0.1:5173/admin
```

## 검증 명령

Vue API client 구조 검증:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
bash tools/run_smoke_vue_shell.sh
```

Vue build 검증:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run build
```

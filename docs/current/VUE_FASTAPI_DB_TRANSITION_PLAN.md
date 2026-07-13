# Vue/FastAPI/DB 전환 준비 계획 — v271

## 목적

기존 HTML/JS 기반 게임과 관리자 도구를 바로 갈아엎지 않고, 검증된 기능과 계약을 보존한 상태에서 Vue + FastAPI + PostgreSQL 구조로 점진 전환합니다.

v271의 핵심 결론:

- `frontend/vue-app/`에 Vite + Vue 기본 shell이 유지됩니다.
- v271에서 Vue 읽기 전용 API client 준비 구조를 추가했습니다.
- 기존 `admin.html`, `index.html`, 루트 `src/`는 그대로 유지했습니다.
- Vue shell은 route 목록을 보여주지만 아직 자동 API 호출은 하지 않습니다.
- Vue shell/API 검증은 기존 core smoke와 분리했습니다.
- DB/env/seed/인증/API route/response body/write 로직은 변경하지 않았습니다.

## 절대 원칙

1. 먼저 분석하고 문서화합니다.
2. 실제 파일 이동은 smoke 영향 범위를 확인한 뒤 진행합니다.
3. 기존 route path와 API response body는 유지합니다.
4. 기존 관리자 Preview/Apply 안전장치는 유지합니다.
5. Write Guard와 실제 write 로직은 사용자 승인 없이 변경하지 않습니다.
6. DB/env/seed/인증은 사용자 승인 없이 변경하지 않습니다.
7. 게임 콘텐츠 신규 개발은 전환 구조가 안정화된 뒤 진행합니다.

## 현재 legacy 기준

아래 파일/폴더는 Vue 전환 전까지 기준 동작과 검증 대상으로 유지합니다.

| 대상 | 현재 역할 | 당장 처리 |
|---|---|---|
| `index.html` | 실제 게임 화면 | 이동/삭제 금지 |
| `admin.html` | 관리자 운영/검증 화면 | 이동/삭제 금지 |
| `src/api/admin/*.js` | 관리자 기능별 브라우저 helper | 이동 금지, Vue 이식 후보로 분석 |
| `src/api/admin-page-readonly.js` | 관리자 메인 glue/helper | 이동 금지, Vue 분해 계획 필요 |
| `src/api/game-api-client.js` | API client | Vue API client 설계 참고 |
| `src/data/` | 현재 게임 데이터 | DB seed 기준 자료로 보존 |
| `src/rules/` | 게임 규칙 | 콘텐츠 개발 보류, 나중에 domain module로 보존/이식 |
| `src/state/` | legacy 게임 상태 | Vue store 후보 |
| `src/systems/` | 전투/아이템/스탯 시스템 | Vue와 독립적인 domain module 후보 |
| `src/ui/` | legacy DOM 렌더링 | Vue component로 대체 후보 |
| `src/styles/` | legacy CSS | 점진 분해 후보 |

## v270 Vue shell

생성 위치:

```txt
frontend/vue-app/
```

생성한 주요 파일:

```txt
frontend/vue-app/
├── package.json
├── index.html
├── vite.config.js
├── README.md
└── src/
    ├── main.js
    ├── App.vue
    ├── router/index.js
    ├── pages/AdminShell.vue
    ├── pages/GameShell.vue
    ├── components/ShellCard.vue
    └── styles/base.css
```

현재 route:

| Vue route | 의미 |
|---|---|
| `/` | `/game`으로 이동 |
| `/game` | 게임 Vue 이식 준비 shell |
| `/admin` | 관리자 Vue 이식 준비 shell |


## v271 Vue read-only API client

추가 위치:

```txt
frontend/vue-app/src/api/
```

추가한 파일:

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

원칙:

- `GET` 요청만 준비합니다.
- Preview/Apply/write 계열 `POST`는 아직 연결하지 않습니다.
- 인증 interceptor는 아직 만들지 않습니다.
- `.env` 파일은 만들거나 수정하지 않았습니다.
- 기본 API 주소는 `http://127.0.0.1:8000/api/v1`입니다.

자세한 내용은 `docs/current/VUE_READONLY_API_CLIENT.md`를 기준으로 봅니다.

## 사용자가 설치해야 하는 것

Vue 앱은 Node 패키지가 필요합니다.
ZIP에는 `node_modules`를 넣지 않습니다.

처음 한 번 설치:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm install
```

개발 서버 실행:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run dev
```

브라우저 확인:

```txt
http://127.0.0.1:5173
```

빌드 확인:

실행 위치: `frontend/vue-app` 폴더  
`.venv` 상태: 꺼져 있어도 됨 / 켤 필요 없음

```bash
npm run build
```

## v271 검증 명령

Vue shell/API 구조 검사:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
bash tools/run_smoke_vue_shell.sh
```

기존 legacy/core smoke:

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

## 다음 단계 로드맵

### Phase 0 — 현재 legacy 고정

완료/유지:

- `admin.html`
- `index.html`
- 루트 `src/`
- 기존 FastAPI route path
- 기존 smoke/contract 의미

### Phase 1 — 구조/경로 의존성 문서화

완료:

- v268 프로젝트 구조 문서화
- v269 legacy 경로 의존성 자동 목록화
- v270 Vue shell 위치 고정
- v271 Vue 읽기 전용 API client 구조 추가

### Phase 2 — Vue shell 생성

v270 완료:

- Vite + Vue shell 생성
- Vue Router 기본 구조 생성
- AdminShell/GameShell 생성
- legacy와 Vue 검증 분리

### Phase 3 — Vue API client/interceptor 설계

v271에서 시작했습니다.

완료:

- 읽기 전용 GET route 상수 추가
- GET 전용 `requestReadOnly` client 추가
- 관리자/게임 읽기 전용 API wrapper 추가
- Vue API client smoke 추가

주의:

- 아직 인증을 넣지 않습니다.
- 기존 route path와 response body를 그대로 사용해야 합니다.
- Preview/Apply/write 요청 body는 아직 건드리지 않습니다.
- 다음 단계에서 실제 화면 호출을 하더라도 먼저 GET API만 사용합니다.

### Phase 4 — 관리자 페이지 Vue 이식 계획

순서:

1. AdminShell 안에 읽기 전용 카탈로그 자리만 만듭니다.
2. 기존 `admin.html`은 계속 유지합니다.
3. Preview 기능은 요청 body/response body 계약 확인 후 이식합니다.
4. Apply/write 관련 기능은 가장 마지막에 이식합니다.

### Phase 5 — 게임 화면 Vue 이식 계획

순서:

1. GameShell 안에 HUD/layout 자리만 만듭니다.
2. 기존 `index.html`은 계속 유지합니다.
3. `src/systems/`는 Vue와 독립적인 domain module 후보로 분리 계획을 세웁니다.
4. 게임 콘텐츠 추가는 계속 보류합니다.

### Phase 6 — PostgreSQL/Alembic 준비

아직 실제 DB 구조 변경은 하지 않습니다.

준비할 것:

- migration 전략
- seed와 운영 데이터 분리
- rollback snapshot 정책
- transaction 정책

### Phase 7 — 인증 설계

아직 실제 인증 구현은 하지 않습니다.

준비할 것:

- 일반 사용자/관리자 권한
- 토큰 저장 방식
- FastAPI dependency
- Vue route guard
- 기존 Write Guard와의 관계

## v271에서 하지 않은 것

- DB 구조 변경 없음
- env 변경 없음
- seed 변경 없음
- 인증 변경 없음
- 기존 API route path 변경 없음
- 기존 API response body 변경 없음
- 실제 write 로직 변경 없음
- Write Guard 변경 없음
- 관리자 Preview/Apply 요청 body 변경 없음
- 게임 콘텐츠 개발 없음

# Project Structure — v270

현재 ZIP 기준 프로젝트 구조 점검 문서입니다.

v270에서는 기존 legacy 화면을 건드리지 않고 새 Vue 기본 shell만 `frontend/vue-app/`에 추가했습니다.

중요한 결론:

- 루트 `admin.html`, `index.html`, `src/`는 그대로 유지합니다.
- 루트 `src/`는 Vue 폴더가 아니라 legacy JS/CSS 폴더입니다.
- 새 Vue 앱은 `frontend/vue-app/`에 분리했습니다.
- DB/env/seed/인증/API 응답 body/route/write 로직은 변경하지 않았습니다.
- 기존 smoke/contract 의미는 변경하지 않았습니다.

## 최상위 구조

```txt
.
├── index.html
├── admin.html
├── README.md
├── README_BACKEND_READY.md
├── NEXT_CHAT_HANDOFF.md
├── NEXT_CHAT_PROMPT.md
├── docker-compose.yml
├── backend/
├── docs/
├── frontend/
│   └── vue-app/
├── src/
└── tools/
```

## 루트 파일 역할

| 경로 | 현재 역할 | v270 판단 |
|---|---|---|
| `index.html` | 현재 실제 게임 화면 진입점 | Vue 이식 전까지 legacy 기준 화면으로 유지 |
| `admin.html` | 현재 관리자 페이지 진입점 | Vue 관리자 이식 전까지 운영/검증 도구로 유지 |
| `src/` | legacy JS/CSS | 이동 금지, Vue 앱 `src/`와 구분 |
| `frontend/vue-app/` | 새 Vue 기본 shell | v270에서 추가, 아직 실제 로직 연결 없음 |
| `backend/` | FastAPI 백엔드 | 기존 route/body/DB/env/seed 유지 |
| `tools/` | smoke/contract/검증 도구 | 기존 core smoke 유지, Vue shell 별도 smoke 추가 |
| `docs/` | 현재 상태/전환 계획/인수인계 문서 | v270 기준 갱신 |

## `frontend/vue-app/` 역할

v270에서 새로 추가한 Vue/Vite 기본 앱입니다.

```txt
frontend/vue-app/
├── package.json
├── index.html
├── vite.config.js
├── README.md
└── src/
    ├── App.vue
    ├── main.js
    ├── api/
    │   └── README.md
    ├── app/
    │   └── README.md
    ├── components/
    │   └── ShellCard.vue
    ├── pages/
    │   ├── AdminShell.vue
    │   └── GameShell.vue
    ├── router/
    │   └── index.js
    ├── stores/
    │   └── README.md
    └── styles/
        └── base.css
```

현재 Vue route:

| Vue 경로 | 화면 | legacy 기준 |
|---|---|---|
| `/` | `/game`으로 redirect | 실제 게임은 아직 `index.html` |
| `/game` | `GameShell.vue` | 나중에 게임 UI 이식 |
| `/admin` | `AdminShell.vue` | 나중에 관리자 UI 이식 |

v270 Vue shell은 실제 관리자 API나 게임 로직을 호출하지 않습니다.

## `backend/` 역할

FastAPI 백엔드입니다.

현재 역할:

- master-data API
- save snapshot API
- admin read/write API
- create/delete/restore/rollback 제한 API
- PostgreSQL/Alembic 도입 준비 파일 보유
- 관리자 contract/readiness 검증 대상

주요 구조:

```txt
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── router.py
│   │   └── routes/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   └── services/
├── scripts/
├── seeds/
├── sql/
├── alembic/
├── alembic.ini
├── pyproject.toml
└── README.md
```

관리자 route/service 구조는 기존과 동일합니다.

## `src/` 역할

현재 `src/`는 Vue 앱 폴더가 아닙니다. 브라우저에서 `admin.html`과 `index.html`이 직접 읽는 legacy JS/CSS 모듈입니다.

```txt
src/
├── api/
├── app/
├── data/
├── rules/
├── state/
├── styles/
├── systems/
├── ui/
└── utils/
```

| 경로 | 현재 역할 | Vue 전환 판단 |
|---|---|---|
| `src/api/game-api-client.js` | legacy 화면과 관리자 화면의 API client | Vue API client 설계 시 참고/이식 후보 |
| `src/api/admin-page-readonly.js` | 관리자 페이지 메인 glue/helper | Vue 관리자 이식 시 가장 큰 분해 대상 |
| `src/api/admin/*.js` | 관리자 기능별 helper | Vue composable/store/service로 이식 후보 |
| `src/api/master-data-*.js` | master-data 로딩/검증/전환 | Vue 전환 초기에도 보존 필요 |
| `src/api/save-data-*.js` | save data bridge/slot/integrity | 인증/DB 전환 전까지 보존 필요 |
| `src/data/*.js` | 현재 게임 데이터/부트스트랩 데이터 | DB seed와 Vue data adapter의 기준 자료 |
| `src/rules/*.js` | 드랍/표시/장비 규칙 | 게임 콘텐츠 개발 보류, 전환 후 이식 |
| `src/state/game-state.js` | legacy 게임 상태 | Vue store 전환 후보 |
| `src/systems/*.js` | 전투/아이템/스탯/action result 로직 | Vue와 독립적인 domain module로 분리 후보 |
| `src/ui/render-ui.js` | legacy DOM 렌더링 | Vue component로 대체 후보 |
| `src/styles/style.css` | 현재 게임 CSS | Vue 전환 시 legacy CSS 보존 후 점진 분해 |

## `tools/` 역할

smoke test와 계약 점검 스크립트 폴더입니다.

```txt
tools/
├── run_smoke_core.sh
├── run_smoke_all.sh
├── run_smoke_vue_shell.sh
├── check_backend_ready.py
├── report_legacy_path_dependencies.py
├── contracts/
└── smoke/
```

기존 core smoke:

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

Python compile 검사:

실행 위치: 프로젝트 루트

```bash
python -m compileall -q backend/app backend/scripts tools
```

legacy 경로 의존성 보고서 검사:

실행 위치: 프로젝트 루트

```bash
python tools/report_legacy_path_dependencies.py --check
```

Vue shell 구조 검사:

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_vue_shell.sh
```

## v270 설치/확인 필요 사항

이번 ZIP에는 `node_modules`를 포함하지 않습니다.
Vue 앱을 직접 실행하려면 사용자가 한 번 설치해야 합니다.

실행 위치: `frontend/vue-app` 폴더

```bash
npm install
```

개발 서버 실행:

실행 위치: `frontend/vue-app` 폴더

```bash
npm run dev
```

브라우저 확인 주소:

```txt
http://127.0.0.1:5173
```

## v270 보존/변경 요약

변경함:

- `frontend/vue-app/` 추가
- Vue shell 구조 smoke 추가
- 문서 갱신

변경하지 않음:

- DB 구조
- env
- seed
- 인증
- 기존 route path
- 기존 API 응답 body
- 기존 write 로직
- Write Guard
- 관리자 Preview/Apply 요청 body
- 기존 smoke/contract 의미

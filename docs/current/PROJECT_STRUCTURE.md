# Project Structure — v269

현재 ZIP 기준 프로젝트 구조 점검 문서입니다.

v269에서는 실제 파일 대이동을 하지 않았습니다. 이유는 `admin.html`, `index.html`, `src/`, `backend/`, `tools/` 경로가 기존 smoke/contract에 많이 연결되어 있기 때문입니다.

이번 단계에서는 legacy 경로 의존성을 자동으로 목록화하는 도구를 추가했고, 새 Vue 앱 위치를 `frontend/vue-app/`로 결정했습니다.

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
├── src/
└── tools/
```

아직 `frontend/vue-app/`는 만들지 않았습니다. 다음 v270에서 사용자 승인 후 생성하는 것이 안전합니다.

## 루트 파일 역할

| 경로 | 현재 역할 | v269 판단 |
|---|---|---|
| `index.html` | 현재 실제 게임 화면 진입점 | Vue 이식 전까지 legacy 기준 화면으로 유지 |
| `admin.html` | 현재 관리자 페이지 진입점 | Vue 관리자 이식 전까지 운영/검증 도구로 유지 |
| `README.md` | 최신 상태 요약 | v269 기준으로 갱신 대상 |
| `README_BACKEND_READY.md` | 백엔드 readiness 요약 | 현상 유지 |
| `NEXT_CHAT_HANDOFF.md` | 다음 채팅 인수인계 | v269 완료 후 갱신 대상 |
| `NEXT_CHAT_PROMPT.md` | 다음 채팅 시작 프롬프트 | v269 완료 후 갱신 대상 |
| `docker-compose.yml` | 로컬 PostgreSQL/Adminer 실행 설정 | DB 실제 도입 전까지 현상 유지 |

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

### `backend/app/api/routes/`

관리자 route는 기능별 파일로 분리되어 있습니다.

| 파일 | 역할 |
|---|---|
| `admin.py` | 관리자 router facade |
| `admin_overview_snapshot_routes.py` | requirements/overview/save-snapshots/change-preview 계열 |
| `admin_master_data_routes.py` | master-data catalog/detail/create/edit/relation 계열 |
| `admin_change_log_routes.py` | change-logs/rollback/create-delete/restore 계열 |
| `admin_*_contract.py` | route/request/response/schema/write safety 계약 검증용 route |
| `game.py` | 게임 API 초안 |
| `health.py` | health check |

### `backend/app/services/`

`AdminService`는 facade이고 실제 기능은 `backend/app/services/admin/` 하위 service로 분리되어 있습니다.

| 경로 | 역할 |
|---|---|
| `admin_service.py` | facade |
| `admin_service_split_contract.py` | backend split readiness contract |
| `admin/admin_config.py` | 관리자 설정/카탈로그 설정 |
| `admin/admin_shared_utils.py` | 공통 유틸 |
| `admin/admin_readiness_service.py` | readiness 계산 |
| `admin/admin_overview_snapshots_service.py` | overview/save snapshot 계열 |
| `admin/admin_master_catalog_service.py` | master catalog/detail 계열 |
| `admin/admin_create_lifecycle_service.py` | create/delete/restore 계열 |
| `admin/admin_change_log_service.py` | change log/rollback 계열 |
| `admin/admin_edit_draft_service.py` | edit draft/preview 계열 |
| `admin/admin_diff_engine.py` | 공통 diff 계산 |
| `admin/admin_rollback_snapshot.py` | 공통 rollback snapshot |
| `admin/admin_preview_enrichment.py` | preview 응답 보강 |

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
├── check_backend_ready.py
├── report_legacy_path_dependencies.py
├── contracts/
└── smoke/
```

현재 가장 중요한 검증 명령:

실행 위치: 프로젝트 루트

```bash
bash tools/run_smoke_core.sh
```

실행 위치: 프로젝트 루트

```bash
python -m compileall -q backend/app backend/scripts tools
```

legacy 경로 의존성 보고서 검사:

실행 위치: 프로젝트 루트

```bash
python tools/report_legacy_path_dependencies.py --check
```

## `docs/` 역할

```txt
docs/
├── current/
├── handoff/
├── contracts/
├── archive/
└── *.md
```

| 경로 | 역할 | v269 판단 |
|---|---|---|
| `docs/current/` | 현재 기준 문서 | 앞으로 우선 갱신할 canonical 문서 |
| `docs/current/LEGACY_PATH_DEPENDENCIES.md` | legacy 경로 자동 분석 보고서 | Vue 전환 전 필수 참고 문서 |
| `docs/handoff/` | 다음 채팅 인수인계 복사본 | 루트 handoff 문서와 함께 유지 |
| `docs/contracts/` | admin contract registry 문서/JSON | contract 추가 시 동기화 대상 |
| `docs/archive/stage-notes/` | 과거 단계 문서 | 실제 이동은 smoke 영향 확인 후 진행 |
| `docs/*.md` | 단계별 기록 문서 | 당장 삭제/이동하지 않고 archive 계획만 먼저 작성 |

## v269 자동 분석 결과 요약

자세한 내용은 `docs/current/LEGACY_PATH_DEPENDENCIES.md`를 봅니다.

핵심 결론:

- `admin.html`은 관리자 smoke와 문서가 많이 참조하므로 이동 금지입니다.
- `index.html`은 게임 smoke와 HTML 직접 로드 관계가 있으므로 이동 금지입니다.
- 기존 `src/`는 Vue 앱용 `src/`가 아니라 legacy JS/CSS 루트입니다.
- `backend/app/api/routes/`와 `backend/app/services/`는 backend contract가 직접 확인하므로 이동 금지입니다.
- `tools/run_smoke_core.sh`와 `tools/smoke/`는 검증 기준이므로 유지합니다.

## Vue 앱 생성 위치 결정

새 Vue 앱은 다음 위치가 안전합니다.

```txt
frontend/vue-app/
```

아직 생성하지 않았습니다.

이 위치를 선택한 이유:

- 기존 root `src/`와 Vue app `src/` 충돌 방지
- 기존 legacy smoke 유지
- 기존 `admin.html`/`index.html` 유지
- 추후 Vue shell 검증과 legacy smoke 분리 가능

## Vue 전환 시 보존/이식/대체 후보

### 반드시 보존

- `admin.html`
- `index.html`
- `src/` 전체 legacy 동작
- `backend/app/api/routes/` 기존 route path
- `backend/app/services/` 기존 service 의미
- `backend/seeds/` 현재 seed 자료
- `tools/run_smoke_core.sh`
- 기존 smoke/contract 의미

### Vue로 이식할 후보

- `src/api/admin/*.js` → Vue admin composable/service/store 후보
- `src/api/game-api-client.js` → Vue API client/interceptor 설계 참고
- `src/state/game-state.js` → Pinia 또는 별도 store 후보
- `src/ui/render-ui.js` → Vue component 후보
- `src/styles/style.css` → page/component CSS로 점진 분해 후보

### 나중에 대체할 후보

- `admin.html` → Vue 관리자 라우트로 대체
- `index.html` → Vue 게임 라우트로 대체
- legacy DOM 직접 조작 함수 → Vue component/state 기반 구조로 대체

## 다음 구조 변경 전 체크리스트

1. `python tools/report_legacy_path_dependencies.py --check`를 통과시킵니다.
2. `admin.html` script 경로를 바꾸지 않고 Vue shell을 새로 만들 수 있는지 확인합니다.
3. `index.html`을 이동하지 않고 Vue 앱을 별도 폴더에 만들 수 있는지 확인합니다.
4. route path/API response body는 변경하지 않습니다.
5. 새 Contract가 필요하면 실제 실행 결과를 먼저 수집합니다.
6. core smoke가 끝까지 통과하기 전 ZIP을 만들지 않습니다.

## ZIP 포함/제외 원칙

포함:

- 전체 프로젝트 소스
- `backend/`
- `src/`
- `docs/`
- `tools/`
- `.env.example`

제외:

- `.env`
- `.git`
- `.venv`
- `node_modules`
- `__pycache__`
- `.pyc`
- 임시 로그/캐시
- 이전 채팅 작업용 `/mnt/data/rpg_v*_work` 폴더

# Project Structure — v306

현재 ZIP 기준 프로젝트 구조 점검 문서입니다.

v306에서는 완료된 baseline을 유지한 채 새 revision이 필요한지 읽기 전용으로 판단하는 preflight를 추가했습니다. single Alembic graph, 승인 model/env source hash, canonical schema differences, Alembic candidate operation, PostgreSQL sequence ownership을 함께 확인하며 revision/autogenerate/upgrade/downgrade는 계속 차단합니다.

중요한 결론:

- 루트 `admin.html`, `index.html`, `src/`는 그대로 유지합니다.
- 루트 `src/`는 Vue 폴더가 아니라 legacy JS/CSS 폴더입니다.
- 새 Vue 앱은 `frontend/vue-app/`에 분리되어 있습니다.
- Vue API client는 아직 `GET` 조회용 준비 단계입니다.
- DB/env/seed/인증/API 응답 body/route/write 로직은 변경하지 않았습니다.
- 기존 smoke/contract 의미는 변경하지 않았습니다.
- `docs/current/BACKEND_STRUCTURE_PLAN.md`가 backend route/service/schema/model/db/core 유지 범위를 설명하고, `docs/current/BACKEND_ROUTE_MAP.md`가 실제 FastAPI route 27개를 정리합니다.

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

| 경로 | 현재 역할 | v275 판단 |
|---|---|---|
| `index.html` | 현재 실제 게임 화면 진입점 | Vue 이식 전까지 legacy 기준 화면으로 유지 |
| `admin.html` | 현재 관리자 페이지 진입점 | Vue 관리자 이식 전까지 운영/검증 도구로 유지 |
| `src/` | legacy JS/CSS | 이동 금지, Vue 앱 `src/`와 구분 |
| `frontend/vue-app/` | 새 Vue shell + 읽기 전용 API client 준비 | 실제 기능 대체 전 단계 |
| `backend/` | FastAPI 백엔드 | 기존 route/body/DB/env/seed 유지 |
| `tools/` | smoke/contract/검증/backup/restore/migration 도구 | v306 next-revision read-only preflight와 회귀 smoke 보강 |
| `docs/` | 현재 상태/전환 계획/DB 준비/인수인계 문서 | v306 기준 갱신 |


## v306 PostgreSQL next revision read-only preflight

추가 위치:

```txt
tools/check_postgres_next_revision_preflight.py
tools/smoke/backend/smoke_postgres_next_revision_preflight.py
docs/current/POSTGRES_NEXT_REVISION_PREFLIGHT.md
docs/current/POSTGRES_NEXT_REVISION_READONLY_PLAN.md
```

고정 경계:

- v305 completion state `postgres-baseline-completion-state-verified` 필요
- Alembic graph는 `v295_initial_schema` single base/single head만 허용
- 승인 model/env source snapshot 13개 파일 SHA-256 고정
- canonical schema는 22/22 tables, differences=0 필요
- Alembic metadata 비교는 PostgreSQL read-only transaction과 SQL write guard 안에서만 수행
- type/server default/nullable/index/constraint 후보와 sequence ownership 확인
- candidate operation 0개면 새 revision을 만들지 않음
- 후보가 있으면 별도 schema-change intent review에서 정지
- revision/autogenerate/upgrade/downgrade/stamp는 실행하지 않음

## `frontend/vue-app/` 역할

v270에서 만든 Vue/Vite shell에, v272에서 읽기 전용 API client 준비 구조를 추가했고, v275에서 backend route map 기준 query 이름을 점검했습니다.

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
    │   ├── README.md
    │   ├── adminReadOnlyApi.js
    │   ├── config.js
    │   ├── gameReadOnlyApi.js
    │   ├── index.js
    │   ├── readOnlyClient.js
    │   └── readOnlyRoutes.js
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

v272 Vue shell은 안전한 read-only API 상태 확인을 실제로 호출합니다. v273에서는 이 호출이 로컬 CORS에 막히지 않도록 FastAPI local/debug CORS 기본값을 보강했습니다.

## v275 Vue API client/CORS/route map 준비 범위

추가 위치:

```txt
frontend/vue-app/src/api/
```

| 파일 | 역할 |
|---|---|
| `config.js` | API 기본 주소 관리. 기본값은 `http://127.0.0.1:8000/api/v1` |
| `readOnlyRoutes.js` | 읽기 전용 route 상수 목록 |
| `readOnlyClient.js` | `fetch` 기반 GET 전용 요청 함수 |
| `adminReadOnlyApi.js` | 관리자 읽기 전용 API 함수 묶음 |
| `gameReadOnlyApi.js` | 게임 읽기 전용 API 함수 묶음 |
| `index.js` | API layer export 모음 |

아직 추가하지 않은 것:

- 인증 interceptor
- token 저장/갱신
- Preview/Apply/write API wrapper
- `.env` 생성/수정

## v275 backend route map

추가 위치:

```txt
tools/report_backend_route_map.py
tools/smoke/backend/smoke_backend_route_map_report.py
docs/current/BACKEND_ROUTE_MAP.md
```

요약:

| 구분 | 수 |
|---|---:|
| 전체 route | 27 |
| GET | 15 |
| POST | 12 |
| admin group | 21 |
| game group | 4 |
| health group | 2 |

현재 Vue 자동 smoke 화면에 연결된 route는 `GET /api/v1/health`, `GET /api/v1/admin/requirements`입니다. 다음 후보는 `GET /api/v1/admin/master-data/domains`입니다. Preview/Apply/write route는 계속 보류합니다.


## v274 backend 구조 계획

추가된 문서/도구:

```txt
tools/report_backend_structure_plan.py
tools/smoke/backend/smoke_backend_structure_plan.py
docs/current/BACKEND_STRUCTURE_PLAN.md
```

현재 결론:

- `backend/app/api/routes/`는 route path/contract 보호 대상으로 유지합니다.
- `backend/app/services/admin_service.py` facade는 유지합니다.
- `backend/app/services/admin/`은 이미 분리된 service 후보지만 당장 이동하지 않습니다.
- `backend/app/schemas/`, `backend/app/models/`, `backend/app/db/`는 DB/Alembic 실제 전환 전까지 구조 변경하지 않습니다.
- Vue에서는 당분간 안전한 `GET` read-only API만 연결합니다.
- Preview/Apply/write API는 인증/권한/Write Guard 설계 전까지 Vue에서 확장하지 않습니다.


## v282~v284 PostgreSQL/Alembic 준비 도구

추가 위치:

```txt
tools/report_postgres_alembic_readiness.py
tools/check_postgres_alembic_prerequisites.py
tools/check_alembic_readonly_state.py
tools/smoke/backend/smoke_postgres_alembic_readiness.py
tools/smoke/backend/smoke_backend_alembic_async_env.py
docs/current/POSTGRES_ALEMBIC_READINESS.md
docs/current/POSTGRES_ALEMBIC_LOCAL_CHECKLIST.md
```

이 도구들은 DB 연결, `.env` 변경, migration 생성/적용을 하지 않습니다. 현재 파일과 로컬 설치 상태만 읽기 전용으로 확인합니다.

## `backend/` 역할

FastAPI 백엔드입니다.

현재 역할:

- master-data API
- save snapshot API
- admin read/write API
- create/delete/restore/rollback 제한 API
- PostgreSQL/Alembic 도입 준비 파일 보유
- 관리자 contract/readiness 검증 대상

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

legacy 경로 의존성 보고서 검사:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
python tools/report_legacy_path_dependencies.py --check
```

Vue shell/API 구조 검사:

실행 위치: 프로젝트 루트  
`.venv` 상태: 켜진 상태 권장

```bash
bash tools/run_smoke_vue_shell.sh
```

## v273 설치/확인 필요 사항

v273에서 새 라이브러리는 추가하지 않았습니다.

단, Vue 앱을 처음 실행한다면 `node_modules`가 ZIP에 없기 때문에 한 번 설치해야 합니다.

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

브라우저 확인 주소:

```txt
http://127.0.0.1:5173
```

## v273 보존/변경 요약

변경함:

- Vue 읽기 전용 API client 준비 구조 추가
- Vue shell에 읽기 전용 route 목록 표시
- Vue API client smoke 추가
- Vue 개발 서버 local CORS 오류 수정
- backend local CORS smoke 추가
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

## v289 전달/폴더 정리

- `backend/idle_rpg_backend.egg-info/`는 editable install이 만드는 생성 산출물이므로 제거하고 `*.egg-info/`를 ignore합니다.
- 중복된 `backend/env.example`은 제거하고 `backend/.env.example`만 유지합니다.
- 오래된 루트 `tools/smoke_next_chat_handoff.py`는 제거하고 `tools/smoke/game/smoke_next_chat_handoff.py`를 canonical 경로로 사용합니다.
- 전달 ZIP에는 `.git`, `backend/.venv`, `backend/.env`, `node_modules`, `dist`, Python cache를 포함하지 않습니다.

## v290 PostgreSQL backup/restore preflight 구조

```txt
tools/check_postgres_backup_restore_preflight.py
tools/smoke/backend/smoke_postgres_backup_restore_preflight.py
docs/current/POSTGRES_BACKUP_RESTORE_PREP.md
local-backups/postgres/  # 실제 backup 생성 전에는 존재하지 않을 수 있으며 Git/ZIP 제외
```

- preflight 도구는 schema equivalence gate와 PostgreSQL client 버전만 확인합니다.
- 실제 `pg_dump`, `pg_restore`, `createdb`, `dropdb` 동작은 실행하지 않습니다.
- source `rpg_game`, restore rehearsal `rpg_game_restore_rehearsal_v290`, migration test `rpg_game_migration_empty_v290` 경계를 고정합니다.
- `/local-backups/`는 민감 데이터 보호를 위해 `.gitignore`와 `.dockerignore`에서 제외합니다.


## v291 PostgreSQL backup 생성 도구

추가 위치:

```txt
tools/create_postgres_backup.py
tools/smoke/backend/smoke_postgres_backup_creation.py
docs/current/POSTGRES_BACKUP_CREATION.md
```

- source DB `rpg_game` 읽기 전용 dump만 수행합니다.
- `.partial` 생성 후 `pg_restore --list` 검증 성공 시에만 정식 dump로 확정합니다.
- SHA-256, TOC, source row-count snapshot, manifest를 함께 생성합니다.
- restore/createdb/dropdb/Alembic mutation은 포함하지 않습니다.
- 산출물은 `local-backups/`에만 남고 Git/ZIP에서 제외됩니다.

## v292 PostgreSQL restore rehearsal DB 생성 도구

```txt
tools/create_postgres_restore_rehearsal_database.py
tools/smoke/backend/smoke_postgres_restore_rehearsal_database_creation.py
docs/current/POSTGRES_RESTORE_REHEARSAL_DB_CREATION.md
```

이 도구는 verified backup의 SHA-256과 source 22 tables / 748 rows 상태를 재확인하고, target `rpg_game_restore_rehearsal_v290`이 없을 때만 빈 DB를 생성합니다. `pg_restore`, `dropdb`, `.env`, Docker resource, Alembic 작업은 포함하지 않습니다.


## v293 PostgreSQL restore rehearsal 도구

```txt
tools/restore_postgres_rehearsal_database.py
tools/smoke/backend/smoke_postgres_restore_rehearsal.py
docs/current/POSTGRES_RESTORE_REHEARSAL.md
```

- exact backup과 SHA-256/source snapshot을 다시 검증합니다.
- 이미 생성된 빈 `rpg_game_restore_rehearsal_v290`에만 restore합니다.
- `--single-transaction`으로 부분 restore commit을 방지합니다.
- restore 후 22 tables / 748 rows / table별 counts / schema differences=0을 확인합니다.
- source 변경, target create/drop/clean, Docker/.env/Alembic 작업은 하지 않습니다.


## v295 Alembic revision 준비 범위

추가 위치:

```txt
backend/alembic/script.py.mako
tools/create_postgres_initial_alembic_revision.py
tools/smoke/backend/smoke_postgres_initial_alembic_revision_creation.py
docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_CREATION.md
```

- revision target은 `rpg_game_migration_empty_v290`으로 고정합니다.
- `.env`를 수정하지 않고 child process 환경변수만 사용합니다.
- generated revision과 schema-only review bundle만 생성합니다.
- `local-review-artifacts/`는 Git/Docker/전달 ZIP에서 제외합니다.
- upgrade/downgrade/stamp와 DB create/drop/restore는 실행하지 않습니다.

## v297 op.f parser recovery 범위

`tools/create_postgres_initial_alembic_revision.py`는 migration workspace에 정확히 빈 `alembic_version` 테이블 하나만 있을 때 재시도를 허용합니다. 별도 DB 삭제·table drop·revision 적용은 하지 않습니다.

## v298 manual review / isolated upgrade 범위

- `backend/alembic/versions/v295_initial_schema_initial_postgresql_schema.py`: exact reviewed revision, SHA-256 고정
- `docs/current/review/v295_initial_schema.manual-review.json`: machine-readable 수동 검토 증거
- `docs/current/POSTGRES_INITIAL_ALEMBIC_REVISION_MANUAL_REVIEW.md`: 사람이 읽는 검토 결론
- `tools/upgrade_postgres_migration_test_database.py`: `rpg_game_migration_empty_v290`에만 `upgrade head` 허용
- `tools/smoke/backend/smoke_postgres_initial_alembic_revision_manual_review.py`: 모델/revision 전체 구조 교차 검증
- `tools/smoke/backend/smoke_postgres_migration_test_database_upgrade.py`: target/command/postcondition 경계 검증

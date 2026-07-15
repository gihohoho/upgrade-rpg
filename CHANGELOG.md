# v312.production-managed-postgres-reverse-proxy-config-render-ready

- 기호 승인에 따라 운영 기본 방향을 관리형 PostgreSQL + provider CA verify-full + 외부 reverse proxy HTTPS + backend 1 replica/1 worker로 확정.
- production Compose에서 bundled PostgreSQL, Adminer, named DB volume, host ports, build를 제거하고 backend-only exact-digest image template로 전환.
- `production-architecture-selection.example.json`, reverse proxy 경계 문서, v312 selection checker 추가.
- 실제 `.env`/secret을 읽지 않고 정확히 `docker compose config`만 호출하는 confirmation-gated wrapper 추가.
- Docker CLI가 없는 handoff 환경에서는 실제 config를 실행하지 않았고, fake Docker smoke로 config 외 명령 미호출과 임시 review 파일 정리를 검증.
- image pull/build, container/network/volume mutation, managed DB 연결, Alembic/DB mutation은 계속 미승인.

# v311.production-capacity-tls-network-isolated-plan

- Added a review-only production capacity input and a read-only fail-closed checker.
- Calculated the current 1 replica × 1 worker SQLAlchemy steady/burst connections as 5/15.
- Added 10 non-application reserve connections and 20% safety margin, producing minimum 30 and review candidate 40.
- Added scale scenarios: 2 replicas require minimum 50; 2 replicas × 2 workers require minimum 90.
- Recorded managed PostgreSQL as the preferred review path and documented bundled PostgreSQL TLS requirements as an unapproved alternative.
- Documented reverse proxy HTTPS-only, backend/PostgreSQL internal-network, image digest approval, and isolated config/build/run/cleanup stages.
- Added dedicated smoke, core registration, synchronized current/handoff documents, and no Docker/DB/env/Alembic mutation.

# v310.production-secrets-tls-container-static-validation-preflight

- 운영 secret/TLS/container template 정적 checker와 smoke 추가
- production variable placeholder inventory 및 password/CA Compose secret 경계 추가
- backend container healthcheck 추가
- 실제 deployment env/secret 파일 Git·Docker context 제외
- 완료된 PostgreSQL baseline 문서를 archive로 이동해 docs/current 정리
- v309 사용자 PC strict + health 통과 상태를 handoff에 반영
- 실제 DB/.env/Docker/Alembic mutation 없음

# v309 - Runtime engine source-binding inspector fix

- Fixed a false positive where the readiness checker only recognized a single-line `create_async_engine(settings.database_url...)` call.
- Replaced the brittle string match with Python AST inspection of positional and `url=`/`database_url=` arguments.
- Added a dedicated multiline regression smoke and wired it into the core smoke runner.
- Kept FastAPI runtime, pool policy, DB, `.env`, Docker, Alembic history, API contracts, and game content unchanged.

# v308 - FastAPI/PostgreSQL runtime config hardening

- Recorded the user PC v307 `--strict --require-health` success with exact `rpg_game`, PostgreSQL 16.14, healthy Docker, and 12 production-hardening warnings.
- Added five environment-backed SQLAlchemy async pool options while preserving local defaults.
- Added FastAPI lifespan shutdown disposal with no startup migration or schema mutation.
- Added a fail-closed production settings guard for DEBUG and local/default or short JWT/admin secrets.
- Added a non-root FastAPI Dockerfile and a separate production Compose review template without Adminer or PostgreSQL host-port publication.
- Added a read-only v308 verifier, dedicated smoke, readiness/current/handoff documentation, and a new handoff ZIP.
- Did not edit the real `.env`, run Docker build/up/down, change DB schema/data, add revisions, alter API contracts, auth/write behavior, Vue, or game content.

# v307 - PostgreSQL/FastAPI deployment runtime readiness

- Added a read-only runtime readiness checker for exact `rpg_game`, `postgresql+asyncpg`, live revision, FastAPI startup mutation boundaries, Docker running/healthy state, env key inventory, and DB health contract.
- Added a production-hardening warning classification for pool policy, engine disposal lifecycle, local secrets, published Adminer/PostgreSQL ports, image digest, TLS, and FastAPI container image.
- Added a manual deployment migration runbook that keeps migrations out of server startup and requires backup, isolated rehearsal, and separate approval.
- Added dedicated v307 smoke, core registration, readiness/current/handoff documentation, and a new handoff ZIP.
- No `.env`, Docker container/volume, DB schema/data, Alembic revision/history, API route/body, auth, write logic, seed, Vue, or game content was changed.

# v306 - PostgreSQL next revision read-only preflight

- Recorded the user PC v305 completion result as `postgres-baseline-completion-state-verified`.
- Added a read-only next-revision preflight that verifies the single Alembic graph, approved model/env source hashes, canonical schema equivalence, Alembic metadata candidate operations, and PostgreSQL sequence ownership.
- Runs metadata comparison inside a PostgreSQL read-only transaction with an SQL statement guard; no revision file or Alembic mutation command is executed.
- Returns either no-new-revision-required or separate-schema-change-intent-review and never auto-approves autogenerate/upgrade/downgrade.
- Added dedicated smoke, core registration, readiness/current/handoff documentation, and v306 ZIP handoff.
- Did not change DB schema/data, `.env`, Docker resources, seed, auth, API routes/bodies, Write Guard, Vue write integration, or game content.

# v305 - PostgreSQL baseline completion state lock

- Confirmed the user PC v304 source post-check result: source 23/749, application 22/748, current `v295_initial_schema`, v304 execution report verified.
- Added `tools/check_postgres_baseline_completion_state.py`, a read-only completion checker for source/rehearsal/migration state, v302/v304 reports, application digests, and the exact single-revision set.
- Added a regression smoke that blocks legacy pre-stamp classification, missing reports, changed migration endpoint, and unapproved extra revisions.
- Updated current/readiness/handoff documents to `alembic-managed-baseline-complete`.
- Added a separate next-revision read-only plan; no revision generation, autogenerate, upgrade, downgrade, stamp retry, DB create/drop/restore, `.env`, seed, auth, API, or game-content change was performed.

# v304 - PostgreSQL source baseline stamp final guard

- Added an exact-source `rpg_game` baseline stamp guard with read-only pre/post inspection.
- Pinned revision, backup SHA-256, verified rehearsal result, and approved application schema/data digests.
- Added exact confirmation flags for the future source-only `stamp head` approval boundary.
- Added post-stamp recovery classification that prevents automatic retries after a partial report failure.
- Added dedicated source stamp smoke coverage and updated handoff/current-status documentation.
- Did not execute source stamp, upgrade, downgrade, DB create/drop/restore, `.env`, Docker, API/write, auth, seed, or game-content changes.

# v303 - Restore rehearsal stamp post-check recovery

- Recorded the user-approved v302 rehearsal-only `stamp head` execution.
- Identified the immediate v302 `--inspect` failure as a post-stamp inspector bug: it reused the pre-stamp 22-table validator and rejected the expected `alembic_version` table.
- Updated `--inspect` to recognize both pre-stamp and post-stamp states without running any mutation or subprocess.
- Pinned the actual user-confirmed pre-stamp application schema/data digests and require 22 application tables / 748 rows to remain identical after stamp.
- Independently revalidate source `rpg_game`, the verified v300 migration endpoint, exact revision/SHA-256, and the local v302 execution report when present.
- Added report-missing recovery classification without retrying stamp, rollback, upgrade, downgrade, DB create/drop/restore, or source mutation.
- Expanded dedicated smoke coverage for pre-stamp, post-stamp with verified report, and post-stamp report-missing states.
- Kept source stamp, API/write/auth/seed/game-content changes, `.env`, and Docker resources untouched.

# v302 - Restore rehearsal baseline stamp guard ready

- Recorded the user-PC v301 source preflight success.
- Added `tools/stamp_postgres_restore_rehearsal_database.py`, pinned to `rpg_game_restore_rehearsal_v290`, `v295_initial_schema`, and exact revision SHA-256.
- Added read-only full application schema and row-content SHA-256 signatures for all 22 tables / 748 rows.
- Added postconditions allowing only `alembic_version` 1 table / 1 row while requiring source and migration DB signatures to remain identical.
- Added exact `--confirm-target` and `--confirm-revision` execution confirmations; actual stamp was not executed.
- Added dedicated simulated smoke, core registration, current/handoff documentation, and v302 ZIP handoff.
- Kept DB schema/data, `.env`, Docker resources, seed, auth, API routes/bodies, Write Guard, Preview/Apply bodies, and game content unchanged.

## v300.postgres-migration-roundtrip-reupgrade-ready

- v298 first upgrade와 v299 downgrade report를 모두 요구하는 두 번째 `upgrade head` 왕복 검증 가드 추가
- 첫/두 번째 upgrade의 table list, row counts, revision, schema classification, differences exact signature 비교
- source/rehearsal DB 보존, no retry, no stamp/downgrade/create/drop/restore 경계 유지
- 전용 smoke, core 등록, readiness/current/handoff 문서 v300 동기화

## v299.postgres-migration-test-downgrade-base-ready

- 사용자 PC에서 v298 isolated `upgrade head` 성공 결과 반영
- exact reviewed revision과 v298 upgrade report를 요구하는 `downgrade base` 실행 가드 추가
- target DB가 빈 `alembic_version` placeholder로 복귀하는지 검증
- source/rehearsal DB 작업 전후 보존, 자동 retry/upgrade/stamp/create/drop/restore 차단
- 전용 smoke, core 등록, readiness/current/handoff 문서 v299 동기화

# Changelog

## v298.postgres-initial-alembic-manual-review-upgrade-ready

- 사용자 review bundle의 exact revision SHA-256과 bundle SHA-256을 재검증
- `v295_initial_schema`를 SQLAlchemy model과 수동 교차 검토: 22 tables / 209 columns / 42 indexes / 21 FK / 6 Unique
- 타입, 길이, nullable, PK/FK/ondelete/onupdate, unique, index, server default 일치 확인
- PostgreSQL FLOAT 2개가 v289 DOUBLE PRECISION alias 정책과 일치함을 확인
- downgrade index/table 대응과 FK dependency reverse order 검증
- 검토된 revision 파일과 machine-readable manual review manifest를 프로젝트 기준 파일로 포함
- `tools/upgrade_postgres_migration_test_database.py` 추가: exact reviewed revision을 `rpg_game_migration_empty_v290`에만 `upgrade head`하도록 준비
- 실제 upgrade/downgrade/stamp/source DB mutation은 실행하지 않음
- manual review/upgrade guard smoke, core 등록, v298 문서/handoff 동기화

## v297.postgres-initial-alembic-op-f-parser-recovery

- 사용자 실제 v296 결과 `unexpected Alembic operations: upgrade=['f'], downgrade=['f']`를 재현하고 원인을 확인
- Alembic generated revision의 nested `op.f(...)`를 naming helper로 분리해 operation allowlist false positive 제거
- 실제 create/drop/index/constraint operation 검사와 execute/data/destructive operation 차단 유지
- 전용 smoke가 `op.create_index(op.f(...))`, `op.drop_index(op.f(...))`를 생성하고 `f`가 operation count에 포함되지 않음을 검증
- 실패 시 생성 revision/review artifact 정리, empty `alembic_version` placeholder 재사용, DB/env/Alembic apply 경계 유지
- v297 current/readiness/handoff 문서 동기화

## v296.postgres-initial-alembic-revision-placeholder-recovery

- v295 autogenerate가 남긴 정확히 `alembic_version` 1 table / 0 rows / no revision 상태를 안전한 recovery workspace로 인정
- `--inspect-workspace` 읽기 전용 진단과 placeholder 재사용 경계 추가
- 다른 application table/row/revision이 있으면 실행 전 차단
- upgrade/downgrade/stamp, DB create/drop/restore 미실행

## v295.postgres-initial-alembic-revision-create-review-tool

- 실제 v294 empty migration test DB 생성 성공 결과를 현재 기준에 반영
- `backend/alembic/script.py.mako` 표준 revision 템플릿 추가
- `tools/create_postgres_initial_alembic_revision.py` 추가
- child process `DATABASE_URL`을 `rpg_game_migration_empty_v290`으로만 override하고 `.env`는 유지
- deterministic revision ID `v295_initial_schema`와 예상 파일명 고정
- 생성된 revision의 22 tables / 209 columns / nullable / PK / FK / unique / index 자동 검토
- upgrade destructive/data operations와 downgrade create/data operations 차단
- source/rehearsal/migration DB before/after 동일 확인
- schema-only local review JSON/bundle 생성, Git/Docker/전달 ZIP 제외
- Alembic upgrade/downgrade/stamp와 DB create/drop/restore는 실행하지 않음
- 전용 smoke, core smoke 등록, v295 문서/handoff 동기화

## v294.postgres-migration-empty-database-create-tool

- 실제 v293 restore rehearsal 성공 결과를 현재 기준에 반영
- `tools/create_postgres_migration_test_database.py` 추가
- exact backup/SHA-256, restore report, source/rehearsal live 상태를 생성 전 재검증
- `rpg_game_migration_empty_v290`이 없을 때만 `createdb` 1회 허용
- owner `rpg_user`, `template0`, source와 같은 locale metadata 적용
- 생성 후 0 tables / 0 rows / alembic_version 없음 확인
- source/rehearsal before/after 동일 확인
- pg_restore/dropdb/Alembic revision/upgrade/downgrade/stamp 차단
- 전용 smoke와 core smoke 등록, v294 문서/handoff 동기화

# v292 - PostgreSQL empty restore rehearsal database creation tool

- Added `tools/create_postgres_restore_rehearsal_database.py` for the user-approved existence-check-and-create-empty-DB boundary.
- Requires the verified v291 backup, recomputes SHA-256, rechecks the 22-table/748-row source baseline, and checks `pg_database` before any mutation.
- Creates only `rpg_game_restore_rehearsal_v290` when absent, with owner `rpg_user`, template `template0`, and source-compatible encoding/collation/locale metadata.
- Verifies the target has zero public tables and no `alembic_version`, then confirms the source remains 22 tables / 748 rows.
- Stops when the target already exists and never runs `pg_restore`, `dropdb`, `.env` edits, Docker changes, Alembic mutations, API/auth/write changes, or game-content changes.
- Added dedicated smoke coverage, core-smoke registration, current-state documentation, and v292 handoff synchronization.

# v291 - PostgreSQL backup creation and archive verification tool

- Added `tools/create_postgres_backup.py` for the user-approved source backup step only.
- Re-runs schema/preflight gates, pins `rpg_game`/`rpg_user`/`upgrade_rpg_postgres`, streams a custom-format dump to a private partial file, validates the archive with `pg_restore --list`, and publishes it only after validation.
- Adds SHA-256, TOC, source table/row snapshot, and manifest sidecars under ignored `local-backups/postgres/`.
- Refuses overwrite/collision and does not restore, create/drop databases, change Docker resources, edit `.env`, run Alembic mutations, or change API/auth/write/game content.
- Added a dedicated smoke and core-smoke registration; the handoff ZIP excludes all backup artifacts.

# v290 - PostgreSQL backup/restore read-only preflight gate

- Added `tools/check_postgres_backup_restore_preflight.py` to re-run the schema-equivalence gate, check host/existing-container `pg_dump`, `pg_restore`, `createdb`, and `dropdb` availability, and report whether the project is ready to request backup execution approval.
- Fixed the backup policy at `local-backups/postgres/` with KST timestamped PostgreSQL custom-format dump names and SHA-256 sidecars; added `/local-backups/` to Git/Docker exclusions.
- Fixed isolated database boundaries: source `rpg_game`, restore rehearsal `rpg_game_restore_rehearsal_v290`, and empty migration test `rpg_game_migration_empty_v290`.
- Added restore before/after table and row-count comparison planning, separate empty-DB Alembic validation planning, a dedicated smoke, and core-smoke registration.
- The handoff sandbox could not connect because `psycopg` and PostgreSQL client/Docker tooling were unavailable there; this is recorded as non-authoritative and no zero-difference claim was made.
- Did not create a dump, restore data, create/drop a database, modify Docker resources, edit `.env`, create/apply/stamp migrations, or change routes/auth/write/game content.

# v289 - PostgreSQL FLOAT alias normalization and handoff cleanup

- Normalized PostgreSQL `FLOAT` aliases in the read-only schema checker so SQLAlchemy `FLOAT` and reflected `DOUBLE PRECISION` are compared as the same storage type.
- Added smoke coverage for `FLOAT`, `FLOAT(24)`, `FLOAT(25)`, `REAL`, and `DOUBLE PRECISION` normalization.
- Updated and registered the canonical next-chat handoff smoke.
- Removed generated `backend/idle_rpg_backend.egg-info/`, added `*.egg-info/` to `.gitignore`, removed duplicate `backend/env.example`, and synchronized current/root/handoff docs.
- Did not change PostgreSQL schema/data, Docker resources, `.env`, seed, Alembic revisions, routes, response bodies, authentication, or write logic.

# v288 - PostgreSQL schema equivalence read-only preflight

- Added `tools/check_postgres_schema_equivalence.py` to compare live PostgreSQL tables, columns, types, nullability, PK, FK, unique constraints, indexes, and check constraints with SQLAlchemy metadata.
- Added `docs/archive/postgres-baseline/POSTGRES_SCHEMA_EQUIVALENCE_CHECK.md` and a dedicated core smoke.
- Kept DB schema/data, Docker resources, env, seed, revisions, migration apply/stamp, API contracts, auth, and write behavior unchanged.

# v287 - Windows subprocess decode fix and baseline strategy confirmation

- Fixed the user-reproduced Windows `cp949`/UTF-8 mixed Docker output `UnicodeDecodeError` with `tools/_safe_subprocess.py`.
- Applied safe decoding to PostgreSQL runtime, prerequisite, and Alembic read-only checkers.
- Recorded the actual DB result: PostgreSQL 16.14, 22 model/public tables, 748 rows, no `alembic_version`, healthy DB endpoint.
- Confirmed `existing-schema-without-alembic-baseline` and the existing-data-preserving baseline strategy.

# v286 - PostgreSQL/Alembic baseline strategy plan

- Added a decision matrix for empty DB, existing create_all schema with preserved data, and schema drift.
- Requires backup/restore rehearsal and separate empty-DB migration verification before any baseline stamp.
- Kept revision creation, upgrade, downgrade, stamp, DB schema/data, Docker resources, and env unchanged.

# v285 - PostgreSQL runtime read-only state checker

- Added `tools/check_postgres_runtime_readonly_state.py` for read-only Docker status, PostgreSQL schema/table/row counts, model-table comparison, Alembic version state, and FastAPI DB health.
- Added automatic classifications: `empty-database`, `existing-schema-without-alembic-baseline`, `schema-drift`, and `alembic-managed`.
- Added a dedicated smoke and registered it in core smoke.
- The checker never starts/stops Docker, mutates SQL data/schema, edits env, or runs migration mutation commands.

# v284 - Alembic asyncpg online env fix

- Fixed the user-reproduced `sqlalchemy.exc.MissingGreenlet` from `python -m alembic current`.
- Replaced sync `engine_from_config()` with `async_engine_from_config()`, async connection handling, and `connection.run_sync()`.
- Added `tools/check_alembic_readonly_state.py` for read-only `history`, `heads`, and `current` collection.
- Added a dedicated Alembic async env smoke and registered it in core smoke.
- Recorded that the actual backend virtualenv is `backend/.venv`.
- Kept DB schema/data, Docker volume, env, seed, revisions, migration apply/stamp, routes, API bodies, auth, and write logic unchanged.

# v283 - PostgreSQL/Alembic prerequisite checker

- Added `tools/check_postgres_alembic_prerequisites.py`, a read-only local checker for Python, virtualenv, Docker, Compose, SQLAlchemy, Alembic, asyncpg, psycopg, and required project files.
- Added `docs/archive/postgres-baseline/POSTGRES_ALEMBIC_LOCAL_CHECKLIST.md` with exact install locations, `.venv` states, and dangerous commands that remain forbidden.
- The checker never connects to the DB, starts Docker, changes `.env`, or runs migrations.

# v282 - PostgreSQL/Alembic readiness report

- Added `tools/report_postgres_alembic_readiness.py` and `docs/current/POSTGRES_ALEMBIC_READINESS.md`.
- Documented 22 SQLAlchemy tables, PostgreSQL-specific types, asyncpg/psycopg responsibilities, Docker settings, and the current Alembic state with zero revisions.
- Recorded missing `versions/` and `script.py.mako`, create_all ownership, async online execution verification risk, and destructive reset/down-volume commands.
- Added `tools/smoke/backend/smoke_postgres_alembic_readiness.py`.
- Kept DB schema/data, Docker volumes, env, seed, route paths, response bodies, auth, Write Guard, write logic, and game content unchanged.

# v281 - Vue admin related-row detail navigation

- Added read-only related-row detail navigation from the relations panel.
- Preserves prior selections in a local `selectionHistory` stack and adds `이전 상세로` without changing routes or write behavior.
- Clears history when the domain/catalog selection is reset.

# v280 - Vue admin read-only relations panel

- Added `AdminMasterRelationsPanel.vue` for `GET /admin/master-data/relations`.
- Displays backend-provided relation groups, compact columns/rows, counts, limited indicators, and loading/error/empty/success states.
- Uses `limit=20`, cancels stale requests, and never requests raw JSON/assets or mutation APIs.
- Added a dedicated read-only relations/navigation smoke.
- Kept DB, env, seed, auth, route paths, API response bodies, Write Guard, Preview/Apply request bodies, and actual write logic unchanged.

# v279 - Vue admin read-only detail panel

- Added `AdminMasterDetailPanel.vue` for `GET /admin/master-data/detail`.
- Displays scalar fields, relation hints, sanitized JSON previews, asset hiding state, and warnings without calling relations or write APIs.
- Improved `/admin/requirements` summary from `-` to `준비 완료` using the existing `readOnlyOverviewReady` response field.
- Kept DB, env, seed, auth, route paths, API response bodies, Write Guard, Preview/Apply request bodies, and actual write logic unchanged.

# v278 - Vue admin catalog query controls

- Added search, enabled/disabled filtering, safe sort selection, and previous/next pagination using the existing catalog GET query contract.
- Resets filters/page when the domain changes and clears stale detail selection whenever the catalog is reloaded.
- Keeps page size at 20 and cancels stale requests with `AbortController`.
- Added no library or framework.

# v277 - Vue admin read-only catalog mini panel

- Added `AdminMasterDomainPanel.vue` for `GET /admin/master-data/domains`.
- Added `AdminMasterCatalogMiniPanel.vue` for the selected domain first page using `limit=20`, `page=1`, `sort=id_asc`.
- Added loading/error/empty/success states, domain selection, generic backend column/row rendering, and stale request cancellation.
- Added dedicated Vue read-only catalog smoke and documentation.
- Kept DB, env, seed, auth, route paths, API response bodies, Write Guard, Preview/Apply request bodies, and actual write logic unchanged.

# v276 - Vue admin read-only domain panel

- Connected `GET /admin/master-data/domains` to the Vue admin shell.
- Parsed the actual response from `payload.domains` and `payload.defaultDomain`.
- Added domain counts, retry, and loading/error/empty/success states.
- No new library or framework was added.

## v275.backend-route-map-report

- Added `tools/report_backend_route_map.py` to generate/check a deterministic backend route map without importing `app.main`.
- Added `docs/current/BACKEND_ROUTE_MAP.md` with all 27 FastAPI routes, GET/POST counts, Vue read-only candidates, and postponed Preview/Apply/write routes.
- Added `tools/smoke/backend/smoke_backend_route_map_report.py` and included it in `tools/run_smoke_core.sh`.
- Updated `frontend/vue-app/src/api/adminReadOnlyApi.js` so master-data detail/relations wrappers translate `rowId` to the backend query name `id`.
- Confirmed that route paths, API response bodies, DB, env, seed, auth, Write Guard, Preview/Apply request bodies, write logic, existing smoke/contract meaning, and game content remain unchanged.

## v274.backend-structure-plan

- Added `tools/report_backend_structure_plan.py` to generate/check a deterministic backend structure plan.
- Added `docs/current/BACKEND_STRUCTURE_PLAN.md` with current route/service/schema/model/db/core responsibilities.
- Added `tools/smoke/backend/smoke_backend_structure_plan.py` to guard that the structure plan stays up to date.
- Confirmed that route paths, API response bodies, DB, env, seed, auth, Write Guard, Preview/Apply request bodies, write logic, existing smoke/contract meaning, and game content remain unchanged.

## v272.vue-readonly-api-smoke-screen

- Added `healthReadOnlyApi` for safe `GET /health` and prepared `GET /health/db` without auto-calling DB health.
- Added `ReadOnlyApiStatusPanel.vue` to show loading/success/error states and a retry button inside the Vue shell.
- Connected `/game` to safe `GET /health` status checking and `/admin` to safe `GET /health` plus `GET /admin/requirements` status checking.
- Added `smoke_vue_readonly_api_status_panel.py` and included it in `tools/run_smoke_vue_shell.sh`.
- Kept legacy `index.html`, `admin.html`, root `src/`, route paths, API response bodies, DB, env, seed, auth, Write Guard, Preview/Apply body, write logic, and game content unchanged.

## v269.legacy-path-dependency-report

- Added `tools/report_legacy_path_dependencies.py` to generate/check a legacy path dependency report before Vue/FastAPI/DB transition work.
- Added `docs/current/LEGACY_PATH_DEPENDENCIES.md` with current high-risk legacy path references, HTML direct-load relationships, and core smoke path dependencies.
- Decided that the future Vue app should be created under `frontend/vue-app/` instead of reusing the root `src/` folder.
- Kept `admin.html`, `index.html`, existing `src/`, backend routes/services, DB, env, seed, auth, API response bodies, write guards, and actual write logic unchanged.

## v268 - Project structure transition prep

- 현재 ZIP 기준으로 `admin.html`, `index.html`, `src`, `backend`, `tools`, `docs`의 역할을 다시 정리했습니다.
- Vue/FastAPI/DB 전환을 위해 보존/이식/대체 후보를 문서화했습니다.
- smoke/contract가 직접 참조하는 legacy 경로 의존성을 1차 분석했습니다.
- `admin.html`, `index.html`, `src/api`, `src/api/admin`, `backend/app/api/routes`, `backend/app/services`는 당장 이동하지 않는 것으로 결정했습니다.
- `docs/current/PROJECT_STRUCTURE.md`, `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`, `docs/NEXT_STEPS.md`, `docs/current/ROADMAP.md`, 인계 문서를 갱신했습니다.
- 런타임 코드, DB, env, seed, route path, API response body, auth, write guard, 실제 write 로직은 변경하지 않았습니다.

## v266 - Admin practical UX polish after feedback

- v262의 `보기 방식` 선택은 롤백해 `마스터 데이터 카탈로그`를 다시 단일 목록으로 정리했습니다.
- 카탈로그 필터 행은 기존처럼 한 줄에 더 잘 들어가도록 `보기 방식` 필드를 제거하고 버튼 위험도 텍스트 chip을 제거했습니다.
- 버튼 위험도는 `조회/Preview/적용주의/고위험` 문구를 버튼 안에 추가하지 않고 색상과 tooltip으로만 전달하도록 변경했습니다.
- 긴 값 미리보기 너비를 기존보다 줄여 표 셀이 덜 늘어나게 했습니다. 전체 값은 기존 `전체` 모달에서 확인합니다.
- 상세 화면 상단의 `API 반영 확인`, `연결 항목`, `필드 도움말` 바로가기 버튼은 클릭 시 관련 카드/섹션으로 이동하거나 펼쳐지도록 보완했습니다.
- 새 파일 `src/api/admin/admin-detail-shortcuts.js`를 추가했습니다. 이 파일은 화면 이동/펼치기만 담당하며 API 호출, fetch, write 로직을 사용하지 않습니다.
- DB/env/seed/API body/route/auth/write guard/실제 write 로직은 변경하지 않았습니다.

## v260 - Admin catalog date/limit/json keys UX

- `마스터 데이터 카탈로그`의 수정 시각 계열 셀은 화면에 `YYYY-MM-DD` 일자만 표시하고, 값 옆 `?` tooltip에서 초 단위 상세 시각을 확인하도록 정리했습니다.
- 카탈로그 `표시 개수` 선택지를 `10`, `30`, `50`, `100` 네 개로 제한하고 기본값을 `10`으로 변경했습니다.
- `JSON 키` 셀은 앞 3개 키만 chip으로 표시하고 남은 키는 `외 N개`로 접으며, 전체 키 목록은 `?` tooltip에서 확인하도록 변경했습니다.
- 새 문서 `docs/ADMIN_CATALOG_DATE_LIMIT_JSON_KEYS_UX.md`를 추가했습니다.
- DB/env/seed/API body/route/auth/write guard/실제 write 로직은 변경하지 않았습니다.

## v259 - Admin catalog compact help UX

- `마스터 데이터 카탈로그` 필터와 결과 목록을 하나의 섹션으로 합쳐 같은 탭 안에서 조회 조건과 결과를 확인하도록 정리했습니다.
- 카탈로그 셀의 긴 설명문을 제거하고 `normal · 일반 장비`, `6 · 특수무기`처럼 핵심 라벨만 표시하도록 변경했습니다.
- 자세한 설명은 표 제목/입력칸 옆 `?` 도움말과 tooltip으로 이동했습니다.
- `필드 용어 도움말`을 기본 필드, 아이템·장비, 스킬·전투·보상, 관계·드랍·강화 기준으로 확장했습니다.
- `formatCatalogCellValue()`를 추가해 카탈로그/관계 표가 공통 compact 표시 규칙을 사용하도록 했습니다.
- 새 Smoke `smoke_admin_catalog_help_compact_ux.js`를 추가하고 전체 Smoke에 포함했습니다.
- DB/env/seed/API body/route/auth/write guard/실제 write 로직은 변경하지 않았습니다.

## v258 - Admin workspace navigation UX

- 관리자 페이지 상단에 `Admin Workspace` 작업 시작 허브를 추가했습니다.
- 조회·상세 확인, 신규 row 생성, 편집·적용 검토, Preview 화면 점검, 변경 이력·Rollback 5개 업무 모드로 화면 진입점을 분리했습니다.
- 업무 모드를 누르면 관련 섹션만 펼쳐지고, 확인 순서/주의사항/주요 버튼을 안내하는 모달이 표시됩니다.
- 사이드바에도 업무 모드 바로가기를 추가해 긴 관리자 페이지에서 목적지를 빠르게 찾을 수 있습니다.
- 전체 보기/보조 섹션 접기 버튼을 추가해 한 화면에 너무 많은 정보가 보이는 문제를 줄였습니다.
- 새 UI는 `src/api/admin/admin-workspace-navigation.js`에 분리했으며 API 호출, fetch, apply/write helper 호출을 하지 않습니다.
- DB/env/seed/API body/route/auth/write guard/실제 write 로직은 변경하지 않았습니다.

## v257 - Admin readiness pageReady alias

- `checkAdminReadOnlyPageReady()` 반환 객체에 `pageReady` 별칭을 추가했습니다.
- 기존 `ok` 필드는 그대로 유지하여 기존 Smoke/호출과 호환됩니다.
- 기호가 브라우저 콘솔에서 `ready.pageReady`를 바로 확인할 수 있도록 ReadOnly smoke에 alias 검사를 추가했습니다.
- DB/env/seed/API body/route/auth/write guard/실제 write 로직은 변경하지 않았습니다.

## v250.1 - frontend readiness return hotfix

- Fixed four v247-v250 readiness values that were calculated internally but omitted from `getAdminBackendServiceSplitContractReadiness()` return object.
- Strengthened backend/frontend parity smoke to verify internal calculation, internal return, public calculation, and final public return for every registered contract readiness value.
- No DB, env, seed, route, schema, response body, authentication, or write-guard changes.

## v246.2 - Backend editable-install packaging hotfix

- Added an explicit setuptools build backend and package discovery rule.
- Editable installs now include only `backend/app*` and exclude `alembic`, `seeds`, `sql`, and tests from package discovery.
- Added `tools/smoke/backend/smoke_backend_packaging_contract.py` to prevent the flat-layout discovery error from returning.
- No DB, API route, response body, authentication, seed, or write-guard changes.

# Changelog

## v246.1 — project cleanup and handoff refresh

- Refreshed root/readiness/current-status/next-step documents to v246.
- Removed packaged Windows `.venv`, local `backend/.env`, Python caches, and compiled files.
- Moved the completed v240 next-step note to `docs/archive/stage-notes/`.
- Added `httpx2` to backend dev dependencies for FastAPI TestClient smoke contracts.
- Kept runtime code, DB, seed, routes, schemas, response bodies, authentication, and write guards unchanged.

## v246.backend-admin-write-replay-safety-contract

- Added isolated repeated-preview parsing checks for all five preview request models.
- Verified all five apply route functions still bind `_write_guard` to `ADMIN_WRITE_GUARD_DEP`.
- Explicitly records that `Idempotency-Key` is not currently supported; no replay-protection behavior is claimed or added.
- Service calls and DB write attempts remain zero.
- Added backend/frontend parity coverage and admin readiness marker `backendWriteReplaySafetyContractReady`.
- Route paths, API response bodies, schemas, DB, env, seed, authentication, and splitStatus are unchanged.

## v245.backend-admin-transport-header-observation-contract

- Added `admin_request_transport_header_observation_contract.py` and its smoke test.
- Observes duplicate `Content-Type`/`Accept`, declared `Content-Length`, and `Transfer-Encoding` at the ASGI/TestClient boundary without claiming wire-level enforcement.
- Keeps service and DB execution counts at zero.
- Added `backendRequestTransportHeaderObservationContractReady` to admin readiness.
- Strengthened backend/frontend parity smoke to compare the complete ordered `extractedFiles` and `routeContract` lists and all v240-v245 readiness links.
- No route, response body, DB, env, seed, authentication, or write-guard changes.

## v245.backend-admin-transport-header-observation-contract

- Added isolated FastAPI contract coverage for UTF-8 Korean/symbol payloads.
- Added Content-Type parameter and header-name case normalization checks.
- Added malformed UTF-8 byte compatibility outcomes without service or DB execution.
- Kept route paths, response bodies, DB, env, seed, auth, and write guards unchanged.

# Changelog

## v245.backend-admin-transport-header-observation-contract

- Added `admin_request_media_size_boundary_contract.py` and its smoke test.
- Frozen octet-stream, URL-encoded form, multipart form, empty binary, and arbitrary binary request parsing boundaries without calling admin services or the DB.
- Added a 64 KiB JSON probe to document that the FastAPI application currently has no explicit request-body size limit.
- Declared request-size enforcement ownership as deployment proxy/server configuration rather than silently changing live API behavior.
- Added backend/frontend readiness synchronization and `backendRequestMediaSizeBoundaryContractReady`.
- Kept route paths, response bodies, schemas, write guards, DB, env, seed, and splitStatus unchanged.

## v242.1 frontend/runtime compatibility hotfix

- Fixed the `json-without-content-type` contract for Starlette/FastAPI version differences.
- Accepts either a decoded JSON `200` response or a stable `422 model_attributes_type` response.
- Still strictly validates response content type, payload, and stable error fields.
- DB, env, seed, routes, response bodies, auth, and write guards are unchanged.

## v242.backend-admin-request-content-negotiation-contract

- Added isolated FastAPI request-boundary checks for `application/json; charset=utf-8` and JSON bodies without a Content-Type header.
- Added stable 422 checks for top-level JSON arrays/strings.
- Froze the difference between an empty JSON object (`body.domain` missing) and a completely empty body (`body` missing).
- Verified that both `Accept: application/json` and `Accept: text/plain` keep the default JSON response content type.
- Service calls and DB writes remain zero; route paths, API response bodies, DB, env, seed, auth, and write guards are unchanged.

## v239.2 final handoff cleanup

- Updated next-chat prompt and handoff docs with the latest confirmed working state.
- Added project working rules and v240 request payload validation planning doc.
- Cleaned transient caches/log candidates from the handoff package.
- No runtime code, API path, response body, DB, or env changes.


## v239.2.backend-admin-schema-model-shared-collector-hotfix

- Updated the admin schema/model contract to reuse `collect_admin_runtime_route_entries()` instead of scanning `app.routes` directly.
- Fixes Windows/FastAPI environments where request metadata passed but schema/model route body checks returned `actualModel: None`.
- Added a smoke guard so the schema/model contract cannot reintroduce a direct `app.routes` scan.
- Kept v239.1 Pydantic required-field compatibility helpers unchanged.
- No API path, response body, DB, or env changes.

## v239 - backend admin shared runtime route collector hotfix

- Centralized admin runtime route collection in `collect_admin_runtime_route_entries()`.
- Request metadata now reuses the same app/api_router/owner-router fallback chain as runtime, operation, and response metadata contracts.
- Fixes Windows/FastAPI environments where runtime route smoke passed but request metadata still saw `runtimeRouteCount: 0`.
- API paths, response bodies, DB schema, and environment files remain unchanged.


## v238.6 - backend admin runtime mounted-app hotfix

- Runtime admin route collector now traverses Starlette/FastAPI containers that expose child routes through `node.app.routes` or `node.app.router.routes`.
- Admin page readiness now exposes `failedChecks` and `readinessChecks` so `ok: false` identifies the exact blocking checks.
- API paths, response bodies, DB schema, and environment files remain unchanged.

## v238.9 - backend admin OpenAPI f-string hotfix

- Reworked the default OpenAPI operation-id helper to normalize the route path before interpolation.
- Removes the Python syntax error caused by a regex backslash inside an f-string expression on Windows/Python versions that reject it.
- Runtime, operation, OpenAPI, response metadata, request metadata, and compile smokes pass.
- API paths, response bodies, DB schema, and environment files remain unchanged.

## v240 frontend readiness contract hotfix

- Fixed the admin page static backend split contract so the v240 payload validation file and 422 rule are included.
- Prevented `backendServiceSplitContractReady` from cascading all backend readiness checks to false.
- Added smoke assertions that keep the frontend and backend contract lists synchronized.

## v241.backend-admin-validation-error-compatibility-contract

- Added `admin_request_payload_validation_contract.py` to freeze normal admin request alias serialization.
- Added representative FastAPI 422 `detail` checks for all 10 admin body request schemas.
- Validation runs in an isolated FastAPI app and stops before service or database execution.
- Preserved all admin route paths, response body shapes, write guards, DB settings, env settings, and seed data.
- Added the v240 smoke to `tools/run_smoke_core.sh` and updated admin readiness version.


## v241
- Added malformed JSON, empty body, and unsupported content-type FastAPI 422 compatibility contract.
- Stable contract fields: type, loc, msg. Excluded version-sensitive input and ctx.
- No DB/env/seed/route/response-body changes.

## v247-v250 admin preview/mutation/diff/rollback safety
- Added static preview side-effect and apply mutation-boundary contracts.
- Added deterministic pure admin diff engine.
- Added detached, fingerprinted rollback snapshot helpers.
- Kept DB, env, seed, routes, schemas, response bodies, auth, and write guards unchanged.

## v250.2 project organization and preview integration

- docs를 current/contracts/handoff/archive 역할로 정리
- smoke 파일을 frontend/contracts/backend/game으로 분류하고 모든 참조 경로 갱신
- backend 계약을 기준으로 frontend extractedFiles/routeContract를 동기화하는 도구 추가
- preview 응답에 optional unifiedDiff/rollbackSnapshot 필드 추가
- 생성/수정/rollback/create-delete/restore 관리자 UI에 공통 Diff 표시
- 기존 API 필드, DB, env, seed, 인증, write guard 변경 없음

## v261-v265.admin-practical-ux-bundle

- 관리자 첫 진입 화면에 처음 사용하는 추천 순서와 버튼 안전도 안내를 추가했습니다.
- 마스터 데이터 카탈로그에 기본 보기/자세히 보기/JSON 보기 프리셋을 추가했습니다.
- 긴 카탈로그 값은 표에서 축약하고 `전체` 버튼으로 모달에서 확인하도록 개선했습니다.
- 관리자 버튼에 조회/Preview/적용주의/고위험 위험도 라벨을 자동 표시합니다.
- 선택한 마스터 데이터 상세 화면에 요약과 다음 행동 안내를 추가했습니다.
- DB/env/seed/auth/route/API body/Write Guard/실제 write 로직은 변경하지 않았습니다.
## v267.next-chat-handoff-ready

- 다음 채팅에서 바로 이어갈 수 있도록 root/docs handoff prompt를 최신 v266 기준으로 정리했습니다.
- 오래된 v250/v260 중심 인계 문구를 v267/Vue-FastAPI-DB 전환 방향으로 갱신했습니다.
- `docs/current/VUE_FASTAPI_DB_TRANSITION_PLAN.md`를 추가했습니다.
- `docs/current/CURRENT_STATUS.md`, `docs/current/ROADMAP.md`, `docs/NEXT_STEPS.md`, `README.md`, `README_BACKEND_READY.md`를 최신 방향에 맞게 정리했습니다.
- 런타임 코드, DB, env, seed, 인증, route, API 응답 body, Write Guard, 실제 write 로직은 변경하지 않았습니다.

## v271.vue-readonly-api-client

- Added Vue read-only API client preparation files under `frontend/vue-app/src/api/`.
- Added GET-only route constants for admin/game/health read APIs.
- Added `requestReadOnly` fetch wrapper without write methods.
- Updated AdminShell/GameShell to display prepared GET route lists without auto-calling APIs.
- Added Vue read-only API smoke coverage.
- Updated current docs, handoff docs, and next-step guidance for v272.
- Did not change DB/env/seed/auth/API response body/route paths/write logic/Write Guard/Preview Apply bodies/game content.

## v270.vue-app-basic-shell

- Added a separated Vite + Vue shell under `frontend/vue-app/`.
- Added basic Vue Router routes for `/game` and `/admin` without replacing legacy `index.html` or `admin.html`.
- Added `GameShell.vue`, `AdminShell.vue`, `ShellCard.vue`, and base shell CSS.
- Added Vue shell structure smoke: `tools/smoke/frontend/smoke_vue_shell_structure.py`.
- Added Vue shell smoke runner: `tools/run_smoke_vue_shell.sh`.
- Documented required user install step: `npm install` in `frontend/vue-app`.
- Preserved DB, env, seed, auth, route paths, API response bodies, write guards, write logic, Preview/Apply request bodies, and existing smoke/contract meaning.
## v273.local-dev-cors-vue-fix

- Fixed the local Vue dev server CORS issue reported from `http://127.0.0.1:5173` to `http://127.0.0.1:8000/api/v1/*`.
- Added local/debug fallback CORS origins in `backend/app/core/config.py` so older local `.env` values that omit Vite port `5173` do not block read-only Vue API checks.
- Production CORS behavior remains explicit: production/debug-false settings do not auto-append local dev origins.
- Added `tools/smoke/backend/smoke_backend_local_cors.py` and included it in `tools/run_smoke_core.sh`.
- Added `docs/current/LOCAL_DEV_CORS.md`.
- Did not change `.env`, DB, seed, auth, route paths, API response body, write logic, Write Guard, Preview/Apply request bodies, or game content.



## v293.postgres-restore-rehearsal-execute-tool

- Added `tools/restore_postgres_rehearsal_database.py`.
- Pinned restore source to the exact verified v291 custom archive and SHA-256.
- Required the v292 target DB to exist and remain empty before restore.
- Added single-transaction/exit-on-error pg_restore boundary without create, clean, or drop.
- Added target table/row/table-count/schema-equivalence verification and source before/after checks.
- Added `tools/smoke/backend/smoke_postgres_restore_rehearsal.py` and core smoke registration.
- Updated current/readiness/handoff documentation to v293.
- Did not execute restore in the handoff build environment and did not include local backup artifacts in the ZIP.

## v296.postgres-initial-alembic-revision-placeholder-recovery

- v295 first autogenerate attempt가 만든 empty `alembic_version` placeholder를 정상 recovery state로 분류
- `--inspect-workspace` read-only 진단 추가
- application table/row/revision 존재 시 generation 전 차단
- pristine 0-table DB에서 새 control table 생성 차단
- existing placeholder 재사용 후 revision/autoreview 성공 경계 수정
- PostgreSQL readiness, handoff, smoke, current docs v296 동기화

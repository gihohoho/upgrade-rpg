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

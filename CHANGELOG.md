
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
